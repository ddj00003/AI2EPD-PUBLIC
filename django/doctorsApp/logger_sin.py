import logging
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _

class LoggerSingleton:
    """
    A class implementing the Singleton pattern for a logger instance.

    Attributes:
    __instance (Logger): The instance of the logger.

    Methods:
    __init__(): Initializes the logger instance.
    getInstance(): Returns the logger instance.
    """
    __instance = None

    def __init__(self):
        """
        Initializes the logger instance.
        """
        if LoggerSingleton.__instance is None:
            LoggerSingleton.__instance = logging.getLogger(__name__)
            LoggerSingleton.__instance.setLevel(logging.DEBUG)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            file_handler = logging.FileHandler('log.txt')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)

            LoggerSingleton.__instance.addHandler(file_handler)

    @staticmethod
    def getInstance():
        if LoggerSingleton.__instance is None:
            LoggerSingleton()
        return LoggerSingleton.__instance

def log_exceptions(func):
    """
    A decorator function that logs exceptions.

    Args:
    func (callable): The function to be wrapped.

    Returns:
    callable: The wrapped function.
    """
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            logger = LoggerSingleton.getInstance()
            logger.exception(msg =str(e))
            context ={
                    'error_code': _('Error 500 - Internal Server Error'),
                    'error_title': _('Error de servidor'),
                    'error_description': _('Ha ocurrido un error en el servidor. Contacta con el administrador.'),
                }
            return render(request, template_name='startPage/error.html', context=context)

    return wrapper

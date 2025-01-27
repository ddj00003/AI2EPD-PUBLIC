from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
import time


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            group = request.user.groups.all()[0].name if request.user.groups.exists() else None

            if group in allowed_roles: 
                return view_func(request, *args, **kwargs)
            else:
                context ={
                    'error_code': 'Error 403 - Forbidden',
                    'error_title': _('No estás autorizado'),
                    'error_description': _('Página reservada para la administración del sistema. Si deberías tener acceso, contacta con el administrador.'),
                }
                return render(request, 'adminManager/error.html', context=context)
        return wrapper_func
    return decorator

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Tiempo de ejecución de '{func.__name__}': {end_time - start_time} segundos")
        return result
    return wrapper
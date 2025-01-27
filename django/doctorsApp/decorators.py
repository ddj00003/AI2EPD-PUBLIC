from django.shortcuts import render
from django.utils.translation import gettext_lazy as _


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
                    'error_description': _('Página reservada para la monitorización de los pacientes. \
                        Si deberías tener acceso, contacta con el administrador.'),
                }
                return render(request, 'doctorsApp/error.html', context=context)
        return wrapper_func
    return decorator
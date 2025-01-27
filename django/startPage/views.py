from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, signals
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from . import  forms
from . logger_sin import log_exceptions


# Create your views here.

login_url_string='/login'

@login_required(login_url=login_url_string)
@log_exceptions
def main(request):
    context = { 'user': User.get_full_name(request.user), 'group': str(request.user.groups.all()[0]) }
    return render(request, 'startPage/home.html', context = context)

def singin(request):
    """
    Maneja la vista de inicio de sesión.
    """
    if request.method == 'POST':
        form = forms.Login(request.POST)

        if form.is_valid():
            # Autenticar al usuario y redirigirlo a la página de inicio.
            user = authenticate(
                request=request,
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password'),
            )

            if user is not None:
                login(request, user)
                return redirect('startPage:home')

        # Mostrar un mensaje de error si el usuario no puede autenticarse.
        error_msg = _('Usuario o contraseña incorrectos')
    else:
        # Mostrar la página de inicio de sesión.
        form = forms.Login()
        error_msg = None

    context = {
        'form': form,
        'error': error_msg,
    }

    return render(request, 'startPage/login.html', context)


@login_required(login_url=login_url_string)
@log_exceptions
def singout(request):
    logout(request)
    return redirect('startPage:login')

@log_exceptions
def lockout(request, credentials, *args, **kwargs):
    context ={
                    'error_code': 'Error 403 - Forbidden',
                    'error_title': _('Error de inicio de sesión'),
                    'error_description': _('Has superado el número de intentos de inicio de sesión. \
                        Contacta con el administrador para desbloquear tu cuenta.'),
                }
    return render(request, 'startPage/error.html', context=context)
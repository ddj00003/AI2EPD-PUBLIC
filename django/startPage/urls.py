from django.urls import path
from . import views

app_name = 'startPage'
urlpatterns = [
    path('', views.main, name='home'),
    path('login', views.singin, name='login'),
    path('logout', views.singout, name='logout'),
    path('lockout', views.lockout, name='lockout')
]
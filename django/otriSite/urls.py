"""otriSite URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ASIA/', include('adminManager.urls')),
    path('IA2EPD/', include('doctorsApp.urls')),
    path('api/v1/', include('apiRest.urls')),
    path('', include('startPage.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

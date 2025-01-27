from otriSite.settings.base import *
from otriSite.logging import *
from dotenv import load_dotenv
import os

load_dotenv(Path.joinpath(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False   

ALLOWED_HOSTS = ['*']

LOCAL_APPS += [
    'adminManager',
    'doctorsApp',
    'startPage',
    'apiRest',
]

THIRD_PARTY_APPS += [
    'crispy_forms',
    'crispy_bootstrap5',
    'bootstrap_datepicker_plus',
]

INSTALLED_APPS = BASE_APPS + THIRD_PARTY_APPS + LOCAL_APPS

LOCAL_MIDDLEWARE += [
    'otriSite.middleware.FixForwardedHostMiddleware',
]

MIDDLEWARE = BASE_MIDDLEWARE + LOCAL_MIDDLEWARE + THIRD_PARTY_MIDDLEWARE

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://192.168.48.8:8000'
    'https://asia.ujaen.es/ai2epd/',
    'http://asia.ujaen.es/ai2epd/',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO','https')

USE_X_FORWARDED_HOST = True

FORCE_SCRIPT_NAME = "/ai2epd"

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SESSION_COOKIE_AGE = 60 * 60 * 6

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

#STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

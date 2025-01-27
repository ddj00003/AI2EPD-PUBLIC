from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-w+deo&cn!+v)pm&dn3r@6nrch-0qx2$nfr_^yqlz7q9ka(lqk3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

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

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"
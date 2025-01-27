#! /bin/bash

/usr/sbin/crond -f
gunicorn --bind :8000 --workers 3 otriSite.wsgi:application


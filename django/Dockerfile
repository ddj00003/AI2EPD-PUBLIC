FROM python:3.11.4-slim-bullseye

RUN adduser --system --no-create-home --force-badname djangoUser

WORKDIR /SisCAH_app

ENV TZ 'Europe/Madrid'
RUN echo $TZ > /etc/timezone

RUN apt update \
 && apt install -y python3-dev libpq-dev gcc coreutils \
 && pip install --upgrade pip

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

#USER djangoUser

CMD ["gunicorn", "--bind", ":8000", "--workers", "5", "otriSite.wsgi:application"]


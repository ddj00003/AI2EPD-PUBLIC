FROM python:3.11.2-slim-bullseye

#WORKDIR /App

ENV TZ 'Europe/Madrid'
RUN echo $TZ > /etc/timezone

RUN apt update \
 && apt install -y python3-dev libpq-dev gcc coreutils cron curl \
 && pip install --upgrade pip

ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.2.1/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=d7f4c0886eb85249ad05ed592902fa6865bb9d70

RUN curl -fsSLO "$SUPERCRONIC_URL" \
 && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
 && chmod +x "$SUPERCRONIC" \
 && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
 && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic

WORKDIR /app

COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY crontab crontab
COPY check_devices.py /app/check_devices.py
COPY .env /app/.env
COPY email_sender.py /app/email_sender.py

RUN chmod 0774 crontab
RUN chmod 0774 /app/check_devices.py
RUN chmod 0774 /app/email_sender.py

CMD supercronic crontab
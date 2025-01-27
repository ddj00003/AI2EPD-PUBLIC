FROM nginx:1.25.1-alpine

ENV TZ 'Europe/Madrid'
RUN echo $TZ > /etc/timezone

COPY ./default.conf /etc/nginx/conf.d/default.conf
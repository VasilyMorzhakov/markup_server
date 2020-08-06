FROM tiangolo/uwsgi-nginx-flask:python3.8

COPY ./confd_nginx.conf /etc/nginx/conf.d/nginx.conf
COPY ./app /app

RUN apt update && apt install -y ca-certificates && update-ca-certificates --fresh
RUN pip install -r /app/requirements.txt
FROM python:3.10-slim-bookworm

RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list.d/debian.sources
RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

ADD ./requirements.txt /tmp/requirements.txt

RUN apt-get update && apt-get install -y libcurl4-openssl-dev libffi-dev libxml2-dev libmariadb-dev\
  && pip install -r /tmp/requirements.txt && pip install gunicorn gevent

ADD ./deploy/wait-for-it.sh /wait-for-it.sh
ADD ./deploy/entrypoint.sh /entrypoint.sh

ADD ./server /server

WORKDIR /server

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "--worker-class=gevent", "--workers", "1", "--bind", "0.0.0.0:8888", "-t", "600", "--keep-alive", "60", "--log-level=info", "server:app"]

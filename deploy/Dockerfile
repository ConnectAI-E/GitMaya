FROM python:3.8-bullseye

RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list
RUN sed -i "s@http://security.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list
RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

ADD ./requirements.txt /tmp/requirements.txt

RUN apt-get update && apt-get install -y libcurl4-openssl-dev libffi-dev libxml2-dev libmariadb-dev g++\
  && pip install -r /tmp/requirements.txt && pip install gunicorn gevent

ADD ./server /server

WORKDIR /server

CMD ["gunicorn", "--worker-class=gevent", "--workers", "1", "--bind", "0.0.0.0:8888", "-t", "600", "--keep-alive", "60", "--log-level=debug", "server:app"]

FROM python:3.7
ENV PYTHONUNBUFFERED 1

RUN mkdir /app
COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD gunicorn coronahjalpen.wsgi -k gevent --worker-connections $WORKER_CONNECTIONS --bind 0.0.0.0:$PORT --max-requests 10000 --max-requests-jitter 1000 --access-logfile -

web: gunicorn coronahjalpen.wsgi -k gevent --worker-connections $WORKER_CONNECTIONS --bind 0.0.0.0:$PORT --max-requests 10000 --max-requests-jitter 1000 --access-logfile -

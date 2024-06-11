web: gunicorn Uptrackr.wsgi --log-file -
worker: python manage.py rqworker --url "${REDIS_URL}" default


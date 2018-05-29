newrelic-admin run-program celery -A app:celery -Q intelligence worker --concurrency=4 -l info

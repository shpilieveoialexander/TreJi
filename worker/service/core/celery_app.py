import os

from celery import Celery

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend="rpc://",
)

celery_app.conf.task_routes = {"service.tasks.delay.test_celery": "main-queue"}

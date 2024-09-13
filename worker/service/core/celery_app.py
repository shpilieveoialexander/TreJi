import os

from celery import Celery

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend="rpc://",
)

celery_app.conf.task_routes = {"service.tasks.delay.test_celery": "main-queue"}
celery_app.conf.task_routes = {"service.tasks.delay.send_invite": "mail-queue"}
celery_app.conf.task_routes = {"service.tasks.delay.task_assign_confirm": "mail-queue"}
celery_app.conf.task_routes = {
    "service.tasks.delay.task_unassign_confirm": "mail-queue"
}

# This file for delay tasks
from service.core.celery_app import celery_app


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"Test task return {word}"

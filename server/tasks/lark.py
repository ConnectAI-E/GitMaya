import logging

from celery_app import celery


@celery.task()
def test_task():
    logging.error("test_task")
    return 1

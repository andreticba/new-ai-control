# core/tasks/ingest.py
from celery import shared_task

@shared_task
def process_inbound_message(*args, **kwargs):
    pass

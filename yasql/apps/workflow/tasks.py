# -*- coding:utf-8 -*-
# by pandonglin
from celery import shared_task
from django.utils import timezone
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(queue='workflow', acks_late=False)
def run_task(ticket):
    """处理任务"""
    pass

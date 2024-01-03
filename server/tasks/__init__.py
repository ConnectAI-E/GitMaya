from datetime import timedelta

from celery_app import celery

from .lark import *

celery.conf.beat_schedule = {
    # 定时拉取用户数据
    "get_contact_for_all_lark_application": {
        "task": "tasks.lark.get_contact_for_all_lark_application",
        "schedule": timedelta(minutes=1),  # 定时1minutes执行一次
        "args": (),  # 函数传参的值
    },
}

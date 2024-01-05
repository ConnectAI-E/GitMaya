from datetime import timedelta

from celery_app import celery

from .github import *
from .lark import *

celery.conf.beat_schedule = {
    # 定时拉取用户数据
    "get_contact_for_all_lark_application": {
        "task": "tasks.lark.get_contact_for_all_lark_application",
        "schedule": timedelta(minutes=10),  # 定时1minutes执行一次
        "args": (),  # 函数传参的值
    },
    # 定时创建群聊
    # 不自动创建，手动创建
    # "create_chat_group_for_all_repo": {
    #     "task": "tasks.lark.create_chat_group_for_all_repo",
    #     "schedule": timedelta(minutes=10),  # 定时1minutes执行一次
    #     "args": (),  # 函数传参的值
    # },
}


def get_status_by_id(task_id):
    return celery.AsyncResult(task_id)

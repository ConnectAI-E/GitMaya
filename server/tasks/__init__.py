from celery_app import celery

from .lark import test_task

celery.conf.beat_schedule = {
    # "test_crontab_task": {
    #     "task": "tasks.crontab_task",
    #     "schedule": timedelta(hours=24), # 定时24hours执行一次
    #     "args": (False) # 函数传参的值
    # },
}

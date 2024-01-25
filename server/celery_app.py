import env
from app import app
from celery import Celery

app.config.setdefault("CELERY_BROKER_URL", "redis://redis:6379/0")
app.config.setdefault("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
celery = Celery(
    app.import_name,
    broker=app.config["CELERY_BROKER_URL"],
    backend=app.config["CELERY_RESULT_BACKEND"],
)

celery.conf.update(app.config.get("CELERY_CONFIG", {}), timezone="Asia/Shanghai")
TaskBase = celery.Task


class ContextTask(TaskBase):
    abstract = True

    def __call__(self, *args, **kwargs):
        with app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)


celery.Task = ContextTask

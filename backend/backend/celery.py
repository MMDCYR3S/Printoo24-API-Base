import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.development')

app = Celery('backend')

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# ===== Periodic Tasks ===== #
app.conf.beat_schedule = {
    'cleanup-temp-media-nightly': {
        'task': 'cleanup_temp_media_files_task',
        'schedule': crontab(hour=3, minute=0),
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
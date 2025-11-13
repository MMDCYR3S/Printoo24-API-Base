import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customer_site.settings.development')

app = Celery('customer_site')

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """ تسک برای نمایش تمامی درخواست هایی که ارسال میشه """
    print(f"Request: {self.request!r}")

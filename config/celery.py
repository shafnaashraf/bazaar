import os

from celery import Celery


#Tells Celery which Django settings file to use (config/settings.py). This ensures that when Celery runs background tasks, it has access to your database configurations, secret keys, and installed apps.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

#Initializes the main Celery application object and names it "config". This app variable will be used later to decorate your background functions (@app.task).
app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
"""
Celery wird für die Ausführung von Tasks im Hintergrund verwendet.
Im Fall des Datenmanagements, um Punktwolken Uploads
im Hintergrund an die VCPublisher API zu senden.
Dafür durchsucht Celery automatisch die Django-Apps nach einer `tasks.py`.
"""
import logging
import os
import redis

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datenwerft.settings')

app = Celery('datenwerft')

# define logger for Celery task. it can be importet in tasks.py
logger = logging.getLogger('Celery')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


def is_broker_available():
  """
  Check, if the broker is available.
  :return: True if broker is available, else False
  :rtype: bool
  """
  try:
    # Erstelle eine Redis-Verbindung
    r = redis.Redis.from_url(app.conf.broker_url)
    # Versuche, einen Ping an Redis zu senden
    r.ping()
    return True
  except redis.ConnectionError as e:
    logging.critical(f"Celery Broker is not available: {e}")
    return False


@app.task(bind=True, ignore_result=True)
def debug_task(self):
  print(f'Request: {self.request!r}')


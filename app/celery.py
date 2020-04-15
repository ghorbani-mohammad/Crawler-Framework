from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
# from agency.tasks import add

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app',
             broker='redis://localhost:6379/10',
             backend='redis://localhost:6379/10',
             include=['app.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

app.conf.beat_schedule = {
    'check-agencies-60-seconds': {
        'task': 'check_agencies',
        'schedule': 60,
    },
    'redis-exporter-30-seconds': {
        'task': 'redis_exporter',
        'schedule': 30,
    },
}

if __name__ == '__main__':
    app.start()

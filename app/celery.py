from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

# TODO: redis port and ip and db must be dynamic
crawler = Celery('crawler',
             broker='redis://crawler_redis:6379/10',
             backend='redis://crawler_redis:6379/10',
             include=['app.tasks'])

# Optional configuration, see the application user guide.
crawler.conf.update(
    result_expires=7200,
)

# if you want to purge works queue
crawler.control.purge()

crawler.conf.beat_schedule = {
    'check-agencies-60-seconds': {
        'task': 'check_agencies',
        'schedule': 6 * 3600,
    },
    'redis-exporter-300-seconds': {
        'task': 'redis_exporter',
        'schedule': 3 * 3600,
    },
}

if __name__ == '__main__':
    crawler.start()

from __future__ import absolute_import, unicode_literals
from celery import Celery
# from agency.tasks import add

app = Celery('app',
             broker='redis://localhost:6379/10',
             backend='redis://localhost:6379/10',
             include=['app.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'add_two_number',
        'schedule': 30.0,
        'args': (16, 16)
    },
}

if __name__ == '__main__':
    app.start()

from __future__ import absolute_import, unicode_literals

from .celery import app


@app.task(name='add_two_number')
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)
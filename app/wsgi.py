"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

application = get_wsgi_application()

try:
    from agency.models import Page, Report
    print('********* {} update: lock=False *****'.format(Page.objects.filter(lock=True).update(lock=False)))
    print('********* {} update: status=faild *****'.format(Report.objects.filter(status='pending').update(status='failed')))
except Exception:
    pass

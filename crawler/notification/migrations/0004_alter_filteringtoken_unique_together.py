# Generated by Django 4.1 on 2024-12-29 13:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0003_filteringtag_filteringtoken'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='filteringtoken',
            unique_together={('token', 'tag')},
        ),
    ]

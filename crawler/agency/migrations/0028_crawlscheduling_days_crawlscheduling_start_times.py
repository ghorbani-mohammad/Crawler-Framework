# Generated by Django 4.1 on 2025-01-12 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0027_alter_crawlscheduling_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawlscheduling',
            name='days',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='crawlscheduling',
            name='start_times',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]

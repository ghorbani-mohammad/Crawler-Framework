# Generated by Django 4.1 on 2023-12-23 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0016_option_deleted_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='agency',
            name='load_timeout',
            field=models.PositiveIntegerField(default=30, help_text='how many seconds to wait for page to load'),
        ),
    ]

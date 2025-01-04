# Generated by Django 4.1 on 2025-01-04 07:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0024_offtime_page_off_times'),
    ]

    operations = [
        migrations.AddField(
            model_name='offtime',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='offtime',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='offtime',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

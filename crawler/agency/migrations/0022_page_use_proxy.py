# Generated by Django 4.1 on 2024-11-17 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0021_page_scroll_alter_page_message_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='use_proxy',
            field=models.BooleanField(default=False),
        ),
    ]

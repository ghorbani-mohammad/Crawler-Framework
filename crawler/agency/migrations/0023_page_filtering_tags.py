# Generated by Django 4.1 on 2024-12-28 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0003_filteringtag_filteringtoken'),
        ('agency', '0022_page_use_proxy'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='filtering_tags',
            field=models.ManyToManyField(blank=True, related_name='pages', to='notification.filteringtag'),
        ),
    ]

# Generated by Django 4.1 on 2022-11-13 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0014_structure_deleted_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

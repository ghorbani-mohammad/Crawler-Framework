# Generated by Django 3.0.5 on 2020-11-27 17:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0036_log_phase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='agency.Page'),
        ),
    ]

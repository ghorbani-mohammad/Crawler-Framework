# Generated by Django 3.0.5 on 2020-11-27 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0037_auto_20201127_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='phase',
            field=models.CharField(blank=True, choices=[('cra', 'کرال'), ('sen', 'ارسال به تلگرام')], max_length=3, null=True),
        ),
    ]
# Generated by Django 3.0.5 on 2020-11-27 17:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0035_auto_20201127_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='phase',
            field=models.CharField(blank=True, choices=[('cra', 'کرال'), ('sen', 'متچ')], max_length=3, null=True),
        ),
    ]
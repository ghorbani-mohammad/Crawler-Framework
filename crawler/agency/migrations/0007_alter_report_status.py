# Generated by Django 3.2.9 on 2022-01-06 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0006_auto_20211123_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending')], max_length=300, null=True),
        ),
    ]

# Generated by Django 5.1.3 on 2024-12-04 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taxi_app', '0011_topic_region_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='direction',
            name='message_id',
            field=models.BigIntegerField(default=0),
        ),
    ]
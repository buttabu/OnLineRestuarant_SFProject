# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-14 22:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0004_auto_20170514_2251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='food',
            name='description',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='message',
            name='reason',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='review',
            name='deliverySpeed',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='review',
            name='foodQuality',
            field=models.CharField(default='', max_length=100),
        ),
    ]
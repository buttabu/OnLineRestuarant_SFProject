# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-17 02:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_customer_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='rep',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-27 12:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0002_myuser_access_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='refresh_token',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oidc_auth', '0002_auto_20151106_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openiduser',
            name='access_token',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='openiduser',
            name='refresh_token',
            field=models.CharField(max_length=1000),
        ),
    ]

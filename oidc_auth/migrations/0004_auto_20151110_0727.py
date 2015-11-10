# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oidc_auth', '0003_auto_20151110_0715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openiduser',
            name='access_token',
            field=models.CharField(max_length=1500),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oidc_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nonce',
            name='redirect_url',
            field=models.CharField(max_length=1000),
        ),
    ]

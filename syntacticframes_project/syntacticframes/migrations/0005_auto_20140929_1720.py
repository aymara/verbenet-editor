# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0004_verbtranslation_inherited_from'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verbtranslation',
            name='origin',
            field=models.CharField(max_length=500, blank=True),
        ),
    ]

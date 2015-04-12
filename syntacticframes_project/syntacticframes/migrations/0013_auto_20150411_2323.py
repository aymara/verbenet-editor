# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0012_auto_20150220_1836'),
    ]

    operations = [
        migrations.AddField(
            model_name='verbnetframeset',
            name='tree_position',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]

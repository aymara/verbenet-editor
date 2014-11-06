# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0006_auto_20141103_0939'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='verbnetclass',
            options={'ordering': ['levin_class', 'name']},
        ),
        migrations.AlterModelOptions(
            name='verbnetframeset',
            options={'ordering': ['tree_id']},
        ),
        migrations.AlterField(
            model_name='verbnetframeset',
            name='tree_id',
            field=models.PositiveSmallIntegerField(),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0015_remove_explicit_tree_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='verbnetframeset',
            options={},
        ),
        migrations.RemoveField(
            model_name='verbnetframeset',
            name='tree_position',
        ),
    ]

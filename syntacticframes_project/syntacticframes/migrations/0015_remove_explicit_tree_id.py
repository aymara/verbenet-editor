# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0014_copy_tree_id_to_position_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verbnetframeset',
            name='tree_id',
            field=models.PositiveIntegerField(db_index=True, editable=False),
        ),
        migrations.AlterModelOptions(
            name='verbnetframeset',
            options={'ordering': ['tree_position']},
        ),
    ]


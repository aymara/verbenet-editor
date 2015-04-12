# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


def copy_from_tree_id(apps, schema_editor):
    VerbNetFrameSet = apps.get_model('syntacticframes', 'VerbNetFrameSet')
    db_alias = schema_editor.connection.alias

    for verbnet_fs in VerbNetFrameSet.objects.using(db_alias).all():
        verbnet_fs.tree_position = verbnet_fs.tree_id
        verbnet_fs.save()


class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0013_auto_20150411_2323'),
    ]

    operations = [
        migrations.RunPython(copy_from_tree_id, migrations.RunPython.noop),
    ]

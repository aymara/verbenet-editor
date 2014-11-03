# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def copy_primary_key_id(apps, schema_editor):
    VerbNetFrameSet = apps.get_model('syntacticframes', 'VerbNetFrameSet')
    for fs in VerbNetFrameSet.objects.all():
        fs.tree_id = fs.id
        fs.save()

class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0005_auto_20140929_1720'),
    ]

    operations = [
        migrations.RunPython(copy_primary_key_id),
    ]

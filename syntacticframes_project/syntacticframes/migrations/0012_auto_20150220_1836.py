# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from distutils.version import LooseVersion

from django.db import models, migrations

def set_position_value_for_levin_classes(apps, schema_editor):
    i = 0
    LevinClass = apps.get_model('syntacticframes', 'LevinClass')
    levin_class_list = sorted(LevinClass.objects.all(), key=lambda l: int(l.number))
    for levin_class in levin_class_list:
        verbnet_classes = sorted(
            levin_class.verbnetclass_set.all(),
            key=lambda v: LooseVersion(v.name.split('-')[1]))
        for v in verbnet_classes:
            v.position = i
            v.save()
            i += 10


class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0011_auto_20150121_1600'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='verbnetclass',
            options={'ordering': ['position']},
        ),
        migrations.AddField(
            model_name='verbnetclass',
            name='position',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.RunPython(set_position_value_for_levin_classes),
    ]

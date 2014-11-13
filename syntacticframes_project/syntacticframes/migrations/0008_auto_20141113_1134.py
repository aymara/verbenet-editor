# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def store_translation_status(apps, schema_editor):
    LevinClass = apps.get_model('syntacticframes', 'LevinClass')
    for levin_class in LevinClass.objects.all():
        levin_class.translation_status = 'TRANSLATED' if levin_class.is_translated else 'INPROGRESS'
        levin_class.save()

class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0007_auto_20141106_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='levinclass',
            name='translation_status',
            field=models.CharField(default='INPROGRESS', max_length=10, choices=[('TRANSLATED', 'Translated'), ('REMOVED', 'Removed'), ('INPROGRESS', 'In progress')]),
            preserve_default=True,
        ),
        migrations.RunPython(store_translation_status),
        migrations.RemoveField(
            model_name='levinclass',
            name='is_translated',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0002_auto_20140929_1135'),
    ]

    operations = [
        migrations.AddField(
            model_name='verbtranslation',
            name='validation_status',
            field=models.CharField(choices=[('INFERRED', 'Inferred'), ('VALID', 'Valid'), ('WRONG', 'Wrong')], default='INFERRED', max_length=10),
            preserve_default=True,
        ),
    ]

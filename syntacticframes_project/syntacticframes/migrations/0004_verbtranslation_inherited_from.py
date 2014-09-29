# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0003_verbtranslation_validation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='verbtranslation',
            name='inherited_from',
            field=models.ForeignKey(to='syntacticframes.VerbNetFrameSet', related_name='inheritedmanualtranslation_set', null=True),
            preserve_default=True,
        ),
    ]

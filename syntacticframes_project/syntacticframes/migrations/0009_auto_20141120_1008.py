# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0008_auto_20141113_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='verbnetmember',
            name='received_from',
            field=models.ForeignKey(related_name='receivedmember_set', to='syntacticframes.VerbNetFrameSet', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='verbtranslation',
            name='received_from',
            field=models.ForeignKey(related_name='receivedtranslation_set', to='syntacticframes.VerbNetFrameSet', null=True),
            preserve_default=True,
        ),
    ]

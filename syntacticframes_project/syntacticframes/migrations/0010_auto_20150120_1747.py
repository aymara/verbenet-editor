# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0009_auto_20141120_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verbnetmember',
            name='inherited_from',
            field=models.ForeignKey(related_name='inheritedmember_set', to='syntacticframes.VerbNetFrameSet', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='verbnetmember',
            name='received_from',
            field=models.ForeignKey(related_name='receivedmember_set', to='syntacticframes.VerbNetFrameSet', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='verbtranslation',
            name='inherited_from',
            field=models.ForeignKey(related_name='inheritedmanualtranslation_set', to='syntacticframes.VerbNetFrameSet', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='verbtranslation',
            name='received_from',
            field=models.ForeignKey(related_name='receivedtranslation_set', to='syntacticframes.VerbNetFrameSet', null=True, blank=True),
            preserve_default=True,
        ),
    ]

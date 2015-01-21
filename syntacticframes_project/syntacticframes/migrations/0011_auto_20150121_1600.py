# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('syntacticframes', '0010_auto_20150120_1747'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='verbnetmember',
            unique_together=set([('lemma', 'inherited_from', 'received_from'), ('lemma', 'inherited_from'), ('lemma', 'received_from')]),
        ),
    ]

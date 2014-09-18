# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from os.path import join

from django.db import models, migrations
from django.conf import settings

from loadmapping.models import LVFVerb

def import_verbs(apps, schema_editor):
    LVFVerb = apps.get_model('loadmapping', 'LVFVerb')
    LVFVerb.objects.all().delete()
    with open(join(settings.SITE_ROOT, 'loadmapping/fixtures/lvfverb.json')) as fixture:
            for entry in json.loads(fixture.read()):
                assert entry['model'] == 'loadmapping.lvfverb'
                fields = entry['fields']
                LVFVerb(
                    lemma=fields['lemma'],
                    sense=fields['sense'],
                    lvf_class=fields['lvf_class'],
                    construction=fields['construction']).save()

def delete_verbs(apps, schema_editor):
    LVFVerb = apps.get_model('loadmapping', 'LVFVerb')
    LVFVerb.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('loadmapping', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(import_verbs, delete_verbs)
    ]

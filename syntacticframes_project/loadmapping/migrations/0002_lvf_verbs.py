# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from loadmapping.savelvf import LVFp1_to_database

class Migration(DataMigration):

    def forwards(self, orm):
        "Store all LVF verbs to database"
        LVFp1_to_database(orm.LVFVerb)

    def backwards(self, orm):
        "Delete all LVF verbs from databse"
        orm.LVFVerb.objects.all().delete()

    models = {
        'loadmapping.lvfverb': {
            'Meta': {'object_name': 'LVFVerb'},
            'construction': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lemma': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'lvf_class': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'sense': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        }
    }

    complete_apps = ['loadmapping']
    symmetrical = True

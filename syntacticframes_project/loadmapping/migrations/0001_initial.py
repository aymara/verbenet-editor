# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LVFVerb'
        db.create_table('loadmapping_lvfverb', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lemma', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('sense', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('lvf_class', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('construction', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('loadmapping', ['LVFVerb'])


    def backwards(self, orm):
        # Deleting model 'LVFVerb'
        db.delete_table('loadmapping_lvfverb')


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
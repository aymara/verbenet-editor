# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'VerbNetClass.lvf_string'
        db.delete_column('syntacticframes_verbnetclass', 'lvf_string')

        # Deleting field 'VerbNetClass.ladl_string'
        db.delete_column('syntacticframes_verbnetclass', 'ladl_string')


    def backwards(self, orm):
        # Adding field 'VerbNetClass.lvf_string'
        db.add_column('syntacticframes_verbnetclass', 'lvf_string',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)

        # Adding field 'VerbNetClass.ladl_string'
        db.add_column('syntacticframes_verbnetclass', 'ladl_string',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=100),
                      keep_default=False)


    models = {
        'syntacticframes.levinclass': {
            'Meta': {'object_name': 'LevinClass'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'syntacticframes.verbnetclass': {
            'Meta': {'object_name': 'VerbNetClass'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'levin_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.LevinClass']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'syntacticframes.verbnetframe': {
            'Meta': {'ordering': "['position']", 'object_name': 'VerbNetFrame'},
            'example': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'frameset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.VerbNetFrameSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'roles_syntax': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'semantics': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        'syntacticframes.verbnetframeset': {
            'Meta': {'object_name': 'VerbNetFrameSet'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ladl_string': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lvf_string': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'paragon': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'to': "orm['syntacticframes.VerbNetFrameSet']", 'related_name': "'children'", 'null': 'True', 'blank': 'True'}),
            'removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'verbnet_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.VerbNetClass']"})
        },
        'syntacticframes.verbnetmember': {
            'Meta': {'object_name': 'VerbNetMember'},
            'frameset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.VerbNetFrameSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lemma': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        'syntacticframes.verbnetrole': {
            'Meta': {'ordering': "['position']", 'object_name': 'VerbNetRole'},
            'frameset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.VerbNetFrameSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        'syntacticframes.verbtranslation': {
            'Meta': {'object_name': 'VerbTranslation'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'frameset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.VerbNetFrameSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['syntacticframes']
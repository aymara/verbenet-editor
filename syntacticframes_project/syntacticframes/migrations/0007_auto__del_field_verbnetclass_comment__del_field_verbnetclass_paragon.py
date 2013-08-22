# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'VerbNetClass.comment'
        db.delete_column('syntacticframes_verbnetclass', 'comment')

        # Deleting field 'VerbNetClass.paragon'
        db.delete_column('syntacticframes_verbnetclass', 'paragon')


    def backwards(self, orm):
        # Adding field 'VerbNetClass.comment'
        db.add_column('syntacticframes_verbnetclass', 'comment',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=1000),
                      keep_default=False)

        # Adding field 'VerbNetClass.paragon'
        db.add_column('syntacticframes_verbnetclass', 'paragon',
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
            'ladl_string': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'levin_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.LevinClass']"}),
            'lvf_string': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'syntacticframes.verbnetframe': {
            'Meta': {'object_name': 'VerbNetFrame', 'ordering': "['position']"},
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
            'comment': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'paragon': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '100'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'related_name': "'children'", 'null': 'True', 'to': "orm['syntacticframes.VerbNetFrameSet']", 'blank': 'True'}),
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
            'Meta': {'object_name': 'VerbNetRole'},
            'frameset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.VerbNetFrameSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
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
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'VerbNetFrameSet.lvf_string'
        db.alter_column('syntacticframes_verbnetframeset', 'lvf_string', self.gf('django.db.models.fields.TextField')())

        # Changing field 'VerbNetFrameSet.ladl_string'
        db.alter_column('syntacticframes_verbnetframeset', 'ladl_string', self.gf('django.db.models.fields.TextField')())

    def backwards(self, orm):

        # Changing field 'VerbNetFrameSet.lvf_string'
        db.alter_column('syntacticframes_verbnetframeset', 'lvf_string', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'VerbNetFrameSet.ladl_string'
        db.alter_column('syntacticframes_verbnetframeset', 'ladl_string', self.gf('django.db.models.fields.CharField')(max_length=100))

    models = {
        'syntacticframes.levinclass': {
            'Meta': {'object_name': 'LevinClass'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '100000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_translated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'syntacticframes.verbnetclass': {
            'Meta': {'object_name': 'VerbNetClass'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '100000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'levin_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.LevinClass']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'syntacticframes.verbnetframe': {
            'Meta': {'ordering': "['position']", 'object_name': 'VerbNetFrame'},
            'example': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'frameset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.VerbNetFrameSet']"}),
            'from_verbnet': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'roles_syntax': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'semantics': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        'syntacticframes.verbnetframeset': {
            'Meta': {'ordering': "['id']", 'object_name': 'VerbNetFrameSet'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '100000', 'blank': 'True'}),
            'has_removed_frames': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ladl_string': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lvf_string': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'paragon': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'null': 'True', 'to': "orm['syntacticframes.VerbNetFrameSet']", 'related_name': "'children'", 'blank': 'True'}),
            'removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'verbnet_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.VerbNetClass']"})
        },
        'syntacticframes.verbnetmember': {
            'Meta': {'ordering': "['lemma']", 'object_name': 'VerbNetMember'},
            'frameset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.VerbNetFrameSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inherited_from': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['syntacticframes.VerbNetFrameSet']", 'related_name': "'inheritedmember_set'"}),
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
            'Meta': {'ordering': "['category_id', 'verb']", 'object_name': 'VerbTranslation'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'category_id': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'frameset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.VerbNetFrameSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['syntacticframes']
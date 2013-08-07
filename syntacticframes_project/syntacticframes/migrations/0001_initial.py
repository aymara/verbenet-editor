# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LevinClass'
        db.create_table('syntacticframes_levinclass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('syntacticframes', ['LevinClass'])

        # Adding model 'VerbNetClass'
        db.create_table('syntacticframes_verbnetclass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('levin_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['syntacticframes.LevinClass'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('paragon', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('ladl_string', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('lvf_string', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('syntacticframes', ['VerbNetClass'])

        # Adding model 'VerbNetFrameSet'
        db.create_table('syntacticframes_verbnetframeset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('verbnet_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['syntacticframes.VerbNetClass'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, null=True, related_name='children', to=orm['syntacticframes.VerbNetFrameSet'])),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('syntacticframes', ['VerbNetFrameSet'])

        # Adding model 'VerbNetMember'
        db.create_table('syntacticframes_verbnetmember', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('frameset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['syntacticframes.VerbNetFrameSet'])),
            ('lemma', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal('syntacticframes', ['VerbNetMember'])

        # Adding model 'VerbNetRole'
        db.create_table('syntacticframes_verbnetrole', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('frameset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['syntacticframes.VerbNetFrameSet'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal('syntacticframes', ['VerbNetRole'])

        # Adding model 'VerbNetFrame'
        db.create_table('syntacticframes_verbnetframe', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('frameset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['syntacticframes.VerbNetFrameSet'])),
            ('syntax', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('example', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('roles_syntax', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('semantics', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal('syntacticframes', ['VerbNetFrame'])

        # Adding model 'VerbTranslation'
        db.create_table('syntacticframes_verbtranslation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('frameset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['syntacticframes.VerbNetFrameSet'])),
            ('verb', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('origin', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('syntacticframes', ['VerbTranslation'])


    def backwards(self, orm):
        # Deleting model 'LevinClass'
        db.delete_table('syntacticframes_levinclass')

        # Deleting model 'VerbNetClass'
        db.delete_table('syntacticframes_verbnetclass')

        # Deleting model 'VerbNetFrameSet'
        db.delete_table('syntacticframes_verbnetframeset')

        # Deleting model 'VerbNetMember'
        db.delete_table('syntacticframes_verbnetmember')

        # Deleting model 'VerbNetRole'
        db.delete_table('syntacticframes_verbnetrole')

        # Deleting model 'VerbNetFrame'
        db.delete_table('syntacticframes_verbnetframe')

        # Deleting model 'VerbTranslation'
        db.delete_table('syntacticframes_verbtranslation')


    models = {
        'syntacticframes.levinclass': {
            'Meta': {'object_name': 'LevinClass'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'syntacticframes.verbnetclass': {
            'Meta': {'object_name': 'VerbNetClass'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ladl_string': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'levin_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.LevinClass']"}),
            'lvf_string': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'paragon': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'syntacticframes.verbnetframe': {
            'Meta': {'object_name': 'VerbNetFrame'},
            'example': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'frameset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['syntacticframes.VerbNetFrameSet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'roles_syntax': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'semantics': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'syntax': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        'syntacticframes.verbnetframeset': {
            'Meta': {'object_name': 'VerbNetFrameSet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'null': 'True', 'related_name': "'children'", 'to': "orm['syntacticframes.VerbNetFrameSet']"}),
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
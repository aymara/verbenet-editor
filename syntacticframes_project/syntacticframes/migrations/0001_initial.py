# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LevinClass',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('number', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=100)),
                ('is_translated', models.BooleanField(default=False)),
                ('comment', models.TextField(max_length=100000, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VerbNetClass',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('comment', models.TextField(max_length=100000, blank=True)),
                ('levin_class', models.ForeignKey(to='syntacticframes.LevinClass')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VerbNetFrame',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('position', models.PositiveSmallIntegerField(null=True)),
                ('removed', models.BooleanField(default=False)),
                ('from_verbnet', models.BooleanField(default=True)),
                ('syntax', models.CharField(max_length=1000)),
                ('example', models.CharField(max_length=1000)),
                ('roles_syntax', models.CharField(max_length=1000)),
                ('semantics', models.CharField(max_length=1000)),
            ],
            options={
                'ordering': ['position'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VerbNetFrameSet',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('has_removed_frames', models.BooleanField(default=False)),
                ('removed', models.BooleanField(default=False)),
                ('paragon', models.CharField(max_length=100, blank=True)),
                ('comment', models.TextField(max_length=100000, blank=True)),
                ('ladl_string', models.TextField(blank=True)),
                ('lvf_string', models.TextField(blank=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(to='syntacticframes.VerbNetFrameSet', blank=True, null=True, related_name='children')),
                ('verbnet_class', models.ForeignKey(to='syntacticframes.VerbNetClass')),
            ],
            options={
                'ordering': ['id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VerbNetMember',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lemma', models.CharField(max_length=1000)),
                ('frameset', models.ForeignKey(to='syntacticframes.VerbNetFrameSet')),
                ('inherited_from', models.ForeignKey(to='syntacticframes.VerbNetFrameSet', null=True, related_name='inheritedmember_set')),
            ],
            options={
                'ordering': ['lemma'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VerbNetRole',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=1000)),
                ('position', models.PositiveSmallIntegerField()),
                ('frameset', models.ForeignKey(to='syntacticframes.VerbNetFrameSet')),
            ],
            options={
                'ordering': ['position'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VerbTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('verb', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=20, choices=[('both', 'Both'), ('ladl', 'LADL'), ('lvf', 'LVF'), ('dicovalence', 'Dicovalence'), ('unknown', 'No category')])),
                ('category_id', models.PositiveSmallIntegerField()),
                ('origin', models.CharField(max_length=500)),
                ('frameset', models.ForeignKey(to='syntacticframes.VerbNetFrameSet')),
            ],
            options={
                'ordering': ['category_id', 'verb'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='verbnetframe',
            name='frameset',
            field=models.ForeignKey(to='syntacticframes.VerbNetFrameSet'),
            preserve_default=True,
        ),
    ]

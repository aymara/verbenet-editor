# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LVFVerb',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('lemma', models.CharField(max_length=100)),
                ('sense', models.PositiveSmallIntegerField()),
                ('lvf_class', models.CharField(max_length=10)),
                ('construction', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

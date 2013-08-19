#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import verbnet.verbnetreader
from syntacticframes.models import VerbNetClass, VerbNetFrameSet, VerbNetRole

def save_class(c, vn_class, parent=None, indent=0):
    db_frameset = VerbNetFrameSet.objects.get(name=c['name'], verbnet_class=vn_class, parent=parent)

    VerbNetRole.objects.filter(frameset=db_frameset).delete()
    for r in c['roles']:
        VerbNetRole(frameset=db_frameset, name=r).save()

    for c in c['children']:
        save_class(c, vn_class, db_frameset, indent+4)


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.commit_on_success():
            r = verbnet.verbnetreader.VerbnetReader('verbnet/verbnet-3.2/', False)
            for filename in r.files:
                vn_class = VerbNetClass.objects.get(name=filename)
                save_class(r.files[filename], vn_class)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from syntacticframes.models import LevinClass, VerbNetClass, VerbNetFrameSet, \
    VerbNetFrame

from verbnet.verbnetreader import VerbnetReader


def iprint(indent, stuff):
    if indent > 0:
        print(" " * indent, stuff)
    else:
        print(stuff)


def update_class(xml_frameset, db_frameset, parent=None, indent=0):
    iprint(indent, db_frameset.name)

    for xml_f, db_f in zip(xml_frameset['frames'],
                           db_frameset.verbnetframe_set.all()):

        if db_f.semantics != xml_f.semantics:
            iprint(indent, "INCONSISTENCY")
            db_f.semantics = xml_f.semantics
            db_f.save()
        else:
            iprint(indent, "FINE!")

        iprint(indent, db_f.id)
        iprint(indent, db_f.syntax)
        iprint(indent, xml_f.structure)
        iprint(indent, "DB:  {}".format(db_f.semantics))
        iprint(indent, "XML: {}".format(xml_f.semantics))
        print()

    for xml_children, db_children in zip(xml_frameset['children'],
                                         db_frameset.get_children()):
        update_class(xml_children, db_children, db_frameset, indent+4)


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.commit_on_success():

            r = VerbnetReader('verbnet/verbnet-3.2/', False)
            for filename in r.files:
                lc_number = filename.split('-')[1].split('.')[0]
                lc = LevinClass.objects.get(number=lc_number)
                vn_class = VerbNetClass.objects.get(name=filename,
                                                    levin_class=lc)
                vn_fs = vn_class.verbnetframeset_set.get(parent=None)

                xml_class = r.files[filename]
                update_class(xml_class, vn_fs)

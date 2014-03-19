#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import verbnet.verbnetreader
from loadmapping.verbclasses import verb_classes
from loadmapping import mapping

from syntacticframes.models import LevinClass, VerbNetClass, VerbNetFrameSet, \
    VerbNetMember, VerbNetRole, VerbNetFrame, VerbTranslation




def iprint(indent, stuff):
    print(" " * indent, stuff)


def save_class(xml_class, db_frameset, indent=0):
    iprint(indent, xml_class['name'])

    #iprint(indent, ", ".join(xml_class['roles']))
    for position, role in enumerate(xml_class['roles']):
        VerbNetRole(frameset=db_frameset, name=role, position=position).save()
    #iprint(indent, ", ".join(xml_class['members']))
    for m in xml_class['members']:
        VerbNetMember(frameset=db_frameset, lemma=m).save()

    position = 1
    for f in xml_class['frames']:
        db_f = VerbNetFrame(
            frameset=db_frameset,
            syntax=f.structure,
            roles_syntax=f.roles,
            semantics=f.semantics,
            example=f.example,
            position=position+1)
        db_f.save()
        position += 1

    for xml_child in xml_class['children']:
        db_child_frameset = VerbNetFrameSet(
            verbnet_class=db_frameset.verbnet_class,
            name=xml_child['name'],
            parent=db_frameset)
        db_child_frameset.save()

        save_class(xml_child, db_child_frameset, indent+4)


class Command(BaseCommand):
    def handle(self, *args, **options):

        # import levin classes
        if LevinClass.objects.filter(name__exact=next(iter(verb_classes))) is []:
            print("Levin classes already imported!")
        else:
            for number in verb_classes: 
                LevinClass(number=number, name=verb_classes[number]).save()
            print("Imported Levin classes!")

        # import vn classes, root framesets and LADL/LVF mapping
        mapping.import_mapping()

        with transaction.commit_on_success():

            r = verbnet.verbnetreader.VerbnetReader('verbnet/verbnet-3.2/', False)
            print('-----')
            for filename in r.files:
                print("Saving subclasses of {}".format(filename))
                xml_class = r.files[filename]
                db_vnclass = VerbNetClass.objects.get(name=filename)
                db_root_frameset = db_vnclass.verbnetframeset_set.get(parent=None)

                save_class(xml_class, db_root_frameset, 0)
                db_root_frameset.update_translations()

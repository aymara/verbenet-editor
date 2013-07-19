#s!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import verbnet.verbnetreader
from loadmapping.verbclasses import verb_classes
from loadmapping import mapping

from syntacticframes.models import LevinClass, VerbNetClass, VerbNetFrameSet, VerbNetMember, VerbNetRole, VerbNetFrame, VerbTranslation

def iprint(indent, stuff):
    pass
    #print(" " * indent, stuff)

def save_class(c, vn_class, parent=None, indent=0):
    #iprint(indent, c['name'])
    db_frameset = VerbNetFrameSet(name=c['name'], verbnet_class=vn_class, parent=parent)
    db_frameset.save()

    #iprint(indent, ", ".join(c['roles']))
    for r in c['roles']:
        VerbNetRole(frameset=db_frameset, name=r).save()
    #iprint(indent, ", ".join(c['members']))
    for m in c['members']:
        VerbNetMember(frameset=db_frameset, lemma=m).save()

    for f in c['frames']:
        db_f = VerbNetFrame(
            frameset=db_frameset,
            syntax=f.structure,
            roles_syntax=f.roles,
            semantics=f.semantics,
            example=f.example)
        db_f.save()

        candidates = mapping.translations_for_class(c['members'], vn_class.ladl_string, vn_class.lvf_string)
        for french, categoryname, categoryid, originlist in candidates:
            originset = set(originlist.split(','))
            if set(c['members']) & originset:
                try:
                    VerbTranslation.objects.get(frameset=db_frameset, verb=french)
                except:
                    VerbTranslation(
                        frameset=db_frameset,
                        verb=french,
                        category=categoryname,
                        origin=originlist).save()
        #iprint(indent, f)
        #iprint(indent, f.example)
        #iprint(indent, f.semantics)
    #print()

    for c in c['children']:
        save_class(c, vn_class, db_frameset, indent+4)


class Command(BaseCommand):
    def handle(self, *args, **options):

        # import levin classes
        if LevinClass.objects.filter(name__exact=next(iter(verb_classes))) is []:
            print("Levin classes already imported!")
        else:
            for number in verb_classes: 
                LevinClass(number=number, name=verb_classes[number]).save()
            print("Imported Levin classes!")

        # import vn classes and mapping
        mapping.import_mapping()

        with transaction.commit_on_success():

            r = verbnet.verbnetreader.VerbnetReader('verbnet/verbnet-3.2/', False)
            print('-----')
            for filename in r.files:
                lc_number = filename.split('-')[1].split('.')[0]
                print(lc_number)
                c = r.files[filename]
                lc = LevinClass.objects.get(number=lc_number)
                print("Using {}".format(filename))
                vn_class = VerbNetClass.objects.get(name=filename, levin_class=lc)
                #vn_class.save()
                save_class(c, vn_class)

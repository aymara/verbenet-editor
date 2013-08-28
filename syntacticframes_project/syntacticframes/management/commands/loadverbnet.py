#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from time import gmtime, strftime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import verbnet.verbnetreader
from loadmapping.verbclasses import verb_classes
from loadmapping import mapping

from syntacticframes.models import LevinClass, VerbNetClass, VerbNetFrameSet, \
    VerbNetMember, VerbNetRole, VerbNetFrame, VerbTranslation

verb_logger = logging.getLogger('verbs')


def iprint(indent, stuff):
    pass
    #print(" " * indent, stuff)


def update_verbs(xml_class, db_frameset, current_ladl, current_lvf):
    when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
    verb_logger.info("{}: Removed verbs in subclass {}: {}".format(
        when, db_frameset.name,
        ", ".join([t.verb for t in
                  VerbTranslation.objects.filter(frameset=db_frameset)])))
    VerbTranslation.objects.filter(frameset=db_frameset).delete()

    candidates = mapping.translations_for_class(
        xml_class['members'], current_ladl, current_lvf)

    for french, categoryname, categoryid, originlist in candidates:
        originset = set(originlist.split(','))
        if set(xml_class['members']) & originset:
            VerbTranslation(
                frameset=db_frameset,
                verb=french,
                category=categoryname,
                origin=originlist).save()
    when = strftime("%d/%m/%Y %H:%M:%S", gmtime())

    verb_logger.info("{}: Added verbs in subclass {}: {}".format(
        when, db_frameset.name,
        ", ".join([t.verb for t in
                  VerbTranslation.objects.filter(frameset=db_frameset)])))

    for c in db_frameset.children.all():
        db_frameset = VerbNetFrameSet.objects.get(name=c['name'])
        new_ladl = current_ladl if not db_frameset.ladl_string else db_frameset.ladl_string
        new_lvf = current_lvf if not db_frameset.lvf_string else db_frameset.lvf_string
            
        update_verbs(c, db_frameset, new_ladl, new_lvf)


def save_class(c, db_frameset, indent=0):
    #iprint(indent, c['name'])

    #iprint(indent, ", ".join(c['roles']))
    for position, role in enumerate(c['roles']):
        VerbNetRole(frameset=db_frameset, name=role, position=position).save()
    #iprint(indent, ", ".join(c['members']))
    for m in c['members']:
        VerbNetMember(frameset=db_frameset, lemma=m).save()

    position = 1
    for f in c['frames']:
        db_f = VerbNetFrame(
            frameset=db_frameset,
            syntax=f.structure,
            roles_syntax=f.roles,
            semantics=f.semantics,
            example=f.example,
            position=position+1)
        db_f.save()
        position += 1

        candidates = mapping.translations_for_class(c['members'], db_frameset.ladl_string, db_frameset.lvf_string)
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
        save_class(c, db_frameset, indent+4)


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
                db_rootframeset = db_vnclass.verbnetframeset_set.get(parent=None)
                save_class(xml_class, db_rootframeset)

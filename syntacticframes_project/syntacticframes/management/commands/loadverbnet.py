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
    print(" " * indent, stuff)

def update_verbs(db_frameset, current_ladl, current_lvf):
    verbs = VerbTranslation.objects.filter(frameset=db_frameset)
    initial_set = {(v.verb, v.category) for v in verbs}
    verbs.delete()
    first_when = strftime("%d/%m/%Y %H:%M:%S", gmtime())

    members = [m.lemma for m in db_frameset.verbnetmember_set.all()]
    candidates = mapping.translations_for_class(members, current_ladl, current_lvf)

    for french, categoryname, categoryid, originlist in candidates:
        originset = set(originlist.split(','))
        if set(members) & originset:
            VerbTranslation(
                frameset=db_frameset,
                verb=french,
                category=categoryname,
                category_id=VerbTranslation.CATEGORY_ID[categoryname],
                origin=originlist).save()

    last_when = strftime("%d/%m/%Y %H:%M:%S", gmtime())

    verbs = VerbTranslation.objects.filter(frameset=db_frameset)
    final_set = {(v.verb, v.category) for v in verbs}

    if initial_set != final_set:
        verb_logger.info("{}: Removed verbs in subclass {}: {}".format(
            first_when, db_frameset.name, ", ".join(["{} ({})".format(v, c) for v, c in initial_set])))
        verb_logger.info("{}: Added verbs in subclass {}: {}".format(
            last_when, db_frameset.name, ", ".join(["{} ({})".format(v, c) for v, c in final_set])))

    for db_childrenfs in db_frameset.children.all():
        new_ladl = current_ladl if not db_childrenfs.ladl_string else db_childrenfs.ladl_string
        new_lvf = current_lvf if not db_childrenfs.lvf_string else db_childrenfs.lvf_string
            
        update_verbs(db_childrenfs, new_ladl, new_lvf)


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
                update_verbs(db_root_frameset, db_root_frameset.ladl_string, db_root_frameset.lvf_string)

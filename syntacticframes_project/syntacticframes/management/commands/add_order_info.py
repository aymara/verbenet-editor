#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from syntacticframes.models import LevinClass, VerbNetClass, VerbNetFrameSet, \
    VerbNetFrame

from verbnet.verbnetreader import VerbnetReader

import traceback, sys

class ModifiedException(Exception):
    pass
class RemovedException(Exception):
    pass

def iprint(indent, stuff):
    print(" " * indent, stuff)

def fix_position(db_frames, positions, tuple, indent):
        expected_position = 1
        for db_f in db_frames:
            if tuple == 'STRUCTURE':
                frame_tuple = db_f.syntax
            elif tuple == 'EXAMPLE':
                frame_tuple = db_f.example
            else:
                frame_tuple = db_f.syntax, db_f.example

            iprint(indent, "E: '{}'".format(frame_tuple))

            try:
                correct_position = positions[frame_tuple]
                iprint(indent, "Position is {}".format(correct_position))
                db_f.position = correct_position
                if expected_position != correct_position:
                    iprint(indent, "UNEXPECTED")
                #db_f.save()
            except KeyError as e:
                if db_f.syntax == 'ø':
                    raise RemovedException()
                else:
                    iprint(indent, "MODIFIED")
            except:
                iprint(indent, "OTHER")

            expected_position += 1

def update_class(xml_frameset, db_frameset, parent=None, indent=0):
    iprint(indent, db_frameset.name)

    positions_se, positions_s, positions_e = {}, {}, {}
    valid_se, valid_s, valid_e = True, True, True
    current_position = 1
    xml_frames = xml_frameset['frames']
    db_frames = db_frameset.verbnetframe_set.all()

    for xml_f in xml_frames:
        iprint(indent, "{} -> {}".format((xml_f.structure, xml_f.example), current_position))

        # xml_f.structure, xml_f.example
        assert not (xml_f.structure, xml_f.example) in positions_se
        positions_se[xml_f.structure, xml_f.example] = current_position

        # xml_f.structure
        if xml_f.structure in positions_s:
            valid_s = False
            positions_s = {}
        if valid_s:
            positions_s[xml_f.structure] = current_position

        # xml_f.example
        if xml_f.example in positions_e:
            valid_e = False
            positions_e = {}
        if valid_e:
            positions_e[xml_f.example] = current_position

        current_position += 1

    if valid_s:
        tuple = 'STRUCTURE'
        positions = positions_s
    elif valid_e:
        tuple = 'EXAMPLE'
        positions = positions_e
    else:
        positions = positions_se

    iprint(indent, positions)
    print()

    try:
        fix_position(db_frames, positions, tuple, indent)
    except RemovedException: 
        iprint(indent, "ADDING")
        fix_position(db_frames, positions_e, 'EXAMPLE', indent+8)
    else:
        pass
        #for db_f in db_frames:
        #    db_f.save()

    for xml_children, db_children in zip(xml_frameset['children'],
                                         db_frameset.get_children()):
        update_class(xml_children, db_children, db_frameset, indent+4)


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.commit_on_success():

            r = VerbnetReader('verbnet/verbnet-3.2/', False)
            for filename in sorted(r.files):
                lc_number = filename.split('-')[1].split('.')[0]
                lc = LevinClass.objects.get(number=lc_number)
                vn_class = VerbNetClass.objects.get(name=filename,
                                                    levin_class=lc)
                vn_fs = vn_class.verbnetframeset_set.get(parent=None)

                xml_class = r.files[filename]
                update_class(xml_class, vn_fs)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from syntacticframes.models import LevinClass, VerbNetClass, VerbNetFrameSet, \
    VerbNetFrame

from verbnet.verbnetreader import VerbnetReader


def iprint(indent, stuff):
    print(" " * indent, stuff)


def update_class(xml_frameset, db_frameset, parent=None, indent=0):
    iprint(indent, db_frameset.name)

    positions, current_position = {}, 1
    xml_frames = xml_frameset['frames']
    db_frames = db_frameset.verbnetframe_set.all()

    for xml_f in xml_frames:
        iprint(indent, "{} -> {}".format((xml_f.structure, xml_f.semantics, xml_f.roles), current_position))
        positions[xml_f.structure, xml_f.semantics, xml_f.roles] = current_position
        current_position += 1

    for db_f in db_frames:
        frame_tuple = db_f.syntax, db_f.semantics, db_f.roles_syntax
        iprint(indent, "Let's see {}".format(frame_tuple))

        try:
            correct_position = positions[frame_tuple]
            iprint(indent, "Position for {} is {}".format(db_f.syntax, correct_position))
            db_f.position = correct_position
            db_f.save()
        except KeyError:
            iprint(indent, "Unknown frame {}".format(frame_tuple))
        except:
            iprint(indent, "Other error for frame {}".format(frame_tuple))

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

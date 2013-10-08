#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from collections import defaultdict
import pickle
from glob import glob
import csv
import re
import os

from django.core.management.base import BaseCommand
from django.conf import settings


def LADL_to_verbes():
    verbes = defaultdict(list)

    tables_path = os.path.join(settings.SITE_ROOT, 'loadmapping/resources/tables-3.4')

    for f in (glob(os.path.join(tables_path, 'verbes/*.csv'))
              + glob(os.path.join(tables_path, 'figees/*.csv'))):
        with open(f) as csvfile:
            # Si pas verbe, alors figée
            try:
                classe = re.search('V_([^.]+).lgt.csv', os.path.basename(f)).group(1)
            except AttributeError:
                classe = re.search('([^.]+).lgt.csv', os.path.basename(f)).group(1)

            ladlreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            first_row = next(ladlreader)

            # If it's not really a verb, we're not interested
            try:
                verbe_index = first_row.index('<ENT>V')
            except ValueError:
                continue

            # If there's no pronominal column, never add 'se'
            try:
                pronominal_index = first_row.index('<ENT>Ppv')
            except ValueError:
                pronominal_index = None

            for row in ladlreader:
                if len(row) > 1:
                    verb = row[verbe_index]

                    # Add 'se' and variations if needed
                    if pronominal_index:
                        pronominal_marker = row[pronominal_index]
                        if pronominal_marker != "<E>":
                            verb += " {}".format(pronominal_marker)

                    verbes[classe].append(verb)
                    if classe == '36DT':
                        if row[3] == '+':
                            verbes['36DT-source'].append(verb)
                        if row[4] == '+':
                            verbes['36DT-dest'].append(verb)

    return verbes

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("dumping LADL data")
        with open(os.path.join(settings.SITE_ROOT, 'loadmapping/data/LADL_to_verbes'), 'wb') as f:
            pickle.dump(LADL_to_verbes(), f)

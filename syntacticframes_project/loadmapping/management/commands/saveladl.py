#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from collections import defaultdict
import pickle
from glob import glob
import csv
import re
from os.path import join, basename

from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        verbes = defaultdict(dict)

        for f in (glob(join(settings.SITE_ROOT, 'loadmapping/resources/tables-3.4/verbes/*.csv')) +
                glob(join(settings.SITE_ROOT, 'loadmapping/resources/tables-3.4/figees/*.csv'))):
            csvfile = open(f)
            # Si pas verbe, alors figée
            try:
                classe = re.search('V_([^.]+).lgt.csv', basename(f)).group(1)
            except AttributeError as e:
                classe = re.search('([^.]+).lgt.csv', basename(f)).group(1)

            ladlreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            verbes[classe]['all'] = []

            # Read verb position from first line
            first_line = next(ladlreader)
            try:
                verbe_index = first_line.index('<ENT>V')
                pronominal_index = first_line.index('<ENT>Ppv')
            except ValueError as e:
                if 'figees' not in f:
                    print('ERROR in {}'.format(f))
                continue

            # Read verb attributes with other lines
            for line in ladlreader:
                if len(line) <= 1:
                    continue

                # Search verb
                verbes[classe]['all'].append(line[verbe_index])
                pronominal_marker = line[pronominal_index]
                if pronominal_marker != "<E>":
                    verbes[classe]['all'][-1] += " {}".format(pronominal_marker)

                # Store column information
                for i, col in enumerate(line):
                    # Make sure lists exist in each dictionary value
                    col_name = first_line[i]

                    # We want 32C[+V-n instrument (forme V-n)] to work, that is
                    # also consider verbs as a '+'
                    col_value_list = ['-' if col in ['-', '<E>'] else col]
                    if col_value_list[0] not in ['-', '+', '~']:
                        col_value_list.append('+')


                    if col_name.startswith('<'):
                        continue
                    if not col_name in verbes[classe]:
                        verbes[classe][col_name] = {}
                    for col_value in col_value_list:
                        if not col_value in verbes[classe][col_name]:
                            verbes[classe][col_name][col_value] = []

            csvfile = open(f)
            ladlreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            next(ladlreader)
            for verb_id, line in enumerate(ladlreader):
                if len(line) <= 1:
                    continue
                assert len(line) == len(first_line)

                for i, col in enumerate(line):
                    if col == '~':
                        continue

                    col_name = first_line[i]
                    if col_name.startswith('<'):
                        continue

                    # We want 32C[+V-n instrument (forme V-n)] to work, that is
                    # also consider verbs as a '+'
                    col_value_list = ['-' if col in ['-', '<E>'] else col]
                    if col_value_list[0] not in ['-', '+', '~']:
                        col_value_list.append('+')

                    for col_value in col_value_list:
                        verbes[classe][col_name][col_value].append(verbes[classe]['all'][verb_id])

            print(f)

        with open(join(settings.SITE_ROOT, 'loadmapping/data/LADL_to_verbes'), 'wb') as f:
            pickle.dump(verbes, f, 3)

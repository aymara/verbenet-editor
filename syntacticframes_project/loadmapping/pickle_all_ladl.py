#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from collections import defaultdict
import pickle
from glob import glob
import csv
import re
import os

def LADL_to_verbes():
    verbes = defaultdict(dict)

    for f in glob('resources/tables-3.4/verbes/*.csv') + glob('resources/tables-3.4/figees/*.csv'):
        csvfile = open(f)
        # Si pas verbe, alors figée
        try:
            classe = re.search('V_([^.]+).lgt.csv', os.path.basename(f)).group(1)
        except AttributeError as e:
            classe = re.search('([^.]+).lgt.csv', os.path.basename(f)).group(1)

        ladlreader = csv.reader(csvfile, delimiter=';', quotechar='"')
        verbes[classe]['all'] = []

        # Read verb position from first line
        first_line = next(ladlreader)
        try:
            verbe_index = first_line.index('<ENT>V')
            pronominal_index = first_line.index('<ENT>Ppv')
        except ValueError as e:
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
            verb = verbes[classe]['all'][-1]

            # Store column information
            for i, col in enumerate(line):
                # Make sure lists for - and + exist, even if empty
                if col in ['-', '+', '~', '<E>']:
                    for possible in ['-', '+']:
                        col_name = '{}{}'.format(possible, first_line[i])
                        if not col_name in verbes[classe]:
                            verbes[classe][col_name] = []

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
                if '+{}'.format(col_name) in verbes[classe]:
                    if col in ['-', '<E>']:
                        col = '-'
                    else:
                        col = '+'
                    col_name = '{}{}'.format(col, first_line[i])  # '+N2 détrimentaire'
                    verbes[classe][col_name].append(verbes[classe]['all'][verb_id])

        print(f)

    return verbes

print("dumping LADL data")
with open('data/LADL_to_verbes', 'wb') as f:
    pickle.dump(LADL_to_verbes(), f, pickle.HIGHEST_PROTOCOL)

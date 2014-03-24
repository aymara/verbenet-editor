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
        with open(f) as csvfile:
            # Si pas verbe, alors figée
            try:
                classe = re.search('V_([^.]+).lgt.csv', os.path.basename(f)).group(1)
            except AttributeError as e:
                classe = re.search('([^.]+).lgt.csv', os.path.basename(f)).group(1)

            verbes[classe]['all'] = []

            ladlreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            first_row = next(ladlreader)
            print(f)
            try:
                verbe_index = first_row.index('<ENT>V')
                pronominal_index = first_row.index('<ENT>Ppv')

                for row in ladlreader:
                    if len(row) > 1:
                        # First search verb
                        verbes[classe]['all'].append(row[verbe_index])
                        pronominal_marker = row[pronominal_index]
                        if pronominal_marker != "<E>":
                            verbes[classe]['all'][-1] += " {}".format(pronominal_marker)
                        verb = verbes[classe]['all'][-1] 

                        # Then store column information
                        for i, col in enumerate(row):
                            # Make sure lists for - and + exist, even if empty
                            if col in ['-', '+', '~']:
                                for possible in ['-', '+']:
                                    col_name = '{}{}'.format(possible, first_row[i])
                                    if not col_name in verbes[classe]:
                                        verbes[classe][col_name] = []

                            if col in ['-', '+']:
                                col_name = '{}{}'.format(col, first_row[i])  # '+N2 détrimentaire'
                                verbes[classe][col_name].append(verb)
            except: continue

    return verbes

print("dumping LADL data")
with open('data/LADL_to_verbes', 'wb') as f:
    pickle.dump(LADL_to_verbes(), f, pickle.HIGHEST_PROTOCOL)

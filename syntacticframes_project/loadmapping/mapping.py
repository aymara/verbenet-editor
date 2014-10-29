#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from lxml.etree import ElementTree
from os.path import join
import csv

from django.conf import settings

from syntacticframes.models import LevinClass, VerbNetClass, VerbNetFrameSet
from .mappedverbs import translations_for_class


FORGET_LIST = ['?', '-', '', '*']


def get_members(tree):
    return [member.get('name') for member in tree.findall(".//MEMBER")]

def read_csv(filename):
    with open(filename) as csvfile:
        corresreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        lines = []
        # Forget header
        next(corresreader)
        for row in corresreader:
            print(row)
            vn = row[0].split()[1]
            paragon, commentaire = row[3], row[4]
            # Two empty lines, nothing to do
            # or Impossible to translate, continue
            if (row[1] in FORGET_LIST and row[2] in FORGET_LIST) or (row[1] == '-' or row[2] == '-'):
                lines.append({'classe': vn, 'candidates': [], 'paragon': paragon, 'lvf': row[2], 'lvf_orig': row[2], 'ladl': row[1], 'ladl_orig': row[1], 'verbnet_members': [], 'commentaire': commentaire})
            else:
                tree = ElementTree(file=join(settings.SITE_ROOT,
                                   "verbnet/verbnet-3.2/{}.xml".format(vn)))
                verbnet_members = get_members(tree)
                final = translations_for_class(verbnet_members, row[1], row[2])
                lines.append({'classe': vn, 'candidates':  final,
                             'paragon': paragon, 'lvf_orig': row[2], 'ladl_orig': row[1],
                             'verbnet_members': verbnet_members,
                             'commentaire': commentaire})

    return lines


def get_levin(c):
    # TODO regex
    return c.split('-')[1].split('.')[0]

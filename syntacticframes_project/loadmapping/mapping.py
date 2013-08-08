#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from lxml.etree import ElementTree
import subprocess
import io
import pickle
import os
from os.path import join
import csv
import sys
import locale
import re
from functools import cmp_to_key
import itertools
from operator import itemgetter
from collections import defaultdict

from django.conf import settings

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

FVN_PATH = settings.FVN_PATH
FORGET_LIST = ['?', '*', '', '∅']


def get_members(tree):
    return [member.get('name') for member in tree.findall(".//MEMBER")]

with open(join(FVN_PATH, 'data/LADL_to_verbes'), 'rb') as f:
    ladl_dict = pickle.load(f)
with open(join(FVN_PATH, 'data/LVF+1_to_verbs'), 'rb') as f:
    lvf_dict = pickle.load(f)
with open(join(FVN_PATH, 'data/DICOVALENCE_VERBS'), 'rb') as f:
    dicovalence_verbs = pickle.load(f)
with open(join(FVN_PATH, 'data/verb_dictionary.pickle'), 'rb') as f:
    verb_dict = pickle.load(f)


# We want to allow multiple classes and various writings that make sense for
# humans
def parse_complex_lvfladl(raw):
    ladl = raw.replace("-", "")

    if " ou " in ladl:
        operation = 'ou'
        ladl = ladl.split(" ou ")
    elif " et " in ladl:
        operation = 'et'
        ladl = ladl.split(" et ")
    else:
        operation = None
        ladl = [ladl]

    for i, ladl_class in enumerate(ladl):
        if ladl_class.endswith("source") or ladl_class.endswith("dest"):
            ladl[i] = ladl_class.split()[0]

    return operation, ladl


def parse_path(specific_class):
    path = []
    mode = 'new'
    for c in specific_class:
        if c == '[':
            path.append('')
            mode = 'same'
        elif c == ']':
            mode = 'new'
        elif c == '.':
            continue
        else:
            if mode == 'same':
                path[-1] += c
            elif mode == 'new':
                path.append(c)
            else:
                raise Exception('Unknown mode {}'.format(mode))

    return path


def get_one_verb_class(specific_class, resource):
    if resource == 'LADL':
        return get_one_verb_class_ladl(specific_class)
    elif resource == 'LVF':
        path = parse_path(specific_class)
        return get_one_verb_class_lvf(lvf_dict, path)


def get_one_verb_class_ladl(ladl_class):
    """Generalized version of specific_dict[specific_class] which allows
    regexes"""
    selected_verbs = set()
    for one_class in ladl_dict:
        # if regex is invalid, exit
        stripped = ladl_class.strip()
        if re.match(ladl_class, one_class):
            selected_verbs |= set(ladl_dict[one_class])

    return list(selected_verbs)


def everything_from_dict(d):
    if type(d) == list:
        return d
    elif type(d) == dict:
        l = []
        for k in d:
            l.extend(everything_from_dict(d[k]))
        return l
    else:
        raise Exception("Unknown type {}!".format(type(d)))


def get_one_verb_class_lvf(lvf_dict, lvf_path):
    """Recursively return all verbs for @lvf_class (eg. L3b, N1c.[12])"""
    if not lvf_path:
        if type(lvf_dict) == list:
            return set(lvf_dict)
        elif type(lvf_dict) == dict:
            return everything_from_dict(lvf_dict)
        else:
            raise Exception("Unknown type {}!".format(type(d)))
    else:
        prefix = lvf_path[0]
        suffix = lvf_path[1:]
        if len(prefix) > 1:
            keys = [c for c in prefix]
        else:
            keys = [prefix]

        verb_list = []
        for k in keys:
            new_stuff = get_one_verb_class_lvf(lvf_dict[k], suffix)
            verb_list.extend(new_stuff)

        return verb_list


def get_verbs_for_class_list(operation_and_list, resource):
    """Given a pre-processed list (by parse_*), return corresponding verbs"""
    operation, class_list = operation_and_list
    verbs = set(get_one_verb_class(class_list[0], resource))

    if operation is None:
        assert(len(class_list) == 1)
    else:
        assert(len(class_list) > 1)
        for specific_class in class_list[1:]:
            new_verbs = set(get_one_verb_class(specific_class, resource))
            if operation == 'ou':
                verbs |= new_verbs
            elif operation == 'et':
                verbs &= new_verbs

    return verbs


def translations_for_class(verbs, ladl, lvf):
    ladl_classes = parse_complex_lvfladl(ladl)
    lvf_classes = parse_complex_lvfladl(lvf)

    candidates = defaultdict(set)
    lvf, ladl = set(), set()

    for v in verbs:
        for c in verb_dict[v]:
            candidates[c].add(v)

    if not ladl_classes[1][0] in FORGET_LIST:
        ladl = get_verbs_for_class_list(ladl_classes, 'LADL')
        if not ladl:
            print("Warning, unknown class {}".format(ladl_classes))

    if not lvf_classes[1][0] in FORGET_LIST:
        lvf = get_verbs_for_class_list(lvf_classes, 'LVF')
        if not lvf:
            print("Warning, unknown class {}".format(lvs_classes))

    final = []
    for c in candidates:
        color = 'none'
        if c in ladl and c in lvf:
            color, id_color = 'both', 0
        elif c in lvf:
            color, id_color = 'lvf', 2
        elif c in ladl:
            color, id_color = 'ladl', 1
        elif c in dicovalence_verbs:
            color, id_color = 'dicovalence', 3
        else:
            color, id_color = 'unknown', 4
        final.append((c, color, id_color, ",".join(candidates[c])))

    final = sorted(final, key=lambda c: locale.strxfrm(c[0]))
    final.sort(key=itemgetter(2))

    return final


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
                tree = ElementTree(file=join(FVN_PATH,
                                   "resources/verbnet-3.2/{}.xml".format(vn)))
                verbnet_members = get_members(tree)
                final = translations_for_class(verbnet_members, row[1], row[2])
                lines.append({'classe': vn, 'candidates':  final,
                             'paragon': paragon, 'lvf_orig': row[2], 'ladl_orig': row[1],
                             'verbnet_members': verbnet_members,
                             'commentaire': commentaire})

    return lines

from syntacticframes.models import \
    LevinClass, VerbNetClass, VerbNetMember, VerbTranslation


def get_levin(c):
    # TODO regex
    return c.split('-')[1].split('.')[0]

from django.db import transaction

def import_mapping():
    verbnet = read_csv(join(FVN_PATH, 'resources/Correspondances.csv'))


    with transaction.commit_on_success():
        candidates = {}

        for classe in verbnet:
            print("Saving {}".format(classe["classe"]))
            v = VerbNetClass(
                levin_class=LevinClass.objects.get(
                    number=get_levin(classe["classe"])),
                name=classe["classe"],
                paragon=classe["paragon"],
                comment=classe["commentaire"],
                lvf_string=classe["lvf_orig"],
                ladl_string=classe["ladl_orig"])
            v.save()

            #for word in classe["verbnet_members"]:
            #    VerbNetMember(verbnet_class=v, lemma=word).save()

            #for word in classe["candidates"]:
            #    VerbTranslation(
            #        verb=word[0], verbnet_class=v,
            #        category=word[1], origin=word[3]).save()
            candidates[classe['classe']] = classe['candidates']

        return candidates, verb_dict


if __name__ == '__main__':
    import_mapping()

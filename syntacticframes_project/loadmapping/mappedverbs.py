import pickle
import locale
from os.path import join
from operator import itemgetter
from collections import defaultdict

from django.conf import settings

from parsecorrespondance import parse
from loadmapping.models import LVFVerb

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')


with open(join(settings.SITE_ROOT, 'loadmapping/data/LADL_to_verbes'), 'rb') as f:
    ladl_dict = pickle.load(f)
with open(join(settings.SITE_ROOT, 'loadmapping/data/DICOVALENCE_VERBS'), 'rb') as f:
    dicovalence_verbs = pickle.load(f)
with open(join(settings.SITE_ROOT, 'loadmapping/data/verb_dictionary.pickle'), 'rb') as f:
    verb_dict = pickle.load(f)

class UnknownColumnException(Exception):
    def __init__(self, column, class_name):
        # Remove + or -
        self.column = column[1:]
        self.class_name = class_name

    def __str__(self):
        return 'La classe {} n\'a pas de colonne {}'.format(self.class_name, self.column)

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


def everything_from_dict(d):
    if type(d) == list:
        return set(d)
    elif type(d) == dict:
        l = []
        for k in d:
            l.extend(everything_from_dict(d[k]))
        return set(l)
    else:
        raise Exception("Unknown type {}!".format(type(d)))


def verbs_for_one_class(resource, wanted_class):
    specific_class, column_list = wanted_class

    if resource == 'LADL':
        if column_list is None:
            return set(ladl_dict[specific_class]['all'])
        else:
            if len(column_list) > 2:
                assert column_list[0] in ['and', 'or']

            for column in column_list[1:]:
                if not column in ladl_dict[specific_class]:
                    raise UnknownColumnException(column, specific_class)

            ladl_verbs = set(ladl_dict[specific_class][column_list[1]])
            for column in column_list[2:]:
                if column_list[0] == 'or':
                    ladl_verbs |= set(ladl_dict[specific_class][column])
                elif column_list[0] == 'and':
                    ladl_verbs &= set(ladl_dict[specific_class][column])
            return ladl_verbs

    elif resource == 'LVF':
        lvf_verbs_qs = LVFVerb.objects.filter(lvf_class__startswith=specific_class)
        if column_list is not None:
            if len(column_list) == 2:
                lvf_verbs_qs = LVFVerb.objects.filter(construction__contains=column_list[1][1:])
            else:
                assert column_list[0] in ['and', 'or']

                for column in column_list[1:]:
                    if column_list[0] == 'and':
                        if column[0] == '+':
                            lvf_verbs_qs = lvf_verbs_qs & LVFVerb.objects.filter(
                                construction__contains=column[1:])
                        elif column[0] == '-':
                            lvf_verbs_qs = lvf_verbs_qs & LVFVerb.objects.exclude(
                                construction__contains=column[1:])
                    elif column_list[0] == 'or':
                        if column[0] == '+':
                            lvf_verbs_qs = lvf_verbs_qs | LVFVerb.objects.filter(
                                construction__contains=column[1:])
                        elif column[0] == '-':
                            lvf_verbs_qs = lvf_verbs_qs | LVFVerb.objects.exclude(
                                construction__contains=column[1:])

        return {v.lemma for v in lvf_verbs_qs}


def verbs_for_class_mapping(mapping):
    def verbs_for_class_mapping_aux(resource, parse_tree):
        """Given a pre-processed list (by parse_*), return corresponding verbs"""
        if not parse_tree:
            return []
        elif 'leaf' in parse_tree:
            return verbs_for_one_class(resource, parse_tree['leaf'])
        elif 'operator' in parse_tree:
            verb_lists = [verbs_for_class_mapping_aux(resource, c) for c in parse_tree['children']]
            if parse_tree['operator'] == 'and':
                return set.intersection(*verb_lists)
            elif parse_tree['operator'] == 'or':
                return set.union(*verb_lists)

    return verbs_for_class_mapping_aux(mapping.resource, mapping.parse_tree)



def translations_for_class(verbs, ladl, lvf):
    ladl_verbs = verbs_for_class_mapping(parse.FrenchMapping('LADL', ladl))
    lvf_verbs = verbs_for_class_mapping(parse.FrenchMapping('LVF', lvf))

    candidates = defaultdict(set)
    for v in verbs:
        for c in verb_dict[v]:
            candidates[c].add(v)

    final = []
    for c in candidates:
        color = 'none'
        if c in ladl_verbs and c in lvf_verbs:
            color, id_color = 'both', 0
        elif c in lvf_verbs:
            color, id_color = 'lvf', 2
        elif c in ladl_verbs:
            color, id_color = 'ladl', 1
        elif c in dicovalence_verbs:
            color, id_color = 'dicovalence', 3
        else:
            color, id_color = 'unknown', 4
        final.append((c, color, id_color, ",".join(sorted(candidates[c]))))

    final = sorted(final, key=lambda c: locale.strxfrm(c[0]))
    final.sort(key=itemgetter(2))

    return final

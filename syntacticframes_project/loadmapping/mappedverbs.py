import pickle
from os.path import join

from django.conf import settings

import logging
logger_warnings = logging.getLogger('warnings')


with open(join(settings.SITE_ROOT, 'loadmapping/data/LADL_to_verbes'), 'rb') as f:
    ladl_dict = pickle.load(f)
with open(join(settings.SITE_ROOT, 'loadmapping/data/LVF+1_to_verbs'), 'rb') as f:
    lvf_dict = pickle.load(f)


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


def verbs_for_one_lvf_class(lvf_dict, lvf_path):
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

        verb_set = set()
        for k in keys:
            new_stuff = set(verbs_for_one_lvf_class(lvf_dict[k], suffix))
            verb_set |= new_stuff

        return verb_set


def verbs_for_one_class(specific_class, resource):
    if resource == 'LADL':
        return set(ladl_dict[specific_class])
    elif resource == 'LVF':
        path = parse_path(specific_class)
        return verbs_for_one_lvf_class(lvf_dict, path)



def verbs_for_class_mapping(mapping):
    """Given a pre-processed list (by parse_*), return corresponding verbs"""
    if mapping.operator is None:
        if not mapping.operands:
            return []
        else:
            assert len(mapping.operands) == 1
            return verbs_for_one_class(mapping.operands[0], mapping.resource)
    else:
        verb_lists = [verbs_for_class_mapping(o) for o in mapping.operands]
        if mapping.operator == 'and':
            return set.intersection(*verb_lists)
        elif mapping.operator == 'or':
            return set.union(*verb_lists)

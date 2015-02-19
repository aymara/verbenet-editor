import io
import sys
import traceback
import re
from pathlib import Path
from collections import defaultdict, OrderedDict

from django.shortcuts import render

from syntacticframes.models import VerbNetFrame, VerbNetClass
from export.export import merge_primary_and_syntax, WrongFrameException
from parsecorrespondance.parse import UnknownErrorException
from loadmapping.mappedverbs import translations_for_class


def errors(request):
    issues = defaultdict(list)
    frames_ok, frames_total = 0, 0

    for db_frame in VerbNetFrame.objects.select_related('frameset', 'frameset__verbnet_class', 'frameset__verbnet_class__levin_class').filter(removed=False):
        if db_frame.removed or db_frame.frameset.removed:
            continue

        frames_total += 1
        output = io.StringIO()
        try:
            merge_primary_and_syntax(db_frame.syntax, db_frame.roles_syntax, output)
            frames_ok += 1
        except WrongFrameException as e:
            issues[e.args[0]].append(db_frame)
        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            tb_info = traceback.extract_tb(exc_tb)
            path, line, func, text = tb_info[-1]
            exception = traceback.format_exception_only(exc_type, exc_value)[0]
            filename = Path(path).name
            issues['{} ({}:{})'.format(exception, filename, line)].append(db_frame)


    return render(request, 'errors.html', {
        'issues': OrderedDict(sorted(issues.items(), reverse=True, key=lambda kv: len(kv[1]))),
        'frames_ok': frames_ok,
        'frames_total': frames_total,
        'ratio': '{:.1%}'.format(frames_ok / frames_total),
    })


def get_prep(roles_syntax):
    prep_list = re.findall(r"{[-\w/ +']+}", roles_syntax)
    for prep in prep_list:
        if '/' in prep or ' ' in prep:
            split_char = '/' if '/' in prep else ' '
            for prep_part in prep.strip('{}').split(split_char):
                yield prep_part
        else:
            yield prep.strip('{}')


def get_restr(roles_syntax):
    restr_list = re.findall(r'<.+?>', roles_syntax)
    for restr in restr_list:
        yield restr


def get_roles(roles_syntax):
    split_list = re.findall('[a-zA-Z-]+', roles_syntax)
    for split in split_list:
        if split == 'V':
            continue
        elif split.lower() == split or split.upper() == split:
            continue
        elif '-' in split and not split.startswith('Co-'):
            continue
        elif split in ['Psubj', 'Pind', 'Vinf', 'Il', 'Pr', 'Qu', 'Que', 'Loc', 'Adv', 'Co']:
            continue
        else:
            yield split


def distributions(request):
    role_dict, restriction_dict, preposition_dict = defaultdict(list), defaultdict(list), defaultdict(list)

    for db_frame in VerbNetFrame.objects.select_related('frameset', 'frameset__verbnet_class', 'frameset__verbnet_class__levin_class').filter(removed=False):
        if db_frame.removed or db_frame.frameset.removed:
            continue

        for role in get_roles(db_frame.roles_syntax):
            role_dict[role].append(db_frame)

        for prep in get_prep(db_frame.roles_syntax):
            preposition_dict[prep].append(db_frame)

        prep_list = list(get_restr(db_frame.roles_syntax))
        if ('<' in db_frame.roles_syntax or '>' in db_frame.roles_syntax) and not prep_list:
            print('{} -> {}'.format(db_frame.roles_syntax, prep_list))
        for restr in get_restr(db_frame.roles_syntax):
            restriction_dict[restr].append(db_frame)

    distribution_dict = OrderedDict([
        ('Restrictions', restriction_dict),
        ('Prépositions', preposition_dict),
        ('Rôles', role_dict)
    ])

    for distribution in distribution_dict:
        distribution_dict[distribution] = OrderedDict(sorted(distribution_dict[distribution].items(), key=lambda kv: (len(kv[1]), kv[0]), reverse=True))

    return render(request, 'distributions.html', {
        'distributions': distribution_dict
    })


def url_of_fs(fs):
    return "/class/{}/#{}".format(fs.verbnet_class.levin_class.number, fs.name)

def errors_for_class(frameset, ladl, lvf):
    """
    Lists framesets without any translation from LADL or LVF.

    We start with the root frameset then go on with children. This allows us to
    keep track of LVF and LADL strings: indeed, those get inherited from their
    parents.
    """
    if frameset.removed:
        return []

    errors = []

    try:
        members = [member.lemma for member in frameset.verbnetmember_set.all()]
        if members:
            final_translations = translations_for_class(members, ladl, lvf)
            ladl_verbs = [t for t in final_translations if t[1] in ['ladl', 'both']]
            lvf_verbs = [t for t in final_translations if t[1] in ['lvf', 'both']]

            if ladl and not ladl_verbs:
                errors.append((frameset.name, url_of_fs(frameset), 'ladl', ladl, ", ".join(members)))
            if lvf and not lvf_verbs:
                errors.append((frameset.name, url_of_fs(frameset), 'lvf', lvf, ", ".join(members)))
    except UnknownErrorException as e:
        mail_managers('Error was in {}'.format(frameset.name), message='')

    for child in frameset.children.filter(removed=False):
        new_ladl = ladl if not child.ladl_string else child.ladl_string
        new_lvf = lvf if not child.lvf_string else child.lvf_string
        errors.extend(errors_for_class(child, new_ladl, new_lvf))

    return errors


def get_empty_translations():
    errors = []
    last_lvf = None
    last_ladl = None

    for vn_class in VerbNetClass.objects.prefetch_related('verbnetframeset_set', 'verbnetframeset_set__verbnetmember_set'):
        root_frameset = vn_class.verbnetframeset_set.get(parent=None)
        errors.extend(errors_for_class(root_frameset, root_frameset.ladl_string, root_frameset.lvf_string))

    return errors

def emptytranslations(request):
    return render(request, 'emptytranslations.html', {
        'empty_translations_errors': get_empty_translations(),
    })

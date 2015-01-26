import re
from distutils.version import LooseVersion
from collections import defaultdict, OrderedDict
import locale

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import RequestContext, loader
from django.db.models import Prefetch

from syntacticframes.models import VerbNetFrameSet, VerbTranslation
from parsecorrespondance import parse

def ladl(request):
    def get_ladl_classes(parse_tree):
        if 'leaf' in parse_tree:
            if parse_tree['leaf'][0].startswith('C_'):
                return []
            else:
                return [parse_tree['leaf'][0]]
        elif 'operator' in parse_tree:
            l = []
            for child in parse_tree['children']:
                l.extend(get_ladl_classes(child))
            return l
        else:
            return []

    def ladl_sort_key(ladl):
        digit1, letter, digit2 = re.match('(\d+)(\D+)?(\d)?', ladl).groups()
        digit1 = int(digit1)

        if digit2 is None:
            digit2 = -1
        else:
            digit2 = int(digit2)

        if letter is None:
            letter = ''

        return digit1, letter, digit2

    inversed_ladl = {ladl: defaultdict(list) for ladl in parse.ladl_list if not ladl.startswith('C_')}

    for fs in VerbNetFrameSet.objects.select_related('verbnet_class', 'verbnet_class__levin_class').all():
        ladl_list = get_ladl_classes(parse.FrenchMapping('LADL', fs.ladl_string).parse_tree)
        for ladl in ladl_list:
            levin_number = fs.verbnet_class.levin_class.number
            inversed_ladl[ladl][levin_number].append(fs)

    # Sort LADL tables, Levin groups, and framesets
    for ladl in inversed_ladl:
        for levin_group in inversed_ladl[ladl]:
            inversed_ladl[ladl][levin_group] = sorted(inversed_ladl[ladl][levin_group], key=lambda fs: LooseVersion(fs.name))
        inversed_ladl[ladl] = OrderedDict(sorted(inversed_ladl[ladl].items(), key=lambda kv: LooseVersion(kv[0])))

    inversed_ladl = OrderedDict(sorted(inversed_ladl.items(), key=lambda kv: ladl_sort_key(kv[0])))

    template = loader.get_template('ladl_index.html')
    context = RequestContext(request, {
        'inversed_ladl': inversed_ladl,
    })

    return HttpResponse(template.render(context))

def members(request):
    return redirect('/index/members/a')

def members_letter(request, letter):
    member_index = defaultdict(lambda: defaultdict(list))

    for fs in VerbNetFrameSet.objects.prefetch_related('verbnet_class', 'verbnet_class__levin_class', Prefetch('verbtranslation_set', queryset=VerbTranslation.objects.filter(verb__istartswith=letter), to_attr='filtered_verbs')):
        for verbtranslation in VerbTranslation.all_valid(fs.filtered_verbs):
            member_index[verbtranslation.verb][fs.verbnet_class.levin_class.number].append(fs)

    for verb in member_index:
        for levin_group in member_index[verb]:
            member_index[verb][levin_group] = sorted(member_index[verb][levin_group], key=lambda fs: LooseVersion(fs.name))
        member_index[verb] = OrderedDict(sorted(member_index[verb].items(), key=lambda kv: LooseVersion(kv[0])))
    member_index = OrderedDict(sorted(member_index.items(), key=lambda kv: locale.strxfrm(kv[0])))

    template = loader.get_template('member_index.html')
    context = RequestContext(request, {
        'member_index': member_index,
        'active_letter': letter,
        'letter_list': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
            'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
            'y', 'z']

    })

    return HttpResponse(template.render(context))
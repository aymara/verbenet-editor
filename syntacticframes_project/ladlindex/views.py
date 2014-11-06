import re
from distutils.version import LooseVersion
from collections import defaultdict, OrderedDict

from django.http import HttpResponse
from django.template import RequestContext, loader

from syntacticframes.models import VerbNetFrameSet
from parsecorrespondance import parse

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

def vn_sort_key(vn):
    return LooseVersion(vn)

def index(request):
    inversed_ladl = {ladl: defaultdict(list) for ladl in parse.ladl_list if not ladl.startswith('C_')}

    for fs in VerbNetFrameSet.objects.select_related('verbnet_class', 'verbnet_class__levin_class').all():
        ladl_list = get_ladl_classes(parse.FrenchMapping('LADL', fs.ladl_string).parse_tree)
        for ladl in ladl_list:
            levin_number = fs.verbnet_class.levin_class.number
            inversed_ladl[ladl][levin_number].append(fs.name)

    # Sort LADL tables, Levin groups, and framesets
    for key in inversed_ladl:
        for group in inversed_ladl[key]:
            inversed_ladl[key][group] = sorted(inversed_ladl[key][group], key=vn_sort_key)
        inversed_ladl[key] = OrderedDict(sorted(inversed_ladl[key].items(), key=lambda kv: vn_sort_key(kv[0])))

    inversed_ladl = OrderedDict(sorted(inversed_ladl.items(), key=lambda kv: ladl_sort_key(kv[0])))

    template = loader.get_template('ladl_index.html')
    context = RequestContext(request, {
        'inversed_ladl': inversed_ladl,
    })

    return HttpResponse(template.render(context))

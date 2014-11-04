import re

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

def index(request):
    inversed_ladl = {ladl: [] for ladl in parse.ladl_list if not ladl.startswith('C_')}
    for fs in VerbNetFrameSet.objects.all():
        ladl_list = get_ladl_classes(parse.FrenchMapping('LADL', fs.ladl_string).parse_tree)
        for ladl in ladl_list:
            inversed_ladl[ladl].append(fs.name)

    ladl_sorted_keys = sorted(inversed_ladl.keys(), key=ladl_sort_key)
    inversed_ladl_pairs = [(key, inversed_ladl[key]) for key in ladl_sorted_keys]

    template = loader.get_template('ladl_index.html')
    context = RequestContext(request, {
        'inversed_ladl_pairs': inversed_ladl_pairs,
    })

    return HttpResponse(template.render(context))

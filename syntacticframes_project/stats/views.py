from django.http import HttpResponse
from django.template import RequestContext, loader

from syntacticframes.models import VerbNetClass, VerbTranslation, VerbNetFrameSet
from loadmapping.mapping import translations_for_class


def index(request):
    num_members, unique_members, num_verbs, unique_verbs, num_classes = count_verbs()
    empty_translations_errors = empty_translations()

    template = loader.get_template('stats.html')
    context = RequestContext(request, {
        'num_members': num_members,
        'unique_members': len(unique_members),
        'num_verbs': num_verbs,
        'unique_verbs': len(unique_verbs),
        'num_classes': num_classes,

        'empty_translations_errors': empty_translations_errors,
    })

    return HttpResponse(template.render(context))

def is_any_from_resource(translations, wanted_resource):
    return any([resource == wanted_resource for verb, resource, number, member in translations])

def url_of_fs(fs):
    return "/class/{}/#{}".format(fs.verbnet_class.levin_class.number, fs.name)

def empty_translations():
    errors = []
    last_lvf = None
    last_ladl = None

    for db_fs in VerbNetFrameSet.objects.all():
        lvf = db_fs.lvf_string if db_fs.lvf_string else last_lvf
        ladl = db_fs.ladl_string if db_fs.ladl_string else last_ladl

        members = [member.lemma for member in db_fs.verbnetmember_set.all()]
        if members:
            if ladl not in ['-', '?', '∅']:
                ladl_verbs = translations_for_class(members, ladl, None)
                if not is_any_from_resource(ladl_verbs, 'ladl'):
                    errors.append((db_fs.name, url_of_fs(db_fs), 'ladl', ladl, ", ".join(members)))
            if lvf not in ['-', '?', '∅']:
                lvf_verbs = translations_for_class(members, None, lvf)
                if not is_any_from_resource(lvf_verbs, 'lvf'):
                    errors.append((db_fs.name, url_of_fs(db_fs), 'lvf', lvf, ", ".join(members)))


        if db_fs.lvf_string:
            last_lvf = db_fs.lvf_string
        if db_fs.ladl_string:
            last_ladl = db_fs.ladl_string

    return errors


def count_verbs():
    unique_verbs, unique_members = set(), set()
    num_classes, num_verbs, num_members = 0, 0, 0
    for vn_class in VerbNetClass.objects.all():
        num_classes += 1
        for vn_fs in vn_class.verbnetframeset_set.all():
            for t in VerbTranslation.objects.filter(frameset=vn_fs,
                                                    category = 'both'):
               unique_verbs.add(t.verb) 
               num_verbs += 1
            for m in vn_fs.verbnetmember_set.all():
                unique_members.add(m.lemma)
                num_members += 1

    return num_members, unique_members, num_verbs, unique_verbs, num_classes



from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.mail import mail_managers

from syntacticframes.models import VerbNetClass, VerbTranslation, VerbNetFrameSet
from loadmapping.mappedverbs import translations_for_class
from parsecorrespondance.parse import UnknownErrorException


def index(request):
    num_members, unique_members, num_verbs, unique_verbs, num_validated_verbs, unique_validated_verbs, num_classes, num_framesets = count_verbs()
    empty_translations_errors = empty_translations()

    template = loader.get_template('stats.html')
    context = RequestContext(request, {
        'num_members': num_members,
        'unique_members': len(unique_members),
        'num_verbs': num_verbs,
        'unique_verbs': len(unique_verbs),
        'num_validated_verbs': num_validated_verbs,
        'unique_validated_verbs': len(unique_validated_verbs),
        'num_classes': num_classes,
        'num_framesets': num_framesets,

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

    for db_fs in VerbNetFrameSet.objects.prefetch_related('verbnetmember_set').filter(removed=False):
        if db_fs.lvf_string:
            lvf = db_fs.lvf_string
        else:
            if '-' in db_fs.name:
                lvf = last_lvf
            else:
                lvf = None
        ladl = db_fs.ladl_string if db_fs.ladl_string else last_ladl

        try:
            members = [member.lemma for member in db_fs.verbnetmember_set.all()]
            if members:
                final_translations = translations_for_class(members, ladl, lvf)
                ladl_verbs = [t for t in final_translations if t[1] == 'ladl']
                lvf_verbs = [t for t in final_translations if t[1] == 'lvf']

                if not is_any_from_resource(ladl_verbs, 'ladl'):
                    errors.append((db_fs.name, url_of_fs(db_fs), 'ladl', ladl, ", ".join(members)))
                if not is_any_from_resource(lvf_verbs, 'lvf'):
                    errors.append((db_fs.name, url_of_fs(db_fs), 'lvf', lvf, ", ".join(members)))
        except UnknownErrorException as e:
            mail_managers('Error was in {}'.format(db_fs.name), message='')                


        if db_fs.lvf_string:
            last_lvf = db_fs.lvf_string
        if db_fs.ladl_string:
            last_ladl = db_fs.ladl_string

    return errors

def chosen_verbs(vn_fs):
    all_verbs = vn_fs.verbtranslation_set.all()
    both_verbs = [verb for verb in all_verbs if verb.category == 'both']
    if both_verbs:
        return both_verbs
    else:
        ladl_verbs = set([verb for verb in all_verbs if verb.category == 'ladl'])
        lvf_verbs = set([verb for verb in all_verbs if verb.category == 'lvf'])
        return list(ladl_verbs | lvf_verbs)
    
def count_verbs():
    unique_verbs, unique_validated_verbs, unique_members = set(), set(), set()
    num_framesets, num_classes, num_verbs, num_validated_verbs, num_members = 0, 0, 0, 0, 0
    for vn_class in VerbNetClass.objects.prefetch_related(
        'verbnetframeset_set',
        'verbnetframeset_set__verbnetmember_set',
        'verbnetframeset_set__verbtranslation_set').all():

        num_classes += 1
        for vn_fs in vn_class.verbnetframeset_set.all():
            num_framesets += 1
            for t in chosen_verbs(vn_fs):
               unique_verbs.add(t.verb) 
               num_verbs += 1
               if t.validation_status == VerbTranslation.STATUS_VALID:
                   unique_validated_verbs.add(t.verb)
                   num_validated_verbs += 1
            for m in vn_fs.verbnetmember_set.all():
                unique_members.add(m.lemma)
                num_members += 1

    return num_members, unique_members, num_verbs, unique_verbs, num_validated_verbs, unique_validated_verbs, num_classes, num_framesets



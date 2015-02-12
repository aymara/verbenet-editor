from django.http import HttpResponse
from django.template import RequestContext, loader
from django.core.mail import mail_managers

from syntacticframes.models import VerbNetClass, VerbTranslation


def index(request):
    num_members, unique_members, num_validated_verbs, unique_validated_verbs, num_classes, num_framesets = count_verbs()

    template = loader.get_template('stats.html')
    context = RequestContext(request, {
        'num_members': num_members,
        'unique_members': len(unique_members),
        'num_validated_verbs': num_validated_verbs,
        'unique_validated_verbs': len(unique_validated_verbs),
        'num_classes': num_classes,
        'num_framesets': num_framesets,
    })

    return HttpResponse(template.render(context))

def count_verbs():
    unique_validated_verbs, unique_members = set(), set()
    num_framesets, num_classes, num_validated_verbs, num_members = 0, 0, 0, 0
    for vn_class in VerbNetClass.objects.prefetch_related(
        'verbnetframeset_set',
        'verbnetframeset_set__verbnetmember_set',
        'verbnetframeset_set__verbtranslation_set').all():

        num_classes += 1
        for vn_fs in vn_class.verbnetframeset_set.all():
            num_framesets += 1
            for t in VerbTranslation.all_valid(vn_fs.verbtranslation_set.all()):
                unique_validated_verbs.add(t.verb)
                num_validated_verbs += 1
            for m in vn_fs.verbnetmember_set.all():
                unique_members.add(m.lemma)
                num_members += 1

    return num_members, unique_members, num_validated_verbs, unique_validated_verbs, num_classes, num_framesets


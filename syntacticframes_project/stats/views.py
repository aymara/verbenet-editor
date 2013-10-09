from django.http import HttpResponse
from django.template import RequestContext, loader

from syntacticframes.models import VerbNetClass, VerbTranslation

def index(request):
    
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

    #print("{} classes, {} verbs/class, {} members/class".format(num_classes, num_verbs / num_classes, num_members/num_classes))

    template = loader.get_template('stats.html')
    context = RequestContext(request, {
        'num_members': num_members,
        'unique_members': len(unique_members),
        'num_verbs': num_verbs,
        'unique_verbs': len(unique_verbs),
        'num_classes': num_classes,
    })

    return HttpResponse(template.render(context))

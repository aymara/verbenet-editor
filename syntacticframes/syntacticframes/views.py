from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import redirect

from distutils.version import LooseVersion

from .models import LevinClass, VerbNetClass, VerbNetMember, VerbTranslation

def classe(request, class_number):
    levin_classes = list(LevinClass.objects.all())
    levin_classes.sort(key = lambda l: LooseVersion(l.number))

    active_class = LevinClass.objects.get(number = class_number)
    verbnet_classes = VerbNetClass.objects.filter(levin_class__exact = active_class)
    translations, origins = {}, {}

    for verbnet_class in verbnet_classes:
        translations[verbnet_class.name] = sorted(
            VerbTranslation.objects.filter(verbnet_class=verbnet_class))
        origins[verbnet_class.name] = VerbNetMember.objects.filter(verbnet_class=verbnet_class)

    template = loader.get_template('index.html')
    context = Context({
        'levin_classes': levin_classes,
        'active_class': active_class,
        'verbnet_classes': verbnet_classes,
        'all_translations': translations,
        'all_origins': origins,
    })
    return HttpResponse(template.render(context))

def index(request):
    # Hardcoding that the first class is 9
    return redirect('class/9/')

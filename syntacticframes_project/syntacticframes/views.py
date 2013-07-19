from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import redirect
from django.views.decorators.csrf import ensure_csrf_cookie

from distutils.version import LooseVersion
import logging

from .models import LevinClass, VerbNetClass, VerbNetMember, VerbTranslation, VerbNetFrameSet

logger = logging.getLogger('database')

@ensure_csrf_cookie
def classe(request, class_number):
    levin_classes = list(LevinClass.objects.all())
    levin_classes.sort(key = lambda l: LooseVersion(l.number))

    active_class = LevinClass.objects.get(number = class_number)
    verbnet_classes = list(VerbNetClass.objects.filter(levin_class__exact = active_class))
    verbnet_classes.sort(key = lambda v: LooseVersion(v.name.split('-')[1]))

    translations, origins = {}, {}

    #for verbnet_class in verbnet_classes:
    #    translations[verbnet_class.name] = sorted(
    #        VerbTranslation.objects.filter(verbnet_class=verbnet_class))
    #    origins[verbnet_class.name] = VerbNetMember.objects.filter(verbnet_class=verbnet_class)

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

def update(request):
    if request.method == 'POST':
        post = request.POST
        vn_class, field, label = post["vn_class"], post["field"], post["label"]
        logger.info("Update {}/{} to {}".format(vn_class, field, label))
        verbnet_class = VerbNetClass.objects.filter(name__exact = vn_class)[0]
        if field == 'ladl':
            verbnet_class.ladl_string = label
        elif field == 'lvf':
            verbnet_class.lvf_string = label
        verbnet_class.save()
    return HttpResponse("ok")

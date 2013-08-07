from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import redirect
from django.views.decorators.csrf import ensure_csrf_cookie

from distutils.version import LooseVersion
import logging
from time import gmtime, strftime

from .models import LevinClass, VerbNetClass, VerbNetMember, VerbTranslation, VerbNetFrameSet, VerbNetFrame

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
        when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
        refresh_class = False

        if field == 'roles_syntax':
            frame_id = int(post["frame_id"])
            frame = VerbNetFrame.objects.get(id=frame_id)
            old_label = frame.roles_syntax
            frame.roles_syntax = label
            frame.save()
            logger.info("{}: Updated {} in frame {} of {} from '{}' to '{}'"
                    .format(when, field, frame_id, vn_class, old_label, label))
        elif field == 'syntax':
            frame_id = int(post["frame_id"])
            frame = VerbNetFrame.objects.get(id=frame_id)
            old_label = frame.syntax
            frame.syntax = label
            frame.save()
            logger.info("{}: Updated {} in frame {} of {} from '{}' to '{}'"
                    .format(when, field, frame_id, vn_class, old_label, label))
        elif field == 'ladl':
            refresh_class = True
            verbnet_class = VerbNetClass.objects.get(name__exact = vn_class)
            old_label = verbnet_class.ladl_string
            verbnet_class.ladl_string = label
            verbnet_class.save()
            logger.info("{}: Updated {} in {} from '{}' to '{}'"
                    .format(when, field, vn_class, old_label, label))
        elif field == 'lvf':
            refresh_class = True
            verbnet_class = VerbNetClass.objects.get(name__exact = vn_class)
            old_label = verbnet_class.lvf_string
            verbnet_class.lvf_string = label
            verbnet_class.save()
            logger.info("{}: Updated {} in {} from '{}' to '{}'"
                    .format(when, field, vn_class, old_label, label))

        if refresh_class:
            import verbnet.verbnetreader
            from syntacticframes.management.commands.loadverbnet import save_class
            verbnet_class = VerbNetClass.objects.get(name__exact = vn_class)
            verbnet_class.verbnetframeset_set.all().delete()

            r = verbnet.verbnetreader.VerbnetReader('verbnet/verbnet-3.2/', False)
            c = r.files[verbnet_class.name]
            save_class(c, verbnet_class)
            
            
        return HttpResponse("ok")

def remove(request):
    if request.method == 'POST':
        post = request.POST
        model = post['model']
        when = strftime("%d/%m/%Y %H:%M:%S", gmtime())

        if model == 'VerbNetFrame':
            frame_id = int(request.POST['frame_id'])
            vn_class = request.POST['vn_class']
            syntax = request.POST['syntax']    
            db_frame = VerbNetFrame.objects.get(id=frame_id)
            db_frame.removed = True
            db_frame.save()
            logger.info("{}: Marked frame {}/{} as removed in class {}"
                        .format(when, frame_id, syntax, vn_class))

        return HttpResponse("ok")

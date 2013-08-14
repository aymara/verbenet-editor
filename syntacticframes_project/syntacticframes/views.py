from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.context_processors import csrf
from django.conf import settings
from django import forms

from distutils.version import LooseVersion
import logging
from time import gmtime, strftime
import os.path

from .models import LevinClass, VerbNetClass, VerbNetMember, VerbTranslation, VerbNetFrameSet, VerbNetFrame

logger = logging.getLogger('database')

@ensure_csrf_cookie
def classe(request, class_number):
    levin_classes = list(LevinClass.objects.all())
    levin_classes.sort(key = lambda l: LooseVersion(l.number))

    active_class = LevinClass.objects.get(number = class_number)
    verbnet_classes = list(VerbNetClass.objects.filter(levin_class__exact = active_class))
    verbnet_classes.sort(key = lambda v: LooseVersion(v.name.split('-')[1]))

    template = loader.get_template('index.html')
    context = Context({
        'levin_classes': levin_classes,
        'active_class': active_class,
        'verbnet_classes': verbnet_classes,
    })
    context.update(csrf(request))
    return HttpResponse(template.render(context))

@ensure_csrf_cookie
def vn_class(request, class_name):
    verbnet_class = VerbNetClass.objects.get(name=class_name)
    template = loader.get_template('classe.html')
    context = Context({
        'classe': verbnet_class,
    })
    context.update(csrf(request))
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
        elif field == 'semantics':
            frame_id = int(post["frame_id"])
            frame = VerbNetFrame.objects.get(id=frame_id)
            old_label = frame.semantics
            frame.semantics = label
            frame.save()
            logger.info("{}: Updated {} in frame {} of {} from '{}' to '{}'"
                    .format(when, field, frame_id, vn_class, old_label, label))
        elif field == 'example':
            frame_id = int(post["frame_id"])
            frame = VerbNetFrame.objects.get(id=frame_id)
            old_label = frame.example
            frame.example = label
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

            r = verbnet.verbnetreader.VerbnetReader(os.path.join(settings.FVN_PATH, 'resources/verbnet-3.2/'), False)
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

def add(request):
    if request.method == 'POST':
        post = request.POST
        when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
        if post['type'] == 'frame':
            parent_frameset = VerbNetFrameSet.objects.get(id=int(post['frameset_id']))
            vn_class = VerbNetClass.objects.get(id=int(post['vn_class_id']))
            try:
                max_position = max([f.position for f in parent_frameset.verbnetframe_set.all()])
            except:
                max_position = 0

            if max_position is None:
                max_position = 1

            f = VerbNetFrame(
                frameset=parent_frameset,
                position=max_position+1,
                syntax = post['syntax'],
                example = post['example'],
                roles_syntax = post['roles_syntax'],
                semantics = post['semantics']
            )
            f.save()
            logger.info("{}: Added frame {} ({},{},{}) in frameset {} from class {}".format(
                when, f.syntax, f.example, f.roles_syntax, f.semantics,
                parent_frameset.name, vn_class.name))

        return HttpResponse("ok")

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

        frameset_fields = ['paragon', 'comment', 'ladl_string', 'lvf_string']
        frame_fields = ['roles_syntax', 'syntax', 'semantics', 'example']
        refresh_fields = ['ladl_string', 'lvf_string']

        if field in frame_fields:
            frame_id = int(post["frame_id"])
            frame = VerbNetFrame.objects.get(id=frame_id)
            old_label = getattr(frame, field)
            setattr(frame, field, label)
            frame.save()
            logger.info("{}: Updated {} in frame {} of {} from '{}' to '{}'"
                    .format(when, field, frame_id, vn_class, old_label, label))
        elif field in frameset_fields:
            db_frameset = VerbNetFrameSet.objects.get(id = int(post['frameset_id']))
            old_label = getattr(db_frameset, field)
            setattr(db_frameset, field, label)
            db_frameset.save()
            logger.info("{}: Updated {} in {}/{} from '{}' to '{}'"
                    .format(when, field, vn_class, db_frameset.name, old_label, label))
        else:
            raise Exception("Unknown field {}".format(field))


        if field in refresh_fields:
            import verbnet.verbnetreader
            from syntacticframes.management.commands.loadverbnet import update_verbs
            db_vnclass = VerbNetClass.objects.get(name__exact = vn_class)
            reader = verbnet.verbnetreader.VerbnetReader(os.path.join(settings.SITE_ROOT, 'verbnet/verbnet-3.2/'), False)
            xml_vnclass = reader.files[db_vnclass.name]
            db_rootframeset = db_vnclass.verbnetframeset_set.get(parent=None)
            update_verbs(xml_vnclass, db_rootframeset,
                         db_rootframeset.ladl_string,
                         db_rootframeset.lvf_string)
                         

            
            
        return HttpResponse("ok")

def remove(request):
    if request.method == 'POST':
        post = request.POST
        model = post['model']
        when = strftime("%d/%m/%Y %H:%M:%S", gmtime())

        if model == 'VerbNetFrame':
            frame_id = int(post['frame_id'])
            vn_class = post['vn_class']
            db_frame = VerbNetFrame.objects.get(id=frame_id)
            assert db_frame.removed == False
            db_frame.removed = True
            db_frame.save()
            logger.info("{}: Marked frame {}/{} as removed in class {}"
                        .format(when, frame_id, db_frame.syntax, vn_class))
        elif model == 'VerbNetFrameSet':
            frameset_id = post['frameset_id']
            db_frameset = VerbNetFrameSet.objects.get(name=frameset_id)
            assert db_frameset.removed == False
            db_frameset.removed = True
            db_frameset.save()
            logger.info("{}: Marked frameset {}/{} as removed in class {}"
                        .format(when, frameset_id, db_frameset.name, db_frameset.verbnet_class.name))

        return HttpResponse("ok")

def add(request):

    def child_of_subclass(parent_class):
        children = VerbNetFrameSet.objects.filter(parent=parent_class)
        if not children:
            return "{}-1".format(parent_class.name)
        else:
            last_version = sorted(children, key=lambda c: LooseVersion(c.name))[-1].name
            last_number = int(last_version[-1])
            return "{}{}".format(last_version[:-1], last_number+1)

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
                syntax=post['syntax'],
                example=post['example'],
                roles_syntax=post['roles_syntax'],
                semantics=post['semantics'],
                from_verbnet=False)
            f.save()
            logger.info("{}: Added frame {} ({},{},{}) in frameset {} from class {}".format(
                when, f.syntax, f.example, f.roles_syntax, f.semantics,
                parent_frameset.name, vn_class.name))

        elif post['type'] == 'subclass':
            parent_subclass_id = post['frameset_id']
            parent_subclass = VerbNetFrameSet.objects.get(name=parent_subclass_id)
            subclass_id = child_of_subclass(parent_subclass)

            subclass = VerbNetFrameSet(
                verbnet_class=parent_subclass.verbnet_class,
                name=subclass_id,
                parent=parent_subclass)
            subclass.save()
            logger.info("{}: Added frameset {} in frameset {} from class {}".format(
                when, subclass_id, parent_subclass.name, parent_subclass.verbnet_class))
            

        return HttpResponse("ok")

def show(request):
    if request.method == 'POST':
        post = request.POST
        model = post['model']
        when = strftime("%d/%m/%Y %H:%M:%S", gmtime())

        if model == 'VerbNetFrameSet':
            frameset_id = post['frameset_id']
            db_frameset = VerbNetFrameSet.objects.get(name=frameset_id)
            assert db_frameset.removed == True
            db_frameset.removed = False
            db_frameset.save()
            logger.info("{}: Marked frameset {}/{} as shown in class {}"
                        .format(when, frameset_id, db_frameset.name, db_frameset.verbnet_class.name))
        elif model == 'VerbNetFrame':
            frame_id = post['frame_id']
            db_frame = VerbNetFrame.objects.get(id=frame_id)
            assert db_frame.removed == True
            db_frame.removed = False
            db_frame.save()

            logger.info("{}: Marked frame {} ({}/{}) as shown in class {}"
                        .format(when, frame_id, db_frame.syntax, db_frame.example,
                                db_frame.frameset.name))
            

        return HttpResponse("ok")

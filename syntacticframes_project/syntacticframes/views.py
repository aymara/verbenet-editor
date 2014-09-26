from django.http import HttpResponse, HttpResponseForbidden
from django.template import RequestContext, loader
from django.shortcuts import redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.conf import settings
from django import forms
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.db import transaction

from distutils.version import LooseVersion
import logging
from time import gmtime, strftime
import os.path

from .models import LevinClass, VerbNetClass, VerbNetMember, VerbTranslation, VerbNetFrameSet, VerbNetFrame, VerbNetRole
from parsecorrespondance.parse import UnknownClassException, SyntaxErrorException, UnknownErrorException
from loadmapping.mappedverbs import UnknownColumnException
from role.parserole import ParsedRole

logger = logging.getLogger('database')

@ensure_csrf_cookie
def classe(request, class_number):
    levin_classes = list(LevinClass.objects.all())
    levin_classes.sort(key = lambda l: LooseVersion(l.number))

    active_class = LevinClass.objects.get(number = class_number)
    verbnet_classes = VerbNetClass.objects.filter(levin_class__exact = active_class)
    verbnet_classes = verbnet_classes.prefetch_related(
        'verbnetframeset_set',
        'verbnetframeset_set__verbnetmember_set',
        'verbnetframeset_set__verbtranslation_set',
        'verbnetframeset_set__verbnetrole_set',
        'verbnetframeset_set__verbnetframe_set',
    )
    verbnet_classes = sorted(verbnet_classes, key = lambda v: LooseVersion(v.name.split('-')[1]))

    template = loader.get_template('index.html')
    context = RequestContext(request, {
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
    context = RequestContext(request, {
        'classe': verbnet_class,
    })
    context.update(csrf(request))
    return HttpResponse(template.render(context))

def index(request):
    # Hardcoding that the first class is 9
    return redirect('class/9/')

class LoginForm(forms.Form):
    login = forms.CharField(required=True)

@ensure_csrf_cookie
def login(request):
    form = LoginForm()

    if request.method == 'POST':
        user = authenticate(username=request.POST['login'], password='NO_PASSWORD')
        if user is not None:
            auth_login(request, user)
            return redirect('/')
        else:
            messages.warning(request, 'Login invalide, merci de réessayer !')
            form = LoginForm(request.POST)

    template = loader.get_template('login.html')
    context = RequestContext(request, {
        'form': form,
    })
    context.update(csrf(request))
    return HttpResponse(template.render(context))

@login_required
def update(request):
    if request.method == 'POST':
        post = request.POST
        field, label, object_type = post["field"], post["label"], post["type"]
        when = strftime("%d/%m/%Y %H:%M:%S", gmtime())

        frameset_fields = ['paragon', 'comment', 'ladl_string', 'lvf_string']
        frame_fields = ['roles_syntax', 'syntax', 'semantics', 'example']
        refresh_fields = ['ladl_string', 'lvf_string']  # Verbs need to be updated
        emptyset_fields = ['ladl_string', 'lvf_string']  # '∅' becomes ''

        if object_type == 'frame':
            vn_class_name = post['vn_class']
            frame_id = int(post["frame_id"])
            frame = VerbNetFrame.objects.get(id=frame_id)
            old_label = getattr(frame, field)
            setattr(frame, field, label)
            frame.save()
            logger.info("{}: {} updated {} in frame {} of {} from '{}' to '{}'"
                    .format(when, request.user.username, field, frame_id, vn_class_name, old_label, label))
        elif object_type == 'frameset':
            vn_class_name = post['vn_class']
            if field in emptyset_fields and label.strip() == '∅':
                label = ''
            db_frameset = VerbNetFrameSet.objects.get(id = int(post['frameset_id']))
            old_label = getattr(db_frameset, field)
            setattr(db_frameset, field, label)
            db_frameset.save()
            logger.info("{}: {} updated {} in {}/{} from '{}' to '{}'"
                    .format(when, request.user.username, field, vn_class_name, db_frameset.name, old_label, label))
        elif object_type == 'vn_class':
            vn_class_name = post['vn_class']
            vn_class = VerbNetClass.objects.get(name=vn_class_name)
            old_label = getattr(vn_class, field)
            setattr(vn_class, field, label)
            vn_class.save()
            logger.info("{}: {} updated {} in VN class {} from '{}' to '{}'"
                    .format(when, request.user.username, field, vn_class_name, old_label, label))
        elif object_type == 'levin':
            levin_class = LevinClass.objects.get(number=post['levin_number'])
            old_label = getattr(levin_class, field)
            setattr(levin_class, field, label)
            levin_class.save()
            logger.info("{}: {} updated {} in Levin class {} from '{}' to '{}'"
                    .format(when, request.user.username, field, levin_class, old_label, label))
        elif object_type == 'role':
            try:
                ParsedRole(label)  # check if role is well-formed
                role = VerbNetRole.objects.get(id=post['vn_role_id'])
                old_label = role.name
                role.name = label
                role.save()
                logger.info("{}: {} updated a role in subclass {} from '{}' to '{}'"
                        .format(when, request.user.username, post['frameset_id'], old_label, label))
            except:
                return HttpResponseForbidden('"{}" n\'est pas un rôle valide.'.format(label))
        else:
            raise Exception("Unknown object type {}".format(object_type))


        if field in refresh_fields:
            vn_class_name = post['vn_class']
            db_vnclass = VerbNetClass.objects.get(name__exact = vn_class_name)
            db_rootframeset = db_vnclass.verbnetframeset_set.get(parent=None)
            # if throws, ATOMIC_REQUESTS will revert everything
            db_rootframeset.update_translations()
                         
        return HttpResponse("ok")

@login_required
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
            logger.info("{}: {} marked frame {}/{} as removed in class {}"
                        .format(when, request.user.username, frame_id, db_frame.syntax, vn_class))
        elif model == 'VerbNetFrameSet':
            frameset_id = post['frameset_id']
            db_frameset = VerbNetFrameSet.objects.get(name=frameset_id)
            assert db_frameset.removed == False
            db_frameset.removed = True
            db_frameset.save()
            db_frameset.verbnet_class.update_members_and_translations()
            logger.info("{}: {} marked frameset {}/{} as removed in class {}"
                        .format(when, request.user.username, frameset_id, db_frameset.name, db_frameset.verbnet_class.name))
        elif model == 'VerbNetRole':
            role_id = post['role_id']
            frameset_id = post['frameset_id']
            db_role = VerbNetRole.objects.get(id=role_id)
            role_name = db_role.name
            db_role.delete()
            logger.info("{}: {} removed role {} in subclass {}"
                        .format(when, request.user.username, role_name, frameset_id))

        return HttpResponse("ok")

@login_required
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
            logger.info("{}: {} added frame {} ({},{},{},{}) in frameset {} from class {}".format(
                when, request.user.username, f.id, f.syntax, f.example, f.roles_syntax, f.semantics,
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
            logger.info("{}: {} added frameset {} in frameset {} from class {}".format(
                when, request.user.username, subclass_id, parent_subclass.name, parent_subclass.verbnet_class.name))

        elif post['type'] == 'role':
            label = post['label']
            try:
                ParsedRole(label)  # check if role is well-formed

                frameset_id = post['frameset_id']
                frameset = VerbNetFrameSet.objects.get(id=frameset_id)
                next_position = frameset.update_roles()
                VerbNetRole(
                        name=label,
                        position=next_position,
                        frameset=frameset).save()
                logger.info("{}: {} added role {} in frameset {}".format(
                    when, request.user.username, label, frameset_id))
            except:
                return HttpResponseForbidden('"{}" n\'est pas un rôle valide.'.format(label))
            

        return HttpResponse("ok")

@login_required
def validate(request):
    if request.method == 'POST':
        levin_class_id = request.POST['levin_class']
        db_levin_class = LevinClass.objects.get(number=levin_class_id)
        db_levin_class.is_translated = True
        db_levin_class.save()
        return HttpResponse('ok')

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
            db_frameset.verbnet_class.update_members_and_translations()
            logger.info("{}: {} marked frameset {}/{} as shown in class {}"
                        .format(when, request.user.username, frameset_id, db_frameset.name, db_frameset.verbnet_class.name))
        elif model == 'VerbNetFrame':
            frame_id = post['frame_id']
            db_frame = VerbNetFrame.objects.get(id=frame_id)
            assert db_frame.removed == True
            db_frame.removed = False
            db_frame.save()

            logger.info("{}: {} marked frame {} ({}/{}) as shown in class {}"
                        .format(when, request.user.username, frame_id, db_frame.syntax, db_frame.example,
                                db_frame.frameset.name))
            

        return HttpResponse("ok")


class SearchForm(forms.Form):
    search = forms.CharField(label='Recherche', max_length=100)

def search(request):
    form = SearchForm(request.GET)
    if not form.is_valid():
        return HttpResponse('')

    search = form.cleaned_data['search']

    template = loader.get_template('search.html')
    context = RequestContext(request, {
        'verbs': VerbTranslation.objects.filter(verb=search),
        'search': search
    })
    context.update(csrf(request))
    return HttpResponse(template.render(context))

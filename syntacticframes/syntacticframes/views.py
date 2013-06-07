from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import redirect

from distutils.version import StrictVersion

from .models import LevinClass

def classe(request, class_number):
    levin_classes = list(LevinClass.objects.all())
    levin_classes.sort(key = StrictVersion)


    template = loader.get_template('index.html')
    context = Context({
        'levin_classes': levin_classes,
        'active_class': class_number,
    })
    return HttpResponse(template.render(context))

def index(request):
    # Hardcoding that the first class is 9
    return redirect('class/9/')

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import template
from django.utils.html import mark_safe

register = template.Library()

from django.conf import settings
import os, re

rx = re.compile(r"^(.*)\.(.*?)$")

@register.simple_tag
def version(path):
    full_path = os.path.join(settings.STATIC_ROOT, path)
    if not settings.DEBUG:
        # Get file modification time.
        os.stat_float_times(False)
        mtime = os.path.getmtime(full_path)  # raises OSError if file does not exist
        path = rx.sub(r"\1.{}.\2".format(mtime), path)

    return os.path.join(settings.STATIC_URL, path)

@register.filter
def highlight(text, word):
    return mark_safe(text.replace(word, "<span class='highlight'>%s</span>" % word))

@register.filter
def lvf_link(lvf_class):
    base_url = 'http://rali.iro.umontreal.ca/LVF+1/classe'
    if len(lvf_class) in [1, 2]:
        return '{}/index.html#{}'.format(base_url, lvf_class)
    elif len(lvf_class) == 3:
        return '{}/{}.html'.format(base_url, lvf_class)
    elif len(lvf_class) == 5:
        return '{}/{}.html#{}_{}'.format(base_url, lvf_class[0:3], lvf_class[0:3], lvf_class[4])

@register.filter
def paragon(vn_class):
    return vn_class.split('-')[0]

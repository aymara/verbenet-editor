#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.filter
def is_removed(value, arg):
    return value.filter(removed=arg)

@register.filter
def sort_translations(value):
    return sorted(list(value))

from django.conf import settings
import os, re

rx = re.compile(r"^(.*)\.(.*?)$")

@register.simple_tag
def version(path):
    full_path = os.path.join(settings.STATIC_ROOT, path)
    if not settings.DEBUG:
        try:
            # Get file modification time.
            os.stat_float_times(False)
            mtime = os.path.getmtime(full_path)
            path = rx.sub(r"\1.%d.\2" % mtime, path)
        except OSError:
            # Returns normal url if this file was not found in filesystem.
            path = '%s%s' % (settings.STATIC_URL, path)
    # Cheats, but adding "static" is just what the static tag does anyway...
    return os.path.join('/static', path)

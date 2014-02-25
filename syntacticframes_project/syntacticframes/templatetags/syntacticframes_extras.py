#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import template

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
        path = rx.sub(r"\1.%d.\2" % mtime, path)

    return os.path.join(settings.STATIC_URL, path)

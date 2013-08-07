#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.filter
def is_removed(value, arg):
    return value.filter(removed=arg)

    

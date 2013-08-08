#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.filter
def is_removed(value, arg):
    return value.filter(removed=arg)

@register.filter
def sort_translations(value):
    return value.order_by('category', 'verb')    

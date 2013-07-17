#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from syntacticframes.models import VerbNetClass, VerbTranslation

class Command(BaseCommand):
    def handle(self, *args, **options):
        all_verbs = set()
        num_classes, num_verbs = 0, 0
        for vn_class in VerbNetClass.objects.all():
            num_classes += 1
            for t in VerbTranslation.objects.filter(verbnet_class__exact = vn_class,
                                                    category = 'both'):
               num_verbs += 1
               all_verbs.add(t.verb) 

        print("{} classes, {} verbs/class".format(num_classes, num_verbs / num_classes))

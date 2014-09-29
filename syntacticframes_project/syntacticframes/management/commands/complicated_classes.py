#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from operator import itemgetter

from django.core.management.base import BaseCommand

from syntacticframes.models import LevinClass


class Command(BaseCommand):
    def handle(self, *args, **options):
        numbers = []
        for lc in LevinClass.objects.all():
            local_number = 0
            for vn in lc.verbnetclass_set.all():
                for fs in vn.verbnetframeset_set.all():
                    local_number += len(fs.verbnetframe_set.all())
                
            numbers.append(("{}: {}".format(lc.number, lc.name), local_number))

        numbers.sort(key=itemgetter(1), reverse=True)
        for name, number in numbers:
            print(name, number)

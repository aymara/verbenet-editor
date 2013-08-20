#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from syntacticframes.models import VerbNetClass


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.commit_on_success():
            for vn_class in VerbNetClass.objects.all():
                if '-' in vn_class.ladl_string and vn_class.ladl_string.strip() != '-':
                    print("{}: {} -> {}".format(
                        vn_class.name,
                        vn_class.ladl_string,
                        vn_class.ladl_string.replace('-', '')))
                    vn_class.ladl_string = vn_class.ladl_string.replace('-', '')
                    vn_class.save()

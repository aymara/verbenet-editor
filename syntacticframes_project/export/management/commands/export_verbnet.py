#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from export.export import export_all_vn_classes

class Command(BaseCommand):
    def handle(self, *args, **options):
        export_all_vn_classes()

#!/usr/bin/env python3

import csv
from os.path import join, basename
from glob import glob
import re

from jinja2 import Environment, FileSystemLoader

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.html import strip_spaces_between_tags as minify_html

def formules_definitoires():
    with open(join(settings.SITE_ROOT, 'resources/tables-3.4/tdt-verbes/formules-definitoires.csv')) as tdtf:
        tdt = csv.reader(tdtf, delimiter=';', quotechar='"')
        next(tdt)

        formules = {}
        for table in tdt:
            if not table[5]:
                continue

            table_name = table[5]
            construction = table[0][1:-1]
            conjonction = table[1]
            formules[table_name] = {'construction': construction, 'conjonction': conjonction}

        return formules

class Command(BaseCommand):
    def handle(self, *args, **options):
        env = Environment(loader=FileSystemLoader(join(settings.SITE_ROOT, 'templates/')), autoescape=True, trim_blocks=True)
        template = env.get_template('table.html')

        formules = formules_definitoires()

        for f in (glob(join(settings.SITE_ROOT, 'resources/tables-3.4/verbes/*.csv')) +
                glob(join(settings.SITE_ROOT, 'resources/tables-3.4/figees/*.csv'))):

            classe = re.search('([^.]+).lgt.csv', basename(f)).group(1)
            stripped_class = classe[2:] if classe.startswith('V_') else classe

            with open(f) as csvf, open(join(settings.SITE_ROOT, 'assets/verbes-html/{}.lgt.html'.format(classe)), 'w') as html:
                ladlreader = csv.reader(csvf, delimiter=';', quotechar='"')

                context = {
                    'classe': stripped_class,
                    'formule': formules.get(stripped_class),
                    'header': next(ladlreader),
                    'verb_lines': ladlreader,
                    'toalign': ['+', '~', '-', '?', '<E>']
                }

                html.write(minify_html(template.render(context)))

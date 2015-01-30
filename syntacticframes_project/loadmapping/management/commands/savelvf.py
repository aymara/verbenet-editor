import csv
import re
from os.path import join

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from loadmapping.models import LVFVerb

"""
Save LVF+1 hierarchy by parsing the CSV version

LVFVerb is the LVFVerb model at a given point in time, and not directly
imported from loadmapping.models
"""

def normalize_verb(verb):
    """Return the verb in a normalized form for HTML display"""

    # word number? (se)?
    match = re.match('(\w+)\s?(\d+)?\s?(\(([^\)]+)\))?', verb)

    if not match:
        return 'error: {}'.format(verb)
    else:
        verb, number, outer_se, se = match.groups()
        normalized = verb
        if se:
            normalized += ' {}'.format(se)

        if number:
            number = int(number, base=10)
        else:
            number = 0

        return {'verb': normalized, 'number': number}


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            with open(join(settings.SITE_ROOT, 'resources/LVF+1/LVF+1.csv')) as lvfp1:
                lvfp1reader = csv.reader(lvfp1, delimiter=',', quotechar='"')
                next(lvfp1reader)
                for i, row in enumerate(lvfp1reader):
                    lvf_class = row[7]
                    normalized_verb = normalize_verb(row[1])
                    LVFVerb(
                        lemma=normalized_verb['verb'],
                        sense=normalized_verb['number'],
                        lvf_class = lvf_class,
                        construction = row[11]).save()

                    print("\rLVF import: {:.0%}".format(i/25610), end="", flush=True)
                print()

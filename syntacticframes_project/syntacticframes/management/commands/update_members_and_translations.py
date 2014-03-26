"""
Updates members and translations for all classes

When LVF and LADL mappings change, everything under this change could change.
When a frameset is hidden or shown, everything in that class could change.
When the algorithm changes, everything in VerbeNet could change.

This command ensures that after an algorithmic change, everything is
consistent.
"""

import logging
from time import gmtime, strftime

from django.core.management.base import BaseCommand

from syntacticframes.models import VerbNetClass

class Command(BaseCommand):
    def handle(self, *args, **options):

        verb_logger = logging.getLogger('verbs')
        when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
        verb_logger.info("{}: Start full update of verbs (members and translations)".format(when))

        for vn_class in VerbNetClass.objects.all():
            print(vn_class.name)
            vn_class.update_members_and_translations()

        when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
        verb_logger.info("{}: Ended full update of verbs (members and translations)".format(when))

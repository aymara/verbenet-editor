"""
Updates members and translations for all classes

When LVF and LADL mappings change, everything under this change could change.
When a frameset is hidden or shown, everything in that class could change.
When the algorithm changes, everything in VerbeNet could change.

This command ensures that after an algorithmic change, everything is
consistent.
"""

import sys
import traceback
import logging
from time import gmtime, strftime

from django.core.management.base import BaseCommand
from django.db import transaction

from syntacticframes.models import VerbNetClass, VerbTranslation, VerbNetMember

class Command(BaseCommand):
    def handle(self, *args, **options):

        verb_logger = logging.getLogger('verbs')
        when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
        verb_logger.info("{}: Start full update of verbs (members and translations)".format(when))

        try:
            with transaction.atomic():
                for vn_class in VerbNetClass.objects.all():
                    when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
                    verb_logger.info('{}: {}'.format(when, vn_class.name))

                    # Remove duplicates (O(n²) !)
                    for frameset in vn_class.verbnetframeset_set.all():
                        for verb in frameset.verbtranslation_set.all():
                            other_verbs = VerbTranslation.objects.filter(frameset=frameset,verb=verb.verb)
                            if len(other_verbs) > 1:
                                remove_first = sorted(other_verbs, key=lambda v: (v.validation_status, v.category_id))
                                for verb in remove_first[1:]:
                                    verb.delete()
                                    when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
                                    verb_logger.info("{}: Removed duplicate {} in {}".format(when, verb, frameset.name))

                    # Remove members that were not moved but copied to parent frameset when actual frameset got hidden
                    for frameset in vn_class.verbnetframeset_set.all():

                        all_child_members = set()
                        for child_frameset in frameset.children.all():
                            all_child_members |= child_frameset.get_all_verbs(VerbNetMember)

                        for member in frameset.verbnetmember_set.filter(inherited_from__isnull=False):
                            possible_duplicated_list = [m for m in all_child_members if m.lemma == member.lemma]
                            assert len(possible_duplicated_list) <= 1

                            if len(possible_duplicated_list) == 1:

                                possible_duplicated_list[0].delete()
                                when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
                                verb_logger.info("{}: Removed member {} which was already present as {}".format(when, repr(possible_duplicated_list[0]), repr(member)))

                    # Update everything
                    vn_class.update_members_and_translations()
        except:
            when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
            exc_type, exc_value, exc_traceback = sys.exc_info()
            verb_logger.info(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            verb_logger.info("{}: Exception, everything was backed out.".format(when))
        else:
            when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
            verb_logger.info("{}: Ended full update of verbs (members and translations)".format(when))
        verb_logger.info('')

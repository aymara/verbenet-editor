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
        verb_logger.info("{}: Started Vant update.".format(when))

        try:
            with transaction.atomic():
                for vn_class in VerbNetClass.objects.all():
                    for frameset in vn_class.verbnetframeset_set.all():
                        for frame in frameset.verbnetframe_set.all():
                            if 'Vant' in frame.roles_syntax or 'Vant' in frame.syntax:
                                frame.roles_syntax = frame.roles_syntax.replace('Vant', 'V-ant')
                                frame.syntax = frame.syntax.replace('Vant', 'V-ant')
                                frame.save()
                                when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
                                verb_logger.info("{}: {}, {}: {}".format(when, vn_class.name, frameset.name, frame))
        except:
            when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
            exc_type, exc_value, exc_traceback = sys.exc_info()
            verb_logger.info(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
            verb_logger.info("{}: Exception, everything was backed out.".format(when))
        else:
            when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
            verb_logger.info("{}: Ended Vant update.".format(when))
        verb_logger.info('')

import logging
from time import gmtime, strftime

from django.core.management.base import BaseCommand

from parsecorrespondance import parse
from syntacticframes.models import VerbNetClass


verb_logger = logging.getLogger('verbs')


def update_all_verbs():
    "Updates all verb translations is something went wrong below."
    when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
    verb_logger.info("{}: Start full update of verb translations".format(when))
    for db_vnclass in VerbNetClass.objects.all():
        print(db_vnclass.name)
        db_rootframeset = db_vnclass.verbnetframeset_set.get(parent=None)
        try:
            db_rootframeset.update_translations()
        except parse.UnknownClassException as e:
            print("Ignoring {}".format(e))
    when = strftime("%d/%m/%Y %H:%M:%S", gmtime())
    verb_logger.info("{}: Ended full update of verb translations".format(when))


class Command(BaseCommand):
    def handle(self, *args, **options):
        update_all_verbs()

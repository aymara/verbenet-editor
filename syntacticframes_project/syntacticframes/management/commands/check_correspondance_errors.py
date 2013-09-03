from django.core.management.base import BaseCommand

from syntacticframes.models import VerbNetFrameSet
from parsecorrespondance import parse
from loadmapping import mapping

class Command(BaseCommand):
    def handle(self, *args, **options):
        for frameset in VerbNetFrameSet.objects.all():
            print("{}: {}/{}".format(frameset.name, frameset.ladl_string, frameset.lvf_string))

            if frameset.ladl_string:
                try:
                    parse.FrenchMapping('LADL', frameset.ladl_string).result()
                except parse.UnknownClassException as e:
                    print('{:<30} {}'.format(frameset.name, e))

            if frameset.lvf_string:
                try:
                    parse.FrenchMapping('LVF', frameset.lvf_string)
                except parse.UnknownClassException as e:
                    print('{:<30} {}'.format(frameset.name, e))

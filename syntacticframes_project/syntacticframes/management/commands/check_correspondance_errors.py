from django.core.management.base import BaseCommand

from syntacticframes.models import VerbNetClass
from parsecorrespondance import parse
from loadmapping import mapping

class Command(BaseCommand):
    def handle(self, *args, **options):
        for vn_class in VerbNetClass.objects.all():
            try:
                parse.get_ladl_list(vn_class.ladl_string)
            except parse.UnknownClassException as e:
                print('{:<30} {}'.format(vn_class.name, e))

            try:
                parse.get_lvf_list(vn_class.lvf_string)
            except parse.UnknownClassException as e:
                print('{:<30} {}'.format(vn_class.name, e))

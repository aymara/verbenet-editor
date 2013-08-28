from django.core.management.base import BaseCommand

from syntacticframes.models import VerbNetClass
from parsecorrespondance import parse
from loadmapping import mapping

class Command(BaseCommand):
    def handle(self, *args, **options):
        for vn_class in VerbNetClass.objects.all():
            try:
                old = mapping.parse_complex_lvfladl(vn_class.ladl_string)
                new = parse.get_ladl_list(vn_class.ladl_string)
                if old != new:
                    print("Difference for {} in {}! {} <-> {}".format(vn_class.ladl_string, vn_class.name, old, new))
            except parse.UnknownClassException as e:
                print('{:<30} {}'.format(vn_class.name, e))

            try:
                old = mapping.parse_complex_lvfladl(vn_class.lvf_string)
                new = parse.get_lvf_list(vn_class.lvf_string)
                if old != new:
                    print("Difference for {} in {}! {} <-> {}".format(vn_class.lvf_string, vn_class.name, old, new))
            except parse.UnknownClassException as e:
                print('{:<30} {}'.format(vn_class.name, e))

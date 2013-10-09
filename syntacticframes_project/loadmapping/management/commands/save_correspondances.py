import csv
from os import path
from distutils.version import LooseVersion


from django.core.management.base import BaseCommand
from django.conf import settings

from syntacticframes.models import VerbNetClass

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(path.join(settings.SITE_ROOT, 'loadmapping/resources/Correspondances.csv'), 'w') as csvfile:
            correswriter = csv.writer(csvfile)
            correswriter.writerow(['VerbNet', 'LVF', 'LADL', 'Parangon', 'Commentaires'])

            for vn_class in sorted(VerbNetClass.objects.all(), key = lambda v: LooseVersion(v.name.split('-')[1])):
                root_fs = vn_class.verbnetframeset_set.get(parent=None)
                correswriter.writerow(["{}: {}".format(vn_class.name.split('-')[1], vn_class.name),
                                       root_fs.lvf_string, root_fs.ladl_string,
                                       root_fs.paragon, root_fs.comment])

            

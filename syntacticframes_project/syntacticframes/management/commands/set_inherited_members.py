"""Sets inherited members for all framesets"""


from django.core.management.base import BaseCommand

from syntacticframes.models import VerbNetClass

class Command(BaseCommand):
    def handle(self, *args, **options):
        for vn_class in VerbNetClass.objects.all():
            vn_class.set_inherited_members()


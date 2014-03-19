"""
Updates members and translations for all classes

When LVF and LADL mappings change, everything under this change could change.
When a frameset is hidden or shown, everything in that class could change.
When the algorithm changes, everything in VerbeNet could change.

This command ensures that after an algorithmic change, everything is
consistent.
"""


from django.core.management.base import BaseCommand

from syntacticframes.models import VerbNetClass

class Command(BaseCommand):
    def handle(self, *args, **options):
        for vn_class in VerbNetClass.objects.all():
            print(vn_class.name)
            vn_class.update_members_and_translations()


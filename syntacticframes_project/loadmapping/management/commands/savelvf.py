from django.core.management.base import BaseCommand
from django.db import transaction

from loadmapping import savelvf

class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.commit_on_success():
            savelvf.savelvf()

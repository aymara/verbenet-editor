#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from syntacticframes.models import VerbNetClass, VerbTranslation

class Command(BaseCommand):
    def handle(self, *args, **options):
        all_verbs, all_members = set(), set()
        num_classes, num_verbs, num_members = 0, 0, 0
        for vn_class in VerbNetClass.objects.all():
            num_classes += 1
            for vn_fs in vn_class.verbnetframeset_set.all():
                for t in VerbTranslation.objects.filter(frameset=vn_fs,
                                                        category = 'both'):
                   all_verbs.add(t.verb) 
                   num_verbs += 1
                for m in vn_fs.verbnetmember_set.all():
                    all_members.add(m.lemma)
                    num_members += 1

        print("{} verbs ({} unique)".format(num_verbs, len(all_verbs)))
        print("{} members ({} unique)".format(num_members, len(all_members)))
        print("{} classes, {} verbs/class, {} members/class".format(num_classes, num_verbs / num_classes, num_members/num_classes))

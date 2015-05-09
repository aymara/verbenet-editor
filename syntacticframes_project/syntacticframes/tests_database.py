from django.test import TestCase

from syntacticframes.models import (LevinClass, VerbNetClass, VerbNetFrameSet,
                                    VerbNetMember, VerbTranslation)


class TestHideAndMove(TestCase):
    def setUp(self):
        """Adds a class and a subclass that will get hidden: we'll see how
        things are moved around."""

        # VerbNet class with its parent Levin class
        levin_class = LevinClass(number=4, name='Imaginary class')
        levin_class.save()
        verbnet_class = VerbNetClass(levin_class=levin_class, name='imagine-4', position=1)
        verbnet_class.save()

        # A frameset and its child with verbs in both
        self.root_frameset = VerbNetFrameSet(verbnet_class=verbnet_class,
                                             name='4')
        self.root_frameset.save()
        self.child_frameset = VerbNetFrameSet(verbnet_class=verbnet_class,
                                              parent=self.root_frameset,
                                              name='4.1')
        self.child_frameset.save()

        VerbNetMember(frameset=self.root_frameset, lemma='member_root-1').save()
        VerbNetMember(frameset=self.root_frameset, lemma='member_root-2').save()
        VerbNetMember(frameset=self.child_frameset, lemma='member_child-1').save()
        VerbNetMember(frameset=self.child_frameset, lemma='member_child-2').save()
        VerbTranslation(frameset=self.child_frameset, verb='translation_child-1',
                        category_id=4, category='unknown',
                        validation_status=VerbTranslation.STATUS_VALID).save()
        VerbTranslation(frameset=self.child_frameset, verb='translation_child-2',
                        category_id=4, category='unknown',
                        validation_status=VerbTranslation.STATUS_INFERRED).save()

        # Another target frameset with a child in a new VerbNet class where we'll send verbs from
        # the other child_frameset before hiding the target frameset child
        second_verbnet_class = VerbNetClass(levin_class=levin_class, name='boring-5', position=1)
        second_verbnet_class.save()
        self.target_frameset = VerbNetFrameSet(verbnet_class=second_verbnet_class,
                                               name='5')
        self.target_frameset.save()
        self.target_frameset_child = VerbNetFrameSet(verbnet_class=second_verbnet_class,
                                                     parent=self.target_frameset,
                                                     name='5.1')
        self.target_frameset_child.save()
        VerbNetMember(frameset=self.target_frameset, lemma='member_target-1').save()
        VerbNetMember(frameset=self.target_frameset_child, lemma='member_target_child-1').save()

    def test_members_are_moved_up_on_child_hide(self):
        root_members = self.root_frameset.verbnetmember_set.all()
        root_lemmas = {m.lemma for m in root_members}
        self.assertEqual({'member_root-1', 'member_root-2'}, root_lemmas)
        self.assertTrue(all({m.inherited_from is None for m in root_members}))
        self.assertEqual(self.child_frameset.verbtranslation_set.filter(
            validation_status=VerbTranslation.STATUS_VALID).count(), 1)
        self.assertEqual(self.child_frameset.verbtranslation_set.filter(
            validation_status=VerbTranslation.STATUS_INFERRED).count(), 1)

        # Hide child frameset
        self.child_frameset.mark_as_removed()

        root_members = self.root_frameset.verbnetmember_set.all()
        root_lemmas = {m.lemma for m in root_members}
        self.assertEqual(root_lemmas, {
            'member_root-1', 'member_root-2', 'member_child-1', 'member_child-2'})
        self.assertTrue(all({m.inherited_from.name == '4.1'
                             for m in root_members if 'child' in m.lemma}))
        self.assertEqual(self.child_frameset.verbtranslation_set.filter(
            validation_status=VerbTranslation.STATUS_VALID).count(), 0)
        # TODO delete translations when removed=True in update_translations
        self.assertEqual(self.child_frameset.verbtranslation_set.filter(
            validation_status=VerbTranslation.STATUS_INFERRED).count(), 1)

        self.assertEqual(self.child_frameset.verbnetmember_set.count(),  0)

        # Get back to original state
        self.child_frameset.mark_as_shown()

        root_members = self.root_frameset.verbnetmember_set.all()
        root_lemmas = {m.lemma for m in root_members}
        self.assertEqual({'member_root-1', 'member_root-2'}, root_lemmas)
        self.assertTrue(all({m.inherited_from is None for m in root_members}))

        child_members = self.child_frameset.verbnetmember_set.all()
        child_lemmas = {m.lemma for m in child_members}
        self.assertEqual({'member_child-1', 'member_child-2'}, child_lemmas)
        self.assertTrue(all({m.inherited_from is None for m in child_members}))
        self.assertEqual(self.child_frameset.verbtranslation_set.filter(
            validation_status=VerbTranslation.STATUS_VALID).count(), 1)
        self.assertEqual(self.child_frameset.verbtranslation_set.filter(
            validation_status=VerbTranslation.STATUS_INFERRED).count(), 0)

    def test_move_members_and_verbs_then_hide(self):
        target_child_members = self.target_frameset_child.verbnetmember_set.all()
        target_child_lemmas = {m.lemma for m in target_child_members}
        self.assertEqual(target_child_lemmas, {'member_target_child-1'})
        self.assertTrue(all({m.received_from == None for m in target_child_members}))

        # Move members and verbs
        self.child_frameset.move_members_and_verbs_to(self.target_frameset_child)

        target_child_members = self.target_frameset_child.verbnetmember_set.all()
        target_child_lemmas = {m.lemma for m in target_child_members}
        self.assertEqual(target_child_lemmas, {'member_target_child-1', 'member_child-1', 'member_child-2'})
        self.assertTrue(all({m.received_from.name == '4.1' for m in target_child_members if 'member_child' in m.lemma}))

        # Next, hide the child frameset: the moved members and verbs should go
        # up.
        self.target_frameset_child.mark_as_removed()

        target_child_members = self.target_frameset_child.verbnetmember_set.all()
        target_members = self.target_frameset.verbnetmember_set.all()
        target_lemmas = {m.lemma for m in target_members}
        target_child_lemmas = {m.lemma for m in target_child_members}
        self.assertEqual(target_child_lemmas, set())
        self.assertEqual(target_lemmas, {'member_target-1', 'member_target_child-1', 'member_child-1', 'member_child-2'})

        self.target_frameset_child.mark_as_shown()
        target_child_members = self.target_frameset_child.verbnetmember_set.all()
        target_members = self.target_frameset.verbnetmember_set.all()
        target_lemmas = {m.lemma for m in target_members}
        target_child_lemmas = {m.lemma for m in target_child_members}
        self.assertEqual(target_child_lemmas, {'member_target_child-1', 'member_child-1', 'member_child-2'})
        self.assertTrue(all({m.received_from.name == '4.1' for m in target_child_members if 'member_child' in m.lemma}))

    def tearDown(self):
        # Tear down does not appear to be useful: no objects stay anyway
        pass


class TestUpdateTranslations(TestCase):
    def setUp(self):
        """
        Tests syntacticframes.models.VerbNetFrameSet.update_translations.

        Add three framesets with one English member each: we want everyone of
        those verbs to have at least one French translation in common. We will
        then see, depending on the LVF/LADL mappings, what will be the
        different colors of the French translation.
        """
        # VerbNet class with its parent Levin class
        levin_class = LevinClass(number=3, name='Another imaginary class')
        levin_class.save()
        self.verbnet_class = VerbNetClass(levin_class=levin_class, name='another-3', position=1)
        self.verbnet_class.save()

        # A frameset and its child with verbs in both
        self.root_frameset = VerbNetFrameSet(verbnet_class=self.verbnet_class,
                                             name='3',lvf_string='L1a')
        self.root_frameset.save()
        self.child_frameset = VerbNetFrameSet(verbnet_class=self.verbnet_class,
                                              parent=self.root_frameset,
                                              name='3.1')
        self.child_frameset.save()
        self.grandchild1_frameset = VerbNetFrameSet(verbnet_class=self.verbnet_class,
                                                   parent=self.child_frameset,
                                                   name='3.1.1')
        self.grandchild1_frameset.save()
        self.grandchild2_frameset = VerbNetFrameSet(verbnet_class=self.verbnet_class,
                                                   parent=self.child_frameset,
                                                   name='3.1.2')
        self.grandchild2_frameset.save()

        VerbNetMember(frameset=self.root_frameset, lemma='live').save()
        VerbNetMember(frameset=self.child_frameset, lemma='stay').save()
        VerbNetMember(frameset=self.grandchild1_frameset, lemma='stop').save()
        VerbNetMember(frameset=self.grandchild2_frameset, lemma='remain').save()

        self.verbnet_class.update_members_and_translations()

    def test_translations_goes_down_in_hierarchy(self):
        # Test that rester (a translation of settle, stay and stop) is only in
        # the most specific class (grand child)
        self.assertRaises(
            VerbTranslation.DoesNotExist,
            self.root_frameset.verbtranslation_set.get, verb='rester')
        self.assertRaises(
            VerbTranslation.DoesNotExist,
            self.child_frameset.verbtranslation_set.get, verb='rester')
        rester_grandchild1 = self.grandchild1_frameset.verbtranslation_set.get(verb='rester')
        self.assertEqual(rester_grandchild1.verb, 'rester')
        self.assertEqual(rester_grandchild1.category, 'lvf')

    def test_manually_validated_translations(self):
        # Validate 'rester'
        manual_verb = self.grandchild1_frameset.verbtranslation_set.get(verb='rester')
        manual_verb.validation_status = VerbTranslation.STATUS_VALID
        manual_verb.save()

        # Change mapping: rester should go up but won't since it has been
        # validated.
        self.grandchild1_frameset.lvf_string = 'L1b'  # does not contain 'rester'
        self.grandchild1_frameset.save()
        self.verbnet_class.update_members_and_translations()

        manual_verb = self.grandchild1_frameset.verbtranslation_set.get(verb='rester')
        self.assertEqual(manual_verb.frameset, self.grandchild1_frameset)
        self.assertEqual(manual_verb.validation_status, VerbTranslation.STATUS_VALID)
        self.assertEqual(manual_verb.category, 'dicovalence')

        self.assertRaises(
            VerbTranslation.DoesNotExist,
            self.root_frameset.verbtranslation_set.get, verb='rester')
        self.assertRaises(
            VerbTranslation.DoesNotExist,
            self.child_frameset.verbtranslation_set.get, verb='rester')
        self.assertEqual(self.grandchild1_frameset.verbtranslation_set.get(verb='rester').verb, 'rester')

    def test_colored_translations_go_higher_in_hierarchy(self):
        """
        Tests that colored translations go higher in hierarchy.

        By design, VerbNet verbs only appear in the most specific subclasses
        they can belong in. Often, paragons accept more frames. Since
        subclasses *add* frames, those paragons are often deep in the
        hierarchy.

        The same thing should happen for translations, and this is what
        update_translation does: it only adds verbs that wouldn't go in
        subclasses. However, there's one caveat. Verb translations can have
        many statuses: purple, red, green, black and gray. So when we choose
        the lowest possible position, we risk choosing a black or gray verb
        which will be hidden, while a colored verbs could have been added to
        our translation!

        So, if a translation is black or gray in a subclass and purple or red
        or green in a higher class, this translation should go in the higher
        class. This is what we're testing here.

        Other notes:
          * When we have to decide between purple and red/green however, we
          still want to choose the lower class: this will be less surprising
          and the verb will be visible anyway
          * While this is an issue that was considered some time ago, we never
          expected it to change a lot of things: maybe a position change or
          two. Moreover, the French verb validation has advanced a lot, and we
          are more conservative about moving validated verbs. Still, we're
          doing this to ensure our update translation code is principled.
        """

        self.grandchild1_frameset.lvf_string = 'L1b'  # does not contain 'rester'
        self.grandchild1_frameset.save()
        self.grandchild2_frameset.lvf_string = 'L1b'  # does not contain 'rester'
        self.grandchild2_frameset.save()
        self.verbnet_class.update_members_and_translations()

        # Test that the two translations of rester (a translation of settle,
        # stay, stop and remain) are only in the most specific class (child, no
        # longer the two grand children)
        for rester_child in self.child_frameset.verbtranslation_set.filter(verb='rester'):
            self.assertEqual(rester_child.verb, 'rester')
            self.assertEqual(rester_child.category, 'lvf')

        self.assertRaises(
            VerbTranslation.DoesNotExist,
            self.root_frameset.verbtranslation_set.get, verb='rester')
        self.assertRaises(
            VerbTranslation.DoesNotExist,
            self.grandchild1_frameset.verbtranslation_set.get, verb='rester')

        # Go back to normal
        self.grandchild1_frameset.lvf_string = ''
        self.grandchild1_frameset.save()
        self.grandchild2_frameset.lvf_string = ''
        self.grandchild2_frameset.save()
        self.verbnet_class.update_members_and_translations()

        rester_grandchild1 = self.grandchild1_frameset.verbtranslation_set.get(verb='rester')
        self.assertEqual(rester_grandchild1.verb, 'rester')
        self.assertEqual(rester_grandchild1.category, 'lvf')
        rester_grandchild2 = self.grandchild2_frameset.verbtranslation_set.get(verb='rester')
        self.assertEqual(rester_grandchild2.verb, 'rester')
        self.assertEqual(rester_grandchild2.category, 'lvf')

        self.assertRaises(
            VerbTranslation.DoesNotExist,
            self.root_frameset.verbtranslation_set.get, verb='rester')
        self.assertRaises(
            VerbTranslation.DoesNotExist,
            self.child_frameset.verbtranslation_set.get, verb='rester')

    def tearDown(self):
        # Nothing to do, the entries get removed from the database
        pass


class TestAllValid(TestCase):
    def setUp(self):
        levin_class = LevinClass(number=4, name='Imaginary class')
        levin_class.save()
        verbnet_class = VerbNetClass(levin_class=levin_class, name='imagine-4', position=1)
        verbnet_class.save()
        self.frameset = VerbNetFrameSet(verbnet_class=verbnet_class, name='4')
        self.frameset.save()

    def test_purple(self):
        VerbTranslation(frameset=self.frameset, verb='translation_child-1',
                        category_id=0, category='both',
                        validation_status=VerbTranslation.STATUS_VALID).save()
        VerbTranslation(frameset=self.frameset, verb='translation_child-2',
                        category_id=0, category='both',
                        validation_status=VerbTranslation.STATUS_INFERRED).save()

        # When validated verbs exist, the inferred one are not consider valid
        self.assertEqual(len(VerbTranslation.all_valid(self.frameset.verbtranslation_set.all())), 1)

    def test_red(self):
        VerbTranslation(frameset=self.frameset, verb='translation_child-1',
                        category_id=1, category='ladl',
                        validation_status=VerbTranslation.STATUS_VALID).save()
        VerbTranslation(frameset=self.frameset, verb='translation_child-2',
                        category_id=1, category='ladl',
                        validation_status=VerbTranslation.STATUS_INFERRED).save()

        # When validated verbs exist, the inferred one are not consider valid
        self.assertEqual(len(VerbTranslation.all_valid(self.frameset.verbtranslation_set.all())), 1)

    def test_black(self):
        VerbTranslation(frameset=self.frameset, verb='translation_child-1',
                        category_id=3, category='dicovalence',
                        validation_status=VerbTranslation.STATUS_VALID).save()
        VerbTranslation(frameset=self.frameset, verb='translation_child-2',
                        category_id=3, category='dicovalence',
                        validation_status=VerbTranslation.STATUS_INFERRED).save()
        self.assertEqual(len(VerbTranslation.all_valid(self.frameset.verbtranslation_set.all())), 1)

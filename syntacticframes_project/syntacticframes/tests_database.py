from django.test import TestCase

from syntacticframes.models import (LevinClass, VerbNetClass, VerbNetFrameSet,
                                    VerbNetMember, VerbTranslation)


class TestUpdateTranslations(TestCase):
    def setUp(self):
        """Adds a class and a subclass that will get hidden: we'll see how
        things are moved around."""

        # VerbNet class with its parent Levin class
        levin_class = LevinClass(number=4, name='Imaginary class')
        levin_class.save()
        verbnet_class = VerbNetClass(levin_class=levin_class, name='imagine-4')
        verbnet_class.save()

        # A frameset and its child with verbs in both
        self.root_frameset = VerbNetFrameSet(verbnet_class=verbnet_class,
                                             name='4', tree_id=1)
        self.child_frameset = VerbNetFrameSet(verbnet_class=verbnet_class,
                                              parent=self.root_frameset,
                                              name='4.1', tree_id=1)
        self.root_frameset.save()
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
        second_verbnet_class = VerbNetClass(levin_class=levin_class, name='boring-5')
        second_verbnet_class.save()
        self.target_frameset = VerbNetFrameSet(verbnet_class=second_verbnet_class,
                                               name='5', tree_id=1)
        self.target_frameset_child = VerbNetFrameSet(verbnet_class=second_verbnet_class,
                                                     parent=self.target_frameset,
                                                     name='5.1', tree_id=1)
        self.target_frameset.save()
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

class TestAllValid(TestCase):
    def setUp(self):
        levin_class = LevinClass(number=4, name='Imaginary class')
        levin_class.save()
        verbnet_class = VerbNetClass(levin_class=levin_class, name='imagine-4')
        verbnet_class.save()
        self.frameset = VerbNetFrameSet(verbnet_class=verbnet_class, name='4', tree_id=1)
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

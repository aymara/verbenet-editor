from django.test import SimpleTestCase

from loadmapping import mappedverbs 
from parsecorrespondance import parse

class TestMappedVerbsFunctions(SimpleTestCase):
    def test_verbs_for_one_class(self):
        self.assertIn('mettre', mappedverbs.verbs_for_one_class('38LD', 'LADL'))
        self.assertIn('mettre', mappedverbs.verbs_for_one_class('L3b', 'LVF'))

    def test_verbs_for_class_mapping(self):
        verbs = mappedverbs.verbs_for_class_mapping(parse.FrenchMapping(
            'LADL', '32A et (37M1 ou 37M2 ou 37M3 ou 37M4 ou 37M5 ou 37M6)'))
        self.assertIn('sculpter', verbs)
        self.assertIn('mouler', verbs)

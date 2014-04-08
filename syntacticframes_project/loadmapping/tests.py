from django.test import SimpleTestCase

from loadmapping import mappedverbs 
from parsecorrespondance import parse

class TestMappedVerbsFunctions(SimpleTestCase):
    def test_verbs_for_one_class(self):
        self.assertIn('mettre', mappedverbs.verbs_for_one_class('LADL', ('38LD', None)))
        self.assertIn('mettre', mappedverbs.verbs_for_one_class('LVF', ('L3b', None)))

    def test_verbs_for_class_mapping(self):
        verbs = mappedverbs.verbs_for_class_mapping(parse.FrenchMapping(
            'LADL', '32A et (37M1 ou 37M2 ou 37M3 ou 37M4 ou 37M5 ou 37M6)'))
        self.assertIn('sculpter', verbs)
        self.assertIn('mouler', verbs)

    def test_columns(self):
        verbs = mappedverbs.verbs_for_class_mapping(
            parse.FrenchMapping('LADL', '32C[+N1 =: Nabs métaphore]'))
        self.assertIn('abîmer', verbs)
        self.assertNotIn('accidenter', verbs)

    def test_two_mixed_columns(self):
        verbs = mappedverbs.verbs_for_class_mapping(
            parse.FrenchMapping('LADL', '32C[+N1 =: Nabs métaphore et +N0 être V-n]'))
        self.assertNotIn('abîmer', verbs)
        self.assertIn('ankyloser', verbs)

    def test_three_mixed_columns(self):
        verbs = mappedverbs.verbs_for_class_mapping(
            parse.FrenchMapping('LADL', '32C[+N1 =: Nabs métaphore et +N0 être V-n et +N1 être Vpp W]'))
        self.assertNotIn('inspecter', verbs)
        self.assertIn('ankyloser', verbs)

    def test_ored_columns(self):
        verbs = mappedverbs.verbs_for_class_mapping(
            parse.FrenchMapping('LADL', '32C[+N1 V ou +N0 être V-n]'))
        self.assertIn('ankyloser', verbs)
        self.assertNotIn('accidenter', verbs)

    def test_column_and_class(self):
        verbs = mappedverbs.verbs_for_class_mapping(
            parse.FrenchMapping('LADL', '32C[+N1 =: Nabs métaphore] et 37M1'))
        self.assertEqual(verbs, {'envenimer', 'restaurer', 'rafraîchir'})

    def test_36dt(self):
        verbs = mappedverbs.verbs_for_class_mapping(
            parse.FrenchMapping('LADL', '36DT[+N2 détrimentaire]'))
        self.assertIn('voler', verbs)
        self.assertNotIn('vouer', verbs)
        self.assertIn('chiper', verbs)

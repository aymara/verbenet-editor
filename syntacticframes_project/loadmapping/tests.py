from django.test import SimpleTestCase

from loadmapping import mappedverbs
from parsecorrespondance import parse
from loadmapping.savelvf import normalize_verb


class TestNormalize(SimpleTestCase):
    def test_normalize_verb(self):
        """Test parsing of various LVF verb senses"""

        verbs_lvfp1 = {
            'abaisser 01': {'verb': 'abaisser', 'number': 1},
            'abaisser 08 (s\')': {'verb': "abaisser s'", 'number': 8},
            'zinzinuler': {'verb': 'zinzinuler', 'number': 0},
            'amuïr (s\')': {'verb': "amuïr s'", 'number': 0},
            'zéolitiser (se)': {'verb': 'zéolitiser se', 'number': 0}
        }

        for v in verbs_lvfp1:
            self.assertEqual(normalize_verb(v), verbs_lvfp1[v])

class TestLVFMappedVerbs(SimpleTestCase):
    def test_verbs_for_one_class(self):
        self.assertIn('mettre', mappedverbs.verbs_for_one_class('LVF', ('L3b', None)))

    def test_restrictions(self):
        verbs = mappedverbs.verbs_for_class_mapping(parse.FrenchMapping('LVF', 'M3c[+P3000]'))
        self.assertEqual(verbs, {'amortir', 'attiser', 'corser', 'désexciter',
            'développer', 'exalter', 'forcer', 'hausser', 'multiplier',
            'pousser', 'préconcentrer', 'ralentir', 'ranimer', 'renforcer',
            'réattiser', 'sous', 'suractiver', 'ébranler', 'élever', 'étaler',
            'étouffer'})

    def test_negative_restriction(self):
        verbs = mappedverbs.verbs_for_class_mapping(parse.FrenchMapping('LVF', 'P1i.2[-T14b0]'))

        # Verb "craindre" is included because of craindre 6 (in T1500), not
        # because of craindre 2 (in T14b0)
        self.assertEqual(verbs, {'convoiter', 'craindre', 'revouloir', 'supporter',
            'choyer', 'bercer', 'compter', 'redésirer', 'brûler', 'savourer', 'regretter',
            'chérir', 'mépriser', 'haïr', 'rougir', 'ressentir', 'espérer', 'appéter',
            'envier', 'caresser', 'détester', 'oser', 'idolâtrer', 'coter', 'désirer',
            'préférer', 'trembler', 'réaimer', 'jalouser', 'déguster', 'inattendre être',
            'adorer', 'admirer', 'entendre', 'vouloir', 'goûter', 'chercher', 'daigner',
            'désespérer', 'aimer', 'souhaiter'})


class TestLADLMappedVerbsFunctions(SimpleTestCase):
    def test_verbs_for_one_class(self):
        self.assertIn('mettre', mappedverbs.verbs_for_one_class('LADL', ('38LD', None)))

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

    def test_noun_column(self):
        verbs = mappedverbs.verbs_for_class_mapping(parse.FrenchMapping('LADL', '32C[+V-n instrument (forme V-n)]'))
        self.assertNotIn('acérer', verbs)
        self.assertIn('baratter', verbs)
        self.assertIn('shampouiner', verbs)

    def test_36dt(self):
        verbs = mappedverbs.verbs_for_class_mapping(
            parse.FrenchMapping('LADL', '36DT[+N2 détrimentaire]'))
        self.assertIn('voler', verbs)
        self.assertNotIn('vouer', verbs)
        self.assertIn('chiper', verbs)

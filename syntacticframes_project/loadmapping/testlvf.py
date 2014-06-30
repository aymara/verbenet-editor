import unittest

from loadmapping.savelvf import normalize_verb

class TestNormalize(unittest.TestCase):
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

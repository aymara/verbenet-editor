import unittest

import parse

class TestParsingFunctions(unittest.TestCase):

    def test_tokenize(self):
        self.assertEqual(parse.FrenchMapping._tokenize('L3b'), ['L3b'])
        self.assertEqual(parse.FrenchMapping._tokenize('L3b ou L3c'), ['L3b', 'ou', 'L3c'])
        self.assertEqual(
            parse.FrenchMapping._tokenize('L3b ou(L3c)'),
            ['L3b', 'ou', '(', 'L3c', ')'])
        self.assertEqual(parse.FrenchMapping._tokenize('(L3b'), ['(', 'L3b'])

    def test_nothing(self):
        self.assertEqual(parse.FrenchMapping('LADL', '-').infix(), '')
        self.assertEqual(parse.FrenchMapping('LADL', '?').infix(), '')
        self.assertEqual(parse.FrenchMapping('LADL', '').infix(), '')
        self.assertEqual(parse.FrenchMapping('LVF', '∅').infix(), '')

    def test_syntaxerror(self):
        with self.assertRaises(parse.SyntaxErrorException):
            parse.FrenchMapping('LVF', 'C ou L3b et X4a')

    def test_fakename(self):
        with self.assertRaises(parse.UnknownClassException):
            parse.FrenchMapping('LVF', 'L6d')
        with self.assertRaises(parse.UnknownClassException):
            parse.FrenchMapping('LADL', '38-LD')

    def test_simple(self):
        self.assertEqual(parse.FrenchMapping('LVF', 'L3b').infix(), 'L3b')
        self.assertEqual(parse.FrenchMapping('LADL', '38LD').infix(), '38LD')

    def test_sourcedest(self):
        self.assertEqual(parse.FrenchMapping('LADL', '36DT-source').infix(), '36DT-source')
        self.assertEqual(parse.FrenchMapping('LADL', '36DT-dest').infix(), '36DT-dest')

    def test_operator(self):
        self.assertEqual(parse.FrenchMapping('LVF', 'L3b ou X4a.2').infix(), '(or L3b X4a.2)')
        self.assertEqual(parse.FrenchMapping('LADL', '37M2 et 32A').infix(), '(and 37M2 32A)')

    def test_nestedoperators(self):
        self.assertEqual(
            parse.FrenchMapping('LVF', 'L3b ou (X4a.2 et X4a.1)').infix(),
            '(or L3b (and X4a.2 X4a.1))')
        self.assertEqual(
            parse.FrenchMapping('LADL', '32A et (37M2 ou 37M3 ou 37M4)').infix(),
            '(and 32A (or 37M2 37M3 37M4))')

    def test_entries(self):
        self.assertEqual(
            parse.FrenchMapping('LVF', 'L3b ou (X4a.2 et X4a.1)').entries(),
            ['L3b', 'X4a.2', 'X4a.1'])
        self.assertEqual(parse.FrenchMapping('LADL', '-').entries(), [])


if __name__ == '__main__':
    unittest.main()

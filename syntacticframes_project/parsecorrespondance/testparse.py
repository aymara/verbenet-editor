import unittest

import parse

class TestParsingFunctions(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(parse.FrenchMapping('LVF', 'L3b').result(), (None, ['L3b']))
        self.assertEqual(parse.FrenchMapping('LADL', '38LD').result(), (None, ['38LD']))

    def test_fakename(self):
        with self.assertRaises(parse.UnknownClassException):
            parse.FrenchMapping('LVF', 'L6d')
        with self.assertRaises(parse.UnknownClassException):
            parse.FrenchMapping('LADL', '38-LD')

    def test_operator(self):
        self.assertEqual(parse.FrenchMapping('LVF', 'L3b ou X4a.2').result(), ('or', ['L3b', 'X4a.2']))
        self.assertEqual(parse.FrenchMapping('LADL', '37M2 et 32A').result(), ('and', ['37M2', '32A']))

    def test_sourcedest(self):
        self.assertEqual(parse.FrenchMapping('LADL', '36DT source').result(), (None, ['36DT']))

    def test_nothing(self):
        self.assertEqual(parse.FrenchMapping('LADL', '-').result(), (None, []))
        self.assertEqual(parse.FrenchMapping('LADL', '?').result(), (None, []))
        self.assertEqual(parse.FrenchMapping('LADL', '').result(), (None, []))
        self.assertEqual(parse.FrenchMapping('LVF', '∅').result(), (None, []))

    def test_syntaxerror(self):
        with self.assertRaises(parse.SyntaxErrorException):
            parse.FrenchMapping('LVF', 'L6d ou L3b et X4a')


if __name__ == '__main__':
    unittest.main()

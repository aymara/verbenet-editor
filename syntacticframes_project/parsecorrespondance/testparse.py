import unittest

import parse

class TestParsingFunctions(unittest.TestCase):

    def test_simple(self):
        self.assertEqual(parse.get_lvf_list('L3b'), (None, ['L3b']))
        self.assertEqual(parse.get_ladl_list('38LD'), (None, ['38LD']))

    def test_fakename(self):
        with self.assertRaises(parse.UnknownClassException):
            parse.get_lvf_list('L6d')
        with self.assertRaises(parse.UnknownClassException):
            parse.get_ladl_list('38-LD')

    def test_operator(self):
        self.assertEqual(parse.get_lvf_list('L3b ou X4a.2'), ('or', ['L3b', 'X4a.2']))
        self.assertEqual(parse.get_ladl_list('37M2 et 32A'), ('and', ['37M2', '32A']))

    def test_sourcedest(self):
        self.assertEqual(parse.get_ladl_list('36DT source'), (None, ['36DT']))

    def test_nothing(self):
        self.assertEqual(parse.get_lvf_list('-'), (None, []))
        self.assertEqual(parse.get_lvf_list('?'), (None, []))
        self.assertEqual(parse.get_lvf_list(''), (None, []))
        self.assertEqual(parse.get_lvf_list('∅'), (None, []))

    def test_syntaxerror(self):
        with self.assertRaises(parse.SyntaxErrorException):
            parse.get_lvf_list('L6d ou L3b et X4a')


if __name__ == '__main__':
    unittest.main()

import unittest

from parsecorrespondance import parse

class TestParsingFunctions(unittest.TestCase):

    def test_tokenize(self):
        self.assertEqual(parse.FrenchMapping._tokenize('LVF', 'L3b'), ['L3b'])
        self.assertEqual(parse.FrenchMapping._tokenize('LVF', 'L3b ou L3c'), ['L3b', 'or', 'L3c'])
        self.assertEqual(
            parse.FrenchMapping._tokenize('LVF', 'L3b ou(L3c)'),
            ['L3b', 'or', '(', 'L3c', ')'])
        self.assertEqual(parse.FrenchMapping._tokenize('LVF', '(L3b'), ['(', 'L3b'])
        self.assertEqual(parse.FrenchMapping._tokenize('LADL', '(37M2 ou 37M3 ou 37M4) et 32A)'), ['(', '37M2', 'or', '37M3', 'or', '37M4', ')', 'and', '32A', ')'])

    def test_nothing(self):
        self.assertEqual(parse.FrenchMapping('LADL', '-').infix(), '')
        self.assertEqual(parse.FrenchMapping('LADL', '?').infix(), '')
        self.assertEqual(parse.FrenchMapping('LADL', '').infix(), '')
        self.assertEqual(parse.FrenchMapping('LVF', '*').infix(), '')

    def test_syntaxerror(self):
        with self.assertRaises(parse.SyntaxErrorException):
            parse.FrenchMapping('LVF', 'C ou L3b et X4a')

    def test_fakename(self):
        with self.assertRaises(parse.UnknownClassException):
            parse.FrenchMapping('LVF', 'L6d')
        with self.assertRaises(parse.UnknownClassException):
            parse.FrenchMapping('LADL', '38LJ')

    def test_simple(self):
        self.assertEqual(parse.FrenchMapping('LVF', 'L3b').infix(), 'L3b')
        self.assertEqual(parse.FrenchMapping('LADL', '38LD').infix(), '38LD')

    def test_operator(self):
        self.assertEqual(parse.FrenchMapping('LVF', 'L3b ou X4a.2').infix(), '(or L3b X4a.2)')
        self.assertEqual(parse.FrenchMapping('LADL', '37M2 et 32A').infix(), '(and 37M2 32A)')

    def test_missing_operator(self):
        with self.assertRaises(parse.SyntaxErrorException):
            parse.FrenchMapping('LVF', 'S3c ou S3b S3a')

    def test_nestedoperators(self):
        self.assertEqual(
            parse.FrenchMapping('LVF', 'L3b ou (X4a.2 et X4a.1)').infix(),
            '(or L3b (and X4a.2 X4a.1))')
        self.assertEqual(
            parse.FrenchMapping('LADL', '32A et (37M2 ou 37M3 ou 37M4)').infix(),
            '(and 32A (or 37M2 37M3 37M4))')
        self.assertEqual(
            parse.FrenchMapping('LADL', '(37M2 ou 37M3 ou 37M4) et 32A)').infix(),
            '(and (or 37M2 37M3 37M4) 32A)')

    def test_flatparse(self):
        self.assertEqual(
            parse.FrenchMapping('LADL', '32A et (37M2 ou 37M3)').flat_parse(),
            [('32A', '32A'), ('et', None), ('(', None), ('37M2', '37M2'),
             ('ou', None), ('37M3', '37M3'), (')', None)])
        self.assertEqual(
            parse.FrenchMapping('LADL', '32C[+N1 être Vpp W]').flat_parse(),
            [('32C[+N1 être Vpp W]', '32C')])

class TestLVFColumns(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(
            parse.FrenchMapping('LVF', 'L3b[+T1300]').parse_tree,
            {'leaf': ('L3b', [None, {'column': 'T1300', 'value': '+'}])})
        self.assertEqual(
            parse.FrenchMapping('LVF', 'P1i.2[-T14b0]').parse_tree,
            {'leaf': ('P1i.2', [None, {'column': 'T14b0', 'value': '-'}])})

class TestLADLColumns(unittest.TestCase):
    def test_tokenize(self):
        self.assertEqual(
            parse.FrenchMapping._tokenize('LADL', '38L[+N1 V W]'),
            ['38L', '[', '+', 'N1 V W', ']'])
        self.assertEqual(
            parse.FrenchMapping._tokenize('LADL', '38L[-N1 V W]'),
            ['38L', '[', '-', 'N1 V W', ']'])
        self.assertEqual(
            parse.FrenchMapping._tokenize('LADL', '36DT[+N2 détrimentaire]'),
            ['36DT', '[', '+', 'N2 détrimentaire', ']'])
        self.assertEqual(
            parse.FrenchMapping._tokenize('LADL', '38[+inexistant] et 22'),
            ['38', '[', '+', 'inexistant', ']', 'and', '22'])
        self.assertEqual(
            parse.FrenchMapping._tokenize('LADL', '38L[+V-n transport (forme V-n)]'),
            ['38L', '[', '+', 'V-n transport (forme V-n)', ']'])
        self.assertEqual(
            parse.FrenchMapping._tokenize('LADL', '38L[+V-n transport (forme V-n) et +N0 V]'),
            ['38L', '[', '+', 'V-n transport (forme V-n)', 'and', '+', 'N0 V', ']'])
        self.assertEqual(
            parse.FrenchMapping._tokenize('LADL', '35L[+[extrap]]'),
            ['35L', '[', '+', '[extrap]', ']'])
        self.assertEqual(
            parse.FrenchMapping._tokenize('LADL', '38R[Prép2=par]'),
            ['38R', '[', '=', 'Prép2', 'par', ']'])
        self.assertEqual(
            parse.FrenchMapping._tokenize('LADL', '15[Prép2=auprès de]'),
            ['15', '[', '=',  'Prép2', 'auprès de', ']'])
        self.assertEqual(
            parse.FrenchMapping._tokenize('LADL', '15[Prép2=auprès de et +N0 V]'),
            ['15', '[', '=',  'Prép2', 'auprès de', 'and' , '+', 'N0 V', ']'])

        self.assertEqual(
            parse.FrenchMapping._tokenize('LADL', '38R[Prép2=par et +N0 V]'),
            ['38R', '[', '=', 'Prép2', 'par', 'and', '+', 'N0 V', ']'])

        with self.assertRaises(parse.SyntaxErrorException):
            parse.FrenchMapping._tokenize('LADL', '38L[+V-n transport ou -N et +N0 V]'),
        with self.assertRaises(parse.SyntaxErrorException):
            parse.FrenchMapping._tokenize('LADL', '38L[+V-n transport ou N]'),
        with self.assertRaises(parse.SyntaxErrorException):
            parse.FrenchMapping._tokenize('LADL', '38R[Prép2 = par]'),
        with self.assertRaises(parse.SyntaxErrorException):
            parse.FrenchMapping._tokenize('LADL', '38R[Prép2= par]'),
            parse.FrenchMapping._tokenize('LADL', '38R[Prép2 =par]'),

    def test_operator_in_column_name(self):
        # The only two cases containing an 'or'
        self.assertEqual(
            parse.FrenchMapping._tokenize('LADL', '9[+N2 =: si P ou si P]'),
            ['9', '[', '+',  'N2 =: si P ou si P', ']'])
        self.assertEqual(
            parse.FrenchMapping._tokenize('LADL', '15[-N1 =: si P ou si P]'),
            ['15', '[', '-',  'N1 =: si P ou si P', ']'])

    def test_infix(self):
        self.assertEqual(parse.FrenchMapping('LADL', '38LD[+A ou +B]').infix(), '38LD[+A ou +B]')

    def test_parse(self):
        self.assertEqual(
            parse.FrenchMapping('LADL', '36DT[+N2 détrimentaire]').parse_tree,
            {'leaf': ('36DT', [None, {'column': 'N2 détrimentaire', 'value': '+'}])})
        self.assertEqual(
            parse.FrenchMapping('LADL', '36DT[+N2 détrimentaire ou -N2 être V-n]').parse_tree,
            {'leaf': ('36DT', ['or', {'column': 'N2 détrimentaire', 'value': '+'}, {'column': 'N2 être V-n', 'value': '-'}]), })

        self.assertEqual(
            parse.FrenchMapping('LADL', '38R[Prép2=par]').parse_tree,
            {'leaf': ('38R', [None, {'column': 'Prép2', 'value': 'par'}]), })

    def test_flatparse(self):
        self.assertEqual(
                parse.FrenchMapping('LADL', '36DT[+N2 détrimentaire et -Ppv =: y]').flat_parse(),
                [('36DT[+N2 détrimentaire et -Ppv =: y]', '36DT')])

    def test_syntaxerror(self):
        with self.assertRaises(parse.SyntaxErrorException):
            parse.FrenchMapping('LADL', '38L [+N1 V W]')  # extra space
        with self.assertRaises(parse.SyntaxErrorException):
            parse.FrenchMapping('LADL', '38L [-N1 V W]')  # extra space
        with self.assertRaises(parse.SyntaxErrorException):
            parse.FrenchMapping('LADL', '38L[N1 V W]')  # missing plus or minus
        with self.assertRaises(parse.SyntaxErrorException):
            parse.FrenchMapping('LADL', '38L[N1 V V]')  # unknown column
        with self.assertRaises(parse.SyntaxErrorException):
            parse.FrenchMapping('LADL', '38L[N1 V W')  # missing closing bracket

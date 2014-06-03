from django.test import TestCase

from role.parserole import ParsedRole


class TestRoleParses(TestCase):
    def test_simple(self):
        agent = ParsedRole('Agent')
        self.assertEqual(agent.role, 'Agent')
        self.assertEqual(agent.selrestrs, {})

    def test_one_restr(self):
        agent_animate = ParsedRole('Agent [+animate]')
        self.assertEqual(agent_animate.role, 'Agent')
        self.assertEqual(agent_animate.selrestrs, '+animate')

    def test_and_restr(self):
        role = ParsedRole('Instrument [+concrete & -animate]')
        self.assertEqual(role.role, 'Instrument')
        self.assertEqual(role.selrestrs, {
            'logic': '&',
            'children': ['+concrete', '-animate']})

    def test_or_restr(self):
        experiencer = ParsedRole('Experiencer [+animate | +organization]')
        self.assertEqual(experiencer.role, 'Experiencer')
        self.assertEqual(experiencer.selrestrs, {
            'logic': '|',
            'children': ['+animate', '+organization']})

    def test_mixed_restr(self):
        role = ParsedRole('Destination [+animate | [+location & -region]]')
        self.assertEqual(role.role, 'Destination')
        self.assertEqual(role.selrestrs, {
            'logic': '|',
            'children': [
                '+animate',
                {'logic': '&', 'children': ['+location', '-region']}
            ]})

    def test_deep_restr(self):
        role = ParsedRole('Agent [+b | [+c & [-d | -a]]]')
        self.assertEqual(role.role, 'Agent')
        self.assertEqual(role.selrestrs, {
            'logic': '|',
            'children': [
                '+b',
                {'logic': '&',
                 'children': [
                     '+c',
                     {'logic': '|',
                      'children': ['-d', '-a']}]}]})

    def test_multi_restr(self):
        role = ParsedRole('Agent [+b | +a | +i]')
        self.assertEqual(role.selrestrs, {
            'logic': '|',
            'children': ['+b', '+a', '+i']})

    def test_lexical_errors(self):
        with self.assertRaises(AttributeError):
            ParsedRole('')
        with self.assertRaises(AttributeError):
            ParsedRole('  ')

        with self.assertRaises(AssertionError):
            ParsedRole('Agent[+b]')

        with self.assertRaises(AssertionError):
            ParsedRole('Agent [b]')
        with self.assertRaises(AssertionError):
            ParsedRole('Agent [+b | c]')

        with self.assertRaises(AssertionError):
            ParsedRole('Agent [+b')

    def test_syntax_errors(self):
        with self.assertRaises(AssertionError):
            ParsedRole('Agent [+b & +c | -a]')

    def test_semantic_errors(self):
        with self.assertRaises(AssertionError):
            ParsedRole('ThisRoleDoesntExist')

import sys
import xml.etree.ElementTree as ET

from django.test import SimpleTestCase

from export.export import (
    tokenize_syntax, separate_syntax_part,
    separate_phrasetype,
    merge_primary_and_syntax, xml_of_syntax)

class TestTokenizeSyntax(SimpleTestCase):
    def test_simple(self):
        self.assertEqual(list(tokenize_syntax('Agent V Patient')),
                         ['Agent', 'V', 'Patient'])
        self.assertEqual(list(tokenize_syntax('Agent V  Patient')),
                         'Agent V   Patient'.split())

    def test_preposition_list(self):
        self.assertEqual(list(tokenize_syntax('Agent V {{+loc}} Location')),
                         ['Agent', 'V', {'+loc'}, 'Location'])
        self.assertEqual(list(tokenize_syntax('Agent V {pour à de} Patient')),
                         ['Agent', 'V', {'pour', 'à', 'de'}, 'Patient'])

        self.assertEqual(
            list(tokenize_syntax('Agent V {à dans verbs} Location')),
            ['Agent', 'V', {'à', 'dans', 'verbs'}, 'Location'])
        self.assertEqual(list(tokenize_syntax('Agent V {à} Location')), ['Agent', 'V', {'à'}, 'Location'])
        self.assertEqual(list(tokenize_syntax('Agent V {de} Location')), ['Agent', 'V', {'de'}, 'Location'])

        self.assertEqual(list(tokenize_syntax('Agent V {pour/de la part de} Patient')),
                         ['Agent', 'V', {'pour', 'de la part de'}, 'Patient'])

    def test_restriction(self):
        self.assertEqual(
            list(tokenize_syntax('Agent V Theme<+de_Vinf>')),
            ['Agent', 'V', 'Theme<+de_Vinf>'])


class TestSeparatePhraseType(SimpleTestCase):
    def test_simple_phrase(self):
        self.assertEqual(separate_phrasetype('NP'), ('NP', None))

    def test_phrase_with_role(self):
        self.assertEqual(separate_phrasetype('NP.Agent'), ('NP', 'Agent'))
        self.assertEqual(separate_phrasetype('NP.agent'), ('NP', 'Agent'))

    def test_phrase_with_alternation(self):
        # Get rid of -Middle - doesn't seem useful and should be in the
        # secondary attribute
        self.assertEqual(separate_phrasetype('NP-Middle'), ('NP', None))
        self.assertEqual(separate_phrasetype('NP-Moyen'), ('NP', None))

    def test_something_else(self):
        self.assertEqual(separate_phrasetype('V'), ('V', None))
        self.assertEqual(separate_phrasetype('se'), ('se', None))
        self.assertEqual(separate_phrasetype('abcd.ert'), ('abcd.ert', None))


class TestSeparateSyntax(SimpleTestCase):
    def test_no_role(self):
        self.assertEqual(separate_syntax_part('NP'), ('NP', None))
        self.assertEqual(separate_syntax_part('V'), ('V', None))
        self.assertEqual(separate_syntax_part('V<+neutre>'), ('V', '<+neutre>'))

    def test_simple_role(self):
        self.assertEqual(separate_syntax_part('Agent'), ('Agent', None))

    def test_modified_role(self):
        self.assertEqual(separate_syntax_part('Instrument<+Plural>'), ('Instrument', '<+Plural>'))


class TestFullMerge(SimpleTestCase):
    def test_simple_sentence(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V NP', 'Agent V Patient', output=sys.stdout),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'NP', 'role': 'Patient'}])

    def test_single_preposition(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V PP', 'Agent V {foo} Patient', output=sys.stdout),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'PREP', 'Value': {'foo'}},
             {'type': 'PP', 'role': 'Patient'}])

    def test_preposition_list(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V PP', 'Agent V {à dans pour} Patient', output=sys.stdout),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'Value': {'à', 'dans', 'pour'}, 'type': 'PREP'},
             {'role': 'Patient', 'type': 'PP'}])

        self.assertEqual(
            merge_primary_and_syntax('NP V PP', 'Agent V {pour/de la part de} Patient', output=sys.stdout),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'Value': {'pour', 'de la part de'}, 'type': 'PREP'},
             {'role': 'Patient', 'type': 'PP'}])

    def test_preposition_class(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V PP', 'Agent V {{+loc}} Patient', output=sys.stdout),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'PREP', 'type_': 'loc', 'Value': '+'},
             {'type': 'PP', 'role': 'Patient'}])


    def test_neutral_verb(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V NP', 'Agent V<+neutre> Patient', output=sys.stdout),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V', 'restr': 'neutre'},
             {'type': 'NP', 'role': 'Patient'}])

    def test_adverb_as_role(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V ADV-Middle', 'Patient V ADV', output=sys.stdout),
            [{'type': 'NP', 'role': 'Patient'},
             {'type': 'V'},
             {'type': 'ADV'}])

    def test_adj_as_role(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V NP ADJ', 'Pivot V Theme ADJ', output=sys.stdout),
            [{'type': 'NP', 'role': 'Pivot'},
             {'type': 'V'},
             {'type': 'NP', 'role': 'Theme'},
             {'type': 'ADJ'}])

    def test_que(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V que S', 'Agent V Theme<+que_comp>', output=sys.stdout),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'S', 'role': 'Theme', 'introduced_by': 'que', 'restr': 'comp'}])

    def test_vinf(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V de Vinf', 'Pivot V Theme<+de V0-inf>', output=sys.stdout),
            [{'type': 'NP', 'role': 'Pivot'},
             {'type': 'V'},
             {'type': 'Vinf', 'role': 'Theme', 'introduced_by': 'de', 'restr': 'V0-inf'}])

    def test_quep(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V Qu Psubj', 'Agent V Topic<+Qu Psubj>', output=sys.stdout),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'Psubj', 'role': 'Topic', 'introduced_by': 'Qu', 'restr': 'Psubj'}])

    def test_comment_noextract(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V comment P', 'Experiencer V Stimulus<+comment P>', output=sys.stdout),
            [{'type': 'NP', 'role': 'Experiencer'},
             {'type': 'V'},
             {'type': 'P', 'role': 'Stimulus', 'introduced_by': 'comment', 'restr': 'P'}])

    def test_plural(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V', 'Patient<+plural> V', output=sys.stdout),
            [{'type': 'NP', 'role': 'Patient', 'modifier': '+plural'},
             {'type': 'V'}])

    def test_comment(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V comment S', 'Experiencer V Stimulus<+comment_extract>', output=sys.stdout),
            [{'type': 'NP', 'role': 'Experiencer'},
             {'type': 'V'},
             {'type': 'S', 'role': 'Stimulus', 'introduced_by': 'comment', 'restr': 'extract'}])

class TestExport(SimpleTestCase):
    def test_simple_sentence(self):
        new_syntax = merge_primary_and_syntax('NP V NP', 'Agent V Patient', output=sys.stdout)
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX><NP value="Agent"><SYNRESTRS /></NP><VERB /><NP value="Patient"><SYNRESTRS /></NP></SYNTAX>')

    def test_pp(self):
        new_syntax = merge_primary_and_syntax('NP V PP', 'Agent V {de} Patient', output=sys.stdout)
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX><NP value="Agent"><SYNRESTRS /></NP><VERB /><PREP><SELRESTRS><SELRESTR Value="de" /></SELRESTRS></PREP><NP value="Patient"><SYNRESTRS /></NP></SYNTAX>')

    def test_pp_category(self):
        new_syntax = merge_primary_and_syntax('NP V PP', 'Agent V {{+loc}} Patient', output=sys.stdout)
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX><NP value="Agent"><SYNRESTRS /></NP><VERB /><PREP><SELRESTRS><SELRESTR Value="+" type="loc" /></SELRESTRS></PREP><NP value="Patient"><SYNRESTRS /></NP></SYNTAX>')

    def test_modifier(self):
        new_syntax = merge_primary_and_syntax('NP V NP', 'Agent V Patient<+plural>', output=sys.stdout)
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX><NP value="Agent"><SYNRESTRS /></NP><VERB /><NP modifier="+plural" value="Patient"><SYNRESTRS /></NP></SYNTAX>')

        new_syntax = merge_primary_and_syntax('NP V S', 'Agent V Patient<+plural>', output=sys.stdout)
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX><NP value="Agent"><SYNRESTRS /></NP><VERB /><S modifier="+plural" value="Patient" /></SYNTAX>')

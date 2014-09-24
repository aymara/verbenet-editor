import sys
import xml.etree.ElementTree as ET

from django.test import SimpleTestCase

from export.export import (
    split_syntax, separate_phrasetype, separate_syntax,
    merge_primary_and_syntax, xml_of_syntax)


class TestSplitSyntax(SimpleTestCase):
    def test_normal_split(self):
        self.assertEqual(split_syntax('Agent V Patient'), ['Agent', 'V', 'Patient'])
        self.assertEqual(split_syntax('Agent V   Patient'), ['Agent', 'V', 'Patient'])
        self.assertEqual(split_syntax(
            'Agent V {{+loc}} Location'),
            ['Agent', 'V', {'{{+loc}}'}, 'Location'])

    def test_preposition_list(self):
        self.assertEqual(split_syntax(
            'Agent V {à dans verbs} Location'),
            ['Agent', 'V', {'à', 'dans', 'verbs'}, 'Location'])
        self.assertEqual(split_syntax('Agent V {à} Location'), ['Agent', 'V', {'à'}, 'Location'])
        self.assertEqual(split_syntax('Agent V {de} Location'), ['Agent', 'V', {'de'}, 'Location'])


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
        self.assertEqual(separate_syntax('NP'), ('NP', None))
        self.assertEqual(separate_syntax('V'), ('V', None))
        self.assertEqual(separate_syntax('V<+neutre>'), ('V', '<+neutre>'))

    def test_simple_role(self):
        self.assertEqual(separate_syntax('Agent'), ('Agent', None))

    def test_modified_role(self):
        self.assertEqual(separate_syntax('Instrument<+Plural>'), ('Instrument', '<+Plural>'))


class TestFullMerge(SimpleTestCase):
    def test_simple_sentence(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V NP', 'Agent V Patient', output=sys.stderr),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'NP', 'role': 'Patient'}])

    def test_single_preposition(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V PP', 'Agent V {lol} Patient', output=sys.stderr),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'PP', 'role': 'Patient', 'prep': {'lol'}}])

    def test_preposition_list(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V PP', 'Agent V {à dans pour} Patient', output=sys.stderr),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'PP', 'role': 'Patient', 'prep': {'à', 'dans', 'pour'}}])

    def test_neutral_verb(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V NP', 'Agent V<+neutre> Patient', output=sys.stderr),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V', 'restr': 'neutre'},
             {'type': 'NP', 'role': 'Patient'}])

    def test_adverb_as_role(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V ADV-Middle', 'Patient V ADV', output=sys.stderr),
            [{'type': 'NP', 'role': 'Patient'},
             {'type': 'V'},
             {'type': 'ADV'}])

    def test_adj_as_role(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V NP ADJ', 'Pivot V Theme ADJ', output=sys.stderr),
            [{'type': 'NP', 'role': 'Pivot'},
             {'type': 'V'},
             {'type': 'NP', 'role': 'Theme'},
             {'type': 'ADJ'}])

    def test_que(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V que S', 'Agent V Theme<+que_comp>', output=sys.stderr),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'S', 'role': 'Theme', 'introduced_by': 'que', 'restr': 'comp'}])

    def test_de(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V de V-inf', 'Pivot V Theme<+de_Vinf>', output=sys.stderr),
            [{'type': 'NP', 'role': 'Pivot'},
             {'type': 'V'},
             {'type': 'V-inf', 'role': 'Theme', 'introduced_by': 'de', 'restr': 'Vinf'}])

    def test_comment(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V comment S', 'Experiencer V Stimulus<+comment_extract>', output=sys.stdout),
            [{'type': 'NP', 'role': 'Experiencer'},
             {'type': 'V'},
             {'type': 'S', 'role': 'Stimulus', 'introduced_by': 'comment', 'restr': 'extract'}])

class TestExport(SimpleTestCase):
    def test_simple_sentence(self):
        new_syntax = merge_primary_and_syntax('NP V NP', 'Agent V Patient', output=sys.stderr)
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX><NP role="Agent"><SYNRESTRS /></NP><VERB /><NP role="Patient"><SYNRESTRS /></NP></SYNTAX>')

    def test_pp(self):
        new_syntax = merge_primary_and_syntax('NP V PP', 'Agent V {de} Patient', output=sys.stderr)
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX><NP role="Agent"><SYNRESTRS /></NP><VERB /><PP prep="de" role="Patient"><SYNRESTRS /></PP></SYNTAX>')

    def test_pp_category(self):
        new_syntax = merge_primary_and_syntax('NP V PP', 'Agent V {{+loc}} Patient', output=sys.stderr)
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX><NP role="Agent"><SYNRESTRS /></NP><VERB /><PP prep="{{+loc}}" role="Patient"><SYNRESTRS /></PP></SYNTAX>')

import sys
import xml.etree.ElementTree as ET

from django.test import SimpleTestCase

from export.export import (
    tokenize_syntax, tokenize_primary,
    separate_syntax_part, separate_phrasetype,
    merge_primary_and_syntax, xml_of_syntax,
    WrongFrameException)

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
        self.assertEqual(list(tokenize_syntax('Agent V {pour/à/de} Patient')),
                         ['Agent', 'V', {'pour', 'à', 'de'}, 'Patient'])

        self.assertEqual(
            list(tokenize_syntax('Agent V {à dans BAR} Location')),
            ['Agent', 'V', {'à', 'dans', 'BAR'}, 'Location'])
        self.assertEqual(list(tokenize_syntax('Agent V {à} Location')), ['Agent', 'V', {'à'}, 'Location'])
        self.assertEqual(list(tokenize_syntax('Agent V {de} Location')), ['Agent', 'V', {'de'}, 'Location'])

        self.assertEqual(list(tokenize_syntax('Agent V {pour/de la part de} Patient')),
                         ['Agent', 'V', {'pour', 'de la part de'}, 'Patient'])

    def test_restriction(self):
        self.assertEqual(
            list(tokenize_syntax('Agent V Theme<+de_Vinf>')),
            ['Agent', 'V', 'Theme<+de_Vinf>'])


class TestTokenizePrimary(SimpleTestCase):
    def test_simple_split(self):
        self.assertEqual(list(tokenize_primary('NP V NP')), ['NP', 'V', 'NP'])

    def test_preposition(self):
        self.assertEqual(list(tokenize_primary('NP V de V-inf')), ['NP', 'V', {'de'}, 'V-inf'])

    def test_qu(self):
        self.assertEqual(list(tokenize_primary('NP V Qu Psubj')), ['NP', 'V', 'Qu', 'Psubj'])


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
        self.assertEqual(separate_phrasetype('Qu'), ('Qu', None))
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
            merge_primary_and_syntax('NP V NP', 'Agent V Patient'),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'NP', 'role': 'Patient'}])

    def test_single_preposition(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V PP', 'Agent V {foo} Patient'),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'PREP', 'Value': {'foo'}},
             {'type': 'PP', 'role': 'Patient'}])

    def test_preposition_list(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V PP', 'Agent V {à dans pour} Patient'),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'Value': {'à', 'dans', 'pour'}, 'type': 'PREP'},
             {'role': 'Patient', 'type': 'PP'}])

        self.assertEqual(
            merge_primary_and_syntax('NP V PP', 'Agent V {pour/de la part de} Patient'),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'Value': {'pour', 'de la part de'}, 'type': 'PREP'},
             {'role': 'Patient', 'type': 'PP'}])

    def test_preposition_class(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V PP', 'Agent V {{+loc}} Patient'),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'PREP', 'type_': 'loc', 'Value': '+'},
             {'type': 'PP', 'role': 'Patient'}])


    def test_neutral_verb(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V NP', 'Agent V<+neutre> Patient'),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V', 'restr': 'neutre'},
             {'type': 'NP', 'role': 'Patient'}])

    def test_adverb_as_role(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V ADV-Middle', 'Patient V ADV'),
            [{'type': 'NP', 'role': 'Patient'},
             {'type': 'V'},
             {'type': 'ADV'}])

    def test_adj_as_role(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V NP ADJ', 'Pivot V Theme ADJ'),
            [{'type': 'NP', 'role': 'Pivot'},
             {'type': 'V'},
             {'type': 'NP', 'role': 'Theme'},
             {'type': 'ADJ'}])

    def test_vinf(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V de V-inf', 'Pivot V Theme<+de VAgent-inf>'),
            [{'type': 'NP', 'role': 'Pivot'},
             {'type': 'V'},
             {'type': 'VINF', 'role': 'Theme', 'is_true_prep': False, 'emptysubjectrole': 'Agent', 'introduced_by': {'de'}}])

    def test_explicitprep_vinf(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V à V-inf', 'Pivot V {à} Theme<+VAgent-inf>'),
            [{'type': 'NP', 'role': 'Pivot'},
             {'type': 'V'},
             {'type': 'VINF', 'role': 'Theme', 'is_true_prep': True, 'emptysubjectrole': 'Agent', 'introduced_by': {'à'}}])

    def test_twoprep_vinf(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V à/de V-inf', 'Pivot V {à/de} Theme<+VAgent-inf>'),
            [{'type': 'NP', 'role': 'Pivot'},
             {'type': 'V'},
             {'type': 'VINF', 'role': 'Theme', 'is_true_prep': True, 'emptysubjectrole': 'Agent', 'introduced_by': {'à', 'de'}}])

    def test_bad_vinf(self):
        with self.assertRaises(WrongFrameException):
            merge_primary_and_syntax(
                'NP V de V-inf', 'Pivot V Theme<+deVAgent-inf>',
                output=sys.stdout)

    # phrastique direct
    def test_quep(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V Qu Psubj', 'Agent V Topic<+Qu Psubj>'),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'PSUBJ', 'role': 'Topic', 'introduced_by': None}])

    # phrastique indirect
    def test_dece_quep(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V PP de ce Qu Pind', 'Agent V {avec} Co-Agent {de} Topic<+Qu Pind>'),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'PREP', 'Value': {'avec'}},
             {'type': 'PP', 'role': 'Co-Agent'},
             {'type': 'PREP', 'Value': {'de'}},
             {'type': 'PIND', 'role': 'Topic', 'introduced_by': 'de'}])

    def test_sip(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V si P', 'Agent V Topic<+si P>'),
            [{'type': 'NP', 'role': 'Agent'},
             {'type': 'V'},
             {'type': 'P', 'role': 'Topic', 'introduced_by': 'si'}])

    def test_plural(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V', 'Patient<+plural> V'),
            [{'type': 'NP', 'role': 'Patient', 'modifier': '+plural'},
             {'type': 'V'}])

    def test_comment(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V comment P', 'Experiencer V Stimulus<+comment P>'),
            [{'type': 'NP', 'role': 'Experiencer'},
             {'type': 'V'},
             {'type': 'P', 'role': 'Stimulus', 'introduced_by': 'comment'}])

    def test_interrogative_prep(self):
        self.assertEqual(
            merge_primary_and_syntax('NP V de comment P', 'Experiencer V {de} Stimulus<+comment P>'),
            [{'type': 'NP', 'role': 'Experiencer'},
             {'type': 'V'},
             {'type': 'PREP', 'Value': {'de'}},
             {'type': 'P', 'role': 'Stimulus', 'introduced_by': 'comment'}])


class TestExport(SimpleTestCase):
    def test_simple_sentence(self):
        new_syntax = merge_primary_and_syntax('NP V NP', 'Agent V Patient')
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX><NP value="Agent"><SYNRESTRS /></NP><VERB /><NP value="Patient"><SYNRESTRS /></NP></SYNTAX>')

    def test_pp(self):
        new_syntax = merge_primary_and_syntax('NP V PP', 'Agent V {de} Patient')
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX><NP value="Agent"><SYNRESTRS /></NP><VERB /><PREP><SELRESTRS><SELRESTR Value="de" /></SELRESTRS></PREP><NP value="Patient"><SYNRESTRS /></NP></SYNTAX>')

    def test_pp_category(self):
        new_syntax = merge_primary_and_syntax('NP V PP', 'Agent V {{+loc}} Patient')
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX><NP value="Agent"><SYNRESTRS /></NP><VERB /><PREP><SELRESTRS><SELRESTR Value="+" type="loc" /></SELRESTRS></PREP><NP value="Patient"><SYNRESTRS /></NP></SYNTAX>')

    def test_modifier(self):
        new_syntax = merge_primary_and_syntax('NP V NP', 'Agent V Patient<+plural>')
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX><NP value="Agent"><SYNRESTRS /></NP><VERB /><NP modifier="+plural" value="Patient"><SYNRESTRS /></NP></SYNTAX>')

        new_syntax = merge_primary_and_syntax(
            'NP se V ADV', 'Patient se V<+middle> ADV')
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX><NP value="Patient"><SYNRESTRS /></NP><VERB pronominal="true" restr="middle" /><ADV /></SYNTAX>')

    def test_p(self):
        new_syntax = merge_primary_and_syntax('NP V Qu Psubj', 'Agent V Topic<+Qu Psubj>')
        xml = xml_of_syntax(new_syntax)
        print(new_syntax)
        print(xml)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX>'
            '<NP value="Agent"><SYNRESTRS /></NP>'
            '<VERB />'
            '<PSUBJ value="Topic" />'
            '</SYNTAX>')

    def test_dece_quep(self):
        self.maxDiff = None
        new_syntax = merge_primary_and_syntax('NP V PP de ce Qu Pind', 'Agent V {avec} Co-Agent {de} Topic<+Qu Pind>')
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX>'
            '<NP value="Agent"><SYNRESTRS /></NP>'
            '<VERB />'
            '<PREP><SELRESTRS><SELRESTR Value="avec" /></SELRESTRS></PREP>'
            '<NP value="Co-Agent"><SYNRESTRS /></NP>'
            '<PREP><SELRESTRS><SELRESTR Value="de" /></SELRESTRS></PREP>'
            '<PIND introduced_by="de" value="Topic" />'
            '</SYNTAX>')

    def test_vinf(self):
        self.maxDiff = None
        new_syntax = merge_primary_and_syntax(
            'NP V PP.source de V-inf',
            'Pivot V {pour/de la part de} Source Theme<+de VSource-inf>')
        xml = xml_of_syntax(new_syntax)
        self.assertEqual(
            ET.tostring(xml, encoding='unicode'),
            '<SYNTAX>'
            '<NP value="Pivot"><SYNRESTRS /></NP>'
            '<VERB />'
            '<PREP><SELRESTRS><SELRESTR Value="de la part de;pour" /></SELRESTRS></PREP>'
            '<NP value="Source"><SYNRESTRS /></NP>'
            '<VINF emptysubjectrole="Source" introduced_by="de" is_true_prep="false" value="Theme" />'
            '</SYNTAX>')

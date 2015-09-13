import io
import os
import re
import sys
import locale
from xml.etree import ElementTree as ET

from syntacticframes.models import LevinClass, VerbNetFrameSet, VerbTranslation
from role.parserole import ROLE_LIST

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

# no speficic treatment for those phrase types
EASY_PHRASE_TYPE_LIST = ['NP', 'PP', 'ADJ', 'ADV', 'ADVP', 'V-inf']
VINF_PREPS = {'de', 'à', 'comment', 'pour'}

class WrongFrameException(Exception):
    pass

total_frames, handled_frames = 0, 0

def tokenize_syntax(syntax):
    def part_between_braces(syntax, i):
        j = i + 1
        while syntax[j] != '}':
            j += 1
        return syntax[i:j+2]

    current_word = ''

    i = 0
    while i < len(syntax):
        c = syntax[i]
        if c == ' ':
            if current_word:
                if syntax[i+1] == '<':  # only allow Theme<+de VAgent-inf>, not Theme <+de VAgent-inf>
                    raise WrongFrameException('Space between role and restriction forbidden')
                else:
                    yield current_word
            current_word = ''
        elif c == '{':
            assert current_word == ''
            syntax_part = part_between_braces(syntax, i)
            if syntax_part.startswith('{{') and syntax_part.endswith('}}'):
                yield set([syntax_part[2:-2]])
            elif '/' in syntax_part:
                yield set(syntax_part[1:-2].split('/'))
            else:
                yield set(syntax_part[1:-2].split(' '))

            i += len(syntax_part) - 1
        elif c == '<':
            while syntax[i] != '>':
                current_word += syntax[i]
                i += 1
            current_word += syntax[i]
        else:
            current_word += c

        i += 1

    if current_word:
        yield current_word


def tokenize_primary(primary):
    for primary_part in primary.split():
        if primary_part in VINF_PREPS | {'ce', 'si', 'combien', 'comment'}:
            yield {primary_part}
        elif '/' in primary_part:
            prep_set = set(primary_part.split('/'))
            assert prep_set & VINF_PREPS is not None
            yield prep_set
        else:
            yield primary_part


def separate_phrasetype(primary_part):
    # prep
    if isinstance(primary_part, set):
        return primary_part, None

    # NP.Agent
    try:
        phrase_type, role = primary_part.split('.')
        if phrase_type in EASY_PHRASE_TYPE_LIST and role.title() in ROLE_LIST:
            return phrase_type, role.title()
    except ValueError:
        pass

    if primary_part.endswith('-Middle') or primary_part.endswith('-Moyen'):
        real_phrasetype = '-'.join(primary_part.split('-')[:-1])
        assert real_phrasetype in EASY_PHRASE_TYPE_LIST
        return real_phrasetype, None

    return primary_part, None


def separate_syntax_part(syntax_part):
    if isinstance(syntax_part, set):
        return syntax_part, None

    mode = 'ROLE'  # can also be RESTR, NEAR_END and END
    role, restr = '', ''

    for c in syntax_part:
        if c == '<':
            mode = 'RESTR'
        elif c == '>':
            mode = 'NEAR_END'

        if mode == 'ROLE':
            role += c
        elif mode == 'RESTR':
            restr += c
        elif mode == 'NEAR_END':
            restr += c
            mode = 'END'
        else:
            assert mode == 'END'
            raise WrongFrameException('Pas de caractères attendus après > dans {}'.format(syntax_part))

    if not restr:
        return role, None
    else:
        return role, restr


def merge_primary_and_syntax(primary, syntax, output=sys.stdout):
    print('{:<40} {}'.format(primary, syntax), file=output)
    primary_parts = list(tokenize_primary(primary))
    syntax_parts = list(tokenize_syntax(syntax))
    parsed_frame = []
    pronominal = False

    print(primary_parts, syntax_parts, file=output)

    i, j = 0, 0
    while i < len(syntax_parts) and j < len(primary_parts):
        print(i, j, syntax_parts[i], primary_parts[j], file=output)

        syntax_role, restr = separate_syntax_part(syntax_parts[i])
        phrase_type, primary_role = separate_phrasetype(primary_parts[j])

        print('   |{}| |{}|'.format(syntax_role, restr), file=output)
        print('   |{}| |{}|'.format(phrase_type, primary_role), file=output)

        np_vinf = False
        if primary_parts[j] == 'NP':
            final_role = i + 1 == len(syntax_parts)
            np_vinf_syntax = j + 2 == len(primary_parts) and primary_parts[j+1] in ['V-inf', 'V-ant']
            np_vinf = final_role and np_vinf_syntax

        if np_vinf:
            # everything was asserted above, we only need to output the result
            parsed_frame.append({
                'type': 'VINF',
                'role': syntax_role,
                'is_npvinf': True,
                'emptysubjectrole': None})

            j += 2
            i += 1

        # Usual NP.Agent
        elif syntax_role in ROLE_LIST and phrase_type in EASY_PHRASE_TYPE_LIST:
            if primary_role is not None and syntax_role != primary_role:
                raise WrongFrameException('Roles in primary and syntax don\'t match')

            parsed_frame.append({'type': phrase_type, 'role': syntax_role})

            if restr is not None:
                parsed_frame[-1]['modifier'] = restr[1:-1]

            i, j = i+1, j+1

        elif syntax_role == 'se' and primary_parts[j] == 'se':
            pronominal = True
            i, j = i+1, j+1

        # Verbs, can also be neutral
        elif syntax_role == 'V' and primary_parts[j] == 'V':
            parsed_verb = {'type': 'V'}
            if pronominal is True:
                parsed_verb['pronominal'] = True

            if restr in ['<+middle>', '<+neutre>', '<+reflexive>', '<+reciproque>']:
                parsed_verb['restr'] = restr[2:-1]
            elif restr is not None:
                raise WrongFrameException('Restriction de verbe {} inconnue'.format(restr))

            parsed_frame.append(parsed_verb)
            i, j = i+1, j+1

        # Various words appear both in primary and syntax
        elif syntax_role in ['ADV', 'ADJ', 'LUI', 'IL', 'ensemble'] and phrase_type == syntax_role:
            parsed_frame.append({'type': phrase_type})
            i, j = i+1, j+1

        elif restr is not None and ('+Qu Pind' in restr or '+Qu Psubj' in restr):
            restr_dict = re.match(r'<\+Qu (?P<ptype>P[a-z]+)>', restr).groupdict()

            # Check len 1 set until we handle multiple prepositions in primary
            if isinstance(primary_parts[j], set):
                assert len(primary_parts[j]) == 1

            preposition = None
            if primary_parts[j] == {'de'} or primary_parts[j] == {'à'}:
                preposition = next(iter(primary_parts[j]))
                assert primary_parts[j+1] == {'ce'}
                j = j + 2

            next_phrase_type, next_primary_role = separate_phrasetype(primary_parts[j+1])

            assert primary_parts[j] == 'Qu'
            if next_primary_role is not None and syntax_role != next_primary_role:
                raise WrongFrameException('In Qu, roles in primary and syntax don\'t match')

            xml_type = {'P': 'P', 'Pind': 'PIND', 'Psubj': 'PSUBJ'}

            parsed_frame.append({
                'type': xml_type[next_phrase_type],
                'role': syntax_role,
                'introduced_by': preposition})

            i += 1
            j += 2

        elif set(primary_parts[j]) & VINF_PREPS and primary_parts[j+1] == 'V-inf':
            preposition = primary_parts[j]
            preposition_type = False
            if isinstance(syntax_parts[i], set):  # préposition
                assert syntax_parts[i] == preposition
                preposition_type = True
                i += 1

            role_plus_restr = syntax_parts[i]
            rolerestr_regex = (
                r'(?P<role>[\-\w_]+)'
                '<\+(?P<prep>\w+)?'
                '(?P<spaceafterprep>\s*)'
                'V(?P<emptysubjectrole>[\-\w_]+)-inf>')
            rolerestr_match = re.match(rolerestr_regex, role_plus_restr)
            if not rolerestr_match:
                raise WrongFrameException('Bad restriction {}'.format(role_plus_restr))

            rolerestr_dict = rolerestr_match.groupdict()
            if rolerestr_dict['prep'] and not rolerestr_dict['spaceafterprep']:
                raise WrongFrameException('Missing space in {}'.format(role_plus_restr))

            if preposition_type is False:
                assert {rolerestr_dict['prep']} == preposition


            parsed_frame.append({
                'type': 'VINF',
                'role': rolerestr_dict['role'],
                'introduced_by': preposition,
                'is_true_prep': preposition_type,
                'emptysubjectrole': rolerestr_dict['emptysubjectrole']})

            i, j = i+1, j+2

        elif set(primary_parts[j]) & {'si', 'comment', 'combien'}:
            assert len(primary_parts[j]) == 1
            primary_word = next(iter(primary_parts[j]))
            # Ensure that que also appears in syntax
            next_phrase_type, next_primary_role = separate_phrasetype(primary_parts[j+1])

            assert restr.startswith('<+{}'.format(primary_word))
            assert restr.endswith('>')
            if next_primary_role is not None:
                assert next_primary_role == syntax_role

            # Remove <+que and >
            specific_restr = restr[3+len(primary_word):-1]
            assert specific_restr in ['Pind', 'Psubj', 'P']

            parsed_frame.append({
                'type': next_phrase_type,
                'role': syntax_role,
                'introduced_by': primary_word})

            j = j+2
            i = i+1

        elif isinstance(syntax_parts[i], set):
            restr = syntax_parts[i]
            # {{+loc}}
            if len(restr) == 1 and next(iter(restr))[0] in ['+', '-']:
                class_restr = next(iter(restr))
                print('{{ ', phrase_type, class_restr, file=output)
                value = class_restr[0]
                type_ = class_restr[1:]
                parsed_frame.append({'type': 'PREP', 'type_': type_, 'Value': value})
            # {avec dans pour}
            else:
                print('set ', phrase_type, syntax_parts[i], file=output)
                parsed_frame.append({'type': 'PREP', 'Value': syntax_parts[i]})

                if len(primary_parts) > j+1 and isinstance(primary_parts[j], set) and isinstance(primary_parts[j+1], set) and primary_parts[j+1] & {'comment', 'si'}:
                    j += 1
            i += 1

        # We should have handled everything
        else:
            raise WrongFrameException('Didn\'t expect |{}| and |{}|'.format(primary_parts[j], syntax_parts[i]))

        print(parsed_frame, file=output)

    if not (i == len(syntax_parts) and j == len(primary_parts)):
        raise WrongFrameException('Match error')
    assert i == len(syntax_parts)
    assert j == len(primary_parts)

    print(parsed_frame, file=output)

    return parsed_frame

def xml_of_syntax(parsed_frame):
    syntax = ET.Element('SYNTAX')

    for frame_part in parsed_frame:
        if frame_part['type'] in ['NP', 'PP']:
            np = ET.SubElement(syntax, 'NP')
            np.set('value', frame_part['role'])
            if 'modifier' in frame_part:
                np.set('modifier', frame_part['modifier'])
            synrestrs = ET.SubElement(np, 'SYNRESTRS')
        elif frame_part['type'] == 'PREP':
            prep = ET.SubElement(syntax, 'PREP')
            selrestr_list = ET.SubElement(prep, 'SELRESTRS')
            selrestr = ET.SubElement(selrestr_list, 'SELRESTR')
            if 'type_' in frame_part:
                selrestr.set('type', frame_part['type_'])
            joined_values = ';'.join(sorted(frame_part['Value'], key=locale.strxfrm))
            selrestr.set('Value', joined_values)
        elif frame_part['type'] == 'V':
            v = ET.SubElement(syntax, 'VERB')
            if frame_part.get('pronominal') is True:
                v.set('pronominal', 'true')
            if 'restr' in frame_part:
                v.set('restr', frame_part['restr'])
        elif frame_part['type'] in ['ADV', 'ADJ', 'LUI', 'IL']:
            adv = ET.SubElement(syntax, frame_part['type'])
        elif frame_part['type'] == 'VINF':
            vinf = ET.SubElement(syntax, frame_part['type'])
            vinf.set('value', frame_part['role'])
            vinf.set('is_true_prep', 'true' if frame_part['is_true_prep'] else 'false')
            if 'np_vinf' in frame_part:
                vinf.set('np_vinf', '1')
            else:
                vinf.set('emptysubjectrole', frame_part['emptysubjectrole'])
                joined_values = ';'.join(sorted(frame_part['introduced_by'], key=locale.strxfrm))
                vinf.set('introduced_by', joined_values)
        elif frame_part['type'] in ['P', 'PIND', 'PSUBJ']:
            p = ET.SubElement(syntax, frame_part['type'])
            p.set('value', frame_part['role'])
            if frame_part['introduced_by']:
                p.set('introduced_by', frame_part['introduced_by'])
        else:
            raise WrongFrameException('Unhandled {} in {}.'.format(frame_part, parsed_frame))

    return syntax

def role_selrestr(selrestr_split):
    def tokenize(selrestr_split):
        for selrestr in selrestr_split:
            while selrestr.startswith('['):
                selrestr = selrestr[1:]
                yield '['
            yield selrestr.strip(']')
            while selrestr.endswith(']'):
                selrestr = selrestr[:-1]
                yield ']'

    # Shunting-yard algorithm
    operand_list = []
    operator_list  = []
    for token in tokenize(selrestr_split):
        if token in ['[', '&', '|']:
            operator_list.append(token)
        elif token.startswith('+') or token.startswith('-'):
            operand_list.append(ET.Element('SELRESTR', {'Value': token[0], 'type': token[1:]}))
        elif token == ']':
            operator = operator_list.pop()
            if operator != '[':
                assert operator_list.pop() == '['
                selrestr_combination = ET.Element('SELRESTRS', logic='or' if operator == '|' else 'and')
                selrestr_combination.append(operand_list.pop())
                selrestr_combination.append(operand_list.pop())
                operand_list.append(selrestr_combination)
        else:
            raise WrongFrameException('Unknown token {}'.format(token))

    assert len(operand_list) == 1
    assert len(operator_list) == 0
    return operand_list[0]


def export_subclass(db_frameset, classname=None):
    global handled_frames, total_frames

    if classname is not None:
        xml_vnclass = ET.Element('VNCLASS', {'ID': classname})
    else:
        xml_vnclass = ET.Element('VNSUBCLASS', {'ID': db_frameset.name})

    # Members
    xml_members = ET.SubElement(xml_vnclass, 'MEMBERS')
    for db_translation in VerbTranslation.all_valid(db_frameset.verbtranslation_set.all()):
        ET.SubElement(xml_members, 'MEMBER', {'name': db_translation.verb})

    # Roles
    xml_role_list = ET.SubElement(xml_vnclass, 'THEMROLES')
    for db_role in db_frameset.verbnetrole_set.all():
        role, *selrestr_split = db_role.name.split(' ')
        xml_role = ET.SubElement(xml_role_list, 'THEMROLE', {'type': role})
        if selrestr_split:
            xml_role.append(role_selrestr(selrestr_split))

    # Frames
    xml_frames = ET.SubElement(xml_vnclass, 'FRAMES')
    for db_frame in db_frameset.verbnetframe_set.filter(removed=False):
        frame = ET.SubElement(xml_frames, 'FRAME')
        ET.SubElement(frame, 'DESCRIPTION', primary=db_frame.syntax)

        # Example
        examples = ET.SubElement(frame, 'EXAMPLES')
        example = ET.SubElement(examples, 'EXAMPLE')
        example.text = db_frame.example

        # Syntax
        syntax = ET.SubElement(frame, 'SYNTAX')
        syntax.text = db_frame.roles_syntax

        total_frames += 1
        output = io.StringIO()
        print(example.text, file=output)
        try:
            parsed_frame = merge_primary_and_syntax(db_frame.syntax, db_frame.roles_syntax, output)
            syntax = xml_of_syntax(parsed_frame)
            frame.remove(frame.find('SYNTAX'))
            frame.append(syntax)
            handled_frames += 1
        except Exception as e:
            print('Oops')
            print(output.getvalue())
            print(e)
            print()
            pass

        # Semantics
        semantics = ET.SubElement(frame, 'SEMANTICS')
        semantics.text = db_frame.semantics

    if db_frameset.children.filter(removed=False):
        xml_subclass_list = ET.SubElement(xml_vnclass, 'SUBCLASSES')

    for db_childfs in db_frameset.children.filter(removed=False):
        xml_subclass = export_subclass(db_childfs)
        xml_subclass_list.append(xml_subclass)

    return xml_vnclass


def export_all_vn_classes():
    os.makedirs('export/verbenet', exist_ok=True)
    for db_levinclass in LevinClass.objects.filter(translation_status=LevinClass.STATUS_TRANSLATED):
        for db_vnclass in db_levinclass.verbnetclass_set.all():
            try:
                db_rootframeset = db_vnclass.verbnetframeset_set.get(parent=None, removed=False)
            except VerbNetFrameSet.DoesNotExist:
                continue

            print(db_vnclass)

            xml_vnclass = export_subclass(db_rootframeset, classname=db_vnclass.name)
            ET.ElementTree(xml_vnclass).write('export/verbenet/{}.xml'.format(db_vnclass.name))

    print('Handled {:.2%} of {} frames'.format(handled_frames/total_frames, total_frames))

import io
import os
from xml.etree import ElementTree as ET

from syntacticframes.models import LevinClass, VerbNetFrameSet
from role.parserole import ROLE_LIST

PHRASE_TYPE_LIST = ['NP', 'PP', 'ADJ', 'ADV', 'ADVP', 'S', 'S_INF', 'S_ING']

total_frames, handled_frames = 0, 0


def split_syntax(syntax):
    mode = 'NORMAL'
    current_part = []
    final_list = []

    for syntax_part in syntax.split():
        if syntax_part.startswith('{') and not syntax_part.endswith('}'):
            assert mode == 'NORMAL' and not current_part
            mode = 'BRACE_LIST'
            current_part = [syntax_part]
        elif syntax_part.endswith('}') and not syntax_part.startswith('{'):
            assert mode == 'BRACE_LIST'
            current_part.append(syntax_part)
            mode = 'NORMAL'
            if current_part:
                final_list.append(' '.join(current_part))
                current_part = []
            else:
                raise Exception('End of list but the list didn\'t start.')
        elif mode == 'BRACE_LIST':
            current_part.append(syntax_part)
        else:
            final_list.append(syntax_part)

    if current_part:
        raise Exception('Start of list but the list didn\'t end.')

    return final_list


def separate_phrasetype(primary_part):
    try:
        phrase_type, role = primary_part.split('.')
        if phrase_type in PHRASE_TYPE_LIST and role.title() in ROLE_LIST:
            return phrase_type, role.title()
    except ValueError:
        pass

    if primary_part.endswith('-Middle') or primary_part.endswith('-Moyen'):
        real_phrasetype = '-'.join(primary_part.split('-')[:-1])
        assert real_phrasetype in PHRASE_TYPE_LIST
        return real_phrasetype, None

    return primary_part, None


def separate_syntax(syntax_part):
    split = syntax_part.split('<')
    if len(split) == 1:
        return syntax_part, None

    if not split[1].endswith('>'):
        raise Exception('Unknown modifier {}.'.format(syntax_part))

    role = split[0]
    restr = '<{}'.format(split[1])

    return role, restr


def merge_primary_and_syntax(primary, syntax, output):
    print('{:<40} {}'.format(primary, syntax), file=output)
    primary_parts, syntax_parts = primary.split(), split_syntax(syntax)
    parsed_frame = []

    print(primary_parts, syntax_parts, file=output)

    i, j = 0, 0
    while i < len(syntax_parts) and j < len(primary_parts):
        print(i, j, syntax_parts[i], primary_parts[j], file=output)

        syntax_role, restr = separate_syntax(syntax_parts[i])
        phrase_type, primary_role = separate_phrasetype(primary_parts[j])

        print('   |{}| |{}|'.format(syntax_role, restr), file=output)
        print('   |{}| |{}|'.format(phrase_type, primary_role), file=output)

        # Usual NP.Agent
        if syntax_role in ROLE_LIST and phrase_type in PHRASE_TYPE_LIST:
            if primary_role is not None:
                assert syntax_role == primary_role
            parsed_frame.append({'type': phrase_type, 'role': syntax_role})
            i, j = i+1, j+1

        # Verbs, can also be neutral
        elif syntax_parts[i] == 'V' and primary_parts[j] == 'V':
            parsed_frame.append({'type': 'V'})
            i, j = i+1, j+1
        elif syntax_parts[i] == 'V<+neutre>' and primary_parts[j] == 'V':
            parsed_frame.append({'type': 'V', 'restr': 'neutre'})
            i, j = i+1, j+1

        # Various words appear both in primary and syntax
        elif syntax_role in ['ADV', 'ADVP', 'Adj', 'se', 'CL-lui'] and phrase_type == syntax_role:
            parsed_frame.append({'type': phrase_type})
            i, j = i+1, j+1

        # Redundancy between NP V que S and Agent V Theme<+que_comp>
        elif primary_parts[j] in ['que', 'de', 'comment']:
            primary_word = primary_parts[j]
            # Ensure that que also appears in syntax
            next_phrase_type, next_primary_role = separate_phrasetype(primary_parts[j+1])

            assert restr.startswith('<+{}_'.format(primary_word)) and restr.endswith('>')
            if next_primary_role is not None:
                assert next_primary_role == syntax_role

            # Remove <+que and >
            specific_restr = restr[3+len(primary_word):-1]

            assert specific_restr in ['comp', 'Psubj', 'Vinf', 'extract']

            parsed_frame.append({
                'type': next_phrase_type, 'role': syntax_role,
                'introduced_by': primary_word, 'restr': specific_restr})

            j = j+2
            i = i+1

        # Handle special syntax like {{+loc}} or {avec dans pour}
        elif syntax_parts[i].startswith('{') and syntax_parts[i].endswith('}'):
            parsed_frame.append({'type': 'special', 'content': syntax_parts[i]})
            i += 1

        # We should have handled everything
        else:
            raise Exception('Didn\'t expect {} and {}'.format(primary_parts[j], syntax_parts[i]))

        print(parsed_frame, file=output)

    assert i == len(syntax_parts)
    assert j == len(primary_parts)

    print(parsed_frame, file=output)

    return parsed_frame


def export_subclass(db_frameset, classname=None):
    global handled_frames, total_frames

    if classname is not None:
        xml_vnclass = ET.Element('VNCLASS', {'ID': classname})
    else:
        xml_vnclass = ET.Element('VNSUBCLASS', {'ID': db_frameset.name})

    # Members
    xml_members = ET.SubElement(xml_vnclass, 'MEMBERS')
    for db_translation in db_frameset.verbtranslation_set.all():
        if db_translation.category == 'both':
            ET.SubElement(xml_members, 'MEMBER', {'name': db_translation.verb})

    # Roles
    xml_roles = ET.SubElement(xml_vnclass, 'THEMROLES')
    for db_role in db_frameset.verbnetrole_set.all():
        role, *selrestrs = db_role.name.split(' ')
        ET.SubElement(
            xml_roles, 'THEMROLE',
            {'type': role, 'selrestrs': ' '.join(selrestrs)})

    # Frames
    xml_frames = ET.SubElement(xml_vnclass, 'FRAMES')
    for db_frame in db_frameset.verbnetframe_set.filter(removed=False):
        frame = ET.SubElement(xml_frames, 'FRAME')
        frame.set('primary', db_frame.syntax)
        # Example
        examples = ET.SubElement(frame, 'EXAMPLES')
        example = ET.SubElement(examples, 'EXAMPLE')
        example.text = db_frame.example
        # Syntax
        syntax = ET.SubElement(frame, 'SYNTAX')
        syntax.text = db_frame.roles_syntax
        # Semantics
        semantics = ET.SubElement(frame, 'SEMANTICS')
        semantics.text = db_frame.semantics

        total_frames += 1
        output = io.StringIO()
        print(example.text, file=output)
        try:
            parsed_frame = merge_primary_and_syntax(db_frame.syntax, db_frame.roles_syntax, output)
            handled_frames += 1
        except Exception as e:
            print(output.getvalue())
            print(e)
            print()
            pass

    if db_frameset.children.filter(removed=False):
        xml_subclass_list = ET.SubElement(xml_vnclass, 'SUBCLASSES')

    for db_childfs in db_frameset.children.filter(removed=False):
        xml_subclass = export_subclass(db_childfs)
        xml_subclass_list.append(xml_subclass)

    return xml_vnclass


def export_all_vn_classes():
    os.makedirs('export/verbenet', exist_ok=True)
    for db_levinclass in LevinClass.objects.filter(is_translated=True):
        for db_vnclass in db_levinclass.verbnetclass_set.all():
            if db_vnclass.name in ['hold-15.1']:
                continue

            try:
                db_rootframeset = db_vnclass.verbnetframeset_set.get(parent=None, removed=False)
            except VerbNetFrameSet.DoesNotExist:
                continue

            print(db_vnclass)

            xml_vnclass = export_subclass(db_rootframeset, classname=db_vnclass.name)
            ET.ElementTree(xml_vnclass).write('export/verbenet/{}.xml'.format(db_vnclass.name))

    print('Handled {:.2%} of frames'.format(handled_frames/total_frames))

import os
from xml.etree import ElementTree as ET

from syntacticframes.models import LevinClass 

def export_subclass(db_frameset, tagname=None):
    xml_vnclass = ET.Element(tagname)
    xml_vnclass.set('ID', db_frameset.name)

    # Members
    xml_members = ET.SubElement(xml_vnclass, 'MEMBERS')
    for db_translation in db_frameset.verbtranslation_set.all():
        if db_translation.category == 'both':
            ET.SubElement(xml_members, 'MEMBER', {'name': db_translation.verb})

    # Roles
    xml_roles = ET.SubElement(xml_vnclass, 'THEMROLES')
    for db_role in db_frameset.verbnetrole_set.all():
        ET.SubElement(xml_roles, 'THEMROLE', {'type': db_role.name})

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
        semantics = ET.SubElement(frame, 'SYNTAX')
        semantics.text = db_frame.semantics

    if db_frameset.children.all():
        xml_subclass_list = ET.SubElement(xml_vnclass, 'SUBCLASSES')
    for db_childfs in db_frameset.children.all():
        xml_subclass = export_subclass(db_childfs, tagname='VNSUBCLASS')
        xml_subclass_list.append(xml_subclass)

    return xml_vnclass


def export_all_vn_classes():
    os.makedirs('export/verbenet', exist_ok=True)
    for db_levinclass in LevinClass.objects.filter(is_translated=True):
        for db_vnclass in db_levinclass.verbnetclass_set.all():
            db_rootframeset = db_vnclass.verbnetframeset_set.get(parent=None)
            xml_vnclass = export_subclass(db_rootframeset, tagname='VNCLASS')
            ET.ElementTree(xml_vnclass).write('export/verbenet/{}.xml'.format(db_vnclass.name))

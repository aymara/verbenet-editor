import re


# http://verbs.colorado.edu/verb-index/vn/reference.php
ROLE_LIST = ['Agent', 'Asset', 'Attribute', 'Beneficiary', 'Cause', 'Co-Agent',
'Co-Patient', 'Co-Theme', 'Destination', 'Experiencer', 'Extent', 'Goal',
'Initial_Location', 'Instrument', 'Location', 'Material', 'Patient', 'Pivot',
'Predicate', 'Product', 'Recipient', 'Reflexive', 'Result', 'Source',
'Stimulus', 'Theme', 'Time', 'Topic', 'Trajectory', 'Value']


class ParsedRole(object):
    """
    Stores role name and selection restrictions
    """
    def __init__(self, role_str):
        match = re.match('(\w+)( )?(.+)?', role_str)
        self.role, space, selrestrs_str = match.groups()

        assert self.role in ROLE_LIST

        if selrestrs_str is None:
            assert space is None
            self.selrestrs = {}
        else:
            assert space == ' '
            self.selrestrs = self.selrestrs_tree(selrestrs_str)

    def split_selrestr(self, selrestrs_str):
        nest_count = 0
        selrestrs_list = ['']
        operator = None

        for c in selrestrs_str:
            if c == '[':
                nest_count += 1
            elif c == ']':
                nest_count -= 1

            if nest_count == 0 and c == ' ':
                continue
            elif nest_count == 0 and c == '&':
                assert operator is None or operator == '&'
                operator = '&'
                selrestrs_list.append('')
            elif nest_count == 0 and c == '|':
                assert operator is None or operator == '|'
                operator = '|'
                selrestrs_list.append('')
            else:
                selrestrs_list[-1] += c

        return operator, selrestrs_list

    def selrestrs_tree(self, selrestrs_str):
        if selrestrs_str[0] == '[' and selrestrs_str[-1] == ']':
            selrestrs_str = selrestrs_str[1:-1]  # removing []
        logic, selrestrs_list = self.split_selrestr(selrestrs_str)

        if logic:
            if '[' and ']' in selrestrs_str:
                selrestrs = {
                    'logic': logic,
                    'children': [
                        self.selrestrs_tree(c) for c in selrestrs_list]}
            else:
                for c in selrestrs_list:
                    assert c[0] in ['-', '+']
                selrestrs = {'logic': logic, 'children': selrestrs_list}
        else:
            assert selrestrs_str[0] in ['-', '+']
            selrestrs = selrestrs_str

        return selrestrs

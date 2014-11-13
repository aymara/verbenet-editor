import traceback

from django.core.mail import mail_managers

class UnknownClassException(Exception):
    def __init__(self, partial_name):
        self.partial_name = partial_name

    def __str__(self):
        return 'L\'entrée "{}" n\'existe pas.'.format(self.partial_name)

class SyntaxErrorException(Exception):
    def __init__(self, error, name):
        self.error = error
        self.name = name

    def __str__(self):
        return '{} : {}'.format(self.name, self.error)

class UnknownErrorException(Exception):
    """
    Errors that were not identified precisely. They make FrenchMapping.__init__ fail.
    """
    def __init__(self, resource, name):
        self.resource = resource
        self.name = name

    def __str__(self):
        return 'Erreur : {} ({}) invalide'.format(self.name, self.resource)

class FrenchMapping(object):
    """
    Stores a mapping like 'L3f ou E3c', '38LD et (37M1 ou 37M2)'
    """
    def __init__(self, resource, name):
        self.resource = resource

        # Used to check that every name exists
        self.reference_list = ladl_list if self.resource == 'LADL' else lvf_list

        if name is None: name = ''

        try:
            token_list = FrenchMapping._tokenize(self.resource, name)
            self.parse_tree = FrenchMapping._parse(token_list, self.reference_list)
        except (SyntaxErrorException, UnknownClassException) as e:
            raise e
        except:   # We don't want to send anything else than our errors
            mail_managers('Unknown error for {}'.format(name), traceback.format_exc())
            raise UnknownErrorException(resource, name)

    @staticmethod
    def _tokenize(resource, name):
        token_list = []
        current_token = ''
        i = 0

        while i < len(name):
            c = name[i]

            if c == ' ' and current_token:
                token_list.append(current_token)
                current_token = ''
            elif c == '[':
                if name[i-1] == ' ':
                    raise SyntaxErrorException('Pas d\'espace après {}'.format(token_list[-1]), name)
                else:
                    if current_token:
                        token_list.append(current_token)
                        current_token = ''

                    token_list.append(c)  # [

                    j = i + 2
                    bracket_stack_len = 0
                    while not(name[j] == ']' and bracket_stack_len == 0):
                        if len(name) <= j+1:
                            raise SyntaxErrorException('Crochet ] manquant', name)

                        if name[j] == '[':
                            bracket_stack_len += 1
                        elif name[j] == ']':
                            bracket_stack_len -= 1
                        j += 1

                    if ' et ' in name[i+1:j] and ' ou ' in name[i+1:j]:
                        raise SyntaxErrorException('Combinaison de "ou" et "et" dans la restriction {}', name[i+1:j])
                    elif ' et ' in name[i+1:j]:
                        restriction_list = name[i+1:j].split(' et ')
                        restriction_operator = 'et'
                    elif ' ou ' in name[i+1:j]:
                        restriction_list = name[i+1:j].split(' ou ')
                        restriction_operator = 'ou'
                    else:
                        restriction_list = [name[i+1:j]]
                        restriction_operator = None

                    for part in restriction_list:
                            if part[0] not in ['-', '+']:
                                raise SyntaxErrorException('+ ou - requis après un crochet', name)
                            token_list.append(part[0])
                            token_list.append(part[1:])
                            token_list.append(restriction_operator)
                    token_list.pop()

                    token_list.append(name[j])  # ]
                    i = j + 1
            elif c in ['(', ')']:
                if current_token:
                    token_list.append(current_token)
                    current_token = ''
                token_list.append(c)
            else:
                current_token += c

            i += 1

        if current_token:
            token_list.append(current_token)
            current_token = ''

        for i, token in enumerate(token_list):
            if token == 'et':
                token_list[i] = 'and'
            elif token == 'ou':
                token_list[i] = 'or'

        return token_list

    @staticmethod
    def _parse(token_list, reference_list):
        if not token_list:
            return {}
        elif len(token_list) == 1:
            class_name = token_list[0]
            if class_name in FORGET_LIST:
                return {}
            if not class_name in reference_list:
                raise UnknownClassException(class_name)
            return {'leaf': (class_name, None)}
        else:
            parse_tree = {'children': []}
            i = 0
            last_token = None
            while i < len(token_list):
                if token_list[i] in ['and', 'or']:
                    if 'operator' in parse_tree and parse_tree['operator'] != token_list[i]:
                        raise SyntaxErrorException('Combinaison de "ou" et "et"', " ".join(token_list))
                    parse_tree['operator'] = token_list[i]
                elif token_list[i] == '(':
                    j = i
                    while token_list[j] != ')':
                        j += 1
                    parse_tree['children'].append(FrenchMapping._parse(token_list[i+1:j], reference_list))
                    i = j
                elif token_list[i] == '[':
                    class_name, restriction = parse_tree['children'][-1]['leaf']
                    assert restriction == None
                    if not class_name in reference_list:
                        raise UnknownClassException(class_name)

                    restr_op_list = []
                    operator = None
                    i += 1
                    while token_list[i] != ']':
                        if token_list[i] in ['and', 'or']:
                            operator = token_list[i]
                            i += 1
                        else:
                            restr_op_list.append(token_list[i] + token_list[i+1])
                            i += 2

                    restr_op_list = [operator] + restr_op_list

                    parse_tree['children'][-1]['leaf'] = (class_name, restr_op_list)
                else:
                    if last_token not in [None, 'and', 'or', '(']:
                        raise SyntaxErrorException('Opérateur manquant.', ' '.join(token_list))
                    parse_tree['children'].append(FrenchMapping._parse([token_list[i]], reference_list))

                last_token =  token_list[i]
                i += 1

            if 'children' in parse_tree and not 'operator' in parse_tree:
                assert len(parse_tree['children']) == 1
                return parse_tree['children'][0]

            return parse_tree

    def infix(self):
        def infix_aux(parse_tree):
            french_operators = {'or': 'ou', 'and': 'et'}
            if not parse_tree:
                return ''
            elif 'leaf' in parse_tree:
                class_name, restr = parse_tree['leaf']
                if restr is not None:
                    if restr[0]:
                        restr_string = ' {} '.format(french_operators[restr[0]]).join(restr[1:])
                    else:
                        assert len(restr) == 2
                        restr_string = restr[1]
                    return '{}[{}]'.format(class_name, restr_string)
                else:
                    return class_name
            elif 'operator' in parse_tree:
                children_infix = [infix_aux(c) for c in parse_tree['children']]
                return '({} {})'.format(parse_tree['operator'], ' '.join(children_infix))
            else:
                assert False

        return infix_aux(self.parse_tree)

    def flat_parse(self):
        """
        "A ou B" return [('A', True), ('ou', False), ('B', True)]
        """
        def flat_parse_aux(parse_tree):
            french_operators = {'or': 'ou', 'and': 'et'}
            if not parse_tree:
                return [('∅', None)]
            elif 'leaf' in parse_tree:
                class_name, restr = parse_tree['leaf']
                if restr is not None:
                    if restr[0]:
                        space_french_operator = ' {} '.format(french_operators[restr[0]])
                        restr_string = space_french_operator.join(restr[1:])
                    else:
                        assert len(restr) == 2
                        restr_string = restr[1]
                    return [('{}[{}]'.format(class_name, restr_string), class_name)]
                else:
                    return [(class_name, class_name)]
            elif 'operator' in parse_tree:
                parts = [('(', None)]
                if parse_tree['children']:
                    for c in parse_tree['children']:
                        parts.extend(flat_parse_aux(c))
                        parts.append((french_operators[parse_tree['operator']], None))
                    parts.pop()  # remove last unneeded operator
                parts.append((')', None))
                return parts

        flat_parts = flat_parse_aux(self.parse_tree)

        if len(flat_parts) > 1:
            flat_parts = flat_parts[1:-1]
        return flat_parts
                

# Module level constants


FORGET_LIST = ['?', '', '-', '*']


ladl_list = [ 
    # verbes
    '1', '2', '2T', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13',
    '14', '15', '16', '18', '31H', '31R', '32A', '32C', '32CL', '32CV', '32D',
    '32H', '32NM', '32PL', '32R1', '32R2', '32R3', '32RA', '33', '34L0', '35L',
    '35LD', '35LR', '35LS', '35R', '35RR', '35S', '35ST', '36DT', '36R', '36S',
    '36SL', '37E', '37M1', '37M2', '37M3', '37M4', '37M5', '37M6', '38L', '38L0',
    '38L1', '38LD', '38LH', '38LHD', '38LHR', '38LHS', '38LR', '38LS', '38PL',
    '38R', '38RR', '39',
    # figees
    'C_31i', 'C_a1', 'C_a12', 'C_a1p2', 'C_a1pn', 'C_anp2', 'C_c0', 'C_c0e',
    'C_c0q', 'C_c1d', 'C_c1dpn', 'C_c1g', 'C_c1gpn', 'C_c1i', 'C_c1ipn', 'C_c1p2',
    'C_c1r', 'C_c1rpn', 'C_c5', 'C_c5c1', 'C_c6', 'C_c7', 'C_c8', 'C_cadv',
    'C_can', 'C_cdn', 'C_cff', 'C_cnp2', 'C_cp1', 'C_cpn', 'C_cpp', 'C_cppn',
    'C_cppq', 'C_cpq', 'C_cv', 'C_e01', 'C_e0p1', 'C_e1', 'C_e1hc', 'C_e1pn',
    'C_eapc', 'C_ec0', 'C_edn', 'C_enpc', 'C_epa', 'C_epac', 'C_epc', 'C_epca',
    'C_epcdc', 'C_epcdn', 'C_epcpc', 'C_epcpn', 'C_epcpq', 'C_epdetc', 'C_fc',
    'C_fca', 'C_fcan', 'C_fcana', 'C_fcann', 'C_fcn', 'C_fcpn', 'C_fcpna',
    'C_fcpnn', 'C_ya', 'C_z1', 'C_z5d', 'C_z5p', 'C_zp', 'C_zs']


lvf_list = [
    'C', 'C1', 'C1a', 'C1a.1', 'C1a.2', 'C1a.3', 'C1a.4', 'C1a.5', 'C1b', 'C1c',
    'C1c.1', 'C1c.2', 'C1c.3', 'C1d', 'C1d.1', 'C1d.2', 'C1d.3', 'C1d.4', 'C1d.5',
    'C1e', 'C1e.1', 'C1e.2', 'C1f', 'C1f.1', 'C1f.2', 'C1f.3', 'C1f.4', 'C1f.5',
    'C1g', 'C1h', 'C1h.1', 'C1h.2', 'C1i', 'C1i.1', 'C1i.2', 'C1i.3', 'C1j',
    'C1j.1', 'C1j.2', 'C1j.3', 'C2', 'C2a', 'C2a.1', 'C2a.2', 'C2a.3', 'C2b',
    'C2b.1', 'C2b.2', 'C2c', 'C2d', 'C2d.1', 'C2d.2', 'C2d.3', 'C2d.4', 'C2e',
    'C2e.1', 'C2e.2', 'C2f', 'C2f.1', 'C2f.2', 'C2f.3', 'C2g', 'C2g.1', 'C2g.2',
    'C2h', 'C2h.1', 'C2h.2', 'C2i', 'C2i.1', 'C2i.2', 'C2j', 'C2j.1', 'C2j.2',
    'C2k', 'C2k.1', 'C2k.2', 'C2k.3', 'C2k.4', 'C3a', 'C3a.1', 'C3a.2', 'C3b',
    'C3b.1', 'C3b.2', 'C3c', 'C3d', 'C3d.1', 'C3d.2', 'C3d.3', 'C3e', 'C3f',
    'C3f.1', 'C3f.2', 'C4', 'C4a', 'C4b', 'C4b.1', 'C4b.2', 'C4b.3', 'C4b.4',
    'C4b.5', 'C4c', 'C4c.1', 'C4c.2', 'C4d', 'C4d.1', 'C4d.2', 'C4d.3', 'D', 'D1',
    'D1a', 'D1a.1', 'D1a.2', 'D1b', 'D1b.1', 'D1b.2', 'D1c', 'D1c.1', 'D1c.2',
    'D1c.3', 'D1d', 'D1d.1', 'D1d.2', 'D2', 'D2a', 'D2b', 'D2c', 'D2c.1', 'D2c.2',
    'D2c.3', 'D2d', 'D2d.1', 'D2d.2', 'D2d.3', 'D2e', 'D3', 'D3a', 'D3a.1',
    'D3a.2', 'D3a.3', 'D3b', 'D3b.1', 'D3b.2', 'D3c', 'D3c.1', 'D3c.2', 'D3d',
    'D3d.1', 'D3d.2', 'D3d.3', 'D3e', 'D3e.1', 'D3e.2', 'D3f', 'D3f.1', 'D3f.2',
    'E', 'E1', 'E1a', 'E1a.1', 'E1a.2', 'E1a.3', 'E1b', 'E1b.1', 'E1b.2', 'E1c',
    'E1c.1', 'E1c.2', 'E1d', 'E1d.1', 'E1d.2', 'E1d.3', 'E1d.4', 'E1e', 'E1e.1',
    'E1e.2', 'E1e.3', 'E1f', 'E1f.1', 'E1f.2', 'E1f.3', 'E1g', 'E1g.1', 'E1g.2',
    'E2', 'E2a', 'E2a.1', 'E2a.2', 'E2b', 'E2c', 'E2c.1', 'E2c.2', 'E2c.3',
    'E2c.4', 'E2d', 'E2d.1', 'E2d.2', 'E2d.3', 'E2d.4', 'E2d.5', 'E2e', 'E3',
    'E3a', 'E3a.1', 'E3a.2', 'E3a.3', 'E3b', 'E3c', 'E3d', 'E3d.1', 'E3d.2',
    'E3d.3', 'E3d.4', 'E3e', 'E3f', 'E3f.1', 'E3f.2', 'E3f.3', 'E3f.4', 'E3f.5',
    'E4', 'E4a', 'E4b', 'E4b.1', 'E4b.2', 'E4c', 'E4c.1', 'E4c.2', 'E4c.3',
    'E4c.4', 'E4c.5', 'E4c.6', 'E4d', 'E4d.1', 'E4d.2', 'E4e', 'E4e.1', 'E4e.2',
    'E4e.3', 'E4e.4', 'E4f', 'F', 'F1', 'F1a', 'F1a.1', 'F1a.2', 'F1b', 'F1b.1',
    'F1b.2', 'F1b.3', 'F1c', 'F1d', 'F1d.1', 'F1d.2', 'F1e', 'F1e.1', 'F1e.2',
    'F1e.3', 'F1f', 'F1f.1', 'F1f.2', 'F2', 'F2a', 'F2a.1', 'F2a.2', 'F2a.3',
    'F2b', 'F2b.1', 'F2b.2', 'F2c', 'F2c.1', 'F2c.2', 'F2d', 'F2d.1', 'F2d.2',
    'F2d.3', 'F2e', 'F3', 'F3a', 'F3a.1', 'F3a.2', 'F3b', 'F3c', 'F3c.1', 'F3c.2',
    'F3c.3', 'F3d', 'F3d.1', 'F3d.2', 'F4', 'F4a', 'F4a.1', 'F4a.2', 'F4a.3',
    'F4a.4', 'F4a.5', 'F4b', 'F4b.1', 'F4b.2', 'F4c', 'H', 'H1', 'H1a', 'H1a.1',
    'H1a.2', 'H1b', 'H1b.1', 'H1b.2', 'H1b.3', 'H1c', 'H1c.1', 'H1c.2', 'H1d',
    'H2', 'H2a', 'H2a.1', 'H2a.2', 'H2b', 'H2c', 'H2d', 'H2d.1', 'H2d.2', 'H2e',
    'H2e.1', 'H2e.2', 'H2f', 'H2f.1', 'H2f.2', 'H2g', 'H2h', 'H2h.1', 'H2h.2',
    'H2i', 'H2i.1', 'H2i.2', 'H2j', 'H2j.1', 'H2j.2', 'H2k', 'H3', 'H3a', 'H3a.1',
    'H3a.2', 'H3a.3', 'H3b', 'H3b.1', 'H3b.2', 'H3c', 'H3c.1', 'H3c.2', 'H3c.3',
    'H3d', 'H3e', 'H3f', 'H3f.1', 'H3f.2', 'H3g', 'H4', 'H4a', 'H4a.1', 'H4a.2',
    'H4b', 'H4b.1', 'H4b.2', 'H4c', 'H4c.1', 'H4c.2', 'H4d', 'L', 'L1', 'L1a',
    'L1a.1', 'L1a.2', 'L1a.3', 'L1b', 'L1b.1', 'L1b.2', 'L1b.3', 'L2', 'L2a',
    'L2a.1', 'L2a.2', 'L2b', 'L2b.1', 'L2b.2', 'L2b.3', 'L3', 'L3a', 'L3a.1',
    'L3a.2', 'L3a.3', 'L3b', 'L3b.1', 'L3b.2', 'L3b.3', 'L3b.4', 'L3b.5', 'L3b.6',
    'L4', 'L4a', 'L4a.1', 'L4a.2', 'L4a.3', 'L4a.4', 'L4b', 'L4b.1', 'L4b.2',
    'L4b.3', 'L4b.4', 'L4b.5', 'L4b.6', 'L4b.7', 'L4b.8', 'L4b.9', 'M', 'M1',
    'M1a', 'M1a.1', 'M1a.2', 'M1a.3', 'M1a.4', 'M1a.5', 'M1a.6', 'M1b', 'M1b.1',
    'M1b.2', 'M1b.3', 'M1c', 'M1c.1', 'M1c.2', 'M1c.3', 'M1c.4', 'M2', 'M2a',
    'M2a.1', 'M2a.2', 'M2b', 'M2b.1', 'M2b.2', 'M2b.3', 'M2b.4', 'M2b.5', 'M2b.6',
    'M2c', 'M2c.1', 'M2c.2', 'M2c.3', 'M3', 'M3a', 'M3a.1', 'M3a.2', 'M3a.3',
    'M3b', 'M3b.1', 'M3b.2', 'M3c', 'M4', 'M4a', 'M4a.1', 'M4a.2', 'M4a.3',
    'M4a.4', 'M4a.5', 'M4b', 'M4b.1', 'M4b.2', 'N', 'N1', 'N1a', 'N1a.1', 'N1a.2',
    'N1b', 'N1b.1', 'N1b.2', 'N1c', 'N1c.1', 'N1c.2', 'N1c.3', 'N1c.4', 'N1c.5',
    'N1d', 'N1d.1', 'N1d.2', 'N2', 'N2a', 'N2a.1', 'N2a.2', 'N2a.3', 'N2a.4',
    'N2a.5', 'N2b', 'N2b.1', 'N2b.2', 'N2b.3', 'N3', 'N3a', 'N3a.1', 'N3a.2',
    'N3b', 'N3b.1', 'N3b.2', 'N3c', 'N3d', 'N3d.1', 'N3d.2', 'N3d.3', 'N3d.4',
    'N4', 'N4a', 'N4b', 'N4b.1', 'N4b.2', 'P', 'P1', 'P1a', 'P1b', 'P1c', 'P1c.1',
    'P1c.2', 'P1c.3', 'P1d', 'P1d.1', 'P1d.2', 'P1d.3', 'P1e', 'P1e.1', 'P1e.2',
    'P1f', 'P1f.1', 'P1f.2', 'P1f.3', 'P1f.4', 'P1g', 'P1g.1', 'P1g.2', 'P1h',
    'P1h.1', 'P1h.2', 'P1i', 'P1i.1', 'P1i.2', 'P1i.3', 'P1j', 'P2', 'P2a',
    'P2a.1', 'P2a.2', 'P2b', 'P2c', 'P2c.1', 'P2c.2', 'P2c.3', 'P3', 'P3a', 'P3b',
    'P3b.1', 'P3b.2', 'P3c', 'P3c.1', 'P3c.2', 'R', 'R1', 'R1a', 'R1a.1', 'R1a.2',
    'R1a.3', 'R1a.4', 'R2', 'R2a', 'R2a.1', 'R2a.2', 'R2a.3', 'R3', 'R3a', 'R3a.1',
    'R3a.2', 'R3a.3', 'R3b', 'R3b.1', 'R3b.2', 'R3c', 'R3c.1', 'R3c.2', 'R3c.3',
    'R3c.4', 'R3c.5', 'R3c.6', 'R3d', 'R3d.1', 'R3d.2', 'R3e', 'R3e.1', 'R3e.2',
    'R3e.3', 'R3e.4', 'R3f', 'R3f.1', 'R3f.2', 'R3f.3', 'R3f.4', 'R3f.5', 'R3g',
    'R3h', 'R3i', 'R3i.1', 'R3i.2', 'R3i.3', 'R3j', 'R4', 'R4a', 'R4a.1', 'R4a.2',
    'R4b', 'R4b.1', 'R4b.2', 'R4c', 'R4c.1', 'R4c.2', 'R4c.3', 'R4c.4', 'R4d',
    'R4d.1', 'R4d.2', 'R4e', 'R4e.1', 'R4e.2', 'R4e.3', 'S', 'S1', 'S1a', 'S1a.1',
    'S1a.2', 'S1a.3', 'S1b', 'S1b.1', 'S1b.2', 'S1c', 'S1c.1', 'S1c.2', 'S1c.3',
    'S2', 'S2a', 'S2a.1', 'S2a.2', 'S2a.3', 'S2b', 'S2b.1', 'S2b.2', 'S2c', 'S2d',
    'S2d.1', 'S2d.2', 'S2d.3', 'S2e', 'S2e.1', 'S2e.2', 'S2f', 'S2f.1', 'S2f.2',
    'S3', 'S3a', 'S3a.1', 'S3a.2', 'S3b', 'S3b.1', 'S3b.2', 'S3c', 'S3c.1',
    'S3c.2', 'S3d', 'S3d.1', 'S3d.2', 'S3e', 'S3f', 'S3f.1', 'S3f.2', 'S3g',
    'S3g.1', 'S3g.2', 'S3g.3', 'S3h', 'S3i', 'S3j', 'S3j.1', 'S3j.2', 'S3j.3',
    'S3k', 'S3k.1', 'S3k.2', 'S3k.3', 'S4', 'S4a', 'S4a.1', 'S4a.2', 'S4b',
    'S4b.1', 'S4b.2', 'S4c', 'S4d', 'S4e', 'S4e.1', 'S4e.2', 'S4f', 'S4f.1',
    'S4f.2', 'S4g', 'S4h', 'S4h.1', 'S4h.2', 'S4h.3', 'S4i', 'T', 'T1', 'T1a',
    'T1a.1', 'T1a.2', 'T1a.3', 'T1b', 'T1c', 'T2', 'T2a', 'T2a.1', 'T2a.2', 'T2b',
    'T2c', 'T2d', 'T2e', 'T2e.1', 'T2e.2', 'T2e.3', 'T2e.4', 'T3', 'T3a', 'T3b',
    'T3c', 'T3d', 'T3e', 'T3e.1', 'T3e.2', 'T3f', 'T3f.1', 'T3f.2', 'T3f.3',
    'T3f.4', 'T3f.5', 'T4', 'T4a', 'T4b', 'T4c', 'T4d', 'T4d.1', 'T4d.2', 'T4e',
    'T4e.1', 'T4e.2', 'T4e.3', 'T4e.4', 'T4e.5', 'U', 'U1', 'U1a', 'U1a.1',
    'U1a.2', 'U1a.3', 'U1b', 'U1b.1', 'U1b.2', 'U1b.3', 'U1b.4', 'U1c', 'U2',
    'U2a', 'U2a.1', 'U2a.2', 'U2a.3', 'U2a.4', 'U2b', 'U2b.1', 'U2b.2', 'U2b.3',
    'U2b.4', 'U2c', 'U2c.1', 'U2c.2', 'U2c.3', 'U2c.4', 'U2c.5', 'U3', 'U3a',
    'U3a.1', 'U3a.2', 'U3b', 'U3b.1', 'U3b.2', 'U3b.3', 'U3c', 'U3c.1', 'U3c.2',
    'U3c.3', 'U3d', 'U3d.1', 'U3d.2', 'U3d.3', 'U3e', 'U3e.1', 'U3e.2', 'U3f',
    'U3f.1', 'U3f.2', 'U4', 'U4a', 'U4a.1', 'U4a.2', 'U4b', 'U4b.1', 'U4b.2',
    'U4b.3', 'U4c', 'U4c.1', 'U4c.2', 'U4c.3', 'U4c.4', 'U4c.5', 'U4d', 'U4d.1',
    'U4d.2', 'X', 'X1', 'X1a', 'X1a.1', 'X1a.2', 'X1a.3', 'X1a.4', 'X1a.5', 'X2',
    'X2a', 'X3', 'X3a', 'X3a.1', 'X3a.2', 'X3a.3', 'X4', 'X4a', 'X4a.1', 'X4a.2',
    'X4a.3']

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Frames, arguments and predicates."""

import unittest
import verbnetprepclasses


class VerbnetFrame:
    """A representation of a frame syntaxic structure

    :var structure: String list containing a VerbNet-style representation of
                    the structure
    :var roles: List of the possible VerbNet roles for each structure's slot
    :var num_slots: Number of argument slots in :structure
    :var verbnet_class: For VerbNet-extracted frames, the class number, eg.
                        9.10
    :var predicate: For FrameNet-extracted frames, the predicate

    """

    slot_types = {
        "subject": "SBJ", "object": "OBJ",
        "indirect_object": "OBJI", "prep_object": "PPOBJ"
    }

    phrase_replacements = {
        "N": "NP", "Poss": "NP", "QUO": "S",
        "Sinterrog": "S", "Sfin": "S",
        "VPbrst": "S", "VPing": "S_ING", "VPto": "to S"
    }

    def __init__(self, structure, roles, vnclass=None, predicate=None):
        self.structure = structure
        self.predicate = predicate

        # Transform "a" in {"a"} and keep everything else unchanged
        self.roles = [{x} if isinstance(x, str) else x for x in roles]
        self.slot_preps = []
        self.slot_types = []
        self.headwords = []

        self.num_slots = len(self.roles)

        # Used to retrieve vnclass and map roles to framenet roles
        self.vnclass = vnclass

        self.compute_slot_types()

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.structure == other.structure and
            self.roles == other.roles and
            self.num_slots == other.num_slots and
            self.predicate == other.predicate)

    def __repr__(self):
        return "VerbnetFrame({}, {}, {}, {})".format(
               self.predicate, self.structure, self.roles, self.vnclass)

    def compute_slot_types(self):
        """Build the list of slot types for this frame"""

        # Re-initialize in case we are called several times
        self.slot_types, self.slot_preps = [], []

        # The next slot we are expecting :
        # always subject before the verb, object immediatly after the verb
        # and indirect_object after we encoutered a slot for object
        next_expected = VerbnetFrame.slot_types["subject"]
        # If last structure element was a preposition, this will be filled
        # with the preposition and will "overwrite" :next_expected
        preposition = ""

        for element in self.structure:
            if element == "V":
                next_expected = VerbnetFrame.slot_types["object"]
            elif element[0].isupper():  # If this is a slot
                if preposition != "":
                    self.slot_types.append(VerbnetFrame.slot_types["prep_object"])
                    self.slot_preps.append(preposition)
                    preposition = ""
                else:
                    self.slot_types.append(next_expected)
                    self.slot_preps.append(None)
                    if next_expected == VerbnetFrame.slot_types["object"]:
                        next_expected = VerbnetFrame.slot_types["indirect_object"]
            elif isinstance(element, list) or element in verbnetprepclasses.all_preps:
                preposition = element

    @staticmethod
    def _is_a_slot(elem):
        """Tell wether an element represent a slot

        :param elem: The element.
        :type elem: str.
        :returns: bool -- True if elem represents a slot, False otherwise
        """

        return elem[0].isupper() and elem != "V"

    @staticmethod
    def _is_a_match(elem1, elem2):
        """Tell wether two elements can be considered as a match

        :param elem1: first element.
        :type elem1: str.
        :param elem2: second element.
        :type elem2: str.
        :returns: bool -- True if this is a match, False otherwise
        """

        return ((isinstance(elem2, list) and elem1 in elem2) or
            elem1 == elem2)

    @staticmethod
    def build_from_frame(frame):
        """Build a VerbNet frame from a Frame object

        :param frame: The original Frame.
        :type frame: Frame.
        :returns: VerbnetFrame -- the built frame, without the roles
        """

        # The main job is to build the VerbNet structure representation
        # from the Frame object data

        num_slots = 0

        # First, delete everything that is before or after the frame
        begin = frame.predicate.begin
        end = frame.predicate.end

        for argument in frame.args:
            if not argument.instanciated:
                continue
            num_slots += 1
            if argument.begin < begin:
                begin = argument.begin
            if argument.end > end:
                end = argument.end

        structure = frame.sentence[begin:end + 1]
        # Then, replace the predicate/arguments by their phrase type
        structure = VerbnetFrame._reduce_args(frame, structure, begin)
        # And delete everything else, except some keywords
        structure = VerbnetFrame._keep_only_keywords(structure)
        # Transform the structure into a list
        structure = structure.split(" ")
        #structure = VerbnetFrame._strip_leftpart_keywords(structure)

        result = VerbnetFrame(structure, [], predicate=frame.predicate.lemma)
        result.num_slots = num_slots

        # Fill the role list with None value
        result.roles = [None] * num_slots

        return result

    def passivize(self):
        """
        Based on current frame, return a list of possible passivizations
        """
        passivizedframes = []

        # Find the position of the first slot following the verb and
        # the last element of the first slot of the frame
        slot_position = 0
        old_sbj_end = 0
        first_slot = True
        for i, element in enumerate(self.structure):
            if first_slot: old_sbj_end = i
            if VerbnetFrame._is_a_slot(element):
                first_slot = False
                slot_position += 1
            if element == "V": break

        # Find the first and last element of the first slot following the verb
        index_v = self.structure.index("V")
        new_sbj_begin, new_sbj_end = index_v + 1, index_v + 1
        while True:
            if new_sbj_end >= len(self.structure): return []
            if VerbnetFrame._is_a_slot(self.structure[new_sbj_end]): break
            new_sbj_end += 1

        # Build the passive frame without "by"
        frame_without_agent = VerbnetFrame(
            (self.structure[new_sbj_begin:new_sbj_end+1] +
                self.structure[old_sbj_end+1:index_v] + ["V"] +
                self.structure[new_sbj_end+1:]),
            ([self.roles[slot_position]] + self.roles[1:slot_position] +
                self.roles[slot_position+1:]),
            vnclass=self.vnclass
        )

        passivizedframes.append(frame_without_agent)

        # Add the frames obtained by inserting "by + the old subject"
        # after the verb and every slot that follows it
        new_index_v = frame_without_agent.structure.index("V")
        i = new_index_v
        slot = slot_position - 1
        while i < len(frame_without_agent.structure):
            if frame_without_agent.structure[i][0].isupper():
                passivizedframes.append(VerbnetFrame(
                    (frame_without_agent.structure[0:i+1] +
                        ["by"] + self.structure[0:old_sbj_end+1] +
                        frame_without_agent.structure[i+1:]),
                    (frame_without_agent.roles[0:slot+1] +
                        [self.roles[0]] +
                        frame_without_agent.roles[slot+1:]),
                    vnclass=self.vnclass
                ))
                slot += 1
            i += 1

        return passivizedframes

    def generate_relatives(self):
        relatives = []
        i_slot = 0
        for i, element in enumerate(self.structure):
            if VerbnetFrame._is_a_slot(element):
                j = i - 1
                while j >= 0 and self.structure[j][0].islower(): j -= 1
                relatives.append(VerbnetFrame(
                    self.structure[j+1:i+1]+self.structure[0:j+1]+self.structure[i+1:],
                    [self.roles[i_slot]]+self.roles[0:i_slot]+self.roles[i_slot+1:],
                    vnclass=self.vnclass
                ))
                i_slot += 1

        return relatives

    @staticmethod
    def _reduce_args(frame, structure, new_begin):
        """Replace the predicate and the argument of a frame by phrase type marks

        :param frame: The original Frame.
        :type frame: Frame.
        :param structure: The current structure representation.
        :type structure: str.
        :param new_begin: The left offset cause by previous manipulations.
        :type new_begin: int.
        :returns: String -- the reduced string
        """
        predicate_begin = frame.predicate.begin - new_begin
        predicate_end = frame.predicate.end - new_begin

        for argument in reversed(frame.args):

            if not argument.instanciated: continue

            phrase_type = argument.phrase_type
            if phrase_type in VerbnetFrame.phrase_replacements:
                phrase_type = VerbnetFrame.phrase_replacements[phrase_type]

            before = structure[0:argument.begin - new_begin]
            after = structure[1 + argument.end - new_begin:]
            arg_first_word = argument.text.lower().split(" ")[0]

            # Fix some S incorrectly marked as PP
            if (phrase_type == "PP" and
                arg_first_word in verbnetprepclasses.sub_pronouns
            ):
                added_length = 5 + len(arg_first_word)
                structure = "{}| {} S|{}".format(before, arg_first_word, after)
            # Replace every "PP" by "prep NP"
            elif phrase_type == "PP":
                prep = ""
                for word in argument.text.lower().split(" "):
                    if word in verbnetprepclasses.keywords:
                        prep = word
                        break
                if prep == "":
                    prep = arg_first_word

                added_length = 6 + len(prep)
                structure = "{}| {} NP|{}".format(before, prep, after)
            # Replace every "PPing" by "prep S_ING",
            elif phrase_type == "PPing":
                prep = ""
                for word in argument.text.lower().split(" "):
                    if word in verbnetprepclasses.keywords:
                        prep = word
                        break
                if prep == "":
                    prep = arg_first_word

                added_length = 9 + len(prep)
                structure = "{}| {} S_ING|{}".format(before, prep, after)
            # Replace every "Swhether" and "S" by "that S", "if S", ...
            elif phrase_type in ["Swhether", "Sub"]:
                added_length = 5 + len(arg_first_word)
                structure = "{}| {} S|{}".format(before, arg_first_word, after)
            else:
                added_length = 3 + len(phrase_type)
                structure = "{}| {}|{}".format(before, phrase_type, after)

            # Compute the new position of the predicate if we reduced an argument before it
            if argument.begin - new_begin < predicate_begin:
                offset = (argument.end - argument.begin + 1) - added_length
                predicate_begin -= offset
                predicate_end -= offset

        structure = "{}| V|{}".format(
            structure[0:predicate_begin], structure[1+predicate_end:])

        return structure

    @staticmethod
    def _keep_only_keywords(sentence):
        """Keep only keywords and phrase type markers in the structure

        :param sentence: The structure to reduce.
        :type sentence: str.
        :returns: String -- the reduced string
        """
        pos = 0
        last_pos = len(sentence) - 1
        inside_tag = False
        closing_tag = False
        result = ""

        while pos < last_pos:
            if inside_tag and sentence[pos] == "|":
                inside_tag = False
                closing_tag = True
            if inside_tag:
                result += sentence[pos]
                pos += 1
                continue
            if not closing_tag and sentence[pos] == "|": inside_tag = True
            closing_tag = False

            for search in verbnetprepclasses.external_lexemes:
                if (search == sentence[pos:pos + len(search)].lower() and
                    (pos == 0 or sentence[pos - 1] == " ") and
                    (pos + len(search) == len(sentence) or
                        sentence[pos + len(search)] == " ")
                ):
                    pos += len(search) - 1
                    result += " "+search

            pos += 1

        if result[0] == " ": result = result[1:]
        if result[-1] == " ": result = result[:-1]

        return result

    @staticmethod
    def _strip_leftpart_keywords(sentence):
        result = []
        found_verb = False
        for elem in sentence:
            if elem == "V": found_verb = True
            if found_verb or elem[0].isupper():
                result.append(elem)

        return result


class VerbnetFrameTest(unittest.TestCase):
    def test_conversion(self):
        tested_frames = [
            Frame(
                "Rep . Tony Hall , D- Ohio , urges the United Nations to allow"+\
                " a freer flow of food and medicine into Iraq .",
                Predicate(28, 32, "urges", "urge"),
                [
                    Arg(34, 51, "the United Nations", "Addressee", True, "NP"),
                    Arg(53, 104,
                        "to allow a freer flow of food and medicine into Iraq",
                        "Content", True, "VPto"),
                    Arg(0, 26, "Rep . Tony Hall , D- Ohio", "Speaker", True, "NP")
                ],
                [
                    Word(0, 2, "NN"), Word(4, 4, "."), Word(6, 9, "NP"),
                    Word(11, 14, "NP"), Word(16, 16, ","), Word(18, 19, "NN"),
                    Word(21, 24, "NP"), Word(26, 26, ","), Word(28, 32, "VVZ"),
                    Word(34, 36, "DT"), Word(38, 43, "NP"), Word(45, 51, "NPS"),
                    Word(53, 54, "TO"), Word(56, 60, "VV"), Word(62, 62, "DT"),
                    Word(64, 68, "JJR"), Word(70, 73, "NN"), Word(75, 76, "IN"),
                    Word(78, 81, "NN"), Word(83, 85, "CC"), Word(87, 94, "NN"),
                    Word(96, 99, "IN"), Word(101, 104, "NP"), Word(106, 106, ".")
                ],
                "Attempt_suasion" ),
            Frame(
                "Rep . Tony Hall , D- Ohio , urges the United Nations to allow"+\
                " a freer flow of food and medicine into Iraq .",
                 Predicate(56, 60, "allow", "allow"),
                 [
                    Arg(62, 104,
                        "a freer flow of food and medicine into Iraq",
                        "Action", True, "NP"),
                    Arg(34, 51, "the United Nations", "Grantee", True, "NP"),
                    Arg(0, -1, "", "Grantor", False, "")
                 ],
                 [
                    Word(0, 2, "NN"), Word(4, 4, "."), Word(6, 9, "NP"),
                    Word(11, 14, "NP"), Word(16, 16, ","), Word(18, 19, "NN"),
                    Word(21, 24, "NP"), Word(26, 26, ","), Word(28, 32, "VVZ"),
                    Word(34, 36, "DT"), Word(38, 43, "NP"), Word(45, 51, "NPS"),
                    Word(53, 54, "TO"), Word(56, 60, "VV"), Word(62, 62, "DT"),
                    Word(64, 68, "JJR"), Word(70, 73, "NN"), Word(75, 76, "IN"),
                    Word(78, 81, "NN"), Word(83, 85, "CC"), Word(87, 94, "NN"),
                    Word(96, 99, "IN"), Word(101, 104, "NP"), Word(106, 106, ".")
                 ],
                 "Grant_permission" ) ]

        vn_frames = [
            VerbnetFrame(["NP", "V", "NP", "to", "S"],
                [None, None, None], predicate="urge"),
            VerbnetFrame(["NP", "V", "NP"], [None, None], predicate="allow"),
            VerbnetFrame(
                ["NP", "NP", "in", "NP", "V", "that", "S",
                    "for", "NP", "NP", "after", "NP"],
                [None, None, None, None, None, None, None])
        ]
        slot_preps = [
            [None, None, "to"],
            [None, None],
            [None, None, "in", None, "for", None, "after"]
        ]
        st = VerbnetFrame.slot_types
        slot_types = [
            [st["subject"], st["object"], st["prep_object"]],
            [st["subject"], st["object"]],
            [st["subject"], st["subject"], st["prep_object"], st["object"],
            st["prep_object"], st["indirect_object"], st["prep_object"]]
        ]

        verbnet_frame = VerbnetFrame.build_from_frame(tested_frames[0])
        self.assertEqual(vn_frames[0], verbnet_frame)
        self.assertEqual(verbnet_frame.slot_types, slot_types[0])
        self.assertEqual(verbnet_frame.slot_preps, slot_preps[0])

        verbnet_frame = VerbnetFrame.build_from_frame(tested_frames[1])
        self.assertEqual(vn_frames[1], verbnet_frame)
        self.assertEqual(verbnet_frame.slot_types, slot_types[1])
        self.assertEqual(verbnet_frame.slot_preps, slot_preps[1])

        # compute_slot_types is idempotent
        verbnet_frame = vn_frames[2]
        verbnet_frame.compute_slot_types()
        verbnet_frame.compute_slot_types()
        self.assertEqual(verbnet_frame.slot_types, slot_types[2])
        self.assertEqual(verbnet_frame.slot_preps, slot_preps[2])

    def test_passivize(self):
        vn_frame_transitive = VerbnetFrame(["NP", "V", "NP"], ["Agent", "Theme"])
        self.assertEqual(vn_frame_transitive.passivize(), [
            VerbnetFrame(["NP", "V"], ["Theme"]),
            VerbnetFrame(["NP", "V", "by", "NP"], ["Theme", "Agent"])])

        vn_frame_ditransitive = VerbnetFrame(["NP", "V", "NP", "at", "NP"],
            ["Agent", "Theme", "Value"])
        self.assertEqual(vn_frame_ditransitive.passivize(), [
            VerbnetFrame(["NP", "V", "at", "NP"],
                ["Theme", "Value"]),
            VerbnetFrame(["NP", "V", "by", "NP", "at", "NP"],
                ["Theme", "Agent", "Value"]),
            VerbnetFrame(["NP", "V", "at", "NP", "by", "NP"],
                ["Theme", "Value", "Agent"])])

        vn_frame_strange = VerbnetFrame(["NP", "NP", "V", "S"],
            ["Agent", "Theme", "Value"])
        self.assertEqual(vn_frame_strange.passivize(), [
            VerbnetFrame(["S", "NP", "V"],
                ["Value", "Theme"]),
           VerbnetFrame(["S", "NP", "V", "by", "NP"],
                ["Value", "Theme", "Agent"])])

    def test_relatives(self):
        test_frame = VerbnetFrame(
        ["NP", "V", "NP", "for", "NP"],
        ["Agent", "Theme", "Beneficiary"])

        self.assertEqual(test_frame.generate_relatives(), [
            VerbnetFrame(
            ["NP", "V", "NP", "for", "NP"],
            ["Agent", "Theme", "Beneficiary"]),
            VerbnetFrame(
            ["NP", "NP", "V", "for", "NP"],
            ["Theme", "Agent", "Beneficiary"]),
            VerbnetFrame(
            ["for", "NP", "NP", "V", "NP"],
            ["Beneficiary", "Agent", "Theme"])
        ])

if __name__ == "__main__":
    unittest.main()

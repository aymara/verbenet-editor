#!/usr/bin/env python3
# -*- coding: utf-8 -*-

verb_classes = {
    "9": "Putting",
    "10": "Removing",
    "11": "Sending and Carrying",
    "12": "Exerting Force: Push/Pull",
    "13": "Change of Posession",
    "14": "Learn",
    "15": "Hold and Keep",
    "16": "Concealment",
    "17": "Throwing",
    "18": "Contact by Impact",
    "19": "Poke",
    "20": "Contact: Touch",
    "21": "Cutting",
    "22": "Combining and Attaching",
    "23": "Separating and Disassembling",
    "24": "Coloring",
    "25": "Image Creation",
    "26": "Creation and Transformation",
    "27": "Engender",
    "28": "Calve",
    "29": "Predicative Complements",
    "30": "Perception",
    "31": "Psychocological",
    "32": "Desire",
    "33": "Judgment",
    "34": "Assessment",
    "35": "Searching",
    "36": "Social Interaction",
    "37": "Communication",
    "38": "Sounds Made by Animals",
    "39": "Ingesting",
    "40": "Body",
    "41": "Grooming and Bodily Care",
    "42": "Killing",
    "43": "Emission",
    "44": "Destroy",
    "45": "Change of State",
    "46": "Lodge",
    "47": "Existence",
    "48": "Appearance, Disappearance and Occurrence",
    "49": "Body-Internal Motion",
    "50": "Assuming a Position",
    "51": "Motion",
    "52": "Avoid",
    "53": "Lingering and Rushing",
    "54": "Measure",
    "55": "Aspectual",
    "56": "Weekend",
    "57": "Weather",

    "58": "Urge and Beg",
    "59": "Force",
    "60": "Order",
    "61": "Try",
    "62": "Wish",
    "63": "Enforce",
    "64": "Allow",
    "65": "Admit",
    "66": "Consume",
    "67": "Forbid",
    "68": "Pay",
    "69": "Refrain",
    "70": "Rely",
    "71": "Conspire",
    "72": "Help",
    "73": "Cooperate",
    "74": "Succeed",
    "75": "Neglect",
    "76": "Limit",
    "77": "Accept",
    "78": "Indicate",
    "79": "Dedicate",
    "80": "Free",
    "81": "Suspect",
    "82": "Withdraw",
    "83": "Cope",
    "84": "Discover",
    "85": "Defend",
    "86": "Correlate and Relate",
    "87": "Focus and Comprehend",
    "88": "Care and Empathize",
    "89": "Settle",
    "90": "Exceed",
    "91": "Matter",
    "92": "Confine",
    "93": "Adopt",
    "94": "Risk",
    "95": "Acquiesce",
    "96": "Addict",
    "97": "Base and Deduce",
    "98": "Confront",
    "99": "Ensure",
    "100": "Own",
    "101": "Patent",
    "102": "Promote",
    "103": "Require",
    "104": "Spend_time",
    "105": "Use",
    "106": "Void",
    "107": "Involve",
    "108": "Multiply",
    "109": "Seem and Become",
}

from syntacticframes.models import LevinClass

for number in verb_classes:
    LevinClass(number=number, name=verb_classes[number]).save()

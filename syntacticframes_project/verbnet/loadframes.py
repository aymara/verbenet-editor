#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Load VerbNet frames for each class"""

from syntacticframes.models import VerbNetClass, VerbNetFrame
from verbnet.verbnetreader import VerbnetReader

reader = VerbnetReader('verbnet/verbnet-3.2/', False)

def print_classe(c, i):
    print(i + " ".join(c["roles"]))
    print(i + " ".join(c["members"]))
    for f in c["frames"]: print (i, f)
    for child in c["children"]:
        print_classe(child, i + "   ")
    print("")

for classe in sorted(reader.files.keys()):
    print(classe)
    print_classe(reader.files[classe], "")

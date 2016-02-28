#!/usr/bin/env python
# -*- coding: utf-8 -*-

# POUR DSSP

import sys
import re

def parse_ss(dssp_file):
    with open(dssp_file, "r") as filein:
        list_ss = []
        regex_ss = re.compile(' +[0-9]+ +[0-9]+ +[A-Z] +[A-z] +([A-z ])')
        for ligne in filein:
            ss = regex_ss.search(ligne)
            if ss:
                list_ss.append(ss.group(1))
        for i, item in enumerate(list_ss):
            if item == " ":
                list_ss[i] = "-"
        print "".join(list_ss)
                

if __name__ == "__main__":
    # Passage du chemin du fichier .dssp en argument
    dssp_file = sys.argv[1]
    structure = parse_ss(dssp_file)

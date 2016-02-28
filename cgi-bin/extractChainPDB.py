#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys

"""
Read a PDB file and create a new PDB file only with the chain you want.
To run :
$ python extractChainPDB.py pdbOriginal.pdb letterOfYourChain
pdbOriginal.pdb = the name of your original PDB file
letterOfYourChain = A or B or etc.
"""

# if we don't have arguments
if len(sys.argv) <= 1:
	print """No argument given ! The program can't run... EXIT WITH ERROR."""
	exit()


pdb_old = sys.argv[1] # name of the original PDB file 
chain = sys.argv[2] # chain to extract
pdb_new = pdb_old[:-4]+"_"+chain+".pdb" # name of the new PDB file


with open(pdb_old,"r") as filin:
	with open(pdb_new,"w") as filout:
		# for each line in the pdb_old
		for li in filin:
			# if we find atoms of the targetChain
			if re.search("^ATOM +[0-9]+ +[A-Z]+[0-9]* +[A-Z]{3} +"+chain,li):
				filout.write(li)

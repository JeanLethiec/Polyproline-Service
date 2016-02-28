#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import sys
import re

def get_structure(pdb_id):
    pdb_url = 'http://www.rcsb.org/pdb/files/'+ pdb_id+ ".pdb"
    try:
        # Ouverture et lecture de la page
        handle = urllib2.urlopen(pdb_url)
        print "Fichier PDB " + pdb_id + " récupéré ! \n"
        return handle
    except:
        print "Erreur lors de l'accès à la PDB\n" + pdb_url + "\n"
        return False
      
if __name__ == "__main__":
    # Passage de l'ID PDB en argument
    # pdb_id = sys.argv[1]
    
    # Lecture de la liste
    with open("liste_pdb_id", "r") as filein:
        for ligne in filein: 
            # Ecriture des fichiers
            pdb_id = ligne[0:4]
            try:
                structure = get_structure(pdb_id)
                if structure:
                    with open(pdb_id + ".pdb", "w") as fileout:
                        fileout.write(structure.read())
            except:
                print "Erreur lors de la récupération de " + pdb_id
    

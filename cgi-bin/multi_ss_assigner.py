#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 1 : Va chercher le fichier PDB à partir de l'identifiant
# 2 : Assigne les SS de la structure par divers secripts (SEGNO, DSSP, PROSS...)
# 3 : Génère les fichiers de sortie
# 4 : Traite les fichiers de sortie pour en extraire et normaliser les données
#        (séquence en SS et angles phi/psi)
# 5 : Rentre les données dans des classes spécifiques

# DSSP    : OK
# DSSPPII : OK
# SEGNO   : OK
# PROSS   : OK
# XTLSSTR : NOT OK

from bdd_classes import PDB_structure, Assignation

import urllib2
import sys
import os
import subprocess
import re

def dssp_ss_seq_parse(dssp_file):
    # Renvoie la séquence en structures secondaires à partir d'un fichier
    # généré par DSSP ou DSSPPII
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
        return "".join(list_ss)
        
def dssp_angles_parse(dssp_file):
    # Renvoie la liste des angles phi et psi à partir d'un fichier
    # généré par DSSP ou DSSPPII
    with open(dssp_file, "r") as filein:
        angles = []
        regex_ss = re.compile(' +[0-9]+ +[0-9]+ +[A-Z] +[A-z] +[A-z ]')
        for ligne in filein:
            ss = regex_ss.search(ligne)
            if ss:
                angles.append((float(ligne[103:109]), float(ligne[110:115])))
        return angles
        
def pross_angles_parse(pross_file):
    # Renvoie la liste des angles phi et psi à partir d'un fichier
    # généré par PROSS
    with open(pross_file, "r") as filein:
        angles = []
        i = 0
        regex_ss = re.compile(' +[0-9]+ +[0-9]+ +[A-Z] +[A-z] +[A-z ]')
        for ligne in filein:
            if i > 1:
                try:
                    angles.append((float(ligne[17:24].replace(" ", "")), float(ligne[26:33].replace(" ", ""))))
                except ValueError:
                    pass
                    #print "\"" + ligne[17:24] + "\"", "\"" + ligne[26:33] + "\""
            i += 1
        return angles
        
def segno_angles_parse(segno_file):
    # Renvoie la liste des angles phi et psi à partir d'un fichier
    # généré par SEGNO
    with open(segno_file, "r") as filein:
        angles = []
        regex_ss = re.compile(' +[0-9]+ +[0-9]+ +[A-Z] +[A-z] +[A-z ]')
        for ligne in filein:
            try:
                angles.append((float(ligne[53:61].replace(" ", "")), float(ligne[62:69].replace(" ", ""))))
            except ValueError:
                pass
        return angles

if __name__ == "__main__":
    ############# Passage de l'ID PDB en argument #############
    try:
        pdb_id = sys.argv[1]
    except:
        print "Usage : \n$ script.py PDB_ID"
        sys.exit()
    
    ############# Création de l'objet structure PDB #################
    structure = PDB_structure(pdb_id, "A")
    
    ############# Chemin vers les fichiers pdb correspondants ############
    pdb_file = "/media/www-dev/public/projet/cgi-bin/data/" + pdb_id + ".pdb"
    ent_file = "/media/www-dev/public/projet/cgi-bin/data/pdb" + pdb_id.lower() + ".ent"
    
    ############# Chemins vers les scripts ############
    dssp_path = "/media/www-dev/public/projet/cgi-bin/tools/dsspcmbi"
    
    dssppii_path = "/media/www-dev/public/projet/cgi-bin/tools/dssppII.pl"
    
    xtlsstr_path = "/media/www-dev/public/projet/cgi-bin/tools/XTLSSTR"
   
    segno_path = "/media/www-dev/public/projet/cgi-bin/tools/segno"
    
    pross_path = "/media/www-dev/public/projet/cgi-bin/tools/PROSS.py"
    
    segno_extractor_path = "/media/www-dev/public/projet/cgi-bin/tools/parsers/extract_SEGNO2SEQ2D.pl"
    
    pross_extractor_path = "/media/www-dev/public/projet/cgi-bin/tools/parsers/extract_PROSS2SEQ2D.pl"
    
    ############# Arguments de certains scripts ############
    all1deg_path = "__RAMAPLOT=/media/www-dev/public/projet/cgi-bin/tools/all1deg.data"
    segno_cmd = all1deg_path + " " + segno_path + " -pdb " + pdb_file
    
    ############# Appel des scripts ############
    dssp_pipe = subprocess.Popen([dssp_path, pdb_file], 
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
                            
    dssppii_pipe = subprocess.Popen(["perl", dssppii_path, pdb_file],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                             
    segno_pipe = subprocess.Popen(segno_cmd, 
                                  stdout=subprocess.PIPE, 
                                  shell=True, 
                                  stderr=subprocess.PIPE)
                            
    pross_pipe = subprocess.Popen(["python", pross_path, pdb_file],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
                             
    # PROBLEME AVEC XTLSSTR : CREATION DE FICHIER - ACCESS DENIED
    # RMQ : XTLSSTR LIT STDIN, D'OU .COMMUNICATE()
    #xtlsstr_pipe = subprocess.Popen([xtlsstr_path, ent_file],
                             #stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    #xtlsstr_interact = xtlsstr_pipe.communicate(input=ent_file)[0]
        
    ############# Récupération des stdout correspondantes ############
    stdout_dssp = dssp_pipe.stdout.read()
    stdout_dssppii = dssppii_pipe.stdout.read()
    stdout_segno = segno_pipe.stdout.read()
    stdout_pross = pross_pipe.stdout.read()
    
    ############# Récupération des stderr correspondantes ############
    stderr_dssp = dssp_pipe.stderr.read()
    stderr_dssppii = dssppii_pipe.stderr.read()
    stderr_segno = segno_pipe.stderr.read()
    stderr_pross = pross_pipe.stderr.read()
    
    ############# Ecriture des résultats dans des fichiers ############
    with open("results/" + pdb_id + ".dssp", "w") as dssp_out:
        dssp_out.write(stdout_dssp)
    with open("results/" + pdb_id + ".dssppii", "w") as dssppii_out:
        dssppii_out.write(stdout_dssppii)
    with open("results/" + pdb_id + ".segno", "w") as segno_out:
        segno_out.write(stdout_segno)
    with open("results/" + pdb_id + ".pross", "w") as pross_out:
        pross_out.write(stdout_pross)
        
    ############# Ecriture des sorties d'erreurs dans les logs ############
    with open("log/" + pdb_id + "_dssp.log", "w") as dssp_err:
        dssp_err.write(stderr_dssp)
    with open("log/" + pdb_id + "_dssppii.log", "w") as dssppii_err:
        dssppii_err.write(stderr_dssppii)
    with open("log/" + pdb_id + "_segno.log", "w") as segno_err:
        segno_err.write(stderr_segno)
    with open("log/" + pdb_id + "_pross.log", "w") as pross_err:
        pross_err.write(stderr_pross)
        
    ############ Extraction des données d'assignation des fichiers créés ##############
    # Execution des fonctions Python pour DSSP et DSSPPII
    dssp_ss_seq = dssp_ss_seq_parse("results/" + pdb_id + ".dssp")
    dssp_angles = dssp_angles_parse("results/" + pdb_id + ".dssp")
    
    dssppii_ss_seq = dssp_ss_seq_parse("results/" + pdb_id + ".dssppii")
    dssppii_angles = dssp_angles_parse("results/" + pdb_id + ".dssppii")
    
    # Appel de l'extracteur Perl et d'une fonction Python pour PROSS
    pross_extractor_pipe = subprocess.Popen(["perl", pross_extractor_path, "results/" + pdb_id + ".pross"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                                    
    pross_ss_seq = pross_extractor_pipe.stdout.read()
    pross_angles = pross_angles_parse("results/" + pdb_id + ".pross")
    
    # Appel de l'extracteur Perl et d'une fonction Python pour SEGNO
    segno_extractor_pipe = subprocess.Popen(["perl", segno_extractor_path, "results/" + pdb_id + ".segno"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                                    
    segno_ss_seq = segno_extractor_pipe.stdout.read()
    segno_angles = segno_angles_parse("results/" + pdb_id + ".segno")
    
    ##################### Création des objets assignation ############
    new_dssp_assignation = Assignation('DSSP', dssp_ss_seq, dssp_angles)
    new_dssppii_assignation = Assignation('DSSPPII', dssppii_ss_seq, dssppii_angles)
    new_pross_assignation = Assignation('PROSS', pross_ss_seq, pross_angles)
    new_segno_assignation = Assignation('SEGNO', segno_ss_seq, segno_angles)
    
    ################### Peuplement de l'objet PDB structure ########
    structure.add_dssp_assignation(new_dssp_assignation)
    structure.add_dssppii_assignation(new_dssppii_assignation)
    structure.add_pross_assignation(new_pross_assignation)
    structure.add_segno_assignation(new_segno_assignation)
    
    print structure.segno_assignation.ss_sequence

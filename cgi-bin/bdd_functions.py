#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rpy import *
import urllib2
import sys
import os
import subprocess
import re
import requests
from requests.exceptions import HTTPError
import cgitb, cgi
import MySQLdb

from bdd_classes import PDB_structure, Assignation

def get_colored_SS_sequence(ss_sequence):
    # type Helix rouge, type Bêta vert, type Coil gris et type PPII en bleu et souligné)
    colored_sequence = ""
    for letter in ss_sequence:
        if letter == "h" or letter == "H" or letter == "g" or letter == "G" or letter == "i" or letter == "I":
            colored_sequence += '<font color="red">' + letter + '</font>'
        elif letter == "b" or letter == "B" or letter == "E" or letter == "e":
            colored_sequence += '<font color="green">' + letter + '</font>'
        elif letter == "p" or letter == "P":
            colored_sequence += '<font color="blue">' + letter + '</font>'
        elif letter == "t" or letter == "T" or letter == "s" or letter == "S" or letter == "n" or letter == "N":
            colored_sequence += '<font color="blue">' + letter + '</font>'
        else:
            colored_sequence += letter
    return colored_sequence
    
def format_sequence(seq):
    seq_f = ""
    i = 0
    while i < len(seq):
        seq_f = seq_f + seq[i:i+79] + "\n"
        i = i + 79
    return seq_f

def read_pdb_list(pdb_list_file):
    pdb_list = []
    i = 0
    with open(pdb_list_file, "r") as filein:
        for ligne in filein:
            pdb_list.append({"id": ligne[0:-2], "chain": ligne[-2:-1]})
    return pdb_list
    
def get_PDBFile(pdb_id):
    if re.match('[A-Z0-9]{4}', pdb_id):
        pdb_url = 'http://www.rcsb.org/pdb/files/'+ pdb_id+ ".pdb"
        #print '#' + pdb_url + '#'
        try:
            # Ouverture et lecture de la page
            handle = urllib2.urlopen(pdb_url)
            #print "Lecture du Fichier PDB " + pdb_id + "\n"
            with open("../data/"+pdb_id+".pdb", "w") as pdb_out:
                for ligne in handle:
                    pdb_out.write(ligne)
            return True
        except HTTPError:
            #print "Erreur lors de l'accès à la PDB\n" + pdb_url + "\n"
            return False
        except IOError:
            #print "Fichier déjà existant ?"
            return True
    else:
        #print "Mauvais ID entré !"
        return False

def assign_pdb(pdb_id, chain, filepath):
    #print "Récupération de la structure de", pdb_id 
    ############# Chemins vers les scripts ############
    dssp_path = "../bin/dsspcmbi"

    dssppii_path = "../bin/dssppII.pl"

    xtlsstr_path = "../bin/XTLSSTR"

    segno_path = "../bin/segno"

    pross_path = "../bin/PROSS.py"

    segno_extractor_path = "../bin/parsers/extract_SEGNO2SEQ2D.pl"

    pross_extractor_path = "../bin/parsers/extract_PROSS2SEQ2D.pl"
    
    all1deg_path = "__RAMAPLOT=../bin/all1deg.data"
    segno_cmd = all1deg_path + " " + segno_path + " -pdb " + filepath
        
    if str(filepath) == '../data/' + pdb_id + ".pdb":
        if not get_PDBFile(pdb_id):
            return None
    
    #print "Assignation pour", pdb_id, "<br \>"
    structure = PDB_structure(pdb_id, chain, filepath)

    ############# Appel des scripts ############
    dssp_pipe = subprocess.Popen([dssp_path, filepath], 
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
                            
    dssppii_pipe = subprocess.Popen(["perl", dssppii_path, filepath],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                             
    segno_pipe = subprocess.Popen(segno_cmd, 
                                  stdout=subprocess.PIPE, 
                                  shell=True, 
                                  stderr=subprocess.PIPE)
                            
    pross_pipe = subprocess.Popen(["python", pross_path, filepath],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
    
                             
    # PROBLEME AVEC XTLSSTR : CREATION DE FICHIER - ACCESS DENIED
    # RMQ : XTLSSTR LIT STDIN, D'OU .COMMUNICATE()
    #xtlsstr_pipe = subprocess.Popen([xtlsstr_path, ent_file],
                             #stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    #xtlsstr_interact = xtlsstr_pipe.communicate(input=ent_file)[0]
        
    ############# Récupération des stdout correspondantes ############
    stdout_dssp = dssp_pipe.communicate()[0]
    #print "DSSP :", stdout_dssp
    stdout_dssppii = dssppii_pipe.communicate()[0]
    #print "DSSPPII :", stdout_dssppii
    stdout_segno = segno_pipe.communicate()[0]
    #print "SEGNO :", stdout_segno
    stdout_pross = pross_pipe.communicate()[0]
    #print "PROSS :", stdout_pross

    ############# Récupération des stderr correspondantes ############
    #stderr_dssp = dssp_pipe.stderr.read()
    #stderr_dssppii = dssppii_pipe.stderr.read()
    #stderr_segno = segno_pipe.stderr.read()
    #stderr_pross = pross_pipe.stderr.read()

    ############# Ecriture des résultats dans des fichiers ############
    with open("../results/" + pdb_id + ".dssp", "w") as dssp_out:
        dssp_out.write(stdout_dssp)
    with open("../results/" + pdb_id + ".dssppii", "w") as dssppii_out:
        dssppii_out.write(stdout_dssppii)
    with open("../results/" + pdb_id + ".segno", "w") as segno_out:
        segno_out.write(stdout_segno)
    with open("../results/" + pdb_id + ".pross", "w") as pross_out:
        pross_out.write(stdout_pross)
        
        
    ############# Ecriture des sorties d'erreurs dans les logs ############
    #with open("log/" + pdb_id + "_dssp.log", "w") as dssp_err:
    #    dssp_err.write(stderr_dssp)
    #with open("log/" + pdb_id + "_dssppii.log", "w") as dssppii_err:
    #    dssppii_err.write(stderr_dssppii)
    #with open("log/" + pdb_id + "_segno.log", "w") as segno_err:
    #    segno_err.write(stderr_segno)
    #with open("log/" + pdb_id + "_pross.log", "w") as pross_err:
    #    pross_err.write(stderr_pross)
        
        
    ############ Extraction des données d'assignation des fichiers créés ###
    # Execution des fonctions Python pour DSSP et DSSPPII
    dssp_ss_seq = dssp_ss_seq_parse("../results/" + pdb_id + ".dssp")
    dssp_angles = dssp_angles_parse("../results/" + pdb_id + ".dssp")

    dssppii_ss_seq = dssp_ss_seq_parse("../results/" + pdb_id + ".dssppii")
    dssppii_angles = dssp_angles_parse("../results/" + pdb_id + ".dssppii")

    # Appel de l'extracteur Perl et d'une fonction Python pour PROSS
    pross_extractor_pipe = subprocess.Popen(["perl", pross_extractor_path, "../results/" + pdb_id + ".pross"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                                    
    pross_ss_seq = pross_extractor_pipe.stdout.read()
    pross_angles = pross_angles_parse("../results/" + pdb_id + ".pross")

    # Appel de l'extracteur Perl et d'une fonction Python pour SEGNO
    segno_extractor_pipe = subprocess.Popen(["perl", segno_extractor_path, "../results/" + pdb_id + ".segno"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
                                    
    segno_ss_seq = segno_extractor_pipe.stdout.read()
    segno_angles = segno_angles_parse("../results/" + pdb_id + ".segno")
    

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
    

    #print "<h2>PDB ID :", structure.pdb_id, "</h2>"
    #print "<h2>DSSP :</h2>", structure.dssp_assignation.ss_sequence, "<br \>"
    #print "<h2>DSSPPII :</h2>", structure.dssppii_assignation.ss_sequence, "<br \>"
    #print "<h2>PROSS :</h2>", structure.pross_assignation.ss_sequence, "<br \>"
    #print "<h2>SEGNO :</h2>", structure.segno_assignation.ss_sequence, "<br \>"
    
    return structure
        

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
                angles.append((int(ligne[7:10]), float(ligne[103:109]), float(ligne[110:115])))
        return angles
        
def pross_angles_parse(pross_file):
    # Renvoie la liste des angles phi et psi à partir d'un fichier
    # généré par PROSS
    with open(pross_file, "r") as filein:
        angles = []
        i = 0
        #regex_ss = re.compile(' +[0-9]+ +[0-9]+ +[A-Z] +[A-z] +[A-z ]')
        for ligne in filein:
            if i > 1:
                try:
                    angles.append((int(ligne[2:5].replace(" ", "")), float(ligne[17:24].replace(" ", "")), float(ligne[26:33].replace(" ", ""))))
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
        #regex_ss = re.compile(' +[0-9]+ +[0-9]+ +[A-Z] +[A-z] +[A-z ]')
        for ligne in filein:
            try:
                angles.append((int(ligne[2:5].replace(" ", "")), float(ligne[53:61].replace(" ", "")), float(ligne[62:69].replace(" ", ""))))
            except ValueError:
                pass
        return angles
  
def insert_into_db(structure_list):      
    # Accès et lecture de la BDD MySQL
    # Open database connection
    db = MySQLdb.connect("localhost","root","root","bdd_m2" )

    for structure in structure_list:  
        # Insertion dans la table PDB
        cursor = db.cursor()
        insert = """INSERT INTO PDB (PDB_ID, chain, PDB_header, amino_seq, seq_size, resol)
            VALUES ("%s", "%s", "%s", "%s", "%d", "%f");""" % (structure.pdb_id, structure.chain, structure.PDB_object.get_header()["journal"], structure.get_sequence(), len(structure.get_sequence()), structure.PDB_object.get_header()["resolution"])
        cursor.execute(insert)
        db.commit()
        try:
            cursor = db.cursor()
            insert = """INSERT INTO SS_Assign (PDB_ID, chain, struct_sec, date_creation, method)
                VALUES ("%s", "%s", "%s", NOW(), "SEGNO");""" % (structure.pdb_id, structure.chain, structure.segno_assignation.ss_sequence)
            cursor.execute(insert)
        except:
            pass
        #print structure.segno_assignation.ss_sequence
        for i, aa in enumerate(structure.segno_assignation.angles):
            try:
                cursor = db.cursor()
                insert = """INSERT INTO AA (PDB_ID, chain, method, phi, psi, num_aa, struct_seq)
                    VALUES ("%s", "%s", "SEGNO", %s, %s, %s, "%s");""" % (structure.pdb_id, structure.chain, aa[1], aa[2], aa[0], structure.segno_assignation.ss_sequence[i])      
                cursor.execute(insert)
            except:
                pass
                #print "Erreur d'ajout de l'AA n°", aa[0]
        db.commit()
        cursor = db.cursor()
        try:
            insert = """INSERT INTO SS_Assign (PDB_ID, chain, struct_sec, date_creation, method)
            VALUES ("%s", "%s", "%s", NOW(), "PROSS");""" % (structure.pdb_id, structure.chain, structure.pross_assignation.ss_sequence)
            cursor.execute(insert)
        except:
            pass
        for i, aa in enumerate(structure.pross_assignation.angles):
            try:
                cursor = db.cursor()
                insert = """INSERT INTO AA (PDB_ID, chain, method, phi, psi, num_aa, struct_seq)
                    VALUES ("%s", "%s", "PROSS", %s, %s, %s, "%s");""" % (structure.pdb_id, structure.chain, aa[1], aa[2], aa[0], structure.pross_assignation.ss_sequence[i])      
                cursor.execute(insert)
            except:
                pass
                #print "Erreur d'ajout de l'AA n°", aa[0]
        db.commit()
        cursor = db.cursor()
        try:
            insert = """INSERT INTO SS_Assign (PDB_ID, chain, struct_sec, date_creation, method)
                VALUES ("%s", "%s", "%s", NOW(), "DSSPPII");""" % (structure.pdb_id, structure.chain, structure.dssppii_assignation.ss_sequence)
            cursor.execute(insert)
        except:
            pass
        for i, aa in enumerate(structure.dssppii_assignation.angles):
            try:
                cursor = db.cursor()
                insert = """INSERT INTO AA (PDB_ID, chain, method, phi, psi, num_aa, struct_seq)
                    VALUES ("%s", "%s", "DSSPPII", %s, %s, %s, "%s");""" % (structure.pdb_id, structure.chain, aa[1], aa[2], aa[0], structure.dssppii_assignation.ss_sequence[i])      
                cursor.execute(insert)
            except:
                pass
                #print "Erreur d'ajout de l'AA n°", aa[0]
        db.commit()
        cursor = db.cursor()
        try:
            insert = """INSERT INTO SS_Assign (PDB_ID, chain, struct_sec, date_creation, method)
                VALUES ("%s", "%s", "%s", NOW(), "DSSP");""" % (structure.pdb_id, structure.chain, structure.dssp_assignation.ss_sequence)
            cursor.execute(insert)
        except:
            pass
        for i, aa in enumerate(structure.dssp_assignation.angles):
            try:
                cursor = db.cursor()
                insert = """INSERT INTO AA (PDB_ID, chain, method, phi, psi, num_aa, struct_seq)
                    VALUES ("%s", "%s", "DSSP", %s, %s, %s, "%s");""" % (structure.pdb_id, structure.chain, aa[1], aa[2], aa[0], structure.dssp_assignation.ss_sequence[i])      
                cursor.execute(insert)
            except:
                pass
                #print "Erreur d'ajout de l'AA n°", aa[0]
        db.commit()
        #print "Insertion de", structure.pdb_id + "<br \>"
        #except:
            #db.rollback()

    db.close()
    
def get_colored_keyword(header, keyword):
    return header.replace(keyword, '<b>' + keyword + '</b>')
    

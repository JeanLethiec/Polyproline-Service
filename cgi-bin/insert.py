#!/usr/bin/env python
# -*- coding: utf-8 -*-

# POUR L'INSTANT GROS PROBLEME A CAUSE DES CHAINES ! A PRENDRE EN COMPTE DANS
# LE PARSING DES FICHIERS DE RESULTATS D'ASSIGNATION POUR NE GARDER QUE LES 
# DONNEES DE LA CHAINE INTERESSANTE ?

# OU EN AMONT, ENLEVER DES FICHIERS LES CHAINES DE MERDE PAR GET_PDB ?

import cgitb, cgi
import MySQLdb
import warnings
import urllib2
import sys
import os
import subprocess
import re
import requests
from requests.exceptions import HTTPError

from bdd_classes import PDB_structure, Assignation

def read_pdb_list(pdb_list_file, lines_to_read=20):
    pdb_list = []
    i = 0
    with open(pdb_list_file, "r") as filein:
        for ligne in filein:
            if i < int(lines_to_read):
                pdb_list.append({"id": ligne[0:-2], "chain": ligne[-2:-1]})
            i = i + 1
    return pdb_list

def assign_pdb(pdb_id, chain, all1deg_path, segno_cmd):
    #print "Récupération de la structure de", pdb_id 
    if get_structure(pdb_id):
        #print "Assignation pour", pdb_id, "<br \>"
        structure = PDB_structure(pdb_id, chain)

        ############# Chemin vers les fichiers pdb correspondants ############
        pdb_file = "data/" + pdb_id + ".pdb"

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
        with open("results/" + pdb_id + ".dssp", "w") as dssp_out:
            dssp_out.write(stdout_dssp)
        with open("results/" + pdb_id + ".dssppii", "w") as dssppii_out:
            dssppii_out.write(stdout_dssppii)
        with open("results/" + pdb_id + ".segno", "w") as segno_out:
            segno_out.write(stdout_segno)
        with open("results/" + pdb_id + ".pross", "w") as pross_out:
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
        

        #print "<h2>PDB ID :", structure.pdb_id, "</h2>"
        #print "<h2>DSSP :</h2>", structure.dssp_assignation.ss_sequence, "<br \>"
        #print "<h2>DSSPPII :</h2>", structure.dssppii_assignation.ss_sequence, "<br \>"
        #print "<h2>PROSS :</h2>", structure.pross_assignation.ss_sequence, "<br \>"
        #print "<h2>SEGNO :</h2>", structure.segno_assignation.ss_sequence, "<br \>"
        
        return structure
    else:
        #print "Erreur d'assignation pour", pdb_id
        return None

def get_structure(pdb_id):
    if re.match('[A-Z0-9]{4}', pdb_id):
        pdb_url = 'http://www.rcsb.org/pdb/files/'+ pdb_id+ ".pdb"
        try:
            # Ouverture et lecture de la page
            handle = urllib2.urlopen(pdb_url)
            #print "Lecture du Fichier PDB " + pdb_id + "\n"
            with open("data/"+pdb_id+".pdb", "w") as pdb_out:
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
        regex_ss = re.compile(' +[0-9]+ +[0-9]+ +[A-Z] +[A-z] +[A-z ]')
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
        regex_ss = re.compile(' +[0-9]+ +[0-9]+ +[A-Z] +[A-z] +[A-z ]')
        for ligne in filein:
            try:
                angles.append((int(ligne[2:5].replace(" ", "")), float(ligne[53:61].replace(" ", "")), float(ligne[62:69].replace(" ", ""))))
            except ValueError:
                pass
        return angles


# Filtration des warnings
warnings.filterwarnings("ignore", category = MySQLdb.Warning)

#### Affichage des erreurs sur la page ####
cgitb.enable()

print "Content-type: text/html\n\n"

print "<html>"

##### HEADER #####
print '<head>'
print '<meta charset="UTF-8">'
print '<title>Insertion des données</title>'
print '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">'
print '</head>'
#### FIN DU HEADER ####

#### BODY ####
print '<body>'

print '''
<ul>
    <li><a href="/~jean/projet/index.html">Home</a></li>
    <li><a href="/~jean/projet/cgi-bin/search.py">Search</a></li>
    <li><a href="/~jean/projet/cgi-bin/analyze.py">Analyze</a></li>
    <li><a href="/~jean/projet/cgi-bin/about.py">About</a></li>
    <li><a href="/~jean/projet/cgi-bin/create.py">Reset DB</a></li>
    <li><a href="/~jean/projet/cgi-bin/insert.py">Populate DB</a></li>
</ul>
'''

formulaire = cgi.FieldStorage()

if formulaire.getvalue('lines_to_read') == None:
    print '''
    <form action="insert.py" method="get">
    <label for="lines_to_read">Number of wanted entries:</label>
        <input type="text" name="lines_to_read"/>
        <input type="submit" value="GO"/>
    </form>
    '''
else:

    # Assignation des SS
    ############# Création de l'objet structure PDB #################
    #arguments = cgi.FieldStorage()
    #pdb_id = arguments["pdb"].value

    ############# Chemin vers la liste de PDB d'intérêt ############
    pdb_list_file = "data/list_pdb_id"

    ############# Chemins vers les scripts ############
    dssp_path = "tools/dsspcmbi"

    dssppii_path = "tools/dssppII.pl"

    xtlsstr_path = "tools/XTLSSTR"

    segno_path = "tools/segno"

    pross_path = "tools/PROSS.py"

    segno_extractor_path = "tools/parsers/extract_SEGNO2SEQ2D.pl"

    pross_extractor_path = "tools/parsers/extract_PROSS2SEQ2D.pl"

    pdb_list = read_pdb_list(pdb_list_file, formulaire.getvalue('lines_to_read'))

    structure_list = []

    for element in pdb_list:
        ############# Arguments de certains scripts ############
        all1deg_path = "__RAMAPLOT=tools/all1deg.data"
        segno_cmd = all1deg_path + " " + segno_path + " -pdb " + "data/" + element["id"] + ".pdb"
        new_structure = assign_pdb(element["id"], element["chain"], all1deg_path, segno_cmd)
        if new_structure != None:
            structure_list.append(new_structure)

    # Accès et lecture de la BDD MySQL
    # Open database connection
    db = MySQLdb.connect("localhost","root","p=jlt56!","bdd_m2" )

    for structure in structure_list:  
        # Insertion dans la table PDB
        cursor = db.cursor()
        try:
            insert = """INSERT INTO PDB (PDB_ID, chain)
                VALUES ("%s", "%s");""" % (structure.pdb_id, structure.chain)
            cursor.execute(insert)
        except:
            pass
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
    print "Tables populated successfully with<b>", len(structure_list), '</b>entries'

print '</body>'

#### FIN DU BODY ####

print '</html>'

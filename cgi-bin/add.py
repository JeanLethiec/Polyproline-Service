#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgitb, cgi
import MySQLdb
import warnings
import re

from bdd_classes import PDB_structure, Assignation
from bdd_functions import *

# Filtration des warnings
warnings.filterwarnings("ignore", category = MySQLdb.Warning)

#### Affichage des erreurs sur la page ####
cgitb.enable()

# Accès et lecture de la BDD MySQL
# Open database connection
db = MySQLdb.connect("localhost","root","p=jlt56!","bdd_m2" )

print "Content-type: text/html\n\n"

print "<html>"

##### HEADER #####
print '<head>'
print '<meta charset="UTF-8">'
print '<title>Analyze</title>'
print '<link rel="stylesheet" href="/~jean/projet/js-css/bootstrap.css">'
print '<link rel="stylesheet" href="/~jean/projet/js-css/style.css">'
print '</head>'
#### FIN DU HEADER ####

#### BODY ####
print '<body>'

print '''
<nav class="navbar navbar-default">
  <div class="container-fluid">
    <div class="navbar-header">
        <a class="navbar-brand" href="/~jean/projet/index.html">Polyproline Service</a>
    </div>
    <ul class="nav navbar-nav">
        <li><a href="/~jean/projet/cgi-bin/search.py">Search</a></li>
        <li><a href="/~jean/projet/cgi-bin/add.py">Analyze</a></li>
        <li><a href="/~jean/projet/cgi-bin/about.py">About</a></li>
        <li><a href="/~jean/projet/cgi-bin/create.py">Reset DB</a></li>
        <li><a href="/~jean/projet/cgi-bin/insert.py">Populate DB</a></li>
        <li><a href="/~jean/projet/cgi-bin/sql.py">SQL</a></li>
    </ul>
  </div>
</nav>
'''

print '''
<div class="row">
    <div class="col-sm-1"></div>
    <div class="col-sm-10">
        <h3>Analyze data</h3>
    </div>
    <div class="col-sm-1"></div>
</div>
<div class="row">
    <div class="col-sm-1"></div>
    <div class="col-sm-5">
    <form action="add.py" method="get" role="form">
        <div class="form-group">
            <label for="pdb_file">PDB File : </label>
            <input type="file" name="pdb_file"/>
        </div>
        <div class="form-group">
            <label for="pdb_chain">Chain : </label>
            <input class="form-control" type="text" name="pdb_chain" value="A"/>
        </div>
        <button type="submit" class="btn btn-default">Insert</button>
    </form>
</div>
<div class="col-sm-5">
    <form action="add.py" method="get" role="form">
        <div class="form-group">
            <label for="pdb_id">PDB ID : </label>
            <input class="form-control" type="text" name="pdb_id"/>
        </div>
        <div class="form-group">
            <label for="pdb_chain">Chain : </label>
            <input class="form-control" type="text" name="pdb_chain" value="A"/>
        </div>
        <button type="submit" class="btn btn-default">Insert</button>
    </form>
</div>
<div class="col-sm-1"></div>
</div>
'''

formulaire = cgi.FieldStorage()

if formulaire.getvalue('pdb_id') != None and formulaire.getvalue('pdb_chain') != None:
    structure = assign_pdb(str(formulaire.getvalue('pdb_id')), str(formulaire.getvalue('pdb_chain')))
    insert_into_db([structure, ])
    
elif formulaire.getvalue('pdb_file') != None and formulaire.getvalue('pdb_chain') != None:
    regex_pdbid = re.compile('(.*).pdb')
    found = regex_pdbid.search(str(formulaire.getvalue('pdb_file')))
    if found:
        pdb_id = found.group(1)
    else:
        pdb_id = 'default'
        
    chain = str(formulaire.getvalue('pdb_chain'))
    
    # TODO : Envoyer le fichier téléchargé dans le dossier data/
    
    ############# Chemins vers les scripts ############
    dssp_path = "../bin/dsspcmbi"

    dssppii_path = "../bin/dssppII.pl"

    xtlsstr_path = "../bin/XTLSSTR"

    segno_path = "../bin/segno"

    pross_path = "../bin/PROSS.py"

    segno_extractor_path = "../bin/parsers/extract_SEGNO2SEQ2D.pl"

    pross_extractor_path = "../bin/parsers/extract_PROSS2SEQ2D.pl"
    
    all1deg_path = "__RAMAPLOT=../bin/all1deg.data"
    segno_cmd = all1deg_path + " " + segno_path + " -pdb " + "../tmp/" + str(pdb_id) + ".pdb"
        
    #print "Assignation pour", pdb_id, "<br \>"
    structure = PDB_structure(pdb_id, chain)

    ############# Chemin vers les fichiers pdb correspondants ############
    pdb_file = "../data/" + pdb_id + ".pdb"

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
    
    insert_into_db([structure, ])
    
    print '''
    <div class="row">
        <div class="col-sm-2"></div>
        <div class="col-sm-8">
    '''
    print pdb_id, 'added into the database.'
    print '''
        </div>
        <div class="col-sm-2"></div>
    </div>
    '''
    

print '</body>'
#### FIN DU BODY ####

print '</html>'

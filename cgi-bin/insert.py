#!/usr/bin/env python
# -*- coding: utf-8 -*-

# POUR L'INSTANT GROS PROBLEME A CAUSE DES CHAINES ! A PRENDRE EN COMPTE DANS
# LE PARSING DES FICHIERS DE RESULTATS D'ASSIGNATION POUR NE GARDER QUE LES 
# DONNEES DE LA CHAINE INTERESSANTE ?

# OU EN AMONT, ENLEVER DES FICHIERS LES CHAINES DE MERDE PAR GET_PDB ?

import cgitb, cgi
import MySQLdb
import warnings


from bdd_classes import PDB_structure, Assignation
from bdd_functions import *


# Filtration des warnings
warnings.filterwarnings("ignore", category = MySQLdb.Warning)

#### Affichage des erreurs sur la page ####
cgitb.enable()

print "Content-type: text/html\n\n"

print "<html>"

##### HEADER #####
print '<head>'
print '<meta charset="UTF-8">'
print '<title>Data insertion</title>'
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
<h3>Insert in Database</h3>
'''

formulaire = cgi.FieldStorage()

print '''
<form action="insert.py" method="post" role="form" enctype="multipart/form-data">
    <div class="form-group">
        <label for="list_file">PDB List File : </label>
        <input type="file" name="list_file"/>
    </div>
    <div class="form-group">
        <label for="pseudo">Pseudo : </label>
        <input class="form-control" type="text" name="pseudo"/>
    </div>
    <div class="form-group">
        <label for="password">Password : </label>
        <input class="form-control" type="password" name="password"/>
    </div>
    <button type="submit" class="btn btn-default">Insert</button>
</form>
'''

if formulaire.has_key('list_file') and formulaire['list_file'].file and formulaire.getvalue('pseudo') != None and formulaire.getvalue('password') != None:
    # Accès et lecture de la BDD MySQL
    # Open database connection
    db = MySQLdb.connect("localhost","root","p=jlt56!", "bdd_m2")
    query = "SELECT count(*) FROM Users WHERE pseudo = \"{}\" AND password = \"{}\"".format(formulaire.getvalue('pseudo'), formulaire.getvalue('password'))
    cursor = db.cursor()
    cursor.execute(query)
    
    data = cursor.fetchone()
    if data[0] != 1:
        print "Failed to authenticate."
    else:
        # Assignation des SS
        ############# Création de l'objet structure PDB #################
        #arguments = cgi.FieldStorage()
        #pdb_id = arguments["pdb"].value
        
        
        # TODO : Le passage par un fichier de sortie n'est plus vraiment approprié, mais bon..
        with open("../tmp/" + formulaire['list_file'].filename, "w") as list_out:
            list_out.write(formulaire['list_file'].value)

        ############# Chemin vers la liste de PDB d'intérêt ############
        pdb_list_file = "../tmp/" + str(formulaire['list_file'].filename)

        pdb_list = read_pdb_list(pdb_list_file)

        structure_list = []

        for element in pdb_list:
            new_structure = assign_pdb(element["id"], element["chain"], "../data/"+ element["id"] + ".pdb")
            if new_structure != None:
                structure_list.append(new_structure)

        insert_into_db(structure_list)
        
        print "Tables populated successfully with<b>", len(structure_list), '</b>entries'

print '''
</div>
<div class="col-sm-1"></div>
</div>
'''

print '</body>'

#### FIN DU BODY ####

print '</html>'

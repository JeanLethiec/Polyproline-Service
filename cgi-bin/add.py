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
db = MySQLdb.connect("localhost","root","root","bdd_m2" )

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
    <form action="add.py" method="post" role="form" enctype="multipart/form-data">
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
    structure = assign_pdb(str(formulaire.getvalue('pdb_id')), str(formulaire.getvalue('pdb_chain')), "../data/" + str(formulaire.getvalue('pdb_id')) + ".pdb")
    insert_into_db([structure, ])
    
    print '''
    <div class="row">
        <div class="col-sm-1"></div>
        <div class="col-sm-10">
    '''
    print str(formulaire.getvalue('pdb_id')), 'added into the database.'
    print '''
        </div>
        <div class="col-sm-1"></div>
    </div>
    '''
    
elif formulaire.has_key('pdb_file') and formulaire['pdb_file'].file and formulaire.getvalue('pdb_chain') != None:
    # Création de l'ID
    regex_pdbid = re.compile('(.*).pdb')
    found = regex_pdbid.search(str(formulaire['pdb_file'].filename))
    if found:
        pdb_id = found.group(1)
    else:
        pdb_id = 'default'
    
    # Récupération de la chaine    
    chain = str(formulaire.getvalue('pdb_chain'))
    
    with open("../tmp/" + pdb_id + ".pdb", "w") as pdb_out:
        pdb_out.write(formulaire['pdb_file'].value)
    
    structure = assign_pdb(pdb_id, chain, "../tmp/" + pdb_id + ".pdb")

    insert_into_db([structure, ])
    
    print '''
    <div class="row">
        <div class="col-sm-1"></div>
        <div class="col-sm-10">
    '''
    print pdb_id, 'added into the database.'
    print '''
        </div>
        <div class="col-sm-1"></div>
    </div>
    '''
    

print '</body>'
#### FIN DU BODY ####

print '</html>'

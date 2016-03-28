#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgitb, cgi
import MySQLdb
import warnings

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
print '<title>SQL Query</title>'
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
        <h3>Custom SQL Query</h3>
        <form action="sql.py" method="get" role="form">
            <div class="form-group">
                <label for="pseudo">Pseudo : </label>
                <input class="form-control" type="text" name="pseudo"/>
            </div>
            <div class="form-group">
                <label for="password">Password : </label>
                <input class="form-control" type="password" name="password"/>
            </div>
            <div class="form-group">
                <label for="sql_query">SQL Query : </label>
                <input class="form-control" type="text" name="sql_query" placeholder="SELECT * FROM PDB"/>
            </div>
            <button type="submit" class="btn btn-default">Send</button>
        </form>
    </div>
    <div class="col-sm-"></div>
</div>
'''

formulaire = cgi.FieldStorage()

if formulaire.getvalue('sql_query') != None and formulaire.getvalue('pseudo') != None and formulaire.getvalue('password') != None:
    query = "SELECT count(*) FROM Users WHERE pseudo = \"{}\" AND password = \"{}\"".format(formulaire.getvalue('pseudo'), formulaire.getvalue('password'))
    cursor = db.cursor()
    cursor.execute(query)
    
    data = cursor.fetchone()
    print '''
            <div class="row">
                <div class="col-sm-1"></div>
                <div class="col-sm-10">
            '''
    if data[0] != 1:
        print "Failed to authenticate."
    else:
        cursor.execute(str(formulaire.getvalue('sql_query')))
        data = cursor.fetchall()
        if data != ():
            print '<h4>Results</h4>'
            for entry in data:
                for attribute in entry:
                    print attribute,
                print '<br \>'
    print '''
        </div>
        <div class="col-sm-1"></div>
    </div>
    '''

print '</body>'
#### FIN DU BODY ####

print '</html>'

#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

# Filtration des warnings
warnings.filterwarnings("ignore", category = MySQLdb.Warning)

#### Affichage des erreurs sur la page ####
cgitb.enable()

print "Content-type: text/html\n\n"

print "<html>"

##### HEADER #####
print '<head>'
print '<meta charset="UTF-8">'
print '<title>Data search</title>'
print '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" integrity="sha384-1q8mTJOASx8j1Au+a5WDVnPi2lkFfwwEAa8hDDdjZlpLegxhjVME1fgjWPGmkzs7" crossorigin="anonymous">'
print '</head>'
#### FIN DU HEADER ####

# Accès et lecture de la BDD MySQL
# Open database connection
db = MySQLdb.connect("localhost","root","p=jlt56!","bdd_m2" )

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

print "<h1>Search data in DB</h1>"

print '''
<h3>Search by PDB ID:</h3>
<form action="search.py" method="get">
    <input type="text" name="pdb_id"/>
    <input type="submit" value="Search"/>
</form>
'''

formulaire = cgi.FieldStorage()

if formulaire.getvalue('pdb_id') != None:
    print "<h4>Query PDB ID : <b>", formulaire.getvalue('pdb_id'), "</b></h4>"
    cursor = db.cursor()
    term = "\"%" + formulaire.getvalue('pdb_id') + "%\""
    query = "SELECT PDB.PDB_ID, PDB.chain, SS_Assign.method, SS_Assign.struct_sec FROM PDB INNER JOIN SS_Assign ON PDB.PDB_ID = SS_Assign.PDB_ID AND PDB.chain = SS_Assign.chain"
    # Ne permet pour le moment que la recherche multiple avec des espaces
    for i, item in enumerate(formulaire.getvalue('pdb_id').split()):
        if i == 0:
            query = query + " WHERE PDB.PDB_ID = \"" + item + "\" "
        else:
            query = query + "OR PDB.PDB_ID = \"" + item + "\" "
    print query
    cursor.execute(query)
    data = cursor.fetchall()
    if data == ():
        print "No results for", item
    else:
        print '<table><tr><th>PDB ID</th><th>Chain</th><th>Algorithm</th><th>Secondary Structure Sequence</th></tr>'
        for entry in data:
            print '<tr>'
            for attribute in entry: 
                print '<td>', attribute, '</td>'
            print '</tr>'
        print '</table>'
        
print '''
<h3>Display PDB in database:</h3>
<form action="search.py" method="get">
    <label for="pdb_min_resolution">Min resolution ?</label>
    <input type="text" name="pdb_min_resolution"/><br \>
    
    <label for="pdb_min_resolution">Max resolution ?</label>
    <input type="text" name="pdb_max_resolution"/><br \>
    
    <label for="pdb_min_resolution">Min size ?</label>
    <input type="text" name="pdb_min_size"/><br \>
    
    <label for="pdb_min_resolution">Max size ?</label>
    <input type="text" name="pdb_max_size"/><br \>
    
    <input type="submit" value="Search"/>
</form>
'''

if (formulaire.getvalue('pdb_min_resolution') != None) or (formulaire.getvalue('pdb_max_resolution') != None) or (formulaire.getvalue('pdb_min_size') != None) or (formulaire.getvalue('pdb_max_size') != None):
    if formulaire.getvalue('pdb_min_resolution') == None:
        min_resolution = "0";
    else:
        min_resolution = formulaire.getvalue('pdb_min_resolution');
    if formulaire.getvalue('pdb_max_resolution') == None:
        max_resolution = "1000";
    else:
        max_resolution = formulaire.getvalue('pdb_max_resolution');
    if formulaire.getvalue('pdb_min_size') == None:
        min_size = "0";
    else:
        min_size = formulaire.getvalue('pdb_min_size');
    if formulaire.getvalue('pdb_max_size') == None:
        max_size = "999999";
    else:
        max_size = formulaire.getvalue('pdb_max_size');
        
    print "<h4>Query: <b>", min_resolution, "</b>< Resolution <<b>", max_resolution, "</b> AND <b>", min_size, "</b>< Size <<b>", max_size, "</b></h4>"
    cursor = db.cursor()
    search_request = """
        SELECT 
            PDB.PDB_ID, PDB.chain
        FROM PDB 
        WHERE PDB.resol < %d AND PDB.resol > %d AND PDB.seq_size < %d AND PDB.seq_size > %d;""" % (max_resolution, min_resolution, max_size, min_size)
    cursor.execute(search_request)
    data = cursor.fetchall()
    if data == ():
        print "No results"
    else:
        print '<table><tr><th>PDB ID</th><th>Chain</th><th>Algorithm</th><th>Secondary Structure Sequence</th></tr>'
        for entry in data:
            print '<tr>'
            for attribute in entry: 
                print '<td>', attribute, '</td>'
            print '</tr>'
        print '</table>'
        
print '''
<h3>Search by keyword:</h3>
<form action="search.py" method="get">
    <input type="text" name="pdb_keyword"/>
    <input type="submit" value="Search"/>
</form>
'''

if formulaire.getvalue('pdb_keyword') != None:
    print "<h3>Query with keyword : <b>", formulaire.getvalue('pdb_keyword'), "</b></h3>"
    cursor = db.cursor()
    search_request = """
        SELECT 
            PDB.PDB_ID, PDB.chain, SS_Assign.method, SS_Assign.struct_sec
        FROM PDB 
        WHERE PDB.PDB_header LIKE "%%s%";""" % (formulaire.getvalue('pdb_keyword'))
    cursor.execute(search_request)
    data = cursor.fetchall()
    if data == ():
        print "No results"
    else:
        print '<table><tr><th>PDB ID</th><th>Chain</th><th>Algorithm</th><th>Secondary Structure Sequence</th></tr>'
        for entry in data:
            print '<tr>'
            for attribute in entry: 
                print '<td>', attribute, '</td>'
            print '</tr>'
        print '</table>'


print '</body>'
#### FIN DU BODY ####


print '</html>'

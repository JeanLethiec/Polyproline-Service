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
print '<title>Data read</title>'
print '<link rel="stylesheet" href="/~jean/projet/js-css/bootstrap.css">'
print '<link rel="stylesheet" href="/~jean/projet/js-css/style.css">'
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

print "<h1>All data in DB</h1>"

# Table PDB
print "<h2>Table PDB</h2>"
cursor = db.cursor()
cursor.execute("SELECT * FROM PDB")
data = cursor.fetchall()

print '<table><tr><th>PDB ID</th><th>Chain</th><th>Header</th><th>Sequence</th><th>Length</th><th>Resolution</th></tr>'
for entry in data:
    print '<tr>'
    for attribute in entry: 
        print '<td>', attribute, '</td>'
    print '</tr>'
print '</table>'

# Table SS_Assign
print "<h2>Table SS_Assign</h2>"
cursor = db.cursor()
cursor.execute("SELECT * FROM SS_Assign")
data = cursor.fetchall()

print '<table><tr><th>PDB ID</th><th>Chain</th><th>SS</th><th>Creation</th><th>Method</th></tr>'
for entry in data:
    print '<tr>'
    for attribute in entry: 
        print '<td>', attribute, '</td>'
    print '</tr>'
print '</table>'

print '</body>'
#### FIN DU BODY ####


print '</html>'

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
print '<title>About</title>'
print '<link rel="stylesheet" href="/~jean/projet/js-css/bootstrap.css">'
print '<link rel="stylesheet" href="/~jean/projet/js-css/jquery-ui.css">'
print '<link rel="stylesheet" href="/~jean/projet/js-css/jquery-tablesorter-bluestyle.css">'
print '<link rel="stylesheet" href="/~jean/projet/js-css/style.css">'
print '<script src="/~jean/projet/js-css/jquery-1.12.2.min.js"></script>'
print '<script src="/~jean/projet/js-css/jquery-ui.js"></script>'
print '<script src="/~jean/projet/js-css/jquery.tablesorter.js"></script>'

print '''
<script>
$(document).ready(function() 
    { 
        $("table").tablesorter(); 
    } 
);
</script> 
'''

print '</head>'
#### FIN DU HEADER ####

# Accès et lecture de la BDD MySQL
# Open database connection
db = MySQLdb.connect("localhost","root","root","bdd_m2" )

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
        <h3>Statistics</h3>
'''

cursor = db.cursor()

cursor.execute("SELECT COUNT(*) FROM PDB")
data = cursor.fetchone()

print "Number of PDB structures :<b>", data[0],"</b><br />"

cursor.execute("SELECT COUNT(*) FROM SS_Assign WHERE struct_sec != \"\"")
data = cursor.fetchone()

print "Number of SS assignations :<b>", data[0],"</b><br />"

cursor.execute('SELECT COUNT(*) FROM AA')
data = cursor.fetchone()

print "Number of amino-acids :<b>", data[0],"</b><br /><br />"

cursor.execute('SELECT method, COUNT(*) FROM SS_Assign WHERE struct_sec != \"\" GROUP BY method')
data = cursor.fetchall()
if data != ():
    print '<h4>Number of assignations by method</h4>'
    print '<table class="tablesorter"><thead><tr><th>Method</th><th>Number</th></tr></thead><tbody>'
    for entry in data:
        print '<tr>'
        for attribute in entry:
            print '<td>', attribute, '</td>'
        print '</tr>'
    print '</tbody></table><br />'

cursor.execute('SELECT struct_seq, COUNT(*) FROM AA GROUP BY struct_seq')
data = cursor.fetchall()
if data != ():
    print '<h4>Distribution of secondary structures assignations</h4>'
    print '<table class="tablesorter"><thead><tr><th>SS Type</th><th>Number</th></tr></thead><tbody>'
    for entry in data:
        print '<tr>'
        for attribute in entry:
            print '<td>', attribute, '</td>'
        print '</tr>'
    print '</tbody></table><br />'
        

cursor.execute('SELECT AVG(seq_size), MAX(seq_size), MIN(seq_size) FROM PDB')
data = cursor.fetchone()

print "Average peptide size : <b>", data[0],"</b><br />"
print "Min/Max peptide size : [<b>", data[2], ' - ', data[1], "</b>]<br /><br />"

cursor.execute('SELECT AVG(resol), MAX(resol), MIN(resol) FROM PDB')
data = cursor.fetchone()

print "Average resolution :<b>", data[0],"</b><br />"
print "Min/Max resolution : [<b>", data[2], ' - ', data[1], "</b>]<br />"


print '''
</div>
    <div class="col-sm-1"></div>
</div>
'''

print '</body>'
#### FIN DU BODY ####


print '</html>'

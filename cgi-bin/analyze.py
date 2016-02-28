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
print '<title>Data analysis</title>'
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

print "<h1>Data Analysis</h1>"

print '</body>'
#### FIN DU BODY ####


print '</html>'

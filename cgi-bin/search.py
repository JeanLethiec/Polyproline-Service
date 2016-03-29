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
print '<title>Data search</title>'
print '<link rel="stylesheet" href="/~jean/projet/js-css/bootstrap.css">'
print '<link rel="stylesheet" href="/~jean/projet/js-css/jquery-ui.css">'
print '<link rel="stylesheet" href="/~jean/projet/js-css/jquery-tablesorter-bluestyle.css">'
print '<link rel="stylesheet" href="/~jean/projet/js-css/style.css">'
print '<script src="/~jean/projet/js-css/jquery-1.12.2.min.js"></script>'
print '<script src="/~jean/projet/js-css/jquery-ui.js"></script>'
print '<script src="/~jean/projet/js-css/jquery.tablesorter.js"></script>'



# TODO : A améliorer en AJAX, lorsque données de trop grande dimension
print '''
<script>
$(function() {
	var availablePDB_ID = [
'''

cursor = db.cursor()
query = "SELECT PDB.PDB_ID FROM PDB"
cursor.execute(query)
data_all = cursor.fetchall()	
if data_all != ():
    for i, element in enumerate(data_all):
        if i < len(data_all)-1:
            print '"' + element[0] + '",'
        else:
            print '"' + element[0] + '"'
		        	
print '''
];
	$( "#pdb_id" ).autocomplete({
		source: availablePDB_ID,
		messages: {
            noResults: '',
            results: function() {}
    }
	});
});
</script>
'''

data = ()

# http://stackoverflow.com/questions/3148195/jquery-ui-autocomplete-use-startswith
# Match only beginning of a string for autocompletion
print '''
<script>
$(document).ready(function() 
    { 
        $("table").tablesorter(); 
    } 
); 
$.ui.autocomplete.filter = function (array, term) {
    var matcher = new RegExp("^" + $.ui.autocomplete.escapeRegex(term), "i");
    return $.grep(array, function (value) {
        return matcher.test(value.label || value.value || value);
    });
};
</script>
'''
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
        <h3>Search data in DB</h3>
  </div>
  <div class="col-sm-1"></div>
</div>
<div class="row">
  <div class="col-sm-1"></div>
  <div class="col-sm-3">
<h4>Search by PDB ID:</h4>
<form name="form_pdb_id" role="form" action="search.py" method="get">
    <div class="form-group">
        <label for="pdb_id">PDB ID:</label>
        <input class="form-control" type="text" name="pdb_id" id="pdb_id"/>
    </div>
    <button type="submit" class="btn btn-default">Search</button>
</form>
</div>
<div class="col-sm-4">
<h4>Display PDB in database:</h4>
<form action="search.py" method="get" role="form">
    <div class="form-group">
        <label for="pdb_min_resolution">Min resolution :</label>
        <input class="form-control" type="text" name="pdb_min_resolution"/><br \>
    </div>
    <div class="form-group">
        <label for="pdb_min_resolution">Max resolution :</label>
        <input class="form-control" type="text" name="pdb_max_resolution"/><br \>
    </div>
    <div class="form-group">
        <label for="pdb_min_resolution">Min size :</label>
        <input class="form-control" type="text" name="pdb_min_size"/><br \>
    </div>
    <div class="form-group">
        <label for="pdb_min_resolution">Max size :</label>
        <input class="form-control" type="text" name="pdb_max_size"/><br \>
    </div>
    <button type="submit" class="btn btn-default">Search</button>
</form>
    
<form role="form" action="search.py" method="get" class="form-inline">
    <input type="hidden" name="pdb_all" value="1"/>
    <button type="submit" class="btn btn-default">Display all PDB ID in DB</button>
</form>

</div>
<div class="col-sm-3">
    <h4>Search by keyword:</h4>
    <form role"form" action="search.py" method="get">
        <div class="form-group">
            <label for="pdb_keyword">Header keyword : </label>
            <input class="form-control" type="text" name="pdb_keyword"/>
        </div>
        <button type="submit" class="btn btn-default">Search</button>
    </form>
</div>
<div class="col-sm-1"></div>
</div>
<div class="row">
    <div class="col-sm-1"></div>
    <div class="col-sm-10">
'''

formulaire = cgi.FieldStorage()

# Requête pour PDB ID
if formulaire.getvalue('pdb_id') != None:
    cursor = db.cursor()
    term = "\"%" + formulaire.getvalue('pdb_id') + "%\""
    query = "SELECT PDB.PDB_ID, PDB.amino_seq, SS_Assign.method, SS_Assign.struct_sec FROM PDB INNER JOIN SS_Assign ON PDB.PDB_ID = SS_Assign.PDB_ID AND PDB.chain = SS_Assign.chain"
    # Ne permet pour le moment que la recherche multiple avec des espaces
    for i, item in enumerate(formulaire.getvalue('pdb_id').split()):
        if i == 0:
            query = query + " WHERE PDB.PDB_ID LIKE \"" + item + "\" "
        else:
            query = query + "OR PDB.PDB_ID LIKE \"" + item + "\" "
    #print query
    cursor.execute(query)
    data = cursor.fetchall()

# Requête pour PDB Header
if formulaire.getvalue('pdb_keyword') != None:
    cursor = db.cursor()
    search_request = """
        SELECT 
            PDB.PDB_ID, PDB.PDB_header, PDB.resol
        FROM PDB
        WHERE PDB.PDB_header LIKE "%{0}%";""".format(formulaire.getvalue('pdb_keyword'))
    cursor.execute(search_request)
    data = cursor.fetchall()

# Requête pour PDB Resolution et Size    
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
        
    cursor = db.cursor()
    search_request = """
        SELECT
            PDB.PDB_ID, PDB.PDB_header, PDB.resol, PDB.seq_size 
            FROM PDB 
        WHERE PDB.resol < %f AND PDB.resol > %f AND PDB.seq_size < %f AND PDB.seq_size > %f;""" % (float(max_resolution), float(min_resolution), float(max_size), float(min_size))
    cursor.execute(search_request)
    data = cursor.fetchall()

# Affichage de la query    
if formulaire.getvalue('pdb_keyword') != None:
    print "Results for :<b>", formulaire.getvalue('pdb_keyword'), '</b>'
elif formulaire.getvalue('pdb_id') != None:
    print "Results for :<b>", formulaire.getvalue('pdb_id'), '</b>'
elif formulaire.getvalue('pdb_min_resolution')!= None or formulaire.getvalue('pdb_max_resolution') != None or formulaire.getvalue('pdb_min_size') != None or formulaire.getvalue('pdb_max_size') != None:
    print "Results for :<b>", min_resolution, "</b>< Resolution <<b>", max_resolution, "</b> AND <b>", min_size, "</b>< Size <<b>", max_size, "</b>"

# Affichage des résultats
if data != ():
    # Résultats pour PDB header
    if formulaire.getvalue('pdb_keyword') != None:
        print '<table class="tablesorter"><thead><tr><th>PDB ID</th><th>Header</th><th>Resolution</th></tr></thead><tbody>'
        for entry in data:
            print '<tr>'
            for i, attribute in enumerate(entry): 
                if i == 0:
                    print '<td><a href="search.py?pdb_id=' + attribute + '">' + attribute +'</a></td>' 
                elif i == 1:
                    print '<td>', get_colored_keyword(attribute, formulaire.getvalue('pdb_keyword')), '</td>'
                else:
                    print '<td>', attribute, '</td>'
            print '</tr>'
        print '</tbody></table>'
    
    # Résultats pour PDB header
    elif formulaire.getvalue('pdb_min_resolution')!= None or formulaire.getvalue('pdb_max_resolution') != None or formulaire.getvalue('pdb_min_size') != None or formulaire.getvalue('pdb_max_size') != None:
        print '<table class="tablesorter"><thead><tr><th>PDB ID</th><th>Header</th><th>Resolution</th><th>Size</th></tr></thead><tbody>'
        for entry in data:
            print '<tr>'
            for i, attribute in enumerate(entry): 
                if i == 0:
                    print '<td><a href="search.py?pdb_id=' + attribute + '">' + attribute +'</a></td>' 
                else:
                    print '<td>', attribute, '</td>'
            print '</tr>'
        print '</tbody></table>'
        
    # Résultats pour PDB ID
    else:
        print '<table class="tablesorter"><thead><tr><th>PDB ID</th><th>Sequence</th><th>Algorithm</th><th>Secondary Structure Sequence</th></tr></thead><tbody>'
        for entry in data:
            print '<tr>'
            for i, attribute in enumerate(entry): 
                if i == 0:
                    print '<td><a href="http://www.rcsb.org/pdb/explore/explore.do?structureId=' + attribute + '"/>' + attribute + ' <a href="https://www.ebi.ac.uk/pdbsum/' + attribute + '" /><img src="/~jean/projet/pictures/pdbsum.gif" width="50px" height="25px"/></a><a href ="ramachandran.py?pdb_id=' + attribute + '"><img src="/~jean/projet/pictures/ramachandran.gif" width="25px" height="35px"/></a></td>' 
                elif i == 1:
                    print '<td>' + format_sequence(attribute) + '</td>'
                elif i == 3:
                    print '<td>' + get_colored_SS_sequence(attribute) + '</td>'
                else:
                    print '<td>' + attribute + '</td>'
            print '</tr>'
        print '</tbody></table>'

    # Résultats pour PDB All    
if formulaire.getvalue('pdb_all') != None and data_all != []:
    print '<table class="tablesorter"><thead><tr><th>PDB ID</th></tr></thead><tbody>'
    for entry in data_all:
        print '<tr>'
        print '<td>' + entry[0] + '</td>' 
        print '</tr>'
    print '</tbody></table>'
        
        

print '''
    </div>
    <div class="col-sm-1"></div>
</div>
'''

print '</body>'
#### FIN DU BODY ####


print '</html>'

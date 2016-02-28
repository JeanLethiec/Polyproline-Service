#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgitb, cgi
import MySQLdb
import warnings

# Filtration des warnings
warnings.filterwarnings("ignore", category = MySQLdb.Warning)

#### Affichage des erreurs sur la page ####
cgitb.enable()

print "Content-type: text/html\n\n"

print "<html>"

##### HEADER #####
print '<head>'
print '<meta charset="UTF-8">'
print '<title>Création des tables</title>'
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

print '<h3>Reset the database ?</h3>'

formulaire = cgi.FieldStorage()

if formulaire.getvalue('pseudo') == None or formulaire.getvalue('password') == None:
    print '''
    <form action="create.py" method="get">
        <label for="pseudo">Pseudo:</label>
        <input type="text" name="pseudo"/>
        <label for="password">Password:</label>
        <input type="text" name="password"/>
        <input type="submit" value="Reset"/>
    </form>
    '''
else:
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
        sql_statements = """      
                    DROP TABLE IF EXISTS AA;
                    DROP TABLE IF EXISTS SS_Assign;
                    DROP TABLE IF EXISTS PDB;
                    CREATE TABLE PDB (
                        PDB_ID VARCHAR(4),
                        chain CHAR(1),
                        PDB_header TEXT,
                        amino_seq TEXT,
                        seq_size SMALLINT,
                        resol FLOAT,
                        CONSTRAINT pk_PDB PRIMARY KEY (PDB_ID, chain)
                    );
                    CREATE TABLE SS_Assign (
                        PDB_ID VARCHAR(4),
                        chain CHAR(1),
                        struct_sec TEXT,
                        date_creation TIMESTAMP,
                        method VARCHAR(10),
                        CONSTRAINT pk_ssassign PRIMARY KEY (PDB_ID, chain, method)
                    );
                    ALTER TABLE SS_Assign ADD CONSTRAINT fk_ssassign_pdb1 FOREIGN KEY (PDB_ID, chain) REFERENCES PDB(PDB_ID, chain);
                    CREATE TABLE AA (
                        PDB_ID VARCHAR(4),
                        chain CHAR(1),
                        method VARCHAR(10),
                        num_aa INT,
                        struct_seq CHAR(1),
                        phi FLOAT,
                        psi FLOAT,
                        CONSTRAINT pk_ssassign PRIMARY KEY (PDB_ID, chain, method, num_aa)
                    );
                    ALTER TABLE AA ADD CONSTRAINT fk_aa_ssassign FOREIGN KEY (PDB_ID, chain, method) REFERENCES SS_Assign(PDB_ID, chain, method)
        """
                              
        for sql in sql_statements.split(";"):
            cursor = db.cursor()
            cursor.execute(sql)
            cursor.close()

        db.close()

        print "Tables reset successfully."

print '</body>'
#### FIN DU BODY ####

print '</html>'

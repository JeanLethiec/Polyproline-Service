#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgitb, cgi



#### Affichage des erreurs sur la page ####
cgitb.enable()

print "Content-type: text/html\n\n"

print "<html>"

##### HEADER #####
print '<head>'
print '<meta charset="UTF-8">'
print '<title>Results</title>'
print '<link rel="stylesheet" href="/~jean/projet/js-css/bootstrap.css">'
print '<link rel="stylesheet" href="/~jean/projet/js-css/style.css">'
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

print "<h1>Results</h1>"

print '</body>'
#### FIN DU BODY ####


print '</html>'



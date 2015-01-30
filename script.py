#!/usr/bin/python

import sys, os, yaml

configFile = "config.yaml" 
rutes = None
pathSites = "/etc/apache2/sites-available/"

# Handle Errors
try:
	stream = open(configFile, "r")
	rutes = yaml.load_all(stream)
except yaml.YAMLError, exc:
	if hasattr(exc, 'problem_mark'):
		mark = exc.problem_mark
		print "Error position: (%s:%s)" % (mark.line+1, mark.column+1)
	else:
		print "Error with %s" % (configFile)
except IOError:
	print "Not found file %s" % (configFile)

# If error with file, exit 
if rutes is None:
	exit()

# Functions
def showRutes():
	for rute in rutes:
	    for k,v in rute.items():
	        print k, "->", v
	    print "\n",

def checkIfNeedAlias(str):
	return str.count(".") == 1

def removePublic(str):
	if str.find("/public") != -1:
		str = str.replace("/public", "")
	return str

def createConfig(map, to):
	map2 = ""

	if checkIfNeedAlias(map):
		map2 = "ServerAlias %s" % (map)
		map = "www.%s" % (map)

	to2 = removePublic(to)

	sconfig =""" <VirtualHost *:80>
    ServerAdmin cristianace@outlook.com
    ServerName %s
    %s

    DocumentRoot /var/www/%s
    <Directory />
            Options FollowSymLinks
            AllowOverride None
    </Directory>
    <Directory /var/www/%s/>
            Options Indexes FollowSymLinks MultiViews
            AllowOverride All
            Order allow,deny
            allow from all
    </Directory>

    ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
    <Directory "/usr/lib/cgi-bin">
            AllowOverride None
            Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
            Order allow,deny
            Allow from all
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log

    # Possible values include: debug, info, notice, warn, error, crit,
    # alert, emerg.
    LogLevel warn

    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost> """ % (map, map2, to, to2)

	return sconfig

def createFile(to, strFile):
	fileName = removePublic(to) + ".conf"
	path = pathSites + fileName

	file = open(path, 'w')
	file.write(strFile)
	file.close()

	return fileName

def upSite(fileName):
	os.system('a2ensite '+ fileName)

def reloadApache():
	os.system('service apache2 reload')

def setSites(objFile):
	rutes = None

	for r in objFile:
		for k,_r in r.items():
			rutes = _r 

	for rute in rutes:
		strFile = createConfig(rute["map"], rute["to"])
		fileName = createFile(rute["to"], strFile)
		upSite(fileName)

	reloadApache()

# showRutes()

##############
# Init Script
##############
setSites(rutes)

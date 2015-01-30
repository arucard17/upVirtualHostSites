#!/usr/bin/python

import sys, os, yaml

configFile = "config.yaml" # archivo de configuración de los diferentes sitios que se alojaran
rutes = None # contenedor de las rutas obtenidas del archivo yaml
pathSites = "/etc/apache2/sites-available/" # carpeta de los sitios disponibles del Apache

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

# Función que revisa si el dominio necesita un alias
# De ser correcto, se le agregará al archivo la configuración de ServerAlias 
# 
# e.j. linkersoft.co
# el alias sería linkersoft.co
# y el nombre sería www.linkersoft.co
# 
# @param str, nombre del dominio
# @return boolean
def checkIfNeedAlias(str):
	return str.count(".") == 1


# Función que elimina la subcadena "/public"
# 
# @param str, cadena del path con el directorio donde irá la página web
# @return str, cadena sin la subcadena "/public"  
def removePublic(str):
	if str.find("/public") != -1:
		str = str.replace("/public", "")
	return str

# Función que genera el texto que irá en el archivo de configuración 
# para el dominio o subdominio
# 
# @param map, nombre del dominio
# @param to, nombre de la carpeta donde irá alojado el dominio
# @return sconfig, texto generado
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


# Función que crear si no existe o edita si existe el archivo de configuración
# del dominio
# 
# @param to, nombre de la carpeta contenedora
# @param strFile, texto de configuración generado en la función "createConfig"
# @return fileName, nombre del archivo generado
def createFile(to, strFile):
	fileName = removePublic(to) + ".conf"
	path = pathSites + fileName

	file = open(path, 'w')
	file.write(strFile)
	file.close()

	return fileName


# Función para habilitar el sitio
# 
# @param fileName, nombre del archivo de configuración del sitio
def upSite(fileName):
	os.system('a2ensite '+ fileName)


# Función para reiniciar el Apache al crear todos los archivos de configuración de los sitios
def reloadApache():
	os.system('service apache2 reload')


# Función que recorre los datos obtenidos del archivo de configuración 
# y genera toda la configuración para cada sitio 
# 
# @param objFile, objeto obtenido de la llamada del archivo "config.yaml"
# @return void
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


##############
# Init Script
##############
setSites(rutes)

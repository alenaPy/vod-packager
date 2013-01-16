#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Stand alone script
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from django.core.management import setup_environ
from Packager import settings
setup_environ(settings)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Modelo de la aplicacion
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from Packager_app import models

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# RPC XML
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# VPApiClient
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from VPApiClient import ItemMetadata, ItemMetadataLanguage, API_VERSION

import ApiSettings

from daemon import Daemon
import logging
import sys

def TestApiVersion(remote_api_version):
    global API_VERSION

    if remote_api_version != API_VERSION:
	return False
    else:
	return True


def VPAddItem(SmbPath=None, FileName=None, ItemMetadata=None, ItemMetadataLanList=[] ):

    if FileName is None or SmbPath is None or ItemMetadata is None:
	return False

    #
    # Se crea un nuevo Item
    #
    Item 			= models.Item()

    #
    # Se cargan los Datos Basicos
    #
    Item.name 			= ItemMetadata["name"]
    Item.format 		= ItemMetadata["format"]
    Item.metarial_type		= ItemMetadata["material_type"]
    #
    # Busca el Lenguage
    #
    try:
	print ItemMetadata["content_language"]
	Language = models.Language.objects.get(code=ItemMetadata["content_language"].lower())
    except:
	Language = models.Language.objects.get(code='en')
	#
	# Si no encuentra el Lenguage falla
	#
	#return False


    Item.content_language	= Language


    #
    # Buscar la Categoria
    #
    try:
	Category = models.Category.objects.get(name=ItemMetadata["category"])
    except:
	#
	# Si no existe la crea
	#
	Category = models.Category()
	Category.name = ItemMetadata["category"]
	Category.save()

    Item.category		= Category

    Item.run_time		= ItemMetadata["run_time"]
    Item.display_run_time	= ItemMetadata["display_runtime"]

    #
    # Busca el Country of Origin
    #
    try:
	Country	= models.Country.objects.get(code=ItemMetadata["country_of_origin"].upper())
    except:
	#
	# Si no existe hay un error, pero por default busca US y lo asigna, y sino, lo crea
	#
	try:
	    Country = models.Country.objects.get(code='US')
	except:
	    Country = models.Country()
	    Country.name = 'United States'
	    Country.code = 'US'
	    Country.save()

    Item.country_of_origin	= Country

    Item.episode_number 	= ItemMetadata["episode_id"]
    Item.episode_name		= ItemMetadata["episode_name"]
    Item.rating 		= ItemMetadata["rating"]
    Item.genres 		= ItemMetadata["genres"]
    Item.actors_display		= ItemMetadata["actors"]
    Item.year 			= ItemMetadata["year"]
    Item.director		= ItemMetadata["director"]
    Item.studio_name 		= ItemMetadata["studio_name"]
    Item.studio			= ItemMetadata["studio_name"]
    Item.mam_id 		= ItemMetadata["mam_id"]

    if ItemMetadata["show_type"].upper() == 'MOVIE':
	Item.show_type		= 'Movie'
    elif ItemMetadata["show_type"].upper() == 'SERIES':
	Item.show_type		= 'Series'

    Item.status			= 'N'
    Item.save()

    for ItemMetadataLan in ItemMetadataLanList:
	
    	MetadataLanguage 			= models.MetadataLanguage()
    	MetadataLanguage.item			= Item

	#
	# Buscar el lenguaje
	#
	try:
	    
	    Language	= models.Language.objects.get(code=ItemMetadataLan["language"].lower())

	    MetadataLanguage.language 		= Language
	    MetadataLanguage.title_sort_name 	= ItemMetadataLan["title_sort_name"]
	    MetadataLanguage.title_brief 	= ItemMetadataLan["title_brief"]
	    MetadataLanguage.title 		= ItemMetadataLan["title"]
	    MetadataLanguage.episode_title 	= ItemMetadataLan["episode_title"]
	    MetadataLanguage.summary_long 	= ItemMetadataLan["summary_long"]
	    MetadataLanguage.summary_medium 	= ItemMetadataLan["summary_short"]
	    MetadataLanguage.summary_short 	= ItemMetadataLan["summary_short"]
	    MetadataLanguage.save()
	    
	except:
	    print "Fallo Metadata Language"
	    pass

    ImportQueue = models.RenditionQueue()
    ImportQueue.item		= Item
    ImportQueue.file_name 	= FileName
    ImportQueue.svc_path	= SmbPath
    ImportQueue.queue_status	= 'Q'

    ImportQueue.save()
    return True

    
def main():

    logging.basicConfig(format='%(asctime)s - VPApiServer.py -[%(levelname)s]: %(message)s', filename='./log/VPApiServer.log',level=logging.INFO)

    server = SimpleXMLRPCServer((ApiSettings.SERVER_HOST, int(ApiSettings.SERVER_PORT)), allow_none=True)
    server.register_introspection_functions()
    server.register_function(VPAddItem)
    server.register_function(TestApiVersion)
    server.serve_forever()


class main_daemon(Daemon):
    def run(self):
        try:
    	    main()
	except KeyboardInterrupt:
	    sys.exit()	    

if __name__ == "__main__":
	daemon = main_daemon('./pid/VPApiServer.pid', stdout='./log/VPApiServer.log', stderr='./log/VPApiServer.log')
	if len(sys.argv) == 2:
		if 'start'     == sys.argv[1]:
			daemon.start()
		elif 'stop'    == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		elif 'run'     == sys.argv[1]:
			daemon.run()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart|run" % sys.argv[0]
		sys.exit(2)    


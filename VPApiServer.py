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
import Settings

from Lib.daemon import Daemon
import logging
import sys
import re


Meses = { '01' : 'Enero',
	  '02' : 'Febrero',
	  '03' : 'Marzo',
	  '04' : 'Abril',
	  '05' : 'Mayo',
	  '06' : 'Junio',
	  '07' : 'Julio',
	  '08' : 'Agosto',
	  '09' : 'Septiembre',
	  '10' : 'Octubre',
	  '11' : 'Noviembre',
	  '12' : 'Diciembre' }




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

    try:
	Item = models.Item.objects.get(name=ItemMetadata["name"])
	RQueue = models.RenditionQueue.objects.get(item=Item)
	RQueue.queue_status = 'Q'
	RQueue.save() 
	logging.info("VPAddItem(): Reimport an existing Item")
	return True
    except: 
	Item 			= models.Item()
	logging.info("VPAddItem(): Creating new Item")

    

    #
    # Se cargan los Datos Basicos
    #
    Item.name 			= ItemMetadata["name"]
    Item.material_type		= ItemMetadata["material_type"]
    Item.especial		= ItemMetadata["especial"]
    
    
    #
    # Si no existe el grupo lo crea
    #     
    try:
	ItemGroup = models.ItemGroup.objects.get(key=ItemMetadata["group"])
	logging.info("VPAddItem(): Using and existing item group [%s]" % ItemGroup.key)
    except:
	ItemGroup = models.ItemGroup()
	ItemGroup.key  = ItemMetadata["group"]
	logging.info("VPAddItem(): Creating a new item group [%s]" % ItemGroup.key)
	result = re.match("([0-9][0-9][0-9][0-9])([0-1][0-9])", ItemGroup.key)
	print result
	if result:
	    print result.group(1)
	    print result.group(2)
	    if int(result.group(2)) <= 12:
	
		ItemGroup.name = Meses[result.group(2)] + ', ' + result.group(1)		
	    print Meses[result.group(2)] + ', ' + result.group(1)
	    
	ItemGroup.save()
    	
    Item.group = ItemGroup  
    
    
    
    logging.info("VPAddItem(): Item Name:   " + Item.name)
    logging.info("VPAddItem(): Item Format: " + Item.format)
    logging.info("VPAddItem(): Item Material Type: " + Item.material_type)
    #
    # Busca el Lenguage
    #
    try:
	Language = models.Language.objects.get(code=ItemMetadata["content_language"].lower())
    except:
	logging.warning("VPAddItem(): Cannot find the specific language: " + ItemMetadata["content_language"].lower())
	try:
	    Language = models.Language.objects.get(code='en')
	except:
	    logging.error("VPAddItem(): Cannot find English language")
	    Language = models.Language()
	    Language.code = 'en'
	    Language.name = 'English'
	    Language.save()
	    logging.info("VPAddItem(): English language created")
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
	logging.warning("VPAddItem(): New category for this item: " + ItemMetadata["category"] )
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
	print ItemMetadata["country_of_origin"].upper()
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
    Item.actors_display		= ItemMetadata["actors_display"]
    Item.year 			= ItemMetadata["year"]
    Item.director		= ItemMetadata["director"]
    Item.studio_name 		= ItemMetadata["studio_name"]
    if Item.studio_name == 'Private' or Item.studio_name == 'Sextreme' or Item.studio_name == 'For Man' or Item.studio_name == 'Sexy Hot':
	Item.format = 'SD'
    else:    
	Item.format 		= ItemMetadata["format"]
    Item.studio			= ItemMetadata["studio_name"]

    Item.brand			= ItemMetadata["studio_name"]
    Item.mam_id 		= ItemMetadata["mam_id"]

    #
    # Agregado 7/6/2013
    #
    try:
	InternalBrand		= models.InternalBrand.objects.get(name=Item.brand)
    except:
	InternalBrand		= models.InternalBrand()
	InternalBrand.name	= Item.brand
	InternalBrand.format	= Item.format
	InternalBrand.save()
	
    Item.internal_brand = InternalBrand
    #
    # Fin Agregado 7/6/2013
    #


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

	    logging.info("Adding Metadata Language: " + ItemMetadataLan["language"].lower())

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
	    logging.error("Cannot find the specific language, fail to add Metadata Language: " + ItemMetadataLan["language"].lower())


    ImportQueue = models.RenditionQueue()
    ImportQueue.item		= Item
    ImportQueue.file_name 	= FileName
    ImportQueue.local_file	= 'N'
    

    ImportQueue.queue_status	= 'W'
	
    logging.info("New Rendition Queue: " + FileName  )

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
		elif 'status'  == sys.argv[1]:
			daemon.status()
	    
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart|run" % sys.argv[0]
		sys.exit(2)    


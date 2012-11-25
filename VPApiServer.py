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
from VPApiClient import ItemMetadata, ItemMetadataLanguage

def VPAddItem(SmbPath=None, FileName=None, ItemMetadata=None, ItemMetadataLanList=[] ):

    try:

	Item 			= models.Item()
        Item.name 		= ItemMetadata["name"]
        Item.format 		= ItemMetadata["format"]
        Item.episode_number 	= ItemMetadata["episode_number"]
        Item.rating 		= ItemMetadata["rating"]
        Item.genre 		= ItemMetadata["genre"]
        Item.actors 		= ItemMetadata["actors"]
        Item.origin_country 	= ItemMetadata["origin_country"]
        Item.year 		= ItemMetadata["year"]
        Item.director		= ItemMetadata["director"]
        Item.studio_name 	= ItemMetadata["studio_name"]
        Item.mam_id 		= ItemMetadata["mam_id"]
    
        Item.save()

        for ItemMatadataLan in ItemMetadataLanList:
    	    MetadataLanguage 				= models.MetadataLanguage()
    	    MetadataLanguage.title_sort_name 		= ItemMetadataLan["title_sort_name"]
	    MetadataLanguage.title_brief 		= ItemMetadataLan["title_brief"]
	    MetadataLanguage.title 			= ItemMetadataLan["title"]
	    MetadataLanguage.episode_tile 		= ItemMetadataLan["episode_tile"]
	    MetadataLanguage.summary_long 		= ItemMetadataLan["summary_long"]
	    MetadataLanguage.summary_medium 		= ItemMetadataLan["summary_medium"]
	    MetadataLanguage.summary_short 		= ItemMetadataLan["summary_short"]
	    
	    MetadataLanguage.save()
	    Item.metadata_language.add(MetadataLanuage)
	    Item.save()

	ImportQueue = models.ImportQueue()

        ImportQueue.item		= Item
        ImportQueue.file_name 		= FileName
        ImportQueue.svc_path		= SmbPath
        ImportQueue.queue_status	= 'Q'

	ImportQueue.save()
	return True

    except:

	return False

server = SimpleXMLRPCServer(("localhost", 8000))
server.register_introspection_functions()
server.register_function(VPAddItem)

server.serve_forever()

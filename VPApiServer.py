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

from daemon import Daemon
import logging
import sys


def VPAddItem(SmbPath=None, FileName=None, ItemMetadata=None, ItemMetadataLanList=[] ):

    if FileName is None or SmbPath is None or ItemMetadata is None:
	return False

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

    for ItemMetadataLan in ItemMetadataLanList:
    	MetadataLanguage 				= models.MetadataLanguage()
    	MetadataLanguage.language = ItemMetadataLan["language"]
	MetadataLanguage.title_sort_name 		= ItemMetadataLan["title_sort_name"]
	MetadataLanguage.title_brief 		= ItemMetadataLan["title_brief"]
	MetadataLanguage.title 			= ItemMetadataLan["title"]
	MetadataLanguage.episode_tile 		= ItemMetadataLan["episode_tile"]
	MetadataLanguage.summary_long 		= ItemMetadataLan["summary_long"]
	MetadataLanguage.summary_medium 		= ItemMetadataLan["summary_medium"]
	MetadataLanguage.summary_short 		= ItemMetadataLan["summary_short"]
	    
	MetadataLanguage.save()
	Item.metadata_language.add(MetadataLanguage)
	Item.save()

    ImportQueue = models.ImportQueue()

    ImportQueue.item		= Item
    ImportQueue.file_name 		= FileName
    ImportQueue.svc_path		= SmbPath
    ImportQueue.queue_status	= 'Q'

    ImportQueue.save()
    return True

    
def main():

    logging.basicConfig(format='%(asctime)s - VPApiServer.py -[%(levelname)s]: %(message)s', filename='./log/VPApiServer.log',level=logging.INFO)

    server = SimpleXMLRPCServer(("localhost", 8000))
    server.register_introspection_functions()
    server.register_function(VPAddItem)
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






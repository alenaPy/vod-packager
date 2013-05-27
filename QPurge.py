#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Carbon Coder
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from carbonapi.CarbonSocketLayer import *
from carbonapi.CarbonUtils import *
from carbonapi.CarbonJob import *
from carbonapi.CarbonSched import *

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import logging
import os
import time
import md5checksum
from datetime import datetime, timedelta

from daemon import Daemon

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


def GetItemsToPurge():
    return models.Item.objects.filter(kill_date__lte=datetime.now())


def DeleteMetadataLanguages(item = None):

    if item is not None:

	logging.info("DeleteMetadataLanguages(): Item: %s" % item.name)

        MetadataLanguages = models.MetadataLanguages.objects.filter(item=item)
        for ML in MetadataLanguages:
    	    logging.info("DeleteMetadataLanguages(): ID:" + str(ML.id))
	    ML.delete()

def DeleteRenditionQueue(item=None):
    if item is not None:
    
	logging.info("DeleteRenditionQueue(): Item: %s" % item.name)
	
	RenditionQueue = models.RenditionQueue.objects.filter(item=item)
	
	for RQueue in RenditionQueue:
	    if RQueue.local_file == 'Y':
		path = models.GetPath("local_master_path")
		if not path.endswith('/'):
		    path = path + '/'
		
		try:
		    os.unlink(path + RQueue.file_name)
		except:
		    logging.error("DeleteRenditionQueue(): Unable to delete file: %s" % path + RQueue.file_name)
		
	    logging.info("DeleteRenditionQueue(): ID: " +  str(RQueue.id))
	    RQueue.delete()
	    

def DeleteImageRendition(item=None):
    if item is not None:
	
	logging.info("DeleteImageRendition(): Item: %s" % item.name)
	
	ImageRendition = models.ImageRendition.objects.filter(item=item)
	image_path     = models.GetPath("image_local_path")
	
	for IRendition in ImageRendition:
	    logging.info("DeleteImageRendition(): Delete Image rendition file Name: %s" % IRendition.file_name)
	    try:
		os.unlink(image_path + '/' + IRendition.file_name)
	    except:
		logging.error("DeleteImageRendition(): Unable to delete file: %s" % IRendition.file_name)
	    IRendition.delete()


def DeleteVideoRendition(item=None):
    if item is not None:
	
	logging.info("DeleteVideoRendition(): Item: %s" % item.name)
	
	VideoRendition = models.VideoRendition.objects.filter(item=item)
	video_path     = models.GetPath("video_local_path")
	
	for VRendition in VideoRendition:
	    logging.info("DeleteVideoRendition(): Delete video rendition file Name: %s" % VRendition.file_name)
	    try:
		os.unlink(video_path + '/' + VRendition.file_name)
	    except:
		logging.error("DeleteVideoRendition(): Unable to delete file: %s" % VRendition.file_name)
	    VRendition.delete()

def DeletePackage(item=None):
    if item is not None:
	logging.info("DeletePackages(): Item: %s" % item.name)
	
	Packages = models.Package.objects.filter(item=item)
	
	for package in Packages:
	    logging.info("DeletePackages(): ID: " + str(package.id))
	    package.delete()


def main():

    logging.basicConfig(format='%(asctime)s - QPurge.py -[%(levelname)s]: %(message)s', filename='./log/QPurge.log',level=logging.INFO) 
   
    end = False

    while not end:
    
	items_to_purge = GetItemsToPurge()
	for items in items_to_purge:
	    DeleteRenditionQueue(items)	    
	    DeleteImageRendition(items)
	    DeleteVideoRendition(items)
	    DeletePackage(items)
	    items.delete()

	if Settings.GLOBAL_SLEEP_TIME:
	    time.sleep(Settings.SLEEP_TIME)
	else:
	    time.sleep(Settings.QPURGE_SLEEP)


class main_daemon(Daemon):
    def run(self):
        try:
    	    main()
	except KeyboardInterrupt:
	    sys.exit()	    

if __name__ == "__main__":
	daemon = main_daemon('./pid/QPurge.pid', stdout='./log/QPurge.err', stderr='./log/QPurge.err')
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





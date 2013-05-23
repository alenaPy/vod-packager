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

import sys


def usage():
    print "===="
    print "Nepe Manager Script - Put files in error"
    print "===="
    print ""
    print "Usage: python nm_markerror <list of video rendition with error>"
    print ""
    

if len(sys.argv) == 1:
    usage()

else:
    try:
	File = open(sys.argv[1])
    except:
	print "Error: Archivo " + sys.argv[1] + " no encontrado"
	sys.exit(-1)

    for f in File.readlines():
	file, enter = f.split('\n')
	try:        
	    VRendition = models.VideoRendition.objects.get(file_name=file)
    	    print str(VRendition.id) + " - " + file
    	    VRendition.status ='E'
    	    VRendition.save()
    	    item = VRendition.item
    	    item.status = 'W'
    	    item.save()
	except:
    	    print "Error: File " + file + " No encontrado en la lista de Video Renditions"
	    


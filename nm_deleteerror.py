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
from datetime import datetime, timedelta

from Lib.daemon import Daemon

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


def GetVideoRenditionError():
    return models.VideoRendition.objects.filter(status='E')


def GetImageRenditionError():
    return models.ImageRendition.objects.filter(status='E')
    

def RequeueItems():

    Items = models.Item.objects.filter(status='W')
    for item in Items:
	try:
	    RQueue = models.RenditionQueue.objects.get(item=item)
	    RQueue.queue_status = 'W'
	    RQueue.save()
	except:
	    print "Error"
	     
	    
def DeleteVideoRendition(VideoRendition=None):
    if VideoRendition is not None:
	
	video_path     = models.GetPath("video_local_path")
	

        print ("DeleteVideoRendition(): Delete video rendition file Name: %s" % VideoRendition.file_name)
        try:
	    os.unlink(video_path + '/' + VideoRendition.file_name)
	except:
	    print ("ERROR: DeleteVideoRendition(): Unable to delete file: %s" % VideoRendition.file_name)
	VideoRendition.delete()


def DeleteImageRendition(ImageRendition=None):
    if ImageRendition is not None:
	
	image_path     = models.GetPath("image_local_path")
	

        print ("DeleteImageRendition(): Delete Image rendition file Name: %s" % ImageRendition.file_name)
        try:
	    os.unlink(image_path + '/' + ImageRendition.file_name)
	except:
	    print ("ERROR: DeleteVideoRendition(): Unable to delete file: %s" % ImageRendition.file_name)
	ImageRendition.delete()

def main():

    VideoErrors = GetVideoRenditionError()
    
    for error in VideoErrors:
	DeleteVideoRendition(error)

    ImageErrors = GetImageRenditionError()
    for error in ImageErrors:
	DeleteImageRendition(error)

    RequeueItems()


main()



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


def FileExist(path, file):
    if os.path.isfile(path+file):
	return True

    return False

def GetJobState(transcoder_ip, job_guid):
    
    carbon = CarbonSocketLayer(transcoder_ip)
    Job = CarbonJob(carbon, job_guid)
    #
    # DEBUG
    #
    logging.info("GetJobState(): Job Progress: " + str(Job.GetProgress()))
    logging.info("GetJobState(): Job State: " + Job.GetState())
    
    return Job.GetState()



def CheckItemStatus():

    logging.info("CheckItemStatus(): Start Item check")
    
    for Item in models.GetProcessingItems():

	logging.info("CheckItemStatus(): Checking item: %s" % Item.name)

	VRenditionList = models.VideoRenditions.objects.filter(item=Item)

	vr_total    = len(VRenditionList)
	vr_queued   = 0
	vr_finished = 0
	vr_error    = 0
	for VRendition in VRenditionList:
	    if VRendition.status   == 'Q':
		vr_queued   = queued + 1
	    elif VRendition.status == 'F':
		vr_finished = finished + 1
	    elif VRendition.status == 'E':
		vr_error    = error +1

	IRenditionList = models.ImageRenditions.objects.filter(item=Item)

	ir_total   = len(IRenditionList)
	ir_empty   = 0
	ir_filled  = 0

	for IRendition in IRenditionList:
	    if IRendition.status   == 'E':
		ir_empty  = ir_empty  + 1
	    elif IRendition.status == 'F':
		ir_filled = ir_filled + 1

	if vr_total == vr_queued and ir_total == ir_filled:
	    #
	    # Termino de procesarse todo
	    #
	    Item.status = 'D'
	    Item.save()
	else:
	    if vr_error > 0:
		Item.status = 'W'
		Item.save()
    logging.info("CheckItemStatus(): End Item Check")


def CheckVideoRenditionStatus():
    
    logging.info("CheckVideoRenditionStatus(): Start Check Video Rendition Status")
        
    video_local_path = models.GetPath("video_local_path")

    logging.debug("CheckVideoRenditionStatus(): video_local_path: " + video_local_path)
    
    if video_local_path is None:
	logging.error("CheckVideoRenditionStatus(): Config Error, video_local_path not defined")
	return False

    #
    # Agrega / si no es que exite al final
    #
    if not video_local_path.endswith('/'):
	video_local_path = video_local_path + '/'

    #
    # Trae todos los video rendition cuyo Status = Q
    #
    for VRendition in models.GetVideoRenditionQueue():
	
	logging.info("CheckVideoRenditionStatus(): Video Rendition Check: " + VRendition.file_name)
	logging.info("CheckVideoRenditionStatus(): Video Rendition Item: " + VRendition.item.name)

	logging.info("CheckVideoRenditionStatus(): Transcoding Server: " + VRendition.transcoding_server.ip_address)
	logging.info("CheckVideoRenditionStatus(): Job GUID: " + VRendition.transcoding_job_guid)
	
	JobState = GetJobState(VRendition.transcoding_server.ip_address, VRendition.transcoding_job_guid)
	
	if JobState == 'NEX_JOB_COMPLETED':
	    #
	    # Si el Job termino de procesarse correctamente
	    # 
	    # Comprueba la existencia del File
	    #
	    logging.info("CheckVideoRenditionStatus(): Video Rendition finish transcoding: " + VRendition.file_name)
	    
	    if FileExist(video_local_path, VRendition.file_name):
		#
		# Si el archivo existe
		#
		# - Calcula su checksum
		# - Calcula su filesize
		# - Establece su Status en F -> Finished
	    
	        VRendition.checksum = md5checksum.md5_checksum(video_local_path + VRendition.file_name)
		logging.debug("CheckVideoRenditionStatus(): Video Rendition Checksum: " + VRendition.file_name + "," + VRendition.checksum)	
		
		VRendition.file_size = os.stat(video_local_path + VRendition.file_name).st_size
		logging.debug("CheckVideoRenditionStatus(): Video Rendition FileSize: " + VRendition.file_name + "," + str(VRendition.file_size))
		
		VRendition.status   = 'F'
		VRendition.save()
		
		logging.info("CheckVideoRenditionStatus(): Video Rendition finish all procesing: " + VRendition.file_name)
	    else:
		#
		# Si el archivo no existe es porque se produjo un error
		#
		logging.error("CheckVideoRenditionStatus(): Video Rendition not exist: [FILE]-> " + VRendition.file_name + ", [PATH]-> " + video_local_path)
		VRendition.status   = 'E'
		VRendition.save()    
	    
        else:
    	    if JobState == 'NEX_JOB_ERROR':
    		#
    		# Si el job termino con errores
    		#
    		
    		VRendition.status = 'E'
    		VRendition.save()
    	
    logging.info("CheckVideoRenditionStatus(): End Check Video Rendition Status")
    return True
    	

def main():

    logging.basicConfig(format='%(asctime)s - QCheckerD.py -[%(levelname)s]: %(message)s', filename='./log/QChecker.log',level=logging.INFO) 
   
    while 1:
	CheckVideoRenditionStatus()
	CheckItemStatus()
	time.sleep(60)

class main_daemon(Daemon):
    def run(self):
        try:
    	    main()
	except KeyboardInterrupt:
	    sys.exit()	    

if __name__ == "__main__":
	daemon = main_daemon('./pid/QChecker.pid', stdout='./log/QChecker.err', stderr='./log/QChecker.err')
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





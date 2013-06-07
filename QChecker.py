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
import Settings

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funciones - Utileria
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from Lib.Utils  import SplitExtension
from Lib.Utils  import RenditionFileName
from Lib.Utils  import PrefixStrId
from Lib.Utils  import FileExist
from Lib.daemon import Daemon
from Lib.CarbonLocal import GetJobState
from Lib.CarbonLocal import GetJobSpeed
from Lib.CarbonLocal import RemoveJob
from Lib.CarbonLocal import StopJob
from Lib.CarbonLocal import GetJobError
from Lib.md5checksum import md5_checksum


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



def CheckItemStatus():

    logging.info("CheckItemStatus(): Start Item check")
    
    for Item in models.GetProcessingItems():

	logging.info("CheckItemStatus(): Checking item: %s" % Item.name)

	VRenditionList = models.VideoRendition.objects.filter(item=Item)

	vr_total    = len(VRenditionList)
	vr_queued   = 0
	vr_unassig  = 0
	vr_finished = 0
	vr_error    = 0
	for VRendition in VRenditionList:
	    if VRendition.status   == 'Q':
		vr_queued   = vr_queued   + 1
	    elif VRendition.status == 'F':
		vr_finished = vr_finished + 1
	    elif VRendition.status == 'E':
		vr_error    = vr_error    + 1

	IRenditionList = models.ImageRendition.objects.filter(item=Item)

	ir_total   	= len(IRenditionList)
	ir_unfilled 	= 0
	ir_filled	= 0
	ir_done	   	= 0
	ir_error   	= 0

	for IRendition in IRenditionList:
	    if IRendition.status   == 'U':
		ir_unfilled	= ir_unfilled  + 1
	    elif IRendition.status == 'F':
		ir_filled 	= ir_filled + 1
	    elif IRendition.status == 'D':
		ir_done		= ir_done   + 1
	    elif IRendition.status == 'E':
		ir_error  	= ir_error  + 1

	if vr_total <= vr_finished:
	    try:
		RQ = models.RenditionQueue.objects.get(item=Item)
	        if RQ.local_file == 'Y':
	    	    master_path = models.GetPath("local_master_path")
	    	    if not master_path.endswith('/'):
	    		master_path = master_path + '/'
		    
		    logging.info("CheckItemStatus(): Deleting Master File: %s" % master_path+RQ.file_name)
		    if FileExist(master_path,RQ.file_name):
			os.unlink(master_path+RQ.file_name)
		    RQ.local_file = 'N'
		    RQ.local_svc_path = ''
		    RQ.save()
		    
	    except:
		logging.error("CheckItemStatus(): Deleting Master File: %s" % master_path+RQ.file_name)


	if vr_total == vr_finished and ir_total == ir_done:
	    #
	    # Termino de procesarse todo
	    #
	    Item.status = 'D'
	    Item.save()
	else:
	    if vr_error > 0 or ir_error > 0:
		Item.status = 'W'
		Item.save()

    logging.info("CheckItemStatus(): End Item Check")


def CheckImageRenditionStatus():

    logging.info("CheckImageRenditionStatus(): Start Check Imagen Rendition Status")
        
    image_local_path = models.GetPath("image_local_path")


    
    if image_local_path is None:
	logging.error("CheckImageRenditionStatus(): Config Error, image_local_path not defined")
	return False

    logging.debug("CheckImageRenditionStatus(): image_local_path: " + image_local_path)

    #
    # Agrega / si no es que exite al final
    #
    if not image_local_path.endswith('/'):
	image_local_path = image_local_path + '/'
    

    #
    # Trae todos los image rendition cuyo Status = F
    #


    for IRendition in models.GetImageRenditionQueue():

	logging.info("CheckImageRenditionStatus(): Image Rendition Check: " + IRendition.file_name)
	logging.info("CheckImageRenditionStatus(): Image Rendition Item: " +  IRendition.item.name)

	if FileExist(image_local_path, IRendition.file_name):
	    #
	    # Si el archivo existe
	    #
	    # - Calcula su checksum
	    # - Calcula su filesize
	    # - Establece su Status en F -> Finished
	    
	    IRendition.checksum = md5_checksum(image_local_path + IRendition.file_name)
	    logging.debug("CheckImageoRenditionStatus(): Image Rendition Checksum: " + IRendition.file_name + "," + IRendition.checksum)	
	    
	    IRendition.file_size = os.stat(image_local_path + IRendition.file_name).st_size
	    logging.debug("CheckImageRenditionStatus(): Image Rendition FileSize: " + IRendition.file_name + "," + str(IRendition.file_size))
	    
	    IRendition.status   = 'D'
	    IRendition.save()
	    
	    logging.info("CheckImageRenditionStatus(): Image Rendition finish all procesing: " + IRendition.file_name)
	else:
	    #
	    # Si el archivo no existe es porque se produjo un error
	    #
    	    logging.error("CheckImageRenditionStatus(): Image Rendition not exist: [FILE]-> " + IRendition.file_name + ", [PATH]-> " + image_local_path)
	    IRendition.status   = 'E'
	    IRendition.error	= "Image Rendition not exist: [FILE]-> " + IRendition.file_name + ", [PATH]-> " + image_local_path
	    IRendition.save()    


    logging.info("CheckImageRenditionStatus(): End Check Image Rendition Status")
    return True



def CancelVideoRenditions():
    
    logging.info("CancelVideoRendition(): Start Canceling Video Rendition")
    
    video_local_path = models.GetPath("video_local_path")


    
    if video_local_path is None:
	logging.error("CanceVideoRenditions(): Config Error, video_local_path not defined")
	return False

    logging.debug("CancelVideoRenditions(): video_local_path: " + video_local_path)

    #
    # Agrega / si no es que exite al final
    #
    if not video_local_path.endswith('/'):
	video_local_path = video_local_path + '/'
    

    for VRendition in models.VideoRendition.objects.filter(status='C'):
    
	JobState, Progress = GetJobState(VRendition.transcoding_server.ip_address, VRendition.transcoding_job_guid)
	
	logging.info("GetJobState(): Job Progress: " + str(Progress))
	logging.info("GetJobState(): Job State: " + JobState)

	if JobState == 'NEX_JOB_COMPLETED':
	    #
	    # Si el Job termino de procesarse
	    # 
	    logging.info("CancelVideoRenditions(): Video Rendition finish transcoding: -> Unlink: " + VRendition.file_name)
	    os.unlink(video_local_path + VRendition.file_name)
	
	else:
	    logging.info("CancelVideoRenditions(): Stopping Job: " + VRendition.transcoding_job_guid + " Server: " + VRendition.transcoding_server_ip_address )
	    StopJob(VRendition.transcoding_server.ip_address, VRendition.transcoding_job_guid)
	        
	VRendition.delete()
	

def CheckVideoRenditionStatus():
    
    logging.info("CheckVideoRenditionStatus(): Start Check Video Rendition Status")
        
    video_local_path = models.GetPath("video_local_path")


    
    if video_local_path is None:
	logging.error("CheckVideoRenditionStatus(): Config Error, video_local_path not defined")
	return False

    logging.debug("CheckVideoRenditionStatus(): video_local_path: " + video_local_path)

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
	
	
	
	JobState, Progress = GetJobState(VRendition.transcoding_server.ip_address, VRendition.transcoding_job_guid)
	logging.info("GetJobState(): Job Progress: " + str(Progress))
	logging.info("GetJobState(): Job State: " + JobState)
	
	if JobState == 'NEX_JOB_COMPLETED':
	    #
	    # Si el Job termino de procesarse correctamente
	    # 
	    # Comprueba la existencia del File
	    #
	    logging.info("CheckVideoRenditionStatus(): Video Rendition finish transcoding: " + VRendition.file_name)
	
	    if VRendition.video_profile.need_to_be_checked == 'T': 
	
	    
		if FileExist(video_local_path, VRendition.file_name):
		    #
		    # Si el archivo existe
		    #
		    # - Calcula su checksum
		    # - Calcula su filesize
		    # - Establece su Status en F -> Finished
	    
	    	    VRendition.checksum = md5_checksum(video_local_path + VRendition.file_name)
		    logging.debug("CheckVideoRenditionStatus(): Video Rendition Checksum: " + VRendition.file_name + "," + VRendition.checksum)	
		
		    VRendition.file_size = os.stat(video_local_path + VRendition.file_name).st_size
		    logging.debug("CheckVideoRenditionStatus(): Video Rendition FileSize: " + VRendition.file_name + "," + str(VRendition.file_size))
		
		    VRendition.status   = 'F'
		    VRendition.progress = '100'
		    VRendition.save()
		
		    logging.info("CheckVideoRenditionStatus(): Video Rendition finish all procesing: " + VRendition.file_name)
		else:
		    #
		    # Si el archivo no existe es porque se produjo un error
		    #
		    logging.error("CheckVideoRenditionStatus(): Video Rendition not exist: [FILE]-> " + VRendition.file_name + ", [PATH]-> " + video_local_path)
		    VRendition.status   = 'E'
		    VRendition.error    = "Video Rendition not exist: [FILE]-> " + VRendition.file_name + ", [PATH]-> " + video_local_path
		    VRendition.save()    
	    else:
		VRendition.status = 'F'
		VRendition.progress = '100'
		logging.info("RemoveJob(): Job Removing: " + VRendition.transcoding_job_guid)
		#RemoveJob(VRendition.transcoding_server.ip_address, VRendition.transcoding_job_guid)
		VRendition.save()
	    
        else:
	    if JobState == 'NEX_JOB_STARTED':
		VRendition.speed = GetJobSpeed(VRendition.transcoding_server.ip_address, VRendition.transcoding_job_guid)
		VRendition.progress = str(Progress)
		VRendition.save()
		
    	    if JobState == 'NEX_JOB_ERROR':
    		#
		# Si el job termino con errores
    		#
    		
    		VRendition.status = 'E'
		VRendition.error  = GetJobError(VRendition.transcoding_server.ip_address, VRendition.transcoding_job_guid)
		logging.info("RemoveJob(): Job Removing: " + VRendition.transcoding_job_guid)
    		#RemoveJob(VRendition.transcoding_server.ip_address, VRendition.transcoding_job_guid)
    		VRendition.save()
	    
	    if JobState == 'NEX_JOB_STOPPED':
    		#
		# Alguien Freno el Job
		# 
		VRendition.status = 'E'
		VRendition.error  = "Stop Job"
		logging.info("RemoveJob(): Job Removing: " + VRendition.transcoding_job_guid)
		#RemoveJob(VRendition.transcoding_server.ip_address, VRendition.transcoding_job_guid)
		VRendition.save()

	    if JobState == '':
		VRendition.status = 'E'
		VRendition.error  = "Job State Empty"
		VRendition.save()

    logging.info("CheckVideoRenditionStatus(): End Check Video Rendition Status")
    return True
    	

def main():

    logging.basicConfig(format='%(asctime)s - QCheckerD.py -[%(levelname)s]: %(message)s', filename='./log/QChecker.log',level=logging.INFO) 
   
    end = False

    while not end:
	CancelVideoRenditions()
    
	if not CheckVideoRenditionStatus():
	    logging.error("main(): Critical error, please check your config [SHUTDOWN]")
	    end = True
	    continue
	if not CheckImageRenditionStatus():
	    logging.error("main(): Critical error, please check your config [SHUTDOWN]")
	    end = True
	    continue

	CheckItemStatus()

	if Settings.GLOBAL_SLEEP_TIME:
	    time.sleep(Settings.SLEEP_TIME)
	else:
	    time.sleep(Settings.QCHECKER_SLEEP)
	    
    
    logging.info("main(): End loop")

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

		elif 'status'  == sys.argv[1]:
			daemon.status()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart|run" % sys.argv[0]
		sys.exit(2)





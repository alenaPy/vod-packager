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
import md5checksum

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


def GetVideoRenditionQueue():
    return models.VideoRendition.objects.filter(status='Q')
    
def GetPath(path=None):
    if path is not None:
	return models.Path.objects.get(key=path).location
    return None

    
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
    logging.debug("GetJobState(): Job Progress: " + str(Job.GetProgress()))
    logging.debug("GetJobState(): Job State: " + Job.GetState())
    
    return Job.GetState()



def CheckQueue():
    
    logging.info("CheckQueue(): Start queue check")
        
    video_local_path = GetPath("video_local_path")

    logging.debug("CheckQueue(): video_local_path: " + video_local_path)
    
    if video_local_path is None:
	logging.error("CheckQueue(): Config Error, video_local_path not defined")
	return False

    #
    # Agrega / si no es que exite al final
    #
    if not video_local_path.endswith('/'):
	video_local_path = video_local_path + '/'

    #
    # Trae todos los video rendition cuyo Status = Q
    #
    for rendition in GetVideoRenditionQueue():
	
	logging.info("CheckQueue(): Video Rendition Check: " + rendition.file_name)
	logging.info("CheckQueue(): Video Rendition Item: " + rendition.item.name)

	logging.debug("CheckQueue(): Transcoding Server: " + rendition.transcoding_server.ip_address)
	logging.debug("CheckQueue(): Job GUID: " + rendition.transcoding_job_guid)
	
	JobState = GetJobState(rendition.transcoding_server.ip_address, rendition.transcoding_job_guid)

	if JobState == 'NEX_JOB_COMPLETED':
	    #
	    # Si el Job termino de procesarse correctamente
	    # 
	    # Comprueba la existencia del File
	    #
	    logging.info("CheckQueue(): Video Rendition finish transcoding: " + rendition.file_name)
	    
	    if FileExist(video_local_path, rendition.file_name):
		#
		# Si el archivo existe
		#
		# - Calcula su checksum
		# - Calcula su filesize
		# - Establece su Status en F -> Finished
	    
	        rendition.checksum = md5checksum.md5_checksum(video_local_path + rendition.file_name)
		logging.debug("CheckQueue(): Video Rendition Checksum: " + rendition.file_name + "," + rendition.checksum)	
		
		rendition.filesize = os.stat(video_local_path + rendition.file_name).st_size
		logging.debug("CheckQueue(): Video Rendition FileSize: " + rendition.file_name + "," + rendirion.filesize)
		
		rendition.status   = 'F'
		rendition.save()
		
		logging.info("CheckQueue(): Video Rendition finish all procesing: " + rendition.file_name)
	    else:
		#
		# Si el archivo no existe es porque se produjo un error
		#
		logging.error("CheckQueue(): Video Rendition not exist: [FILE]-> " + rendition.file_name + ", [PATH]-> " + video_local_path)
		rendition.status   = 'E'
		rendition.save()    
	    
        else:
    	    if JobState == 'NEX_JOB_ERROR':
    		#
    		# Si el job termino con errores
    		#
    		
    		rendition.status = 'E'
    		rendition.save()
    	
    logging.info("CheckQueue(): End queue Check")
    return True
    	

logging.basicConfig(format='%(asctime)s - QCheckerD.py -[%(levelname)s]: %(message)s', filename='./log/QChecker.log',level=logging.DEBUG) 
   	
CheckQueue()	                                                                


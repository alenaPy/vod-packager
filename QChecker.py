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
    logging.info("GetJobState(): Job Progress: " + str(Job.GetProgress()))
    logging.info("GetJobState(): Job State: " + Job.GetState())
    
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

	logging.info("CheckQueue(): Transcoding Server: " + rendition.transcoding_server.ip_address)
	logging.info("CheckQueue(): Job GUID: " + rendition.transcoding_job_guid)
	
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
		
		rendition.file_size = os.stat(video_local_path + rendition.file_name).st_size
		logging.debug("CheckQueue(): Video Rendition FileSize: " + rendition.file_name + "," + str(rendition.file_size))
		
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
    	

def main():

    logging.basicConfig(format='%(asctime)s - QCheckerD.py -[%(levelname)s]: %(message)s', filename='./log/QChecker.log',level=logging.INFO) 
   
    while 1:
	CheckQueue()
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





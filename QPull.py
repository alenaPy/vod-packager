#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Local
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import logging
import os
import sys
import time
import shutil
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funciones - Utileria
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from Lib.Utils  import FileExist
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

import Settings


ErrorString = ''


def PullFile(SrcPath=None,FileName=None,DstPath=None):


    global ErrorString

    ErrorString = ''

    if SrcPath is not None and FileName is not None and DstPath is not None:
	
	if not SrcPath.endswith('/'):
	    SrcPath = SrcPath + '/'
	    
	if not DstPath.endswith('/'):
	    DstPath = DstPath + '/'
	    
	if not FileExist(SrcPath,FileName):
	    ErrorString = 'Unable to find File: %s' % SrcPath+FileName
	    return False
	try:	    
	    if Settings.PULL_LIMIT_AVAILABLE:
		os.system("pv -L %s \'" % Settings.PULL_LIMIT + SrcPath+FileName + "\' > \'" + DstPath+FileName + "\'")
	    else:
		shutil.copy(SrcPath+FileName, DstPath)
	    
	    return True

	except shutil.Error, exc:
	    errors = exc.args[0]
	    ErrorString = str(errors)
	    return False	


def ProcessWaitingRenditionQueue():

    
    logging.info("ProcessWaitingRenditionQueue(): Start Processing Waiting Rendition Queue")

    LocalRepository    = models.GetPath('local_master_path')	
    LocalSvcPath       = models.GetPath('local_master_smb')
    ExternRepositorySD = models.GetPath('remote_nfs_sd')
    ExternRepositoryHD = models.GetPath('remote_nfs_hd')

    logging.info("ProcessWaitingRenditionQueue(): Local Repository -> %s" % LocalRepository)
    logging.info("ProcessWaitingRenditionQueue(): Locasl SVC Path  -> %s" % LocalSvcPath)
    logging.info("ProcessWaitingRenditionQueue(): Exter Repository SD -> %s" % ExternRepositorySD)
    logging.info("ProcessWaitingRenditionQueue(): Exter Repository HD -> %s" % ExternRepositoryHD)

    if LocalRepository is not None and ExternRepositorySD is not None and ExternRepositoryHD is not None and LocalSvcPath is not None:

	QueueLst = models.GetWaitingRenditionQueue()

	for Queue in QueueLst:

	    logging.info("ProcessWaitingRenditionQueue(): Item -> [%s], File Name -> [%s]" % (Queue.item.name, Queue.file_name))

	    #
	    # Chequea que los repositorios esten OK
	    #
	    if not ExternRepositorySD.endswith('/'):
		ExternRepositorySD = ExternRepositorySD + '/'
	    if not ExternRepositoryHD.endswith('/'):
		ExternRepositoryHD = ExternRepositoryHD + '/'
		    
	    if not LocalRepository.endswith('/'):	    
		LocalRepository = LocalRepository + '/'
		    
	    if FileExist(ExternRepositorySD,Queue.file_name):
	    
		logging.info("ProcessWaitingRenditionQueue(): File Exist in -> [%s]" % ExternRepositorySD)
	    
		if FileExist(LocalRepository,Queue.file_name):
		    
		    logging.info("ProcessWaitingRenditionQueue(): File Exist local -> [%s]" % LocalRepository+Queue.file_name)
		    logging.info("ProcessWaitingRenditionQueue(): Overwrite Policy   -> [%s]" % str(Settings.OVERWRITE_PULL_FILES))
		    if Settings.OVERWRITE_PULL_FILES:
			logging.info("ProcessWaitingRenditionQueue(): Pulling File -> [%s]" % Queue.file_name)
			if PullFile(ExternRepositorySD, Queue.file_name, LocalRepository):
			    Queue.local_svc_path = LocalSvcPath
			    Queue.local_file     = 'Y'
			    Queue.queue_status   = 'Q'
			    Queue.save()
			    logging.info("ProcessWaitingRenditionQueue(): Success")
			else:
			    logging.error("ProcessWaitingRenditionQueue(): Pulling file -> [%s], Error -> [%s]" % (Queue.file_name, ErrorString))
			    logging.info("ProcessWaitingRenditionQueue(): Pulling Error Policy -> [%s]" % str(Settings.PULL_ERROR))
			    if Settings.PULL_ERROR:
				Queue.queue_status = 'Q'
				logging.info("ProcessWaitingRenditionQueue(): Put Queue [%d] in Queue State" % Queue.id)
				Queue.save()
			    else:
				Queue.queue_status = 'E'
				logging.info("ProcessWaitingRenditionQueue(): Put Queue [%d] in Error State" % Queue.id)
				Queue.error = "Can not retrive file [%s] to local_master_path [%s] -> %s" % (Queue.file_name, LocalRepository, ErrorString)
				Queue.save()
		    else:
			logging.info("ProcessWaitingRenditionQueue(): Using Existing file [%s]" % (LocalRepository+Queue.file_name))
			Queue.local_file     = 'Y'
			Queue.local_svc_path = LocalSvcPath
			Queue.queue_status   = 'Q'
			Queue.save()    
		else:
		    logging.info("ProcessWaitingRenditionQueue(): Pulling File -> [%s]" % Queue.file_name)
		    if PullFile(ExternRepositorySD, Queue.file_name, LocalRepository):
		        Queue.local_svc_path = LocalSvcPath
		        Queue.local_file     = 'Y'
		        Queue.queue_status   = 'Q'
		        Queue.save()
		        logging.info("ProcessWaitingRenditionQueue(): Success")
		    else:
		        logging.error("ProcessWaitingRenditionQueue(): Pulling file -> [%s], Error -> [%s]" % (Queue.file_name, ErrorString))
		        logging.info("ProcessWaitingRenditionQueue(): Pulling Error Policy -> [%s]" % str(Settings.PULL_ERROR))
		        if Settings.PULL_ERROR:
		    	    Queue.queue_status = 'Q'
			    logging.info("ProcessWaitingRenditionQueue(): Put Queue [%d] in Queue State" % Queue.id)
			    Queue.save()
			else:
			    Queue.queue_status = 'E'
			    logging.info("ProcessWaitingRenditionQueue(): Put Queue [%d] in Error State" % Queue.id)
			    Queue.error = "Can not retrive file [%s] to local_master_path [%s] -> %s" % (Queue.file_name, LocalRepository, ErrorString)
			    Queue.save()
	    
	    elif FileExist(ExternRepositoryHD,Queue.file_name):
		
		logging.info("ProcessWaitingRenditionQueue(): File Exist in -> [%s]" % ExternRepositoryHD)
	    
		if FileExist(LocalRepository,Queue.file_name):
		    
		    logging.info("ProcessWaitingRenditionQueue(): File Exist local -> [%s]" % LocalRepository+Queue.file_name)
		    logging.info("ProcessWaitingRenditionQueue(): Overwrite Policy   -> [%s]" % str(Settings.OVERWRITE_PULL_FILES))
		    if Settings.OVERWRITE_PULL_FILES:
			logging.info("ProcessWaitingRenditionQueue(): Pulling File -> [%s]" % Queue.file_name)
			if PullFile(ExternRepositoryHD, Queue.file_name, LocalRepository):
			    Queue.local_svc_path = LocalSvcPath
			    Queue.local_file	 = 'Y'
			    Queue.queue_status   = 'Q'
			    Queue.save()
			    logging.info("ProcessWaitingRenditionQueue(): Success")
			else:
			    logging.error("ProcessWaitingRenditionQueue(): Pulling file -> [%s], Error -> [%s]" % (Queue.file_name, ErrorString))
			    logging.info("ProcessWaitingRenditionQueue(): Pulling Error Policy -> [%s]" % str(Settings.PULL_ERROR))
			    if Settings.PULL_ERROR:
				Queue.queue_status = 'Q'
				logging.info("ProcessWaitingRenditionQueue(): Put Queue [%d] in Queue State" % Queue.id)
				Queue.save()
			    else:
				Queue.queue_status = 'E'
				logging.info("ProcessWaitingRenditionQueue(): Put Queue [%d] in Error State" % Queue.id)
				Queue.error = "Can not retrive file [%s] to local_master_path [%s] -> %s" % (Queue.file_name, LocalRepository, ErrorString)
				Queue.save()
		    else:
			logging.info("ProcessWaitingRenditionQueue(): Using Existing file [%s]" % (LocalRepository+Queue.file_name))
			Queue.local_svc_path = LocalSvcPath
			Queue.local_file     = 'Y'	
			Queue.queue_status   = 'Q'
			Queue.save()
	    
		else:
		    logging.info("ProcessWaitingRenditionQueue(): Pulling File -> [%s]" % Queue.file_name)
		    if PullFile(ExternRepositoryHD, Queue.file_name, LocalRepository):
		        Queue.local_svc_path = LocalSvcPath
		        Queue.local_file     = 'Y'
		        Queue.queue_status   = 'Q'
		        Queue.save()
		        logging.info("ProcessWaitingRenditionQueue(): Success")
		    else:
		        logging.error("ProcessWaitingRenditionQueue(): Pulling file -> [%s], Error -> [%s]" % (Queue.file_name, ErrorString))
		        logging.info("ProcessWaitingRenditionQueue(): Pulling Error Policy -> [%s]" % str(Settings.PULL_ERROR))
		        if Settings.PULL_ERROR:
		    	    Queue.queue_status = 'Q'
			    logging.info("ProcessWaitingRenditionQueue(): Put Queue [%d] in Queue State" % Queue.id)
			    Queue.save()
			else:
			    Queue.queue_status = 'E'
			    logging.info("ProcessWaitingRenditionQueue(): Put Queue [%d] in Error State" % Queue.id)
			    Queue.error = "Can not retrive file [%s] to local_master_path [%s] -> %s" % (Queue.file_name, LocalRepository, ErrorString)
			    Queue.save()
	    
	    
	    else:
		Queue.queue_status = 'E'
		Queue.error = 'Unable to find file in any Repository'
		Queue.save()	
		logging.error("ProcessWaitingRenditionQueue(): Unable to find file [%s] in any Repository" % Queue.file_name)
    else:
	logging.error("ProcessWaitingRenditionQueue(): Repository bad configured")
	return False

    logging.info("End Processing Waiting Rendition Queue")
    return True
	

def main():
    
    global ErrorString
    ErrorString = ''

    #
    # Configura el Log 
    #
    logging.basicConfig(format   ='%(asctime)s - QPull.py -[%(levelname)s]: %(message)s', 
			filename ='./log/QPull.log',
			level    =logging.INFO) 

    End = False
    while not End:
	if not ProcessWaitingRenditionQueue():
	    logging.error("Main(): Fail in ProcessWaitingRenditionQueue [SHUTDOWN]")
	    End = True
	
	if Settings.GLOBAL_SLEEP_TIME:
	    time.sleep(Settings.SLEEP_TIME)
	else:
	    time.sleep(Settings.QPULL_SLEEP)
	    

class main_daemon(Daemon):
    def run(self):
        try:
    	    main()
	except KeyboardInterrupt:
	    sys.exit()	    


if __name__ == "__main__":
	daemon = main_daemon('./pid/QPull.pid', stdout='./log/QPull.err', stderr='./log/QPull.err')
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

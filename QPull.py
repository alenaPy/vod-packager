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

import Zone


ErrorString = ''


def GetUsage(path = None):
    usage = 0
    if path is not None:
	if not path.endswith('/'):
	    path = path + '/'
	list = os.listdir(path)
	for file in list:
	    usage = usage + os.stat(path+file).st_size 

    return usage

#
# La quota debe estar expresada en Gigas
#
def PathInQuota(path = None, max_quota = None):
    usage = 0
    quota = 0
    if path is not None:
	usage = GetUsage(path)

    if max_quota is not None:
	quota = max_quota * 1024 * 1024 * 1024

    print quota
    print usage	
    if quota > usage:
	return True
    else:
	return False


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
	    LocalZone = models.ExportZone.objects.get(zone_name=Zone.LOCAL)
	    Settings  = models.Settings.objects.get(zone=LocalZone)    
	    	    
	    if Settings.pull_limit_available == 'T':
		os.system("pv -L %s \'" % Settings.pull_limit + SrcPath+FileName + "\' > \'" + DstPath+FileName + "\'")
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
    ExternRepositorySD = models.GetPath('remote_nfs_sd')
    ExternRepositoryHD = models.GetPath('remote_nfs_hd')

    logging.info("ProcessWaitingRenditionQueue(): Local Repository -> %s" % LocalRepository)
    logging.info("ProcessWaitingRenditionQueue(): Exter Repository SD -> %s" % ExternRepositorySD)
    logging.info("ProcessWaitingRenditionQueue(): Exter Repository HD -> %s" % ExternRepositoryHD)

    try:
	LocalZone = models.ExportZone.objects.get(zone_name=Zone.LOCAL)
	Settings  = models.Settings.objects.get(zone=LocalZone)      
    except:
	e = sys.exc_info()[0]
	d = sys.exc_info()[1]
	logging.error("ProcessWaitingRenditionQueue(): Error in LocalZone / Settings [%s -> %s]" % (e,d))
	return False

    if LocalRepository is not None and ExternRepositorySD is not None and ExternRepositoryHD is not None:

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

	    if not PathInQuota(LocalRepository, int(Settings.max_quota)): 
		if not FileExist(LocalRepository,Queue.file_name):
		    logging.info("ProcessWaitingRenditionQueue(): Maximum Quota Limit Exceeded -> [%d]" % int(Settings.max_quota))
		    logging.info("ProcessWaitingRenditionQueue(): End Processing Waiting Queue")
		    return True
		    
	    if FileExist(ExternRepositorySD,Queue.file_name):
	    
		logging.info("ProcessWaitingRenditionQueue(): File Exist in -> [%s]" % ExternRepositorySD)
	    
		if FileExist(LocalRepository,Queue.file_name):
		    
		    logging.info("ProcessWaitingRenditionQueue(): File Exist local -> [%s]" % LocalRepository+Queue.file_name)
		    logging.info("ProcessWaitingRenditionQueue(): Overwrite Policy   -> [%s]" % Settings.overwrite_pull_files)
		    if Settings.overwrite_pull_files == 'T':
			logging.info("ProcessWaitingRenditionQueue(): Pulling File -> [%s]" % Queue.file_name)
			Queue.queue_status = 'P'
			Queue.save()
			if PullFile(ExternRepositorySD, Queue.file_name, LocalRepository):
			    Queue.local_file     = 'Y'
			    Queue.queue_status   = 'Q'
			    Queue.save()
			    logging.info("ProcessWaitingRenditionQueue(): Success")
			else:
			    logging.error("ProcessWaitingRenditionQueue(): Pulling file -> [%s], Error -> [%s]" % (Queue.file_name, ErrorString))
			    Queue.queue_status = 'E'
			    logging.info("ProcessWaitingRenditionQueue(): Put Queue [%d] in Error State" % Queue.id)
			    Queue.error = "Can not retrive file [%s] to local_master_path [%s] -> %s" % (Queue.file_name, LocalRepository, ErrorString)
			    Queue.save()
		    else:
			logging.info("ProcessWaitingRenditionQueue(): Using Existing file [%s]" % (LocalRepository+Queue.file_name))
			Queue.local_file     = 'Y'
			Queue.queue_status   = 'Q'
			Queue.save()    
		else:
		    logging.info("ProcessWaitingRenditionQueue(): Pulling File -> [%s]" % Queue.file_name)
		    Queue.queue_status = 'P'
		    Queue.save()
		    if PullFile(ExternRepositorySD, Queue.file_name, LocalRepository):
		        Queue.local_file     = 'Y'
		        Queue.queue_status   = 'Q'
		        Queue.save()
		        logging.info("ProcessWaitingRenditionQueue(): Success")
		    else:
		        logging.error("ProcessWaitingRenditionQueue(): Pulling file -> [%s], Error -> [%s]" % (Queue.file_name, ErrorString))
			Queue.queue_status = 'E'
			logging.info("ProcessWaitingRenditionQueue(): Put Queue [%d] in Error State" % Queue.id)
			Queue.error = "Can not retrive file [%s] to local_master_path [%s] -> %s" % (Queue.file_name, LocalRepository, ErrorString)
			Queue.save()
	    
	    elif FileExist(ExternRepositoryHD,Queue.file_name):
		
		logging.info("ProcessWaitingRenditionQueue(): File Exist in -> [%s]" % ExternRepositoryHD)
	    
		if FileExist(LocalRepository,Queue.file_name):
		    
		    logging.info("ProcessWaitingRenditionQueue(): File Exist local -> [%s]" % LocalRepository+Queue.file_name)
		    logging.info("ProcessWaitingRenditionQueue(): Overwrite Policy   -> [%s]" % Settings.overwrite_pull_files)
		    if Settings.overwrite_pull_files == 'T':
			logging.info("ProcessWaitingRenditionQueue(): Pulling File -> [%s]" % Queue.file_name)
			Queue.queue_status = 'P'
			Queue.save()
			if PullFile(ExternRepositoryHD, Queue.file_name, LocalRepository):
			    Queue.local_file	 = 'Y'
			    Queue.queue_status   = 'Q'
			    Queue.save()
			    logging.info("ProcessWaitingRenditionQueue(): Success")
			else:
			    logging.error("ProcessWaitingRenditionQueue(): Pulling file -> [%s], Error -> [%s]" % (Queue.file_name, ErrorString))
			    Queue.queue_status = 'E'
			    logging.info("ProcessWaitingRenditionQueue(): Put Queue [%d] in Error State" % Queue.id)
			    Queue.error = "Can not retrive file [%s] to local_master_path [%s] -> %s" % (Queue.file_name, LocalRepository, ErrorString)
			    Queue.save()
		    else:
			logging.info("ProcessWaitingRenditionQueue(): Using Existing file [%s]" % (LocalRepository+Queue.file_name))
			Queue.local_file     = 'Y'	
			Queue.queue_status   = 'Q'
			Queue.save()
	    
		else:
		    logging.info("ProcessWaitingRenditionQueue(): Pulling File -> [%s]" % Queue.file_name)
		    Queue.queue_status = 'P'
		    Queue.save()
		    if PullFile(ExternRepositoryHD, Queue.file_name, LocalRepository):
		        Queue.local_file     = 'Y'
		        Queue.queue_status   = 'Q'
		        Queue.save()
		        logging.info("ProcessWaitingRenditionQueue(): Success")
		    else:
		        logging.error("ProcessWaitingRenditionQueue(): Pulling file -> [%s], Error -> [%s]" % (Queue.file_name, ErrorString))
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
	
	try:
	    LocalZone = models.ExportZone.objects.get(zone_name=Zone.LOCAL)
	    Settings  = models.Settings.objects.get(zone=LocalZone)    
	except:
	    end = True
	    logging.error("main(): Critical error, plase check global_sleep_time [SHUTDOWN]")
	    return False
	    
        if Settings.global_sleep_time != '':
    	    try:
	        time.sleep(int(Settings.global_sleep_time))
	    except:
	        end = True 
	        logging.error("main(): Critical error, plase check global_sleep_time [SHUTDOWN]")   
	        raise KeyboardInterrupt
	else:
	    try:
	        time.sleep(int(Settings.qpull_sleep))
	    except:
	        end = True 
    	        logging.error("main(): Critical error, plase check qpull_sleep [SHUTDOWN]") 
		raise KeyboardInterrupt


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

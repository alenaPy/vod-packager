#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Stand alone script
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from django.core.management import setup_environ
from Packager import settings
setup_environ(settings)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Modelo de la aplicacion
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from Packager_app import models

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Carbon Coder 
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from carbonapi.CarbonSocketLayer import *
from carbonapi.CarbonUtils import *
from carbonapi.CarbonJob import *
from carbonapi.CarbonSched import *

import logging
import sys, time
from daemon import Daemon


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funciones - Utileria
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def SplitExtension(filename=None):
    
    if filename is not None:
	basename_tmp_list = filename.split('.')
	i = 1
	basename = basename_tmp_list[0]
	while i < len(basename_tmp_list) -1:
	    basename = basename + '.' + basename_tmp_list[i]
	    i = i + 1
	return basename
    return None

def RenditionFileName(original_filename = None, sufix = None, ext = None):
    
    logging.debug("RenditionFileName(): FileName-> " + original_filename + " Sufix-> " + sufix + " Ext-> " + ext)
    
    if original_filename is not None and sufix is not None and ext is not None:
	
	# 1- Elimina la extension
	# 2- Agrega Sufijo
	# 3- Agrega extension
	
	basename = SplitExtension(original_filename)
	if basename is None:
	    return None
    
	if not ext.startswith('.'):
	    ext = '.' + ext
	    
	basename = basename + sufix + ext
	return basename
    return None


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funciones - GET
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def GetVideoProfiles(format='ALL'):
    if format == 'ALL':
	vp_list = models.VideoProfile.objects.filter(status='E')
    elif format == 'SD':
	vp_list = models.VideoProfile.objects.filter(status='E',format='SD')
    elif format == 'HD':
	vp_list = models.VideoProfile.objects.filter(status='E',format='HD')
    return vp_list
    
def GetImageProfile():
    return models.ImageProfile.objects.filter(status='E')
    

def GetTranscodingServer():
    return models.TranscodingServer.objects.filter(status='E')
    

def GetImportQueue():
    return models.ImportQueue.objects.filter(queue_status='Q')
    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    
# Procedimientos
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    


def InitCarbonPool():
    #
    # Se crea el pool de Carbon
    #
    CPool = CarbonPool()
    #
    # Se traen todos los transcoder server que estan Enabled
    #
    TServerList = GetTranscodingServer()
    #
    # Se agrega cada transcoder server al pool
    #
    for TServer in TServerList:
	CPool.addCarbon(TServer.ip_address)
	
    return CPool


def MakeImageRenditions(ImportTask=None):

    if ImportTask is None:
	return False

    Item = ImportTask.item
    
    #
    # Trae la lista de profiles activos
    #
    IProfileList = GetImageProfile()
    
    #
    # Por cada image profile debe crear el image rendition
    #
    for IProfile in IProfileList:
	IRendition               = models.ImageRendition()
	IRendition.image_profile = IProfile
	IRendition.item          = Item
	IRendition.status        = 'E'
	IRendition.save()

def CheckVideoRendition(Item=None, VProfile=None):
    list = models.VideoRendition.objects.filter(item=Item, video_profile=VProfile)
    if len(list) > 0:
	return False
    return True	

def MakeVideoRenditions(ImportTask=None, CPool=None):   # CPool = CarbonPool()

    if ImportTask is None:
	
	logging.error("MakeVideoRenditions(): ImportTask is None")

	return False

    
    
    Item = ImportTask.item
    
    logging.info("MakeVideoRenditions(): Creating video rendition for item: " + Item.name )
    #
    # Define que tipos de Video Profiles debe usar
    # SD o HD
    #
    if Item.format == 'HD':
	VProfileList = GetVideoProfiles()
    elif Item.format == 'SD':
	VProfileList = GetVideoProfiles('SD')
        
        
    Source = ImportTask.svc_path
    File   = ImportTask.file_name
    
    logging.debug("MakeVideoRenditions(): Source-> " + Source + " File-> " + File)    
    
    #
    # Por cada video profile crea un video rendition
    #
    for VProfile in VProfileList:
	
	logging.info("MakeVideoRenditions(): VProfile: " + VProfile.name)
	
	TranscodeGuid = VProfile.guid
	
	#
	# Si existe ya existe un video rendition con ese profile para ese item
	# no lo procesa y continua con el siguiente profile
	#
	if not CheckVideoRendition(Item,VProfile):
	    logging.warning("MakeVideoRendition(): Video Profile exist-> Continue")
	    continue
	    
	#
	# Arma el destination filename y el basename
	#
	DstFilename = RenditionFileName(File, VProfile.sufix, VProfile.file_extension)
	DstBasename = SplitExtension(DstFilename)
	
	#
	# Arma los parametros de transcodificacion
	#	
	TranscodeInfo = { 'd_guid'    : TranscodeGuid, 
	                  'd_basename': DstBasename, 
	                  'd_path'    : models.Path.objects.get(key="video_smb_path").location }		

	logging.debug("MakeVideoRenditions(): Transcode Info: " +  str(TranscodeInfo))
	
	#
	# Envia el Job a transcodificar
	#
	XmlJob    = CreateCarbonXMLJob(Source,File,[],[TranscodeInfo],None,None)
	Job       = StartJobCarbonPool(CPool,XmlJob)
	
	#
	# Crea el Video Rendition en el modelo
	#
	VRendition = models.VideoRendition()
	VRendition.file_name            = DstFilename
	VRendition.video_profile        = VProfile
	VRendition.transcoding_job_guid = Job.GetGUID()
	VRendition.status               = 'Q'	# Queued
	VRendition.item		 	= Item
	

	for TServer in GetTranscodingServer():
	    if Job.GetCarbonHostname() == TServer.ip_address:
		VRendition.transcoding_server = TServer
		break
	
	logging.debug("MakeVideoRenditions(): Carbon Server ->" + VRendition.transcoding_server.ip_address)
	VRendition.save()

    return True	 


def main():

    #
    # Configura el Log 
    #

    logging.basicConfig(format='%(asctime)s - QImport.py -[%(levelname)s]: %(message)s', filename='./log/QImport.log',level=logging.INFO) 
    
    #
    # Inicializa el Carbon Pool 
    #
    CPool = InitCarbonPool()

    while 1:
	#
	# En el ciclo principal
	#
	QueueList = GetImportQueue()
	for Queue in QueueList:
	    #
	    # Por cada elemento en la cola de importacion
	    #
	    Queue.status = 'D'			# Lo marca como Tomado
	    Queue.save()			
	    MakeVideoRenditions(Queue,CPool)	# Crea los video renditions
	    MakeImageRenditions(Queue)		# Crea los imagen renditions

	#
	# Duerme 60 Segundos
	#
	time.sleep(60)

class main_daemon(Daemon):
    def run(self):
        try:
    	    main()
	except KeyboardInterrupt:
	    sys.exit()	    

if __name__ == "__main__":
	daemon = main_daemon('./pid/QImport.pid', stdout='./log/QImport.err', stderr='./log/QImport.err')
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


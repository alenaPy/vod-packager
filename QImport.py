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

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funciones - Utileria
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from Lib.Utils  import SplitExtension
from Lib.Utils  import RenditionFileName
from Lib.Utils  import PrefixStrId
from Lib.Utils  import FileExist
from Lib.daemon import Daemon
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Settings
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import Settings


def CreateDummyCarbon():
    try:
	TServer = models.TranscodingServer.objects.get(ip_address='(Dummy)')
    except:
	TServer = models.TranscodingServer()
	TServer.hostname   = '(Dummy)'
	TServer.ip_address = '(Dummy)'
	TServer.status     = 'D'
	TServer.save()
	

ErrorString = ''

def InitCarbonPool():
    #
    # Se crea el pool de Carbon
    #
    CPool       = CarbonPool()
    TServerList = models.GetTranscodingServer()
    
    if len(TServerList) == 0:
	#
	# No hay transcoding Servers
	# 
	return None

    for TServer in TServerList:
	ret = CPool.addCarbon(TServer.ip_address)
	if ret == False:

	    TServer.status = 'D'
	    TServer.save()
	    logging.warning("InitCarbonPool(): Carbon server [%s] fail to init -> Set Disable" % TServer.ip_address)
	else:
	    logging.info("InitCarbonPool(): Carbon server [%s] init OK" % TServer.ip_address)
    if CPool.poolLen() == 0:
	return None
    
    return CPool


def MakeImageRenditions(RenditionTask=None):

    if RenditionTask is None:
	return False

    Item = RenditionTask.item
    
    #
    # Trae la lista de profiles activos
    #
    if Item.format == 'HD':
        IProfileList = models.GetImageProfile()
    else:
	IProfileList = models.GetImageProfile('SD')
    #
    # Por cada image profile debe crear el image rendition
    #
    for IProfile in IProfileList:
	
	if not CheckImagenRendition(Item, IProfile):
	    logging.warning("MakeImagenRendition(): Image Profile exist-> Continue. [IP: %s]" % IProfile.name )
	    continue

	IRendition               = models.ImageRendition()
	IRendition.image_profile = IProfile
	IRendition.item          = Item
	IRendition.status        = 'U'

	logging.info("MakeImageRendition(): Creating Image rendition for Item: " + Item.name + " [IP: " + IProfile.name + "]")
	IRendition.save()

    return True


def CheckVideoRendition(Item=None, VProfile=None):
    VRlist = models.VideoRendition.objects.filter(item=Item, video_profile=VProfile)
    if len(VRlist) > 0:
	return False
    return True	


def CheckImagenRendition(Item=None, IProfile=None):
    IRlist = models.ImageRendition.objects.filter(item=Item, image_profile=IProfile)
    if len(IRlist) > 0:
	return False
    return True


def MakeVideoRenditions(RenditionTask=None, CPool=None, ForceSchedule=False):   # CPool = CarbonPool()

    global ErrorString

    ErrorString = ''

    if RenditionTask is None:
	
	logging.error("MakeVideoRenditions(): ImportTask is None")
	return False

    try:
	Item = RenditionTask.item
    except:
	e = sys.exc_info()[0]
	logging.error("MakeVideoRenditions(): ImportTask not have an Item. Catch: %s" % e)
	ErrorString = "ImportTask not have an Item. Catch: %s" % e
	return False

    logging.info("MakeVideoRenditions(): Creating video rendition for item: " + Item.name )
    #
    # Define que tipos de Video Profiles debe usar
    # SD o HD
    #
    if Item.format == 'HD':
	VProfileList = models.GetVideoProfiles()
    elif Item.format == 'SD':
	VProfileList = models.GetVideoProfiles('SD')
        
    
    if RenditionTask.local_svc_path is not None and RenditionTask.local_svc_path != '':
	logging.info("MakeVideoRenditions(): Try to use local_svc_path [%s]" % RenditionTask.local_svc_path)
	local_master_path =  models.GetPath('local_master_path')
	if local_master_path is not None:
	    if not local_master_path.endswith('/'):
		local_master_path = local_master_path + '/'
	
	    if FileExist(local_master_path,RenditionTask.file_name):
		logging.info("MakeVideoRenditions(): File Exist in local_svc_path [%s]" % (local_master_path + RenditionTask.file_name))
	    	Source = RenditionTask.local_svc_path
	    else:
		logging.info("MakeVideoRenditions(): Can not Find the file in local_svc_path [%s]" % (local_master_path + RenditionTask.file_name))
		Source = RenditionTask.svc_path
	else:
	    Source = RenditionTask.svc_path

    else:    
	Source = RenditionTask.svc_path

    File   = RenditionTask.file_name
    logging.debug("MakeVideoRenditions(): Source-> " + Source + " File-> " + File)    
    logging.debug("MakeVideoRenditions(): VProfileList len: " + str(len(VProfileList)))
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
	    logging.warning("MakeVideoRendition(): Video Profile exist-> Continue. [VP: %s]" % VProfile.name )
	    continue
	    
	#
	# Arma el destination filename y el basename
	#
	DstFilename = RenditionFileName(File, VProfile.sufix, VProfile.file_extension)
	if DstFilename is None:
	    logging.error = "MakeVideoRenditions(): 03: Unable stablish DstFileName, [FILE]-> " + File + " ,[SUFIX]-> " + VProfile.sufix 
	    ErrorString   = "03: Unable stablish DstFileName, [FILE]-> " + File + " ,[SUFIX]-> " + VProfile.sufix
	    return False
	

	DstFilename = DstFilename.replace(' ', '')
	DstFilename = PrefixStrId(Item.id) + '-' + DstFilename

	DstBasename = SplitExtension(DstFilename)
	if DstBasename is None:
	    logging.error = "MakeVideoRenditions(): 04: Unable to stablish DstBasename"
	    ErrorString   = "04: Unable stablish DstBasename"
	    return False
	

	#
	# Arma los parametros de transcodificacion
	#	
	TranscodeInfo = { 'd_guid'    : TranscodeGuid, 
	                  'd_basename': DstBasename, 
	                  'd_path'    : models.GetPath("video_smb_path") }

	logging.debug("MakeVideoRenditions(): Transcode Info: " +  str(TranscodeInfo))
	#
	# Envia el Job a transcodificar
	#

	try:
	    XmlJob    = CreateCarbonXMLJob(Source,File,[],[TranscodeInfo],None,None)
	except:
	    e = sys.exc_info()[0]
	    logging.error("MakeVideoRendition(): 01: Exception making Carbon XML Job. Catch: " + e)
	    ErrorString = '01: Exception making Carbon XML Job. Catch: ' + e 
	
	if XmlJob is None:
	    logging.error("MakeVideoRendition(): 01: Error making Carbon XML Job")
	    ErrorString = '01: Error making Carbon XML Job'
	    return False

	JobReply       = StartJobCarbonPool(CPool,XmlJob, ForceSchedule)
	if JobReply.Result == True:
	    #
	    # Crea el Video Rendition en el modelo
	    #
	    VRendition = models.VideoRendition()
	    VRendition.file_name            = DstFilename
	    VRendition.src_file_name	    = File
	    VRendition.src_svc_path	    = Source
	    VRendition.video_profile        = VProfile
	    VRendition.transcoding_job_guid = JobReply.Job.GetGUID()
	    VRendition.status               = 'Q'	# Queued
	    VRendition.item		    = Item
	
	
	    if Item.format == 'HD':
		if VProfile.format == 'HD':
		    VRendition.screen_format = 'Widescreen'
		else:
		    VRendition.screen_format = 'Letterbox'
	    elif Item.format == 'SD':
		VRendition.screen_format = 'Standard'

	    #+++++++++++++++++++++++++++++++++++++++++++++
	    # TODO: Formato de Item Vs Formato de Brand
	    #+++++++++++++++++++++++++++++++++++++++++++++

	    try:
		TServer = models.TranscodingServer.objects.get(ip_address=JobReply.Job.GetCarbonHostname())
	        VRendition.transcoding_server = TServer
		logging.info("MakeVideoRenditions(): Carbon Server ->" + VRendition.transcoding_server.ip_address)
	    except:
		logging.error("MakeVideoRenditions(): Can not find the Assigned Carbon Server -> " + JobReply.Job.GetCarbonHostname())
	        return False	
	
		
	    
	else:
	    if JobReply.Error == False and ForceSchedule == False:
		#
		# No lo pudo planificar porque no hay ningun Carbon Coder Disponible
		#	
		VRendition = models.VideoRendition()
		VRendition.file_name            = DstFilename
		VRendition.src_file_name	= File
		VRendition.src_svc_path	        = Source
	        VRendition.video_profile        = VProfile
	        VRendition.transcoding_job_guid = ''
	        VRendition.status               = 'U'	# Unasigned
	        VRendition.item		    	= Item
	
		try:
		    TServer = models.TranscodingServer.objects.get(ip_address='(Dummy)')
	    	    VRendition.transcoding_server = TServer
	    	    logging.info("MakeVideoRenditions(): Carbon Server ->" + VRendition.transcoding_server.ip_address)
		except:
		    logging.error("MakeVideoRenditions(): Can not find the Assigned Carbon Server -> " + JobReply.Job.GetCarbonHostname())
	    	    return False
	
		logging.info("MakeVideoRenditions(): Can Not Assign Carbon Server (No one have slots )")
	
		if Item.format == 'HD':
		    if VProfile.format == 'HD':
			VRendition.screen_format = 'Widescreen'
		    else:
			VRendition.screen_format = 'Letterbox'
		elif Item.format == 'SD':
		    VRendition.screen_format     = 'Standard'

	    else:
		ErrorString = '02: Error sending Job'
		logging.error("MakeVideoRendition(): 02: Error sending Job")
	        return False

	print "Estoy Aca"
	VRendition.save()

    return True	 


def MakeRenditions(ForceSchedule=True):

    global ErrorString
    ErrorString = ''

    logging.info("MakeRenditions(): Start Creating Video and Image Renditions")

    QueueList = models.GetRenditionQueue()
    if len(QueueList) > 0:
    
	logging.info("MakeRenditions(): Init Transcoding server pool")
	CPool = InitCarbonPool()
        while CPool is None:
	    logging.info("MakeRenditions(): No transcoding server configured in database... Sleep")
	    time.sleep(10)
	    CPool = InitCarbonPool()

	for Queue in QueueList:
	    #
	    # Por cada elemento en la cola de Rendiciones
	    #
	    Queue.queue_status = 'D'			# Lo marca como Tomado
	    Queue.save()			

	    # Creo los video renditions
	    if not MakeVideoRenditions(Queue,CPool,ForceSchedule):
		Queue.error  = ErrorString
		Queue.queue_status = 'E'
		Queue.save()
		continue

	    # Creo los imagen rendition
	    if not MakeImageRenditions(Queue):
		Queue.error  = ErrorString
		Queue.queue_status = 'E'
		Queue.save()
		continue

	    Queue.item.status = 'P'
	    Queue.item.save()

    logging.info("MakeRenditions(): End Creating Video and Image Renditions")

    return True    


def ReScheduleUnasignedRenditions(ForceSchedule=False):
    global ErrorString
    ErrorString = ''

    logging.info("ReSheduleUnasignedRenditions(): Start Checking Unassingned Video Renditions")

    #
    # Trae todas las Video Renditions que no fueron Asignadas
    #
    UVRenditions = models.GetVideoRenditionUnassigned()


    if len(UVRenditions) > 0:
	#
	# Si hay Elementos en la Cola
	#
	# 1- Inicia el carbon Pool
	#
	logging.info("ReSheduleUnasignedRenditions(): Init Transcoding server pool")
	CPool = InitCarbonPool()
        while CPool is None:
	    logging.info("ReSheduleUnasignedRenditions(): No transcoding server configured in database... Sleep")
	    time.sleep(10)
	    CPool = InitCarbonPool()


	for VRendition in UVRenditions: 
	    #
	    # Arma los parametros de transcodificacion
	    #
	    logging.info("ReSheduleUnasignedRenditions(): -----")
	    logging.info("ReSheduleUnasignedRenditions(): VideoRendition ID: %d" % VRendition.id)
	    logging.info("ReSheduleUnasignedRenditions(): Item -> [%s], VideoProfile -> [%s]" % (VRendition.item.name, VRendition.video_profile.name))	
	    TranscodeInfo = { 'd_guid'    : VRendition.video_profile.guid, 
	                      'd_basename': SplitExtension(VRendition.file_name), 
	                      'd_path'    : models.GetPath("video_smb_path") }


	    logging.debug("ReSheduleUnasignedRenditions(): Transcode Info: " +  str(TranscodeInfo))
	    #
	    # Crea el XML con el Job de Transcodificacion
	    #
	    try:
		XmlJob    = CreateCarbonXMLJob(VRendition.src_svc_path,VRendition.src_file_name,[],[TranscodeInfo],None,None)
	    except:
		e = sys.exc_info()[0]
	        logging.error("ReSheduleUnasignedRenditions(): 01: Exception making Carbon XML Job. Catch: " + e)
		ErrorString = '01: Exception making Carbon XML Job. Catch: ' + e 
		return False

	    if XmlJob is None:
		logging.error("ReSheduleUnasignedRenditions(): 01: Error making Carbon XML Job")
	        ErrorString = '01: Error making Carbon XML Job'
	        return False

	    JobReply       = StartJobCarbonPool(CPool,XmlJob, ForceSchedule)
	    if JobReply.Result == True:
		#
		# Si puedo Asignarle un Transcoding Server
		# 
		# 1- Lo Marca como Encolado
		# 2- Carga en Base de Datos el GUID del Job 
		# 3- Carga el Transcoding Server Asignado
		#
		VRendition.status = 'Q'
		VRendition.transcoding_job_guid = JobReply.Job.GetGUID()

		try:
		    TServer = models.TranscodingServer.objects.get(ip_address=JobReply.Job.GetCarbonHostname())
		    logging.info("ReSheduleUnasignedRenditions(): Carbon Server ->" + TServer.ip_address)
		except:
		    #
		    # Si no encuentra el transcoding Server Asignado
		    #
		    ErrorString = '02: Can not find the Assigned Carbon Server'
		    logging.error("ReSheduleUnasignedRenditions(): Can not find the Assigned Carbon Server -> " + JobReply.Job.GetCarbonHostname())
	    	    return False
	    	    	
		VRendition.transcoding_server = TServer
		VRendition.save()
	    else:
		if JobReply.Error == False:
		    logging.info("ReSheduleUnasignedRenditions(): Can Not Assign Carbon Server ( No one have slots )")	
		    return True
		else:
		    ErrorString = '02: Error sending Job'
		    logging.error("MakeVideoRendition(): 02: Error sending Job")
	    	    return False

    logging.info("ReSheduleUnasignedRenditions(): End Checking Unassingned Video Renditions")
    return True

def Main():

    global ErrorString
    ErrorString = ''

    #
    # Configura el Log 
    #
    logging.basicConfig(format   ='%(asctime)s - QImport.py -[%(levelname)s]: %(message)s', 
			filename ='./log/QImport.log',
			level    =logging.INFO) 

    #
    # Crea un Dummy Carbon si no existe ya creado
    #
    CreateDummyCarbon()

    logging.info("Main(): Enter in main loop")
    
    End = False
    
    while not End:
    
	#
	# Reasignla las transcodificaciones
	#    
	if not ReScheduleUnasignedRenditions(Settings.FORCE_SCHEDULE):
	    loggin.error("Main(): Error in ReSCheduleUnassignedRenditions [SHUTDOWN]")
	    End = True

	#
	# Crea las Video/Images Renditions
	#
	if not MakeRenditions(Settings.FORCE_SCHEDULE):
	    End = True
	    loggin.error("Main(): Error in MakeRenditions [SHUTDOWN]")
	    continue
	
	
	    
	if Settings.GLOBAL_SLEEP_TIME:
	    time.sleep(Settings.SLEEP_TIME)
	else:
	    time.sleep(Settings.QIMPORT_SLEEP)


    logging.info("Main(): Bye Bye")


def StartMessage():
    print "--------"
    print "QImport Daemon"
    print "--------"
    print "Options:"
    print "FORCE_SCHEDULE=" + str(Settings.FORCE_SCHEDULE)
    print "SLEEP_TIME="     + str(Settings.SLEEP_TIME)
    
    
class main_daemon(Daemon):
    def run(self):
        try:
    	    Main()
	except KeyboardInterrupt:
	    sys.exit()	    

if __name__ == "__main__":
	StartMessage()
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
		elif 'status'  == sys.argv[1]:
			daemon.status()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart|run" % sys.argv[0]
		sys.exit(2)


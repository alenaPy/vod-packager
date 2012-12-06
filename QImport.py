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

ErrorString = ''

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
    
	if not sufix.startswith('_'):
	    sufix = '_' +  sufix

	if not ext.startswith('.'):
	    ext = '.' + ext
	    
	basename = basename.upper() + sufix.upper() + ext
	return basename
    return None

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
    TServerList = models.GetTranscodingServer()
    #
    # Se agrega cada transcoder server al pool
    #

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
    IProfileList = models.GetImageProfile()
    
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


def PrefixStrId(itemid=0):
    StrId = str(itemid)
    Zero = ''
    i = len(StrId)
    while i <= 5:
        Zero = Zero + '0'
        i = i + 1

    return 'PB' + Zero + StrId


def MakeVideoRenditions(RenditionTask=None, CPool=None):   # CPool = CarbonPool()

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
	                  #'d_path'    : models.Path.objects.get(key="video_smb_path").location }		
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

	Job       = StartJobCarbonPool(CPool,XmlJob)
	if Job is None:
	    ErrorString = '02: Error sending Job'
	    logging.error("MakeVideoRendition(): 02: Error sending Job")
	    return False
	
	#
	# Crea el Video Rendition en el modelo
	#
	VRendition = models.VideoRendition()
	VRendition.file_name            = DstFilename
	VRendition.video_profile        = VProfile
	VRendition.transcoding_job_guid = Job.GetGUID()
	VRendition.status               = 'Q'	# Queued
	VRendition.item		 	= Item
	
	if Item.format == 'HD':
	    if VProfile.format == 'HD':
		VRendition.screen_format = 'Widescreen'
	    else:
		VRendition.screen_format = 'Letterbox'
	elif Item.format == 'SD':
	    VRendition.screen_format = 'Standard'


	for TServer in models.GetTranscodingServer():
	    if Job.GetCarbonHostname() == TServer.ip_address:
		VRendition.transcoding_server = TServer
		break
	
	logging.debug("MakeVideoRenditions(): Carbon Server ->" + VRendition.transcoding_server.ip_address)
	VRendition.save()

    return True	 


def main():

    global ErrorString
    ErrorString = ''

    #
    # Configura el Log 
    #

    logging.basicConfig(format='%(asctime)s - QImport.py -[%(levelname)s]: %(message)s', filename='./log/QImport.log',level=logging.INFO) 
    
    #
    # Inicializa el Carbon Pool 
    #
    logging.info("main(): Init Transcoding server pool")
    CPool = InitCarbonPool()
    while CPool is None:
	logging.info("main(): No transcoding server configured in database... Sleep")
	time.sleep(10)

	CPool = InitCarbonPool()


    logging.info("main(): Enter in main loop")
    while True:
	#
	# En el ciclo principal
	#
	QueueList = models.GetRenditionQueue()
	logging.debug("main(): QueueLen = " + str(len(QueueList)))
	for Queue in QueueList:
	    #
	    # Por cada elemento en la cola de importacion
	    #
	    Queue.queue_status = 'D'			# Lo marca como Tomado
	    Queue.save()			

	    # Creo los video renditions
	    if not MakeVideoRenditions(Queue,CPool):
		Queue.error  = ErrorString
		Queue.status = 'E'
		Queue.save()
		continue

	    # Creo los imagen rendition
	    if not MakeImageRenditions(Queue):
		Queue.error  = ErrorString
		Queue.status = 'E'
		Queue.save()
		continue

	    Queue.item.status = 'P'
	    Queue.item.save()

	#
	# Duerme 60 Segundos
	#
	logging.info("main(): No more work... Sleep")
	time.sleep(10)

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
		elif 'status'  == sys.argv[1]:
			daemon.status()
	    
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart|run" % sys.argv[0]
		sys.exit(2)


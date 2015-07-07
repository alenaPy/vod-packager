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
from carbonapi.BitmapKeying import *
from carbonapi.XmlTitler 	 import *

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# STL Lib
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
from stl			 import *
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import time
import logging
import sys, time
import string

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
import Zone


def StlToXmlTitler(SubProfile, StlFileName):

    # Abre el archivo STL
    stl = STL()
    stl.load(StlFileName)

    print StlFileName

    # Crea la estructura de datos XmlTitler
    XmlTitler = TitlerData()

    # Crea el estilo
    Style = Data()
    Style.Font     = SubProfile.font
    Style.CharSize = SubProfile.charsize


    # Carga los valores del estilo en el XML de acuerdo al SubtitleProfile
    R,G,B = SubProfile.color_rgb.split(',')
    Style.ColorR = R
    Style.ColorG = G
    Style.ColorB = B
#    Style.Transparency  = SubProfile.transparency
    Style.ShadowSize    = SubProfile.shadow_size
    Style.HardShadow    = SubProfile.hard_shadow
    Style.StartTimecode = '00:00:00;00'
    Style.EndTimecode   = '00:00:00;01'
    Style.Title		= ''
    i = 0
    XmlTitler.AppendData(Style)
    # Por Cada TTI del Stl crea una estructura de tipo Data()
    for tti in stl.tti:
	print i
	TextAndTiming = Data()
#	TextAndTiming.Font          = SubProfile.font
	TextAndTiming.FontCharSet   = 'ANSI'
        TextAndTiming.StartTimecode = str(tti.tci) 
        TextAndTiming.EndTimecode   = str(tti.tco)
        TextAndTiming.Title	    = tti.tf.encode_utf8()
        TextAndTiming.PosX	    = '0.50'
        TextAndTiming.PosY	    = '0.835'
        XmlTitler.AppendData(TextAndTiming)
	i = i + 1
    return XmlTitler


def CreateDummyCarbon():
    try:
	TServer = models.TranscodingServer.objects.get(ip_address='(Dummy)')
    except:
	TServer = models.TranscodingServer()
	TServer.name   = '(Dummy)'
	TServer.ip_address = '(Dummy)'
	TServer.status     = 'D'
	TServer.save()
	
	
Static_Counter = 0

def GetSmbLocalPath():

    global Static_Counter

    try:
	LocalZone = models.ExportZone.objects.get(zone_name=Zone.LOCAL)
	Settings  = models.Settings.objects.get(zone=LocalZone)      
    except:
	e = sys.exc_info()[0]
	d = sys.exc_info()[1]
	logging.error("GetSmbLocalPath: Error in LocalZone / Settings [%s -> %s]" % (e,d))
	return False


    LocalSmbPath = models.Path.objects.filter(key='local_master_smb')
    
    logging.info("GetSmbLocalPath(): LocalSmbPath len: %s" % str(len(LocalSmbPath)))
    
    if len(LocalSmbPath) > 1 and Settings.local_smb_path_round_robin == 'Y':
	Static_Counter = Static_Counter + 1
	return LocalSmbPath[Static_Counter % len(LocalSmbPath)].location
    elif len(LocalSmbPath) == 1 or Settings.local_smb_path_round_robin == 'F':
	return LocalSmbPath[0].location
	
    return None

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
    
    try:
	LocalZone = models.ExportZone.objects.get(zone_name=Zone.LOCAL)
	Settings  = models.Settings.objects.get(zone=LocalZone)      
    except:
	e = sys.exc_info()[0]
	d = sys.exc_info()[1]
	logging.error("MakeImageRenditions(): Error in LocalZone / Settings [%s -> %s]" % (e,d))
	return False
    
    if Settings.optimize_profiles_with_brand == 'Y':
	IProfileList_pre = models.GetImageProfilesBrand(Item.internal_brand)
	if Item.internal_brand == 'HD' and Item.format == 'SD':
	    logging.warning("MakeImageRenditions(): Internal Brand is HD but Item format is SD -> Eliminate HD Profiles")
	    #
	    # Hay que eliminar los HD
	    #
	    IProfileList = []
	    for IProfile in IProfileList_pre:
		if IProfile.format == 'SD':
		    IProfileList.add(IProfile)
	else:
	    IProfileList = IProfileList_pre	    
    else:
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



    IProfileList = models.ImageProfile.objects.filter(is_master='Y')
    for IProfile in IProfileList:
	IRM = models.ImageRenditionMaster()
	IRM.image_profile = IProfile
	IRM.item          = Item
	IRM.status	  = 'U'
	IRM.save()

    return True


def CheckVideoRendition(Item=None, VProfile=None, SubtitleLanguage=None):
    VRList1 = models.VideoRendition.objects.filter(item=Item, video_profile=VProfile)
    VRlist = models.VideoRendition.objects.filter(item=Item, video_profile=VProfile, subtitle_language=SubtitleLanguage)

    print VRList1
    print Item
    print VProfile
    print SubtitleLanguage
    print VRlist
    
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
	LocalZone = models.ExportZone.objects.get(zone_name=Zone.LOCAL)
	Settings  = models.Settings.objects.get(zone=LocalZone)      
    except:
	e = sys.exc_info()[0]
	d = sys.exc_info()[1]
	logging.error("MakeVideoRenditions(): Error in LocalZone / Settings [%s -> %s]" % (e,d))
	return False


    try:
	Item = RenditionTask.item
    except:
	e = sys.exc_info()[0]
	logging.error("MakeVideoRenditions(): ImportTask not have an Item. Catch: %s" % e)
	ErrorString = "ImportTask not have an Item. Catch: %s" % e
	return False

    logging.info("MakeVideoRenditions(): Creating video rendition for item: " + Item.name )


    if Settings.optimize_profiles_with_brand == 'Y':
	VProfileList_pre = models.GetVideoProfilesBrand(Item.internal_brand)
	if Item.internal_brand.format == 'HD' and Item.format == 'SD':
	    logging.warning("MakeVideoRenditions(): Internal Brand is HD but Item format is SD -> Eliminate HD Profiles")
	    #
	    # Hay que eliminar los HD
	    #
	    VProfileList = []
	    for VProfile in VProfileList_pre:
		if VProfile.format == 'SD':
		    VProfileList.append(VProfile)
	else:
	    VProfileList = VProfileList_pre	    
    else:

        #
	# Define que tipos de Video Profiles debe usar
	# SD o HD
        #
	if Item.format == 'HD':
	    VProfileList = models.GetVideoProfiles()
	elif Item.format == 'SD':
	    VProfileList = models.GetVideoProfiles('SD')
        
    
    if RenditionTask.local_file == 'Y':

	local_master_path =  models.GetPath('local_master_path')
	if local_master_path is not None:
	    if not local_master_path.endswith('/'):
		local_master_path = local_master_path + '/'
	else:
	    ErrorString = "MakeVideoRenditions(): local_master_path is None"
	    logging.error("MakeVideoRenditions(): local_master_path is None")
	    return False
    else:    
	ErrorString = "MakeVideoRenditions(): local_file is No"
	logging.error("MakeVideoRenditions(): local_file is No")
	return False

    File   = RenditionTask.file_name
    
    subtitle_local_path = models.GetPath('subtitle_local_path')
    if subtitle_local_path is not None:
        if not subtitle_local_path.endswith('/'):
    	    subtitle_local_path = subtitle_local_path + '/'
    
    #
    # Por cada video profile crea un video rendition ahora deberia chequear si Tiene subtitulo y si existe el archivo
    #
    for VProfile in VProfileList:
	
	burn_spa  = False
	burn_prt  = False
	burn_none = False
	sub_spa   = None
	sub_prt   = None
	
	if Item.subtitle_spa != '':
	    if FileExist(subtitle_local_path,Item.subtitle_spa):	
		if len(models.Customer.objects.filter(subtitle_language='S',video_profile=VProfile)) > 0:
		    #
		    # Hay almenos un cliente que tiene este video profile con esta opcion de subtitlado
		    #
		    burn_spa = True
		    sub_spa  = subtitle_local_path + Item.subtitle_spa
		else:
		    burn_spa = False 
	    else:
		#
		# Que hacemos aca?
		#
		ErrorString = "MakeVideoRenditions(): Can not Find the file in local_svc_path [%s]" % (subtitle_local_path + Item.subtitle_spa)
		logging.error("MakeVideoRenditions(): Can not Find the file in local_svc_path [%s]" % (subtitle_local_path + Item.subtitle_spa))
	        return False
	else:
	    burn_none = True
		    
	if Item.subtitle_prt != '':
	    if FileExist(subtitle_local_path,Item.subtitle_prt):
		if len(models.Customer.objects.filter(subtitle_language='P',video_profile=VProfile)) > 0:
		    #
		    # Hay almenos un cliente que tiene este video profile con esta opcion de subtitlado
		    #
		    burn_prt = True
		    sub_prt  = subtitle_local_path + Item.subtitle_prt
		else:
		    burn_prt = False
	    else:
		#
		# Que hacemos aca?
		#
		ErrorString = "MakeVideoRenditions(): Can not Find the file in local_svc_path [%s]" % (subtitle_local_path + Item.subtitle_prt)
		logging.error("MakeVideoRenditions(): Can not Find the file in local_svc_path [%s]" % (subtitle_local_path + Item.subtitle_prt))
	        return False	    
	else:
	    burn_none = True
	
	if len(models.Customer.objects.filter(subtitle_language='N',video_profile=VProfile)) > 0:
	    burn_none = True	
	
	logging.info("MakeVideoRenditions(): VProfile: " + VProfile.name)
	
	TranscodeGuid = VProfile.guid
	
	if FileExist(local_master_path,RenditionTask.file_name):
	    logging.info("MakeVideoRenditions(): File Exist in local_svc_path [%s]" % (local_master_path + RenditionTask.file_name))
	    Source = GetSmbLocalPath()
	    if Source is None:
	        ErrorString = "MakeVideoRenditions(): Fail in GetSmbLocalPath"
	        logging.error("MakeVideoRenditions(): Fail in GetSmbLocalPath")		
	        return False

	else:
	    ErrorString = "MakeVideoRenditions(): Can not Find the file in local_svc_path [%s]" % (local_master_path + RenditionTask.file_name)
	    logging.error("MakeVideoRenditions(): Can not Find the file in local_svc_path [%s]" % (local_master_path + RenditionTask.file_name))
	    return False
	
	logging.info("MakeVideoRenditions(): Source-> " + Source + " File-> " + File)    
	logging.info("MakeVideoRenditions(): VProfileList len: " + str(len(VProfileList)))
	#
	# Si existe ya existe un video rendition con ese profile para ese item
	# no lo procesa y continua con el siguiente profile
	#
	if burn_none:
	    if not CheckVideoRendition(Item,VProfile,'N'):
		logging.warning("MakeVideoRendition(): Video Profile exist-> Continue. [VP: %s]" % VProfile.name )
	        burn_none = False
	    
	if burn_spa:
	    if not CheckVideoRendition(Item,VProfile,'S'):
		logging.warning("MakeVideoRendition(): Video Profile exist-> Continue. [VP: %s - Subtitle: SPA]" % VProfile.name )
	        burn_spa = False
	    
	if burn_prt:
	    if not CheckVideoRendition(Item,VProfile,'S'):
		logging.warning("MakeVideoRendition(): Video Profile exist-> Continue. [VP: %s - Subtitle: PRT]" % VProfile.name )
	        burn_prt = False    

	if burn_none == False and burn_spa == False and burn_prt == False:
	    continue
	    

	if burn_none == True:
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
	    ####
	    # Reemplaza los signos de puntuacion por vacio
	    #
	    for c in string.punctuation:
	        if c != '.' and c != '-' and c != '_':
	    	    DstFilename= DstFilename.replace(c,'')

	    DstBasename = SplitExtension(DstFilename)
	    if DstBasename is None:
		logging.error = "MakeVideoRenditions(): 04: Unable to stablish DstBasename"
	        ErrorString   = "04: Unable stablish DstBasename"
	        return False
	

	if burn_spa == True:
	    #
	    # Arma el destination filename y el basename
	    #
	    DstFilename_Spa = RenditionFileName(File, VProfile.sufix + '_' + VProfile.sufix_sub_spa, VProfile.file_extension)
	    if DstFilename_Spa is None:
	        logging.error = "MakeVideoRenditions(): 03: Unable stablish DstFileName_Spa, [FILE]-> " + File + " ,[SUFIX]-> " + VProfile.sufix 
	        ErrorString   = "03: Unable stablish DstFileName_Spa, [FILE]-> " + File + " ,[SUFIX]-> " + VProfile.sufix
	        return False
	

	    DstFilename_Spa = DstFilename_Spa.replace(' ', '')
	    DstFilename_Spa = PrefixStrId(Item.id) + '-' + DstFilename_Spa
	    ####
	    # Reemplaza los signos de puntuacion por vacio
	    #
	    for c in string.punctuation:
	        if c != '.' and c != '-' and c != '_':
	    	    DstFilename_Spa= DstFilename_Spa.replace(c,'')


	    DstBasename_Spa = SplitExtension(DstFilename_Spa)
	    if DstBasename_Spa is None:
		logging.error = "MakeVideoRenditions(): 04: Unable to stablish DstBasename_Spa"
	        ErrorString   = "04: Unable stablish DstBasename"
	        return False
	
	
	    try:
		subtitle_profile = models.SubtitleProfile.objects.get(format=VProfile.format)
	    except:
		logging.error = "MakeVideoRenditions(): Unable to get SubtitleProfile in %s" % (VProfile.format)
	        ErrorString   = "Unable to get SubtitleProfile in %s" % (VProfile.format)
	        return False
	
	    XmlTitlerElementSpa = StlToXmlTitler(subtitle_profile, sub_spa) 

	if burn_prt == True:
	    #
	    # Arma el destination filename y el basename
	    #
	    DstFilename_Prt = RenditionFileName(File, VProfile.sufix + '_' + VProfile.sufix_sub_prt, VProfile.file_extension)
	    if DstFilename_Prt is None:
	        logging.error = "MakeVideoRenditions(): 03: Unable stablish DstFileName_Prt, [FILE]-> " + File + " ,[SUFIX]-> " + VProfile.sufix 
	        ErrorString   = "03: Unable stablish DstFileName_Prt, [FILE]-> " + File + " ,[SUFIX]-> " + VProfile.sufix
	        return False
	

	    DstFilename_Prt = DstFilename_Prt.replace(' ', '')
	    DstFilename_Prt = PrefixStrId(Item.id) + '-' + DstFilename_Prt
	    ####
	    # Reemplaza los signos de puntuacion por vacio
	    #
	    for c in string.punctuation:
	        if c != '.' and c != '-' and c != '_':
	    	    DstFilename_Prt= DstFilename_Prt.replace(c,'')

	    DstBasename_Prt = SplitExtension(DstFilename_Prt)
	    if DstBasename_Prt is None:
		logging.error = "MakeVideoRenditions(): 04: Unable to stablish DstBasename_Prt"
	        ErrorString   = "04: Unable stablish DstBasename_Prt"
	        return False

	    try:
		subtitle_profile = models.SubtitleProfile.objects.get(format=VProfile.format)
	    except:
		logging.error = "MakeVideoRenditions(): Unable to get SubtitleProfile in %s" % (VProfile.format)
	        ErrorString   = "Unable to get SubtitleProfile in %s" % (VProfile.format)
	        return False

	    XmlTitlerElementPrt = StlToXmlTitler(subtitle_profile, sub_prt) 

	#
	# Arma los parametros de transcodificacion
	#
	TranscodeInfo    = None
	TranscodeInfoSpa = None
	TranscodeInfoPrt = None
	
	if len(Item.brand.logo.filter(format=VProfile.format)) != 0:	
#	if len(Item.internal_brand.logo.filter(format=VProfile.format)) != 0:
#	    Logo = Item.internal_brand.logo.filter(format=VProfile.format)
	    Logo = Item.brand.logo.filter(format=VProfile.format)
	    BitMap = BitmapKeying()
	    BitMap.Filename      = Logo[0].filename
	    BitMap.Dialog_BIN    = Logo[0].dialog
	    BitMap.Position_DWD  = Logo[0].position
	    BitMap.Scale_DBL     = Logo[0].scale
	    BitMap.Offset_DBL    = Logo[0].offset
	    BitMap.Opacity_DBL   = Logo[0].opacity

	    logging.info("MakeVideoRenditions(): Adding logo: %s (%s)" % (Logo[0].name, Logo[0].filename))
	
	    if burn_none == True:
		TranscodeInfo = { 'd_guid'    : TranscodeGuid, 
		                  'd_basename': DstBasename, 
	    	                  'd_path'    : models.GetPath("video_smb_path"), 
	    	                  'logo'      : BitMap.ToElement()	  }
	    if burn_spa  == True:
		TranscodeInfoSpa = { 'd_guid'    : TranscodeGuid, 
		                     'd_basename': DstBasename_Spa, 
	    	                     'd_path'    : models.GetPath("video_smb_path"), 
	    	                     'logo'      : BitMap.ToElement(),
	    	                     'subtitle'  : XmlTitlerElementSpa.ToElement() }
	    if burn_prt == True:
		TranscodeInfoPrt = { 'd_guid'    : TranscodeGuid, 
		                     'd_basename': DstBasename_Prt, 
	    	                     'd_path'    : models.GetPath("video_smb_path"), 
	    	                     'logo'      : BitMap.ToElement(),
	    	                     'subtitle'  : XmlTitlerElementPrt.ToElement() }
	    	                     	                  
	    	              
	else:
	    if burn_none == True:
		TranscodeInfo = { 'd_guid'    : TranscodeGuid, 
	    	                  'd_basename': DstBasename, 
	                          'd_path'    : models.GetPath("video_smb_path") }
	    
	    if burn_spa  == True:
		TranscodeInfoSpa = { 'd_guid'    : TranscodeGuid, 
		                     'd_basename': DstBasename_Spa, 
	    	                     'd_path'    : models.GetPath("video_smb_path"), 
	    	                     'subtitle'  : XmlTitlerElementSpa.ToElement() }
	    if burn_prt == True:
		TranscodeInfoPrt = { 'd_guid'    : TranscodeGuid, 
		                     'd_basename': DstBasename_Prt, 
	    	                     'd_path'    : models.GetPath("video_smb_path"), 
	    	                     'subtitle'  : XmlTitlerElementPrt.ToElement() }

	logging.debug("MakeVideoRenditions(): Transcode Info: " +  str(TranscodeInfo))
	logging.debug("MakeVideoRenditions(): Transcode Info Spa: " +  str(TranscodeInfoSpa))
	logging.debug("MakeVideoRenditions(): Transcode Info Prt: " +  str(TranscodeInfoPrt))
	#
	# Envia el Job a transcodificar
	#

	XmlJob    = None
	XmlJobSpa = None
	XmlJobPrt = None
	
	try:
	    if burn_none == True:
		XmlJob    = CreateCarbonXMLJob(Source,File,[],[TranscodeInfo],None,None)
	    if burn_spa  == True:
		XmlJobSpa = CreateCarbonXMLJob(Source,File,[],[TranscodeInfoSpa],None,None)
	    if burn_prt  == True:
		XmlJobPrt = CreateCarbonXMLJob(Source,File,[],[TranscodeInfoPrt],None,None)	
	except:
	    e = sys.exc_info()[0]
	    logging.error("MakeVideoRendition(): 01: Exception making Carbon XML Job. Catch: " + e)
	    ErrorString = '01: Exception making Carbon XML Job. Catch: ' + e 
	
	if burn_none == True and XmlJob is None:
	    logging.error("MakeVideoRendition(): 01: Error making Carbon XML Job")
	    ErrorString = '01: Error making Carbon XML Job'
	    return False

	if burn_spa == True and XmlJobSpa is None:
	    logging.error("MakeVideoRendition(): 01: Error making Carbon XML Job Spa")
	    ErrorString = '01: Error making Carbon XML Job'
	    return False

	if burn_prt == True and XmlJobPrt is None:
	    logging.error("MakeVideoRendition(): 01: Error making Carbon XML Job Prt")
	    ErrorString = '01: Error making Carbon XML Job'
	    return False

	
	if burn_none == True:
	    JobReply       = StartJobCarbonPool(CPool,XmlJob, ForceSchedule)
	    VRendition = models.VideoRendition()
	    VRendition.file_name            	= DstFilename
	    VRendition.src_file_name		= File
	    VRendition.src_svc_path	    	= Source
	    VRendition.video_profile        	= VProfile
	    VRendition.item		    	= Item
	    VRendition.subtitle_burned		= 'N'
	    VRendition.subtitle_language    	= 'N'
	
	
	    if Item.format == 'HD':
		if VProfile.format == 'HD':
		    VRendition.screen_format = 'Widescreen'
		else:
		    VRendition.screen_format = 'Letterbox'
	    elif Item.format == 'SD':
		VRendition.screen_format = 'Standard'
	
	    if JobReply.Result == True:
		#
	        # Crea el Video Rendition en el modelo
	        #
	        VRendition.transcoding_job_guid = JobReply.Job.GetGUID()
	        VRendition.stimestamp	    	= str(int(time.time()))
	        VRendition.status               = 'Q'	# Queued
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
		    VRendition.transcoding_job_guid = ''
	            VRendition.status               = 'U'	# Unasigned
		    try:
			TServer = models.TranscodingServer.objects.get(ip_address='(Dummy)')
	    		VRendition.transcoding_server = TServer
	    	        logging.info("MakeVideoRenditions(): Carbon Server ->" + VRendition.transcoding_server.ip_address)
		    except:
			logging.error("MakeVideoRenditions(): Can not find the Assigned Carbon Server -> " + JobReply.Job.GetCarbonHostname())
	    	        return False
	
		    logging.info("MakeVideoRenditions(): Can Not Assign Carbon Server (No one have slots )")
	
		else:
		    ErrorString = '02: Error sending Job'
		    logging.error("MakeVideoRendition(): 02: Error sending Job")
	    	    return False

	    time.sleep(0.5)

	    VRendition.save()

	if burn_spa == True:
	    JobReply       = StartJobCarbonPool(CPool,XmlJobSpa, ForceSchedule)
	    VRendition = models.VideoRendition()
	    VRendition.file_name            	= DstFilename_Spa
	    VRendition.src_file_name		= File
	    VRendition.src_svc_path	    	= Source
	    VRendition.video_profile        	= VProfile
	    VRendition.sub_file_name		= sub_spa
	    VRendition.item		    	= Item
	    VRendition.subtitle_burned		= 'Y'
	    VRendition.subtitle_language    	= 'S'
		
	    if Item.format == 'HD':
		if VProfile.format == 'HD':
		    VRendition.screen_format = 'Widescreen'
		else:
		    VRendition.screen_format = 'Letterbox'
	    elif Item.format == 'SD':
		VRendition.screen_format = 'Standard'
	
	    if JobReply.Result == True:
		#
	        # Crea el Video Rendition en el modelo
	        #
	        VRendition.transcoding_job_guid = JobReply.Job.GetGUID()
	        VRendition.stimestamp	    	= str(int(time.time()))
	        VRendition.status               = 'Q'	# Queued
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
		    VRendition.transcoding_job_guid = ''
	            VRendition.status               = 'U'	# Unasigned
		    try:
			TServer = models.TranscodingServer.objects.get(ip_address='(Dummy)')
	    		VRendition.transcoding_server = TServer
	    	        logging.info("MakeVideoRenditions(): Carbon Server ->" + VRendition.transcoding_server.ip_address)
		    except:
			logging.error("MakeVideoRenditions(): Can not find the Assigned Carbon Server -> " + JobReply.Job.GetCarbonHostname())
	    	        return False
	
		    logging.info("MakeVideoRenditions(): Can Not Assign Carbon Server (No one have slots )")
	
		else:
		    ErrorString = '02: Error sending Job'
		    logging.error("MakeVideoRendition(): 02: Error sending Job")
	    	    return False

	    time.sleep(0.5)

	    VRendition.save()


	if burn_prt == True:
	    JobReply       = StartJobCarbonPool(CPool,XmlJobPrt, ForceSchedule)
	    VRendition = models.VideoRendition()
	    VRendition.file_name            	= DstFilename_Prt
	    VRendition.src_file_name		= File
	    VRendition.src_svc_path	    	= Source
	    VRendition.video_profile        	= VProfile
	    VRendition.sub_file_name		= sub_prt
	    VRendition.item		    	= Item
	    VRendition.subtitle_burned		= 'Y'
	    VRendition.subtitle_language    	= 'P'
		
	    if Item.format == 'HD':
		if VProfile.format == 'HD':
		    VRendition.screen_format = 'Widescreen'
		else:
		    VRendition.screen_format = 'Letterbox'
	    elif Item.format == 'SD':
		VRendition.screen_format = 'Standard'
	
	    if JobReply.Result == True:
		#
	        # Crea el Video Rendition en el modelo
	        #
	        VRendition.transcoding_job_guid = JobReply.Job.GetGUID()
	        VRendition.stimestamp	    	= str(int(time.time()))
	        VRendition.status               = 'Q'	# Queued
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
		    VRendition.transcoding_job_guid = ''
	            VRendition.status               = 'U'	# Unasigned
		    try:
			TServer = models.TranscodingServer.objects.get(ip_address='(Dummy)')
	    		VRendition.transcoding_server = TServer
	    	        logging.info("MakeVideoRenditions(): Carbon Server ->" + VRendition.transcoding_server.ip_address)
		    except:
			logging.error("MakeVideoRenditions(): Can not find the Assigned Carbon Server -> " + JobReply.Job.GetCarbonHostname())
	    	        return False
	
		    logging.info("MakeVideoRenditions(): Can Not Assign Carbon Server (No one have slots )")
	
		else:
		    ErrorString = '02: Error sending Job'
		    logging.error("MakeVideoRendition(): 02: Error sending Job")
	    	    return False

	    time.sleep(0.5)

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

	    #
	    # Arma los parametros de transcodificacion
	    #	
#	    if len(VRendition.item.internal_brand.logo.filter(format=VRendition.video_profile.format)) != 0:
#		Logo = VRendition.item.internal_brand.logo.filter(format=VRendition.video_profile.format)
	    if len(VRendition.item.brand.logo.filter(format=VRendition.video_profile.format)) != 0:
		Logo = VRendition.item.brand.logo.filter(format=VRendition.video_profile.format)
	        BitMap = BitmapKeying()
	        BitMap.Filename      = Logo[0].filename
	        BitMap.Dialog_BIN    = Logo[0].dialog
	        BitMap.Position_DWD  = Logo[0].position
	        BitMap.Scale_DBL     = Logo[0].scale
	        BitMap.Offset_DBL    = Logo[0].offset
	        BitMap.Opacity_DBL   = Logo[0].opacity

		logging.info("ReScheduleUnasignedRenditions(): Adding logo: %s (%s)" % (Logo[0].name, Logo[0].filename))
	
	
		if VRendition.subtitle_burned == 'N':
		    TranscodeInfo = { 'd_guid'    : VRendition.video_profile.guid, 
	                    	      'd_basename': SplitExtension(VRendition.file_name), 
	                              'd_path'    : models.GetPath("video_smb_path"),
	    	    	              'logo'      : BitMap.ToElement()	  }
		else:
		    try:
			subtitle_profile = models.SubtitleProfile.objects.get(format=VRendition.video_profile.format)
		    except:
			logging.error = "ReSecheduleUnassignedVideoRenditions(): Unable to get SubtitleProfile in %s" % (VRendition.video_profile.format)
	    		ErrorString   = "Unable to get SubtitleProfile in %s" % (VRendition.video_profile.format)
	    		return False

		    XmlTitlerElement = StlToXmlTitler(subtitle_profile, VRendition.sub_file_name) 	
	
		    TranscodeInfo = { 'd_guid'    : VRendition.video_profile.guid, 
	                    	          'd_basename': SplitExtension(VRendition.file_name), 
	                                  'd_path'    : models.GetPath("video_smb_path"),
	    	    	                  'subtitle'  : XmlTitlerElement.ToElement(),
	    	    	                  'logo'      : BitMap.ToElement()	  }
	

	    else:
		
		if VRendition.subtitle_burned == 'N':
		    TranscodeInfo = { 'd_guid'    : VRendition.video_profile.guid, 
	                              'd_basename': SplitExtension(VRendition.file_name), 
	                              'd_path'    : models.GetPath("video_smb_path") }	    

		else:
		    try:
			subtitle_profile = models.SubtitleProfile.objects.get(format=VRendition.video_profile.format)
		    except:
			logging.error = "ReSecheduleUnassignedVideoRenditions(): Unable to get SubtitleProfile in %s" % (VRendition.video_profile.format)
	    		ErrorString   = "Unable to get SubtitleProfile in %s" % (VRendition.video_profile.format)
	    		return False

		    XmlTitlerElement = StlToXmlTitler(subtitle_profile, VRendition.sub_file_name) 	
	
		    TranscodeInfo = { 'd_guid'    : VRendition.video_profile.guid, 
	                    	          'd_basename': SplitExtension(VRendition.file_name), 
	                                  'd_path'    : models.GetPath("video_smb_path"),
	    	    	                  'subtitle'  : XmlTitlerElement.ToElement() }
		

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
	
		VRendition.stimestamp = str(int(time.time()))    	    	
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
    
	try:
	    LocalZone = models.ExportZone.objects.get(zone_name=Zone.LOCAL)
	    Settings  = models.Settings.objects.get(zone=LocalZone)      
	except:
	    e = sys.exc_info()[0]
	    d = sys.exc_info()[1]
	    logging.error("Main(): Error in LocalZone / Settings [%s -> %s]" % (e,d))
	    return False
    
	#
	# Reasignla las transcodificaciones
	#    
	if not ReScheduleUnasignedRenditions(True if Settings.force_schedule == 'Y' else False):
	    loggin.error("Main(): Error in ReSCheduleUnassignedRenditions [SHUTDOWN]")
	    End = True
	    continue
	#
	# Crea las Video/Images Renditions
	#
	if not MakeRenditions(True if Settings.force_schedule == 'Y' else False):
	    End = True
	    loggin.error("Main(): Error in MakeRenditions [SHUTDOWN]")
	    continue
	

	if Settings.global_sleep_time != '':
    	    try:
	        time.sleep(int(Settings.global_sleep_time))
	    except:
	        end = True 
	        logging.error("main(): Critical error, plase check global_sleep_time [SHUTDOWN]")   
	        raise KeyboardInterrupt
	else:
	    try:
	        time.sleep(int(Settings.qimport_sleep))
	    except:
	        end = True 
	        logging.error("main(): Critical error, plase check qimport_sleep [SHUTDOWN]") 
		raise KeyboardInterrupt

    logging.info("Main(): Bye Bye")

    
class main_daemon(Daemon):
    def run(self):
        try:
    	    Main()
	except KeyboardInterrupt:
	    sys.exit()	    

if __name__ == "__main__":
#	StartMessage()
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


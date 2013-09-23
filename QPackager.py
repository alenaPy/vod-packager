#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Stand alone script
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from django.core.management import setup_environ
from Packager import settings
setup_environ(settings)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Modelo de la aplicacion
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from Packager_app import models

from cablelabsadi import ADIXml
from cablelabsadi import RiGHTvAsset
from cablelabsadi import NepeXml
from datetime import datetime, timedelta
from Lib.daemon import Daemon


import xml.etree.ElementTree as ET

import string
import os, time, sys, re
import logging
import Settings

from unicodedata import normalize

def normalize_string(unicode_string):
    return normalize('NFKD', unicode_string).encode('ASCII', 'ignore')


ErrorString = ''


def DateCalc(Year = None, Month = None, MonthToAdd = None):
    if Year is not None and Month is not None and MonthToAdd is not None:
        tmp   = int((Month + MonthToAdd) / 13)
        year  = Year + tmp
        month = int((Month + MonthToAdd) % 12)
        month = 12 if month == 0 else month

        return year, month
    return None, None

def GetStartDate(DateStr=''):
    if DateStr != '':

        result = re.match('([0-9]{4})([0][1-9]|[1][0-2])', DateStr)
        if result:
            return result.group(1), result.group(2)

    return None, None		
    	
def write_dtd_file(PackagePath=None):
    if PackagePath is not None:
	try:
	    dtd_src = open('ADI.DTD', 'rt')
	    dtd_dst = open(PackagePath+'ADI.DTD', 'wt')
	    dtd_dst.write(dtd_src.read())
	    dtd_src.close()
	    dtd_dst.close()
	except:
	    pass

    return     	
	
    	
MonthSpanish = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']    	
    	

def MakeAssetId(asset_type='package', asset_id = 0, package_id = 0, reduced = False, special_id = ''):

    first = '4'

    if asset_type == 'package':
	first = '2'
    elif asset_type == 'title':
	first = '3'
    elif asset_type == 'movie':
	first = '1'
    elif asset_type == 'image':
	first = '4'
    elif asset_type == 'preview':
	first = '5'

    str_id = str(asset_id) + str(package_id)
    zero = ''
    i = len(str_id)
    while i < 15:
        zero = zero + '0'
        i = i + 1

    if reduced:
	if special_id != '' and len(special_id) == 4:
	    return special_id + first + str_id
	else:
	    return 'PBLA' + first + str_id
    else:
	if special_id != '' and len(special_id) == 4:
	    return special_id + first + zero + str_id
	else:
	    return 'PBLA' + first + zero + str_id



def GetImageRenditions(Package=None):

    global ErrorString
    ErrorString  = ''

    if Package is None:
	ErrorString = 'Package is None'
	logging.error('GetImageRenditions(): %s' % ErrorString)
	return None

    ImageProfileList   = Package.customer.image_profile.filter(status='E')
    ImageRenditionList = []

    for IProfile in ImageProfileList:
	logging.debug('GetImageRenditions(): Search ImageRendition for this image profile: %s' % IProfile.name)
	try:
	    IRendition = models.ImageRendition.objects.get(item=Package.item, image_profile=IProfile, status='D')
	    logging.debug('GetImageRenditions(): Found: %s' % IRendition.file_name)
	    ImageRenditionList.append(IRendition)
	except:
	    ErrorString = 'Does not exist an Image Rendition for this item: ' + Package.item.name + ', for this profile: ' + IProfile.name
	    logging.error('GetImageRenditions(): %s. RETURN None' % ErrorString)

    return ImageRenditionList

def GetVideoRenditions(Package=None):

    if Package is not None:
	

	Customer         = Package.customer
	VideoProfileList = Package.customer.video_profile.filter(status='E')
	Item		 = Package.item

	global ErrorString
	ErrorString = ''


	ExportSD = False
	ExportHD = False

	ProfileHD = None
	ProfileSD = None

	VRenditionList = []

	VPListLen = len(VideoProfileList)


	if VPListLen == 0 or VPListLen > 2:
	    #
	    # No tiene correctamente definido los profiles
	    #
	    ErrorString = '01: Number of VideoProfile are wrong: ' + str(VPListLen)
	    logging.error("GetVideoRenditions():" + ErrorString)
	    return None

	else:
	    #
	    # Que formatos usa el cliente
	    #
	    logging.info('GetVideoRenditions(): Customer: ' + Customer.name + ', Export Format: ' + Customer.export_format)
	    if Customer.export_format == 'BOTH' or Customer.export_format == 'HD':
		#
	        # Ambos formatos
	        #
		logging.info('GetVideoRenditions(): Len of Video Profiles: ' + str(VPListLen))
		if VPListLen == 2:

		    if VideoProfileList[0].format != VideoProfileList[1].format:
			#
		        # Esta correctamente definido
		        #
		        ExportSD = True
		        ExportHD = True
	    
			if VideoProfileList[0].format == 'SD':
			    ProfileSD = VideoProfileList[0]
			    ProfileHD = VideoProfileList[1]
			else:
			    ProfileSD = VideoProfileList[1]
			    ProfileHD = VideoProfileList[0]

			logging.info("Profile SD: %s" % ProfileSD.name)
			logging.info("Profile HD: %s" % ProfileHD.name)
		    else:
			#
			# Esta mal definido tiene dos profiles pero iguales
		        #
			ErrorString = '02: The customer have 2 profiles but both are in same format: ' + VideoProfileList[0].format
			logging.error("GetVideoRenditions(): " + ErrorString)
			return None
    

		        
		elif VPListLen == 1:
		    #
		    # Tiene un solo profile definido
		    #
		    if VideoProfileList[0] == 'SD':
			logging.info("GetVideoRenditions(): The Customer %s only have a SD profile defined" % Customer.name)
			#
		        # Exporta solamente SD porque no tiene definido uno HD
		        #
			ExportSD = True
			ProfileSD = VideoProfileList[0]
			logging.info("GetVideoRenditions(): Profile SD: %s" % ProfileSD.name)
		    else:
			logging.info("GetVideoRenditions(): The Customer %s only have a HD profile defined" % Customer.name)
			#
		        # Exporta solamente HD porque no tiene definido uno SD
			#
			ProfileHD = VideoProfileList[0]
			logging.info("GetVideoRenditions(): Profile HD: %s" % ProfileHD.name)
			ExportHD = True


	    elif Customer.export_format == 'OSD':
	    
		if VPListLen == 1:
		    if VideoProfileList[0].format == 'SD':
			#
			# Exporta SD
			#
			ExportSD = True
			ProfileSD = VideoProfileList[0]
			logging.info("GetVideoRenditions(): Profile SD: %s" % ProfileSD.name) 
		    else:
			#
			# Tiene un solo profile definido pero no es SD
		        #
			ErrorString = '03: The Customer have preferences of SD but does not have a VideoProfile with SD Format'
			logging.error("GetVideoRenditions(): " + ErrorString)
			return None

		else:
		    if (VideoProfileList[0].format == 'SD' or VideoProfileList[1].format == 'SD') and (VideoProfileList[0].format != VideoProfileList[1].format):
			if VideoProfileList[0].format == 'SD':
			    ProfileSD = VideoProfileList[0]
			else:
			    ProfileSD = VideoProfileList[1]
			logging.info("GetVideoRenditions(): Profile SD: %s" % ProfileSD.name)
			ExportSD = True
		    else:
			#
			# Error logico, solamente el cliente exporta SD pero no tiene ningun
			# Video profile definido SD o tiene los dos profiles definidos como SD
			#
			ErrorString = '04: The Customer have preferences of SD but does not have a VideoProfile with SD Format or have 2 SD format defined' 
			logging.error("GetVideoRenditions(): " + ErrorString)
			return None

	    elif Customer.export_format == 'OHD':
	    
		if VPListLen == 1:
		    if VideoProfileList[0].format == 'HD':
			# 
			# Solamente HD
			#
			ProfileHD = VideoProfileList[0]
			ExportHD = True
		    else:
			#
			# Tiene un solo profile definido pero no es HD
			#
			ErrorString = '05: The Customer have preferences of SD but does not have a VideoProfile with HD Format'
			logging.error("GetVideoRenditions(): " + ErrorString)
			return None
		else:
		    if (VideoProfileList[0].format == 'HD' or VideoProfileList[1].format == 'HD') and (VideoProfileList[0].format != VideoProfileList[1].format):
			if VideoProfileList[0].format == 'HD':
			    ProfileHD = VideoProfileList[0]
			else:
			    ProfileHD = VideoProfileList[1]
			ExportHD = True
			logging.info("GetVideoRenditions(): Profile HD: %s" % ProfileHD.name)
		    else:
			#
			# Error logico, solamente el cliente exporta hd pero no tiene ningun
			# Video profile definido HD o tiene los dos profiles definidos como HD
			#
			ErrorString = '06: The Customer have preferences of HD but does not have a VideoProfile with HD Format or have 2 HD format defined'
			logging.error("GetVideoRenditions(): " + ErrorString)
			return None
		    



	logging.info("GetVideoRenditions(): Item Format: %s" % Item.format)
	if Item.format == 'HD' and Item.internal_brand.format == 'HD':
	    #
	    # El item esta en formato HD
	    #
	    if ExportHD:
		try:
		    VRendition = models.VideoRendition.objects.get(item=Item,video_profile=ProfileHD, status='F')
		    VRenditionList.append(VRendition)
		    logging.info("GetVideoRendition(): Video Rendition HD: %s" % VRendition.file_name)
		    #
		    # Si el cliente prefiere HD no le exporta la version en SD
		    #
		    
		    if Customer.export_format == 'HD':
			logging.info("GetVideoRendition(): Only export a HD format because is the customer preference")
			ExportSD = False			    
    		except:
		    #
		    # No existe un video rendition para ese video
		    #
		    ErrorString = '07: Not exist VideoRendition for this VideoProfile in the Item: [ITEM: ' + Item.name + '], [VP: ' + ProfileHD.name + ']'
		    logging.error("GetVideoRenditions(): " + ErrorString)
		    return None

	    if ExportSD:
		try:
		    VRendition = models.VideoRendition.objects.get(item=Item,video_profile=ProfileSD,status='F')
		    VRenditionList.append(VRendition)
		    logging.info("GetVideoRendition(): Video Rendition SD: %s" % VRendition.file_name)
		except:
		    #
		    # No existe el video rendition para ese video
		    #
		    ErrorString = '08: Not exist VideoRendition for this VideoProfile in the Item: [ITEM: ' + Item.name + '], [VP: ' + ProfileSD.name + ']'
		    logging.error("GetVideoRenditions(): " + ErrorString)
		    return None

	elif Item.format == 'SD' or Item.internal_brand.format == 'SD':
	    #
	    # El item esta en formato SD
	    #
	    if ExportSD:
	    	try:
		    VRendition = models.VideoRendition.objects.get(item=Item,video_profile=ProfileSD, status='F')
		    VRenditionList.append(VRendition)
		    logging.info("GetVideoRendition(): Video Rendition SD: %s" % VRendition.file_name)
		
		except:
		    #
		    # No existe el video rendition para ese video
		    #
		    ErrorString = '09: Not exist VideoRendition for this VideoProfile in the Item: [ITEM: ' + Item.name + '], [VP: ' + ProfileSD.name + ']'
		    logging.error("GetVideoRenditions(): " + ErrorString)
		    return None
	    
	    if ExportHD:
		    logging.info("GetVideoProfile(): Not exist a HD Rendition for this item because the item is in SD Format")

	ErrorString = 'OK'
	return VRenditionList


def GetExportPathFromPackage(Package=None):

    global ErrorString

    ErrorString = 'OK'

    if Package is not None:
	try:
	    export_path = models.Path.objects.get(key='package_export_path').location
	except:
	    #
	    # No esta el export path definido en la base o tiene un nombre incorrecto
	    #
	    ErrorString = '10: Export Path (package_export_path) is not defined' 
	    logging.error("GetExportPathFromPackage():" + ErrorString)
	    return None
	
	if export_path is not None:
	    customer_path = Package.customer.export_folder
	    group_path    = Package.group.name
	
	    #
	    # group_path es el nombre del grupo de exportacion
	    # nunca deberia tener /, siempre se agrega
	    #
	    group_path		= group_path    + '/'
	    export_path		= export_path   + '/' if not export_path.endswith('/')   else export_path
	    customer_path	= customer_path + '/' if not customer_path.endswith('/') else customer_path
	    basepath		= export_path   + customer_path


	    if os.path.exists(basepath):
	    
		if not os.path.exists(basepath+group_path):
		    try:
			os.mkdir(basepath+group_path)
		    except OSError as e:
			#
			# No puede crear el directorio
			#
			ErrorString = '11: Can not create dir -> ' + basepath + group_path + "[" + e.strerror +"]"
			logging.error("GetExportPathFromPackage():" + ErrorString)
			return None
		return_path = basepath + group_path
	    
	    else:
		#
		# No existe en el filesystem el export_path + el customer_path
		#
		ErrorString = '12: Customer export path not exist -> ' + basepath
		logging.error("GetExportPathFromPackage():" + ErrorString)
		return None

	else:
	    #
	    # No tiene valor asignado el export_path
	    #
	    ErrorString = '13: In value package_export_path'
	    logging.error("GetExportPathFromPackage():" + ErrorString)
	    return None
    else:
	#
	# Argumento Package falta
	#
	ErrorString = '14: Argument Package is None'
	logging.error("GetExportPathFromPackage():" + ErrorString)
	return None
    #
    # Termina correctamente
    # 
    ErrorString = 'OK'
    return return_path


def GetMetadataLanguage(Item, Language):
    try:
	return models.MetadataLanguage.objects.get(item=Item, language=Language)
    except:
	return None



def MakeAdiXmlNepe(Package=None, VideoRendition=None, ImageRendition=None):

    if Package is None or VideoRendition is None or ImageRendition is None:
	#
	# Error
	#
	return None
    
    MetadataLanguage = GetMetadataLanguage(Package.item, Package.customer.export_language)
    if MetadataLanguage is None:
	#
	# No hay metadata asociada al item
	#
	return None

    MetadataXml = NepeXml.NepeXml()

    MetadataXml.ItemID = Package.item.mam_id
    
    
    try:
	License_Months = int(Package.customer.license_window)
    except:
	License_Months = 3
    
    year, month = GetStartDate(Package.group.name)
    if year is None or month is None:
	MetadataXml.StartWindow = str(Package.date_published + timedelta(days=15))
	MetadataXml.EndWindow   = str(Package.date_published + timedelta(days=15) + timedelta(days=License_Months))
    else:
    	MetadataXml.StartWindow = year + '-' + month + '-01'
    	end_year, end_month = DateCalc(int(year), int(month), License_Months)
    	if end_year is not None and end_month is not None:
    	    MetadataXml.EndWindow = str(end_year) + '-' + (str(end_month) if len(str(end_month)) == 2 else '0'+str(end_month)) +'-01'
    
    #
    # Busca la categoria de acuerdo con el cliente
    #
    try:
        CategoryRelation = models.CategoryRelation.objects.get(category=Package.item.category,customer=Package.customer)
        CustomCategory   = CategoryRelation.custom_category
    except:
        CustomCategory = Package.item.category
    
    MetadataXml.ExportDate  = str(Package.date_published)
    MetadataXml.Distributor = "Playboy"
    MetadataXml.ContentType = 'Movie'
    MetadataXml.Title = MetadataLanguage.title
    MetadataXml.OriginalTitle = Package.item.name 
    MetadataXml.ShortDescription = MetadataLanguage.summary_short
    MetadataXml.LongDescription = MetadataLanguage.summary_long
    MetadataXml.Country   = Package.item.country_of_origin.code
    MetadataXml.Actors    = Package.item.actors_display
    MetadataXml.Directors = Package.item.director
    MetadataXml.Brand     = Package.item.brand
    MetadataXml.Category  = CustomCategory.name
    MetadataXml.Duration  = Package.item.run_time
    MetadataXml.Standard  = VideoRendition.video_profile.format
    MetadataXml.Rating    = 'XXX'
    MetadataXml.AudioType = 'Stereo'
    MetadataXml.VideoFormat = VideoRendition.video_profile.codec
    
    suffix = '_' + MetadataXml.Standard


    Asset_Name_Normalized = normalize_string(MetadataLanguage.title)
    Asset_Name_Normalized = Asset_Name_Normalized.translate(None, string.punctuation)
    Asset_Name_Normalized = Asset_Name_Normalized.replace(' ', '_')

    
    if VideoRendition.video_profile.file_extension.startswith('.'):
        MetadataXml.VideoFile	= Asset_Name_Normalized + suffix + VideoRendition.video_profile.file_extension
    else:
        MetadataXml.VideoFile	= Asset_Name_Normalized + suffix + '.' + VideoRendition.video_profile.file_extension
    
    if ImageRendition.image_profile.file_extension.startswith('.'):
	MetadataXml.ImageFile   = Asset_Name_Normalized + suffix + ImageRendition.image_profile.file_extension
    else:
	MetadataXml.ImageFile   = Asset_Name_Normalized + suffix + '.' + ImageRendition.image_profile.file_extension
	

    return MetadataXml
    

def MakeAdiXmlRiGHTvAsset(Package=None, VideoRendition=None, ImageRendition=None):
    
    if Package is None or VideoRendition is None or ImageRendition is None:
	#
	# Error
	#
	return None
    
    MetadataLanguage = GetMetadataLanguage(Package.item, Package.customer.export_language)
    if MetadataLanguage is None:
	#
	# No hay metadata asociada al item
	#
	return None
    
    MetadataXml = RiGHTvAsset.RiGHTvAssets()
    #
    # Se carga el ID
    #
    MetadataXml.VideoAssets.ID		= MakeAssetId('package', VideoRendition.id, Package.id)
    MetadataXml.VideoAssets.ProviderID  = 'Claxson'
    
    
    MetadataXml.VideoAssets.Title	= MetadataLanguage.title.upper()
    MetadataXml.VideoAssets.Description = MetadataLanguage.summary_medium


    Asset_Name_Normalized = normalize_string(MetadataLanguage.title)
    Asset_Name_Normalized = Asset_Name_Normalized.translate(None, string.punctuation)
    Asset_Name_Normalized = Asset_Name_Normalized.replace(' ', '_')

    #
    # Metadata Fija
    #
    MetadataXml.VideoAssets.ParentalRating	= 'AO'
    MetadataXml.VideoAssets.Advisories		= 'Advisories'
    
    
    try:
	License_Months = int(Package.customer.license_window)
    except:
	License_Months = 3

    
    
    year, month = GetStartDate(Package.group.name)
    if year is None or month is None:
	MetadataXml.VideoAssets.LicensingWindow.StartDateTime   = str(Package.date_published + timedelta(days=15))
	MetadataXml.VideoAssets.LicensingWindow.EndDateTime     = str(Package.date_published + timedelta(days=15) + timedelta(days=License_Months))
    else:
    	MetadataXml.VideoAssets.LicensingWindow.StartDateTime	= year + '-' + month + '-01'
    	end_year, end_month = DateCalc(int(year), int(month), License_Months)
    	if end_year is not None and end_month is not None:
    	    MetadataXml.VideoAssets.LicensingWindow.EndDateTime	= str(end_year) + '-' + (str(end_month) if len(str(end_month)) == 2 else '0'+str(end_month)) +'-01'
        
    if Package.customer.license_date_format == 'DT':
	MetadataXml.VideoAssets.LicensingWindow.StartDateTime  =  MetadataXml.VideoAssets.LicensingWindow.StartDateTime + 'T00:00:00.00Z'
	MetadataXml.VideoAssets.LicensingWindow.EndDateTime    =  MetadataXml.VideoAssets.LicensingWindow.EndDateTime   + 'T00:00:00.00Z'

    
    MetadataXml.VideoAssets.AMSPath = 'CLAXSON'


    if VideoRendition.video_profile.format == 'HD':
	suffix = '_HD'
    else:
	suffix = '_SD'


# Sacar Poster File


#    MetadataXml.VideoAssets.PosterFiles.Name		= MetadataLanguage.title
#    MetadataXml.VideoAssets.PosterFiles.Description	= MetadataLanguage.title
#    if ImageRendition.image_profile.file_extension.startswith('.'):
#	MetadataXml.VideoAssets.PosterFiles.FileName	= Asset_Name_Normalized + suffix + ImageRendition.image_profile.file_extension
#    else:
#	MetadataXml.VideoAssets.PosterFiles.FileName	= Asset_Name_Normalized + suffix + '.' + ImageRendition.image_profile.file_extension


    #
    # Busca la categoria de acuerdo con el cliente
    #
    try:
        CategoryRelation = models.CategoryRelation.objects.get(category=Package.item.category,customer=Package.customer)
        CustomCategory   = CategoryRelation.custom_category
    except:
        CustomCategory = Package.item.category
        
	
#    MetadataXml.VideoAssets.AMSPath = CustomCategory.name

    MetadataXml.VideoAssets.addExtraFields('Cast', Package.item.actors_display)
    MetadataXml.VideoAssets.addExtraFields('Director', Package.item.director)
    MetadataXml.VideoAssets.addExtraFields('Year', Package.item.year)

    #
    # Nombre del file se Video
    #
    if VideoRendition.video_profile.file_extension.startswith('.'):
    	    MetadataXml.VideoAssets.MediaFiles.FileName	= Asset_Name_Normalized + suffix + VideoRendition.video_profile.file_extension
    else:
	    MetadataXml.VideoAssets.MediaFiles.FileName = Asset_Name_Normalized + suffix + '.' + VideoRendition.video_profile.file_extension

	    
    if month is None:
	month = '01'	    

#    MetadataXml.VideoAssets.MediaFiles.TransferURL = '/contenidos/claxson/' + MonthSpanish[int(month)-1] + '/' + MetadataXml.VideoAssets.MediaFiles.FileName
    MetadataXml.VideoAssets.MediaFiles.TransferURL = '/contenidos/claxson/' + MetadataXml.VideoAssets.MediaFiles.FileName
    MetadataXml.VideoAssets.MediaFiles.RunTime	   = Package.item.run_time
    MetadataXml.VideoAssets.MediaFiles.Encryption  = 'Verimatrix'
    MetadataXml.VideoAssets.MediaFiles.Encoding    = 'MPEG-4'
    if VideoRendition.video_profile.format == 'HD':
	MetadataXml.VideoAssets.MediaFiles.DisplayType = '16:9'
    else:
	MetadataXml.VideoAssets.MediaFiles.DisplayType = '4:3'
	
    MetadataXml.VideoAssets.MediaFiles.BitRate	   = '2345235'	
#    MetadataXml.VideoAssets.MediaFiles.BitRate	   = str(int(VideoRendition.video_profile.bit_rate)*1000)
    
    MetadataXml.VideoAssets.MediaFiles.ServiceDistribution.Name = "VOD"
    MetadataXml.VideoAssets.MediaFiles.ServiceDistribution.Density.Type = "RELATIVE"
    MetadataXml.VideoAssets.MediaFiles.ServiceDistribution.Density.Value = "100"
    

    
    return MetadataXml

        
    
def MakeAdiXmlCablelabs(Package=None, VideoRendition=None, ImageRendition=None):

    if Package is None or VideoRendition is None or ImageRendition is None:
	#
	# Error
	#
	return None


    #
    # Busca la Metadata segun el lenguaje de exportacion del cliente
    #
    MetadataLanguage = GetMetadataLanguage(Package.item, Package.customer.export_language)
    if MetadataLanguage is None:
	#
	# No hay metadata asociada al item
	#
	return None

    Asset_Name_Normalized = normalize_string(MetadataLanguage.title_brief)
    Asset_Name_Normalized = Asset_Name_Normalized.translate(None, string.punctuation)

    if Package.customer.id_len_reduced == 'Y':
	Asset_ID	= MakeAssetId('package', VideoRendition.id, Package.id, True,  Package.customer.id_special_prefix)
    else:
	Asset_ID	= MakeAssetId('package', VideoRendition.id, Package.id, False, Package.customer.id_special_prefix)


    if Package.customer.provider_id_with_brand == 'Y':
	Provider_ID = 'playboy.' + Package.item.brand.replace(' ', '').upper()
    else:
	Provider_ID = 'playboy.com'
	
    if Package.customer.provider_id != '':
	Provider_ID = Package.customer.provider_id

    
    if Package.customer.special_product_type != '':
	Product = Package.customer.special_product_type
    else:
	Product = Package.customer.product_type
	    
    
    MetadataXml = ADIXml.Package(Provider      = 'PLAYBOY',
                		 Product       = Product if Package.customer.empty_product_type == 'N' else '',
                		 Asset_Name    = Asset_Name_Normalized.replace(' ', '_'),
                		 Description   = MetadataLanguage.title_brief,
                		 Creation_Date = str(Package.date_published),
                		 Provider_ID   = Provider_ID,
                		 Asset_ID      = Asset_ID,
                		 App_Data_App  = Package.customer.product_type)


    #
    # Agrega el titulo
    #
    

    MetadataXml.AddTitle()
    if Package.customer.id_len_reduced == 'Y':
	MetadataXml.Title.AMS.Asset_ID = MakeAssetId('title', VideoRendition.id, Package.id, True,  Package.customer.id_special_prefix)
    else:	
	MetadataXml.Title.AMS.Asset_ID = MakeAssetId('title', VideoRendition.id, Package.id, False, Package.customer.id_special_prefix)

    
    MetadataXml.Title.Closed_Captioning = 'N'
    MetadataXml.Title.Year		= Package.item.year

    Actors	= Package.item.actors_display.split(',')

    if Package.customer.actor_display == 'B':
	MetadataXml.Title.Actors_Display	= Package.item.actors_display
	
	for actor in Actors:
	    while actor.startswith(' '):
		actor = actor[1:]
	

	    actor_name = actor.split(' ')
	    if len(actor_name) >= 2:
		(name, surname) = actor_name[0], actor_name[1]
	    else:
		continue
		
	    MetadataXml.Title.AddCustomMetadata('Actors', name + ',' + surname)
	    
    elif Package.customer.actor_display == 'Y':
	for actor in Actors:
	    while actor.startswith(' '):
		actor = actor[1:]
	
	    	
	    actor_name = actor.split(' ')
	    if len(actor_name) >= 2:
		(name, surname) = actor_name[0], actor_name[1]	
	    else:
		continue		    
	    MetadataXml.Title.AddCustomMetadata('Actors', name + ',' + surname)
    elif Package.customer.actor_display == 'N':
	MetadataXml.Title.Actors_Display	= Package.item.actors_display	    

    MetadataXml.Title.Director		= Package.item.director
        
    
    MetadataXml.Title.Box_Office	= '0'
    if Package.customer.billing_id	!= '':
	MetadataXml.Title.Billing_ID	= Package.customer.billing_id

    MetadataXml.Title.Episode_ID	= Package.item.episode_id

    if Package.customer.use_three_chars_country == 'Y':
	MetadataXml.Title.Country_of_Origin = Package.item.country_of_origin.code_three_chars
    else:
	MetadataXml.Title.Country_of_Origin = Package.item.country_of_origin.code

    MetadataXml.Title.Studio		= Package.item.studio_name #.split(' '))[0]
    MetadataXml.Title.Studio_Name	= Package.item.studio_name
    MetadataXml.Title.Show_Type		= Package.item.show_type
    

    if Package.customer.runtype_display == 'S':
	re_result				= re.match("([0-9][0-9]):([0-9][0-9]):([0-9][0-9])", Package.item.run_time)
	if re_result:
	    MetadataXml.Title.Run_Time		= str((int(re_result.group(1)) * 60 * 60) + (int(re_result.group(2)) * 60) + int(re_result.group(3)))
    else:
	MetadataXml.Title.Run_Time		= Package.item.run_time


    MetadataXml.Title.Display_Run_Time	= Package.item.display_run_time


    #
    # Precio segun formato y duracion
    # 
    if Package.item.material_type == 'SF':
	if VideoRendition.video_profile.format == 'SD':
	    MetadataXml.Title.Suggested_Price = Package.customer.suggested_price_shortform_sd
	elif VideoRendition.video_profile.format == 'HD':
	    MetadataXml.Title.Suggested_Price = Package.customer.suggested_price_shortform_hd
    
    elif Package.item.material_type == 'LF':
	if VideoRendition.video_profile.format == 'SD':
	    MetadataXml.Title.Suggested_Price = Package.customer.suggested_price_longform_sd
	elif VideoRendition.video_profile.format == 'HD':
	    MetadataXml.Title.Suggested_Price = Package.customer.suggested_price_longform_hd
	
    #
    # Nunca deberia llegar a este else
    #
    else:
	MetadataXml.Title.Suggested_Price	  = '0.00'

    if Package.customer.provider_qa_contact != '':
	MetadataXml.Title.Provider_QA_Contact = Package.customer.provider_qa_contact
    else:
	MetadataXml.Title.Provider_QA_Contact = 'www.claxson.com'



    #
    # Metadata especifica del lenguage
    # 

    if Package.customer.titles_in_capital_letter == 'Y':
	MetadataXml.Title.Title_Brief		= MetadataLanguage.title_brief[:19].upper()
        MetadataXml.Title.Title_Sort_Name	= MetadataLanguage.title_sort_name.upper()
        MetadataXml.Title.Title			= MetadataLanguage.title.upper()
    else:
	MetadataXml.Title.Title_Brief	= MetadataLanguage.title_brief[:19]
        MetadataXml.Title.Title_Sort_Name	= MetadataLanguage.title_sort_name
        MetadataXml.Title.Title		= MetadataLanguage.title
        
    MetadataXml.Title.Contract_Name	= MetadataLanguage.title
    MetadataXml.Title.Episode_Name	= MetadataLanguage.episode_name

    if Package.customer.brand_in_synopsis == 'Y':
	PreSynopsis = Package.item.brand.upper() + ' - '
    else:
	PreSynopsis = ''

    if Package.customer.summary_long == 'Y':
	MetadataXml.Title.Summary_Long	= PreSynopsis + MetadataLanguage.summary_long

    MetadataXml.Title.Summary_Short	= PreSynopsis + MetadataLanguage.summary_short
    MetadataXml.Title.Summary_Medium	= PreSynopsis + MetadataLanguage.summary_medium
    
    #
    # Metadata Variable por Cliente
    #
    MetadataXml.Title.Preview_Period		= Package.customer.preview_period
    MetadataXml.Title.Rating       		= Package.customer.rating_display.name
    MetadataXml.Title.Maximum_Viewing_Length 	= Package.customer.maximum_viewing_length
    #
    # Licencia de Visualizacion
    # 
    try:
	License_Months = int(Package.customer.license_window)
    except:
	License_Months = 3

    year, month = GetStartDate(Package.group.name)
    if year is None or month is None:
	MetadataXml.Title.Licensing_Window_Start   = str(Package.date_published + timedelta(days=15))
	MetadataXml.Title.Licensing_Window_End     = str(Package.date_published + timedelta(days=15) + timedelta(days=License_Months))
    else:
    	MetadataXml.Title.Licensing_Window_Start	= year + '-' + month + '-01'
    	end_year, end_month = DateCalc(int(year), int(month), License_Months)
    	if end_year is not None and end_month is not None:
    	    MetadataXml.Title.Licensing_Window_End	= str(end_year) + '-' + (str(end_month) if len(str(end_month)) == 2 else '0'+str(end_month)) +'-01'
    
    if Package.customer.license_date_format == 'DT':
	MetadataXml.Title.Licensing_Window_Start = MetadataXml.Title.Licensing_Window_Start + 'T00:00:00'
	MetadataXml.Title.Licensing_Window_End   = MetadataXml.Title.Licensing_Window_End   + 'T23:59:59'


    #
    # Busca la categoria de acuerdo con el cliente
    #
    try:
        CategoryRelation = models.CategoryRelation.objects.get(category=Package.item.category,customer=Package.customer)
        CustomCategory = CategoryRelation.custom_category
    except:
        CustomCategory = Package.item.category



    if Package.customer.category_path_style == 'APC':
	CategoryPath = 'Adultos' + '/' + MetadataXml.Title.Studio + VideoRendition.video_profile.format + '/' + CustomCategory.name
    elif Package.customer.category_path_style == 'DLA':
	CategoryPath = 'Adults' + MetadataXml.Title.Studio + VideoRendition.video_profile.format + '/' + CustomCategory.name
    elif Package.customer.category_path_style == 'AM':
	CategoryPath = 'Adultos' + '/' + MetadataXml.Title.Studio + VideoRendition.video_profile.format
    elif Package.customer.category_path_style == 'PEP':
	CategoryPath = ''
    elif Package.customer.category_path_style == 'CA':
	CategoryPath = 'Adultos' + '/' + CustomCategory.name		
    elif Package.customer.category_path_style == 'ZA':
	CategoryPath = 'Zona Adultos' + '/' + VideoRendition.video_profile.format + '/' + CustomCategory.name
    elif Package.customer.category_path_style == 'SHO':
	RootPath = 'SHOWRUNNER/ADULTO +18/'
	if VideoRendition.video_profile.format == 'SD':
	    RootPath = RootPath + 'CATEGORIAS/' + CustomCategory.name.upper()
	else:
	    if VideoRendition.item.brand == 'Hot Shots':
		RootPath = RootPath + 'HD Y 3D/RAPIDITOS HD $5.50'
	    else:
		RootPath = RootPath + 'HD Y 3D/HD'
	    
	CategoryPath = RootPath

    if Package.customer.category_with_spaces == 'N':
	MetadataXml.Title.Category	= CategoryPath.replace(' ', '')
    else:
	MetadataXml.Title.Category	= CategoryPath

    if Package.customer.use_genres_category == 'Y':
        MetadataXml.Title.Genre 	= CustomCategory.name
    else:
	MetadataXml.Title.Genre		= Package.customer.custom_genres


    MetadataXml.AddMovie()
    if Package.customer.id_len_reduced == 'Y':
	MetadataXml.Movie.AMS.Asset_ID = MakeAssetId('movie', VideoRendition.id, Package.id, True, Package.customer.id_special_prefix )
    else:
	MetadataXml.Movie.AMS.Asset_ID = MakeAssetId('movie', VideoRendition.id, Package.id, False,Package.customer.id_special_prefix )


    if Package.customer.use_hdcontent_var == 'Y':
	if VideoRendition.video_profile.format == 'HD':
	    MetadataXml.Movie.AddCustomMetadata('HDContent', 'Y')
	else:
	    MetadataXml.Movie.AddCustomMetadata('HDContent', 'N')


    MetadataXml.Movie.Content_FileSize 	= str(VideoRendition.file_size)
    MetadataXml.Movie.Content_CheckSum 	= VideoRendition.checksum
    MetadataXml.Movie.Audio_Type	= VideoRendition.video_profile.audio_type
    if Package.customer.extended_video_information == 'Y':
        MetadataXml.Movie.Resolution	= VideoRendition.video_profile.resolution
        MetadataXml.Movie.Frame_Rate	= VideoRendition.video_profile.frame_rate
        MetadataXml.Movie.Codec		= VideoRendition.video_profile.codec
	MetadataXml.Movie.Bit_Rate	= VideoRendition.video_profile.bit_rate


    MetadataXml.Movie.Screen_Format	= VideoRendition.screen_format
    MetadataXml.Movie.Languages		= Package.item.content_language.code


    if VideoRendition.video_profile.format == 'HD':
	suffix = '_HD'
    else:
	suffix = '_SD'

    #
    # Nombre del file se Video
    #
    if Package.customer.limit_content_value == 'N':
	if VideoRendition.video_profile.file_extension.startswith('.'):
    	    MetadataXml.Movie.Content_Value	= MetadataXml.AMS.Asset_Name + suffix + VideoRendition.video_profile.file_extension
	else:
	    MetadataXml.Movie.Content_Value	= MetadataXml.AMS.Asset_Name + suffix + '.' + VideoRendition.video_profile.file_extension
    else:
	if VideoRendition.video_profile.file_extension.startswith('.'):
    	    MetadataXml.Movie.Content_Value	= MetadataXml.AMS.Asset_Name[:12] + suffix + VideoRendition.video_profile.file_extension
	else:
	    MetadataXml.Movie.Content_Value	= MetadataXml.AMS.Asset_Name[:12] + suffix + '.' + VideoRendition.video_profile.file_extension


    if Package.customer.use_preview == 'Y':
	#
	# Busca el preview que le corresponde al cliente
	#    
	try:
	    Preview = models.PreviewRenditions.objects.get(video_profile=VideoRendition.video_profile)
	except:
	    Preview = None
	
	if Preview is not None:
	    MetadataXml.AddPreview()
	    if Package.customer.id_len_reduced == 'Y':
		MetadataXml.Preview.AMS.Asset_ID = MakeAssetId('preview', VideoRendition.id, Package.id, True, Package.customer.id_special_prefix )
	    else:
		MetadataXml.Preview.AMS.Asset_ID = MakeAssetId('preview', VideoRendition.id, Package.id, False,Package.customer.id_special_prefix )
	    MetadataXml.Preview.Content_Value 	     = Preview.file_name
	    MetadataXml.Preview.Content_FileSize     = str(Preview.file_size)
	    MetadataXml.Preview.Content_CheckSum     = Preview.checksum
	    MetadataXml.Preview.Audio_Type	     = Preview.video_profile.audio_type
	    MetadataXml.Preview.Run_Time	     = Preview.run_time
	    MetadataXml.Preview.Rating		     = Package.customer.rating_display.name
    #
    # Defaults values
    #
    MetadataXml.Movie.Viewing_Can_Be_Resumed    = Package.customer.viewing_can_be_resumed
    MetadataXml.Movie.Copy_Protection		= 'N'
    MetadataXml.Movie.Watermarking		= 'N'

    if ImageRendition != []:

	if Package.customer.image_type == 'poster':
	    MetadataXml.AddPoster()
	else:
	    MetadataXml.AddBoxCover()

	if Package.customer.id_len_reduced == 'Y':
	    MetadataXml.StillImage.AMS.Asset_ID	  = MakeAssetId('image', VideoRendition.id, Package.id, True, Package.customer.id_special_prefix)
	else:
	    MetadataXml.StillImage.AMS.Asset_ID	  = MakeAssetId('image', VideoRendition.id, Package.id, False, Package.customer.id_special_prefix)

	MetadataXml.StillImage.Content_CheckSum   = ImageRendition.checksum
        MetadataXml.StillImage.Content_FileSize   = str(ImageRendition.file_size)


	#
	# Nombre del file de imagen
	# 
	
	if Package.customer.limit_content_value == 'N':
	    if ImageRendition.image_profile.file_extension.startswith('.'):
		MetadataXml.StillImage.Content_Value  = MetadataXml.AMS.Asset_Name + suffix + ImageRendition.image_profile.file_extension
	    else:
    		MetadataXml.StillImage.Content_Value  = MetadataXml.AMS.Asset_Name + suffix + '.' + ImageRendition.image_profile.file_extension
	else:
	    if ImageRendition.image_profile.file_extension.startswith('.'):
		MetadataXml.StillImage.Content_Value  = MetadataXml.AMS.Asset_Name[:12] + suffix + ImageRendition.image_profile.file_extension
	    else:
    		MetadataXml.StillImage.Content_Value  = MetadataXml.AMS.Asset_Name[:12] + suffix + '.' + ImageRendition.image_profile.file_extension

	if Package.customer.image_aspect_ratio == 'Y':
    	    MetadataXml.StillImage.Image_Aspect_Ratio = ImageRendition.image_profile.image_aspect_ratio



    show_type = Package.item.show_type

    # 
    # Campos inventados por el cliente sin dependencia de marca o formato
    # 
    CustomMetadataList = models.CustomMetadata.objects.filter(customer=Package.customer, brand_condition='', format_condition='', show_type=show_type)
    for CustomMetadata in CustomMetadataList:
	if CustomMetadata.apply_to == 'T':
    	    MetadataXml.Title.AddCustomMetadata(CustomMetadata.name, CustomMetadata.value)
	elif CustomMetadata.apply_to == 'V':
	    MetadataXml.Movie.AddCustomMetadata(CustomMetadata.name, CustomMetadata.value)
	elif CustmoMetadata.apply_to == 'I':
	    MetadataXml.StillImage.AddCusmomMetadata(CuatomMetadata.name,CustomMetadata.value)


     
    CustomMetadataList = models.CustomMetadata.objects.filter(customer=Package.customer, brand_condition=Package.item.brand, format_condition=VideoRendition.video_profile.format, show_type=show_type)
    for CustomMetadata in CustomMetadataList:
	if CustomMetadata.apply_to == 'T':
    	    MetadataXml.Title.AddCustomMetadata(CustomMetadata.name, CustomMetadata.value)
	elif CustmoMetadata.apply_to == 'V':
	    MetadataXml.Movie.AddCustomMetadata(CustomMetadata.name, CustomMetadata.value)
	elif CustmoMetadata.apply_to == 'I':
	    MetadataXml.StillImage.AddCusmomMetadata(CuatomMetadata.name,CustomMetadata.value)

    CustomMetadataList = models.CustomMetadata.objects.filter(customer=Package.customer, brand_condition='', format_condition=VideoRendition.video_profile.format, show_type=show_type)
    for CustomMetadata in CustomMetadataList:
	if CustomMetadata.apply_to == 'T':
    	    MetadataXml.Title.AddCustomMetadata(CustomMetadata.name, CustomMetadata.value)
	elif CustomMetadata.apply_to == 'V':
	    MetadataXml.Movie.AddCustomMetadata(CustomMetadata.name, CustomMetadata.value)
	elif CustomMetadata.apply_to == 'I':
	    MetadataXml.StillImage.AddCusmomMetadata(CuatomMetadata.name,CustomMetadata.value)

    CustomMetadataList = models.CustomMetadata.objects.filter(customer=Package.customer, brand_condition=Package.item.brand, format_condition='', show_type=show_type)
    for CustomMetadata in CustomMetadataList:
	if CustomMetadata.apply_to == 'T':
    	    MetadataXml.Title.AddCustomMetadata(CustomMetadata.name, CustomMetadata.value)
	elif CustomMetadata.apply_to == 'V':
	    MetadataXml.Movie.AddCustomMetadata(CustomMetadata.name, CustomMetadata.value)
	elif CustomMetadata.apply_to == 'I':
	    MetadataXml.StillImage.AddCusmomMetadata(CuatomMetadata.name,CustomMetadata.value)



    return MetadataXml




def main():
    
    global ErrorString
    ErrorString = ''

    logging.basicConfig(format='%(asctime)s - QIPackager.py -[%(levelname)s]: %(message)s', filename='./log/QPackager.log',level=logging.INFO)


    while True:

	#
	# Trae todos los Paquetes que estan en la cola
	#
	for Package in models.GetPackageQueue():

	    logging.info("main(): NEW PACKAGE -------------")
	    logging.info("main(): Make package: %s" % str(Package.id))
	    logging.info("main(): Customer: %s" % Package.customer.name)
	    logging.info("main(): Item: %s" % str(Package.item.id))

	    ExportPath 		= GetExportPathFromPackage(Package)
	    if ExportPath is None:
		Package.error  = ErrorString
		Package.status = 'E'
		Package.save() 
		continue

	    logging.info("main(): Export Path: %s" % ExportPath)

	    VideoRenditionList 	= GetVideoRenditions(Package)
	    if VideoRenditionList is None:
		Package.error  = ErrorString
		Package.status = 'E'
		Package.save()
		continue

	    ImageRenditionList	= GetImageRenditions(Package)
	    if ImageRenditionList is None:
		Package.error  = ErrorString
		Package.status = 'E'
		Package.save()
		continue

	    for VideoRendition in VideoRenditionList:
		#
		# Genera el XML
		#

		#
		# Si el Video es HD, deberia buscar de la ImageRendition List, todas las que son HD y pasar esa lista
		# filtrada o en su defecto, enviar uno solo
		#
		ImageRendition = []
	    
		for IRendition in ImageRenditionList:
		    if IRendition.image_profile.format == VideoRendition.video_profile.format:
			ImageRendition.append(IRendition)
			
			
		if ImageRendition == []:
		    logging.error("Cannot find properly Image Profile for the export")
		    logging.error("Cannot export " + VideoRendition.video_profile.format + " format for this package")
		    Package.status = 'E'
		    Package.error  = "Cannot find properly Image Profile for the export"
		    Package.save()
		    break

		logging.info("main(): Making Package for VideoRendition: %s" % VideoRendition.file_name)
		MetadataXml 	   = MakeAdiXmlCablelabs(Package, VideoRendition, ImageRendition[0])
		MetadataXmlRiGHT   = MakeAdiXmlRiGHTvAsset(Package,VideoRendition,ImageRendition[0])
		MetadataXmlNepe    = MakeAdiXmlNepe(Package,VideoRendition,ImageRendition[0])
		
		if MetadataXml is None or MetadataXmlRiGHT is None:
		    #
		    # ??? Y el error
		    #
		    Package.status = 'E'
		    Package.save()
		    break

		if VideoRendition.video_profile.format == 'HD':
		    suffix = '_HD'
		else:
		    suffix = '_SD' 

		#
		# Arma el nombre del Path de Exportacion
		#
		if Package.item.especial == 'Y':
		    ExportPath = ExportPath + 'Especial/'

		if Package.customer.category_path_style == 'PEP':
		    PackagePath	= ExportPath
		else: 
		    if Package.customer.category_path_style == 'SHO':
			PackagePath = ExportPath + MetadataXml.Title.Category + '/'
		    else:
			PackagePath = ExportPath + MetadataXml.Title.Category + '/' + MetadataXml.AMS.Asset_Name
		#
		# Agrega la barra al final si no existe
		#
		PackagePath		= PackagePath + '/' if not PackagePath.endswith('/') else PackagePath
		
		logging.info("main(): Package Path: %s" % PackagePath)
		
		
		#
		# Intenta crear el Path de exportacion
		#
		if not os.path.exists(PackagePath):
		    try:
			os.makedirs(PackagePath)
		    except OSError as e:
			ErrorString = 'Error Creating Directorys, Catch: ' + e.strerror
			Package.error  = ErrorString
			Package.status = 'E'
			Package.save()
			logging.error = ('main(): %s' % ErrorString)
			break
		
		
		#
		# Arma el nombre del Xml de Metadata
		#
		if Package.customer.metadata_profile.key == 'RiGHTvAsset5.1':
		    PackageXmlFileName = MetadataXml.AMS.Asset_Name + suffix + '.ast.xml'
		    RiGHTvAsset.toAdiFile(MetadataXmlRiGHT, PackagePath + PackageXmlFileName)
		
		elif Package.customer.metadata_profile.key == 'NepeXml':
		    PackageXmlFileName = MetadataXml.AMS.Asset_Name + suffix + '.nepe.xml'
		    NepeXml.toAdiFile(MetadataXmlNepe, PackagePath + PackageXmlFileName)    
		else:
		    if Package.customer.use_xml_adi_filename == 'Y':
			PackageXmlFileName = 'adi.xml'
			if Package.customer.uppercase_adi == 'Y':
			    PackageXmlFileName = PackageXmlFileName.upper()
		    else:
			PackageXmlFileName = MetadataXml.AMS.Asset_Name + suffix + '.xml'
		    
	
		    if Package.customer.doctype == 'Y':
			ADIXml.Package_toADIFile(MetadataXml, PackagePath + PackageXmlFileName, '1.1', "<!DOCTYPE ADI SYSTEM \"ADI.DTD\">")
		    else:
			ADIXml.Package_toADIFile(MetadataXml, PackagePath + PackageXmlFileName, '1.1')
		    
		logging.info("main(): Xml Metadata FileName: %s" % PackageXmlFileName)
	
		    
		    
		video_local_path = models.GetPath('video_local_path') 
		image_local_path = models.GetPath('image_local_path')

	    
		if video_local_path is not None:
		    video_local_path = video_local_path + '/' if not video_local_path.endswith('/') else video_local_path
		else:
		    logging.error("Critical error: video_local_path is None. Check your configuration")
		    return None

		if image_local_path is not None:
		    image_local_path = image_local_path + '/' if not image_local_path.endswith('/') else image_local_path
		else:
		    logging.error("Critical error: image_local_path is None. Check your configuration")
		    return None

		


		#
		# Intenta crear los links
		#
		if MetadataXml.Preview is not None:
		    try:
			if os.path.isfile(PackagePath + MetadataXml.Preview.Content_Value):
			    os.remove(PackagePath + MetadataXml.Preview.Content_Value)
			os.link(video_local_path + MetadataXml.Preview.Content_Value, PackagePath + MetadataXml.Preview.Content_Value)
		    except:
			ErrorString    = 'Error creating Preview Hard Link -> Catch: ' + e.strerror
			Package.error  = ErrorString
		        logging.error('main(): %s' % ErrorString)
		        Package.status = 'E'
		        Package.save()
		        break
		try:
		    if os.path.isfile(PackagePath + MetadataXml.Movie.Content_Value):
			os.remove(PackagePath + MetadataXml.Movie.Content_Value)
		    # Video
		    os.link(video_local_path + VideoRendition.file_name, PackagePath + MetadataXml.Movie.Content_Value)
		    
		except OSError as e:
		    ErrorString    = 'Error creating Video Hard Link -> Catch: ' + e.strerror
		    Package.error  = ErrorString
		    logging.error('main(): %s' % ErrorString)
		    Package.status = 'E'
		    Package.save()
		    break

    		try:
    		    if os.path.isfile(PackagePath + MetadataXml.StillImage.Content_Value):
    			os.remove(PackagePath + MetadataXml.StillImage.Content_Value)
		# Imagen
		    os.link(image_local_path + ImageRendition[0].file_name, PackagePath + MetadataXml.StillImage.Content_Value)
			
		except OSError as e:
		    ErrorString    = 'Error creating Image Hard Link -> Catch: ' + e.strerror
		    Package.error  = ErrorString
		    logging.error('main(): %s' % ErrorString)
		    Package.status = 'E'
		    Package.save()
		    break;

		#
		# Si tiene dos profiles de imagen, exporta el otro aunque no este linkeado al XML
		#
		if len(ImageRendition[1:]) == 1:
		    if os.path.isfile(PackagePath + ImageRendition[1].image_profile.type + "_" + MetadataXml.StillImage.Content_Value):
			os.remove(PackagePath + ImageRendition[1].image_profile.type + "_" + MetadataXml.StillImage.Content_Value)
		    os.link(image_local_path + ImageRendition[1].file_name, PackagePath + ImageRendition[1].image_profile.type + "_" + MetadataXml.StillImage.Content_Value)
		
		
		if Package.customer.use_dtd_file == 'Y':
		    write_dtd_file(PackagePath)
		    
		logging.info("main(): END PACKAGE -------------")
		Package.error  = ''
		Package.status = 'P'
		Package.save()


	logging.info("main(): Nothing to do... Sleep")

	if Settings.GLOBAL_SLEEP_TIME:
	    time.sleep(Settings.SLEEP_TIME)
	else:
	    time.sleep(Settings.QPACKAGER_SLEEP)
	



class main_daemon(Daemon):
    def run(self):
        try:
    	    main()
	except KeyboardInterrupt:
	    sys.exit()	    

if __name__ == "__main__":
	daemon = main_daemon('./pid/QPackager.pid', stdout='./log/QPackager.err', stderr='./log/QPackager.err')
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



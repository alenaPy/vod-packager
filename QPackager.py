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
from datetime import datetime, timedelta

import xml.etree.ElementTree as ET

import os
import logging

ErrorString = ''


def MakeAssetId(asset_type='package', asset_id = 0):

    first = '4'

    if asset_type == 'package':
	first = '0'
    elif asset_type == 'title':
	first = '1'
    elif asset_type == 'movie':
	first = '2'
    elif asset_type == 'image':
	first = '3'

    str_id = str(asset_id)
    zero = ''
    i = len(str_id)
    while i < 15:
        zero = zero + '0'
        i = i + 1

    return 'PBLA' + first + zero + str_id


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
	    ErrorString = '01: Number of VideoProfile are wrong: ' + VPListLen
	    logging.error("GetVideoRenditions():" + ErrorString)
	    return None

	else:
	    #
	    # Que formatos usa el cliente
	    #
	    if Customer.export_format == 'BOTH' or Customer.export_format == 'HD':
	        #
	        # Ambos formatos
	        #
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
			#
		        # Exporta solamente SD porque no tiene definido uno HD
		        #
			ExportSD = True
			ProfileSD = VideoProfileList[0]

		    else:
			#
		        # Exporta solamente HD porque no tiene definido uno SD
			#
			ProfileHD = VideoProfileList[0]
			ExportHD = True


	    elif Customer.export_format == 'OSD':
	    
		if VPListLen == 1:
		    if VideoProfileList[0].format == 'SD':
			#
			# Exporta SD
			#
			ExportSD = True
			ProfileSD = VideoProfileList[0]
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
		    else:
			#
			# Error logico, solamente el cliente exporta hd pero no tiene ningun
			# Video profile definido HD o tiene los dos profiles definidos como HD
			#
			ErrorString = '06: The Customer have preferences of HD but does not have a VideoProfile with HD Format or have 2 HD format defined'
			logging.error("GetVideoRenditions(): " + ErrorString)
			return None
		    


	if Item.format == 'HD':
	    #
	    # El item esta en formato HD
	    #
	    if ExportHD:
		try:
		    VRendition = models.VideoRendition.objects.get(item=Item,video_profile=ProfileHD, status='F')
		    VRenditionList.append(VRendition)
		    
		    #
		    # Si el cliente prefiere HD no le exporta la version en SD
		    #
		    if Customer.export_format == 'HD':
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
		    
		except:
		    #
		    # No existe el video rendition para ese video
		    #
		    ErrorString = '08: Not exist VideoRendition for this VideoProfile in the Item: [ITEM: ' + Item.name + '], [VP: ' + ProfileSD.name + ']'
		    logging.error("GetVideoRenditions(): " + ErrorString)
		    return None

	elif Item.format == 'SD':
	    #
	    # El item esta en formato SD
	    #
	    if ExportSD:
	    	try:
		    VRendition = models.VideoRendition.objects.get(item=Item,video_profile=ProfileSD, status='F')
		    VRenditionList.append(VRendition)


		
		except:
		    #
		    # No existe el video rendition para ese video
		    #
		    ErrorString = '09: Not exist VideoRendition for this VideoProfile in the Item: [ITEM: ' + Item.name + '], [VP: ' + ProfileSD.name + ']'
		    logging.error("GetVideoRenditions(): " + ErrorString)
		    return None

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
	    group_path = group_path + '/'

	    if not export_path.endswith('/'):
		export_path = export_path + '/'

	    if not customer_path.endswith('/'):
		customer_path = customer_path + '/'

	    basepath = export_path + customer_path
	    if os.path.exists(basepath):
	    
		if not os.path.exists(basepath+group_path):
		    try:
			os.mkdir(basepath+group_path)
		    except:
			#
			# No puede crear el directorio
			#
			ErrorString = '11: Can not create dir -> ' + basepath + group_path
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



def MakeAdiXmlCablelabs(Package=None, VideoRendition=None, ImageRendition=""):

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

    print dir(Package)

    MetadataXml = ADIXml.Package(Provider      = 'PBTVLA',
                		 Product       = 'First-Run',
                		 Asset_Name    = MetadataLanguage.title_brief.replace(' ', '_'),
                		 Description   = MetadataLanguage.title_brief,
                		 Creation_Date = str(Package.date_published),
                		 Provider_ID   = 'playboytvla.com',
                		 Asset_ID      = MakeAssetId('package', Package.id),
                		 App_Data_App  = Package.customer.product_type)


    #
    # Agrega el titulo
    #
    print dir(MetadataXml)

    MetadataXml.AddTitle()
    MetadataXml.Title.AMS.Asset_ID = MakeAssetId('title', Package.item.id)

    
    MetadataXml.Title.Closed_Captioning = 'N'
    MetadataXml.Title.Year		= Package.item.year
    MetadataXml.Title.Actors		= Package.item.actors
    MetadataXml.Title.Actors_Display	= Package.item.actors
    MetadataXml.Title.Director		= Package.item.director
    MetadataXml.Title.Director_Display	= Package.item.director
    MetadataXml.Title.Box_Office	= '0'
    MetadataXml.Title.Billing_ID	= '00001'
    MetadataXml.Title.Episode_ID	= Package.item.episode_id
    MetadataXml.Title.Country_of_Origin = Package.item.country_of_origin.code
    MetadataXml.Title.Studio		= (Package.item.studio_name.split(' '))[0]
    MetadataXml.Title.Studio_Name	= Package.item.studio_name


    MetadataXml.Title.Provider_QA_Contact = 'www.claxson.com'

    print MetadataLanguage.title_brief

    #
    # Metadata especifica del lenguage
    # 

    MetadataXml.Title.Title_Brief	= MetadataLanguage.title_brief
    MetadataXml.Title.Title_Sort_Name	= MetadataLanguage.title_sort_name
    MetadataXml.Title.Title		= MetadataLanguage.title
    MetadataXml.Title.Episode_Name	= MetadataLanguage.episode_name
    MetadataXml.Title.Summary_Long	= MetadataLanguage.summary_long
    MetadataXml.Title.Summary_Short	= MetadataLanguage.summary_short
    MetadataXml.Title.Summary_Medium	= MetadataLanguage.summary_medium
    
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
	License_Days = int(Package.customer.license_window)
    except:
	License_Days = 90

    
    MetadataXml.Title.Licensing_Window_Start = str(Package.date_published + timedelta(days=15))
    MetadataXml.Title.Licensing_Window_End   = str(Package.date_published + timedelta(days=15) + timedelta(days=License_Days))

    
    if Package.customer.license_date_format == 'DT':
	MetadataXml.Title.Licensing_Window_Start = MetadataXml.Title.Licensing_Window_Start + 'T23:59:59'
	MetadataXml.Title.Licensing_Window_End   = MetadataXml.Title.Licensing_Window_End   + 'T23:59:59'



    try:
        CategoryRelation = models.CategoryRelation.objects.get(category=Package.item.category,customer=Package.customer)
        CustomCategory = CategoryRelation.custom_category
    except:
        CustomCategory = Package.item.category


    CategoryPath = 'Adults' + MetadataXml.Title.Studio + VideoRendition.video_profile.format + '/' + CustomCategory.name + '/'

    MetadataXml.Title.Category	= CategoryPath.replace(' ', '')
    MetadataXml.Title.Genre 	= CustomCategory.name


    MetadataXml.AddMovie()
    MetadataXml.Movie.AMS.Asset_ID = MakeAssetId('movie', VideoRendition.id)

    MetadataXml.Movie.Content_FileSize 	= str(VideoRendition.file_size)
    MetadataXml.Movie.Content_CheckSum 	= VideoRendition.checksum
    MetadataXml.Movie.Audio_Type	= VideoRendition.video_profile.audio_type
    MetadataXml.Movie.Resolution	= VideoRendition.video_profile.resolution
    MetadataXml.Movie.Frame_Rate	= VideoRendition.video_profile.frame_rate
    MetadataXml.Movie.Codec		= VideoRendition.video_profile.codec
    MetadataXml.Movie.Bit_Rate		= VideoRendition.video_profile.bit_rate
    MetadataXml.Movie.Screen_Format	= VideoRendition.screen_format
    MetadataXml.Movie.Languages		= Package.item.content_language.code
    MetadataXml.Movie.Content_Value	= VideoRendition.file_name

    #
    # Defaults values
    #
    MetadataXml.Movie.Viewing_Can_Be_Resumed 	= 'N'
    MetadataXml.Movie.Copy_Protection		= 'N'
    MetadataXml.Movie.Watermarking		= 'N'


    return MetadataXml




def main():
    
    logging.basicConfig(format='%(asctime)s - QIPackager.py -[%(levelname)s]: %(message)s', filename='./log/QPackager.log',level=logging.DEBUG)


    x = True
    while x:
	

	for Package in models.GetPackageQueue():

	    ExportPath 		= GetExportPathFromPackage(Package)
	    
	    VideoRenditionList 	= GetVideoRenditions(Package)

	    for VideoRendition in VideoRenditionList:

		MetadataXml 	= MakeAdiXmlCablelabs(Package, VideoRendition)

		PackagePath 	= ExportPath + MetadataXml.Title.Category + MetadataXml.AMS.Asset_Name

		if not os.path.exists(PackagePath):
		    try:
			os.makedirs(PackagePath)
		    except:
			#
			print "El error"
			# Error
			#
			continue
    
		if not PackagePath.endswith('/'):
		    PackagePath = PackagePath + '/'

		print PackagePath
    
		#
		# Exporta el XML en la carpeta
		#
		ADIXml.Package_toADIFile(MetadataXml, PackagePath + MetadataXml.AMS.Asset_Name + '.xml')
		print "Estoy aca"

		video_local_path = models.GetPath('video_local_path')

		print video_local_path + VideoRendition.file_name

		os.link(video_local_path + '/' + VideoRendition.file_name, PackagePath + VideoRendition.file_name )


	x = False

#print len(MakeAssetId('package',12))

#x = models.GetPackageQueue()
#j = x[0]
#MakeAdiXmlCablelabs(x[0], models.VideoRendition.objects.get(id=1))

main()

#j.status = 'P'
#j.error  = 'Trolo'
#j.save()

#GetExportPathFromPackage(j)
#j.error = ErrorString
#j.status = 'P'
#j.save()

#print dir(x[0])
#print type((x[0]).save())
#print x[0].status
#print ErrorString
#print GetVideoRenditions(j)
#j.error = ErrorString
#j.save()
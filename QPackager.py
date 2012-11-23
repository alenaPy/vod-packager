#
# Stand alone script
#
from django.core.management import setup_environ
from Packager import settings
setup_environ(settings)

#
# Modelo de la aplicacion
#
from Packager_app import models

import os
import logging

def GetPackageQueue():
    return models.Package.objects.filter(status='Q')

ErrorString = ''

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
			return None
		    


	if Item.format == 'HD':
	    #
	    # El item esta en formato HD
	    #
	    if ExportHD:
		try:
		    VRendition = models.VideoRendition.objects.get(item=Item,video_profile=ProfileHD)
		    if VRendition.status == 'F':
			VRenditionList.append(VRendition)
		    
		    #
		    # Si el cliente prefiere HD no le exporta la version en SD
		    #
		    if Customer.export_format == 'HD':
			ExportSD = False			    
    
		    else:
			#
			# No esta finalizado el video Rendition
			#
			pass
		except:
		    #
		    # No existe un video rendition para ese video
		    #
		    ErrorString = '07: Not exist VideoRendition for this VideoProfile in the Item: [ITEM: ' + Item.name + '], [VP: ' + ProfileHD.name + ']'
		    return None

	    if ExportSD:
		try:
		    VRendition = models.VideoRendition.objects.get(item=Item,video_profile=ProfileSD)
		    if VRendition.status == 'F':
			VRenditionList.append(VRendition)
		    else:
			#
			# No finalizo el video Rendition
			#
			pass
		except:
		    #
		    # No existe el video rendition para ese video
		    #
		    ErrorString = '08: Not exist VideoRendition for this VideoProfile in the Item: [ITEM: ' + Item.name + '], [VP: ' + ProfileSD.name + ']'
		    return None

	elif Item.format == 'SD':
	    #
	    # El item esta en formato SD
	    #
	    if ExportSD:
	    	try:
		    VRendition = models.VideoRendition.objects.get(item=Item,video_profile=ProfileSD)
		    if VRendition.status == 'F':
			VRenditionList.append(VRendition)
		    else:
			#
			# No esta finalizado el Video Rendition
			#
			pass
		except:
		    #
		    # No existe el video rendition para ese video
		    #
		    ErrorString = '09: Not exist VideoRendition for this VideoProfile in the Item: [ITEM: ' + Item.name + '], [VP: ' + ProfileSD.name + ']'
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
			return None
		return_path = basepath + group_path
	    
	    else:
		#
		# No existe en el filesystem el export_path + el customer_path
		#
		ErrorString = '12: Customer export path not exist -> ' + basepath
		return None

	else:
	    #
	    # No tiene valor asignado el export_path
	    #
	    ErrorString = '13: In value package_export_path'
	    return None
    else:
	#
	# Argumento Package falta
	#
	ErrorString = '14: Argument Package is None'
	return None
    #
    # Termina correctamente
    # 
    ErrorString = 'OK'
    return return_path


logging.basicConfig(format='%(asctime)s - QIPackager.py -[%(levelname)s]: %(message)s', filename='./log/QPackager.log',level=logging.DEBUG)


x = GetPackageQueue()
j = x[0]
j.status = 'P'
j.error  = 'Trolo'
j.save()

GetExportPathFromPackage(j)
j.error = ErrorString
j.status = 'P'
j.save()

#print dir(x[0])
#print type((x[0]).save())
#print x[0].status
#print ErrorString
print GetVideoRenditions(j)
j.error = ErrorString
j.save()
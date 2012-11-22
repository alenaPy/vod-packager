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

def GetPackageQueue():
    return models.Package.objects.filter(status='Q')


errno  = 0
errstr = 'OK'


def GetVideoRenditions(Package=None):
    if Package is not None:
	

	Customer         = Package.customer
	VideoProfileList = Package.customer.video_profile.filter(status='E')
	Item		 = Package.item

	export_sd = False
	export_hd = False

	VideoRendition = []

	VPListLen = len(VideoProfileList)

	if VPListLen == 0 or VPListLen > 2:
	    #
	    # No tiene correctamente definido los profiles
	    #
	    pass
	
	else:
	    #
	    # Que formatos usa el cliente
	    #
	    if Customer.format == 'BOTH':
	        #
	        # Ambos formatos
	        #
		if VPListLen == 2:

		    if VideoProfileList[0].format != VideoProfileList[1].format:
			#
		        # Esta correctamente definido
		        #
		        export_sd = True
		        export_hd = True

		    else:
			#
			# Esta mal definido tiene dos profiles pero iguales
		        #
		        pass
		elif VPListLen == 1:
		    #
		    # Tiene un solo profile definido
		    #
		    if VideoProfileList[0] == 'SD':
			#
		        # Exporta solamente SD porque no tiene definido uno HD
		        #
			export_sd = True
		    else:
			#
		        # Exporta solamente HD porque no tiene definido uno SD
			#
			export_hd = True


	    elif Customer.format == 'SD':
	    
		if VPListLen == 1:
		    if VideoProfileList[0].format == 'SD':
			#
			# Exporta SD
			#
			export_sd = True
		    else:
			#
			# Tiene un solo profile definido pero no es SD
		        #
			pass
		else:
		    if (VideoProfileList[0].format == 'SD' or VideoProfileList[1].format == 'SD') and (VideoProfileList[0].format != VideoProfileList[1].format):
			export_sd = True
		    else:
			#
			# Error logico, solamente el cliente exporta SD pero no tiene ningun
			# Video profile definido SD o tiene los dos profiles definidos como SD
			#
			pass

	    elif Customer.format == 'HD':
	    
		if VPListLen == 1:
		    if VideoProfileList[0].format == 'HD'
			# 
			# Solamente HD
			#
			export_hd = True
		    else:
			#
			# Tiene un solo profile definido pero no es HD
			#
			pass
		else:
		    if (VideoProfileList[0].format == 'HD' or VideoProfileList[1].format == 'HD') and (VideoProfileList[0].format != VideoProfileList[1].format):
			export_hd = True
		    else:
			#
			# Error logico, solamente el cliente exporta hd pero no tiene ningun
			# Video profile definido HD o tiene los dos profiles definidos como HD
			#
			pass


	if Item.format == 'HD':
	    #
	    # El item esta en formato HD
	    #
	    if export_hd:
		

	    if export_sd:

	elif Item.format == 'SD':
	    #
	    # El item esta en formato SD
	    #
	    if export_sd:




def GetImageRenditions(Package=None):



def GetExportPathFromPackage(Package=None):
    if Package is not None:
	try:
	    export_path = models.Path.objects.get(key='package_export_path').location
	except:
	    #
	    # No esta el export path definido en la base o tiene un nombre incorrecto
	    #
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
			return None
		return_path = basepath + group_path
	    else:
		#
		# No existe en el filesystem el export_path + el customer_path
		#
		return None

	else:
	    #
	    # No tiene valor asignado el export_path
	    #
	    return None
    else:
	#
	# Argumento Package falta
	#
	return None
    #
    # Termina correctamente
    # 
    return return_path



x = GetPackageQueue()
print GetExportPathFromPackage(x[0])
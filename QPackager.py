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
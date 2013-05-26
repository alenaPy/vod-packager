import os

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funciones - Utileria
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Elimina las extensiones (Considera que puede haber puntos en el medio del archivo)
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

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Genera el rendition File Name
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def RenditionFileName(original_filename = None, sufix = None, ext = None):
    
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

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Genera el Prefix File String ID
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def PrefixStrId(itemid=0):
    StrId = str(itemid)
    Zero = ''
    i = len(StrId)
    while i <= 5:
        Zero = Zero + '0'
        i = i + 1

    return 'PB' + Zero + StrId
    
    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Comprueba la existencia de un archivo
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    
def FileExist(path, file):
    if os.path.isfile(path+file):
	return True

    return False
    
    
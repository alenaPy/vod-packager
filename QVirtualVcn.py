import os
import sys
import re
import time
import PyBitMap
import subprocess
from stat import *
from Lib.daemon import Daemon

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Stand alone script
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from django.core.management import setup_environ
from Packager import settings
setup_environ(settings)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Modelo de la aplicacion
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from Packager_app import models

LOGOPATH = '/home/logos_vod/'

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Elimina las extensiones (Considera que puede haber puntos en el medio del archivo)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def splitExtension(filename=None):
    
    if filename is not None:
	basename_tmp_list = filename.split('.')
	i = 1
	basename = basename_tmp_list[0]
	while i < len(basename_tmp_list) -1:
	    basename = basename + '.' + basename_tmp_list[i]
	    i = i + 1
	return basename
    return None

def isVertical(w,h):
    if int(w) < int(h):
	return True
    else:
	return False

def getSufix(filename):
    refn = '(.+)_(....).jpg'
    result = re.match(refn, filename)
    if result:
	return result.group(2)
	
def derivatebitmap(srcfile,dstfile):
    cmd = 'ffmpeg -y -loglevel error -i %s %s' % (srcfile, dstfile)
    subprocess.check_call(cmd.split(' '))
    return True	
	
def scaleImage(srcfile,scale,dstfile):
    cmd = 'ffmpeg -y -loglevel error -i %s -vf scale=%s %s' % (srcfile,scale,dstfile)	
    subprocess.check_call(cmd.split(' '))	
    return True	

def getImageProfiles(sufix):
    imageRenditionList = []

    if sufix == 'HSES':
	tmpList = models.ImageProfile.objects.filter(language='S',type='S')
	for tmp in tmpList:
	    w,h = tmp.image_aspect_ratio.split('x')
	    if not isVertical(w,h):
		imageRenditionList.append(tmp)    	
	    	
    elif sufix == 'VHES':
	tmpList = models.ImageProfile.objects.filter(language='S',type='H')
	for tmp in tmpList:
	    w,h = tmp.image_aspect_ratio.split('x')
	    if isVertical(w,h):
		imageRenditionList.append(tmp)

    elif sufix == 'VSES':
	tmpList = models.ImageProfile.objects.filter(language='S', type='S')
	for tmp in tmpList:
	    w,h = tmp.image_aspect_ratio.split('x')
	    if isVertical(w,h):
		imageRenditionList.append(tmp)

    elif sufix == 'VSNO':
	tmpList = models.ImageProfile.objects.filter(language='E', type='S')
	for tmp in tmpList:
	    w,h = tmp.image_aspect_ratio.split('x')
	    if isVertical(w,h):
		imageRenditionList.append(tmp)

    elif sufix == 'VHLU':
	tmpList = models.ImageProfile.objects.filter(language='L', type='H')
	for tmp in tmpList:
	    w,h = tmp.image_aspect_ratio.split('x')
	    if isVertical(w,h):
		imageRenditionList.append(tmp)

    elif sufix == 'VHPO':
	tmpList = models.ImageProfile.objects.filter(language='P', type='H')
	for tmp in tmpList:
	    w,h = tmp.image_aspect_ratio.split('x')
	    if isVertical(w,h):
		imageRenditionList.append(tmp)
    
    return imageRenditionList

def makeImageRendition(irm):
    sufix	     = irm.image_profile.sufix.replace('_', '')
    plist	     = getImageProfiles(sufix)
    ir		     = getImageRendition(plist,irm.item)
    
    if irm.status != 'F':
	return
        
    srcpath = models.GetPath('image_local_path')
    
    if not srcpath.endswith('/'):
        srcpath = srcpath + '/'
    
    basename   = splitExtension(irm.file_name)        
    bitmapname = str(splitExtension(irm.file_name) + '.bmp')
    ret = derivatebitmap(srcpath+irm.file_name,srcpath+bitmapname)
    
    for image_rendition in ir:
	dst_file = basename + image_rendition.image_profile.sufix + '.' + image_rendition.image_profile.file_extension

	if image_rendition.image_profile.format == 'SD':
	    ret = scaleImage(srcpath+irm.file_name,image_rendition.image_profile.image_aspect_ratio.replace('x',':').replace(' ',''),srcpath + dst_file)
	    if (ret == True):
		image_rendition.file_name = dst_file
		image_rendition.status = 'F'
		image_rendition.save()

	elif image_rendition.image_profile.format == 'HD':
	    #
	    # Genera la imagen derivada
	    #   
	    if image_rendition.image_profile.language == 'P':
		bmp  = PyBitMap.PyBitMap()
	        logo = PyBitMap.PyBitMap()
	        print srcpath+bitmapname
	        bmp.load (str(srcpath+bitmapname))
	        if sufix.startswith('H'):
		    logo.load(LOGOPATH+'HHDPO.bmp')
		    x = 0
		    y = 0
		else:
		    logo.load(LOGOPATH+'VHDPO.bmp')
		    x = 0
		    y = 0
	    else:
		bmp  = PyBitMap.PyBitMap()
	        logo = PyBitMap.PyBitMap()
	        bmp.load (str(srcpath+bitmapname))
	        if sufix.startswith('H'):
		    logo.load(LOGOPATH+'HHD.bmp')
		    x = 570
		    y = 20
		else:
		    logo.load(LOGOPATH+'VHD.bmp')   
		    x = 600
		    y = 20
	    bmp.overlap(logo, x, y)	
	    bmp.save(str(srcpath+bitmapname))
	    ret = scaleImage(srcpath+bitmapname,image_rendition.image_profile.image_aspect_ratio.replace('x',':').replace(' ',''),srcpath + dst_file)
	    if (ret == True):
		image_rendition.file_name = dst_file
		image_rendition.status = 'F'
		image_rendition.save()

    irm.status ='D'
    irm.save()
    
    

def getImageRendition (ProfileLst, Item):
    tmp = []
    for pl in ProfileLst:
	try:
	    ir = models.ImageRendition.objects.get(item=Item, image_profile=pl)
	    tmp.append(ir)
	except:
	    pass
    return tmp


def Main():


    while True:

	irmlist = models.ImageRenditionMaster.objects.filter(status='F')
    
	for irm in irmlist:
	    makeImageRendition(irm)
    
	time.sleep(300)
    
    


class main_daemon(Daemon):
    def run(self):
        try:
    	    Main()
	except KeyboardInterrupt:
	    sys.exit()	    


if __name__ == "__main__":
    daemon = main_daemon('./pid/QVirtualVcn.pid', stdout='./log/QVirtualVcn.err', stderr='./log/QVirtualVcn.err')
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

	
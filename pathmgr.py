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


def Header():
    print "\n"
    print "#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#"
    print "#				Vod-Packager Path Config				#"
    print "#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#"
    print "\n"


def ConfigPaths(Path, Description = ""):

    try:
	location = models.Path.objects.get(key=Path)
	print "\n"
	print "#+++++++++++++++++++++++++++++++++++++"
	print "#- " +  Path + ": -> " + location.location
	print "#+++++++++++++++++++++++++++++++++++++"
	if not os.path.exists(location.location):
	    print "[WARNING]: This path: " + location.location + " not exist in filesystem, please create!!" 
	else:
	    print "[OK]: Path are set correctly"
    except:
	print "\n"
	print "#+++++++++++++++++++++++++++++++++++++"
	print "#- Path -> %s: is not set" % Path
	print "#+++++++++++++++++++++++++++++++++++++"
	flag = True
	while flag:
	    var = raw_input("Do you want set it?(y/n)[y]:")
	    if var == 'Y' or var == 'y' or var == '':
		location = raw_input("Set Path -> %s: " % Path)
		path = models.Path()
		path.key = Path
		path.location = location
		path.description =  Description
		path.save()
		
		if not os.path.exists(location):
		    print "[WARNING]: This path: %s not exist in filesystem, please create!!" % Path
		
		if Path == "video_local_path":
		    serverip = raw_input("Please enter the ip address to set up -> video_smb_path: ")
		    path = models.Path()
		    path.key = "video_smb_path"
		    path.location = "\\\\" +  serverip + "\\" + "VIDEO_PROC\\"
		    path.description = "Video SMB Access"
		    path.save()
		    print "Please add this lines to /etc/samba/smb.conf"
		    print "[VIDEO_PROC]"
		    print "\tcomment = VIDEO_PROC"
		    print "\tbrowseable = yes"
		    print "\tpath = " + location
		    print "\tguest ok = yes"
		    print "\tread only = no"
		flag = False
	    elif var == 'N' or var == 'n':
		flag = False


Header()
ConfigPaths("video_local_path", "Video Local Path")
ConfigPaths("imagen_local_path", "Imagen Local Path")
ConfigPaths("package_export_path", "Export Package Path")



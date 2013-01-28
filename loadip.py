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


file = open('etc/ImageProfiles', 'r')
for line in file.readlines():
    IProfile = models.ImageProfile()
    print line
    name,type,sufix,ext,format,dim = line.split(',')

    IProfile.name 		= name
    IProfile.sufix 		= sufix
    IProfile.file_extension 	= ext
    IProfile.status		= 'E'
    IProfile.format		= format
    IProfile.image_aspect_ratio	= dim.rstrip('\n')
    IProfile.type 		= type

    IProfile.save()



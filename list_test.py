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


#
# Crear 3 video Profiles
# 

vp =  models.VideoProfile.objects.all()
for v in vp:
    print v.id
    print v.name 
    print v.guid 
    print v.file_extension 
    print v.status
    print v.sufix
    print v.bit_rate
    print v.format
    

ts= models.TranscodingServer.objects.all()
for t in ts:
    print t.host_name
    print t.ip_address
    print t.status


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

vp = models.VideoProfile()
#vr = models.VideoRendition()


vp.name = 'Video Profile 1'
vp.guid = '{C986FE19-E729-4882-8180-8C1E89FC7DD5}'
vp.file_extension = '.m2t'
vp.sufix	  = '_PV01'
vp.status         = 'E'
vp.bit_rate       = '3.18'
vp.format         = 'HD'
print vp.save()

#vr.video_profile = vp
#vr.save()

vp = models.VideoProfile()
vp.name = 'Video Profile 2'
vp.guid = '{C986FE19-E729-4882-8180-8C1E89FC7DD5}'
vp.file_extension = '.m2t'
vp.sufix	  = '_PV02'
vp.status         = 'E'
vp.bit_rate       = '3.18'
vp.format         = 'SD'
print vp.save()
    
    
vp = models.VideoProfile()
vp.name = 'Video Profile 3'
vp.guid = '{C986FE19-E729-4882-8180-8C1E89FC7DD5}'
vp.file_extension = '.m2t'
vp.sufix	  = '_PV03'
vp.status         = 'D'
vp.bit_rate       = '3.18'
vp.format         = 'SD'
print vp.save()

ts = models.TranscodingServer()
ts.hostname = 'rzt'
ts.ip_address = '10.3.3.60'
ts.status     = 'E'
ts.save()




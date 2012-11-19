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


path = models.Path()
path.key = 'video_local_path'
path.location = '/home/VIDEO_PROC'
path.description = 'Bolsa de caca'

path.save()

path = models.Path()
path.key = 'video_smb_path'
path.location = '\\\\10.3.0.166\\VIDEO_PROC'
path.description = 'Bolsa de Caca'

path.save()


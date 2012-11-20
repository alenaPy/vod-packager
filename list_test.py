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


f = 'trolita_PIS01.jpg'

# Agregar una expresion Regular    

suf, ext = f.split('_')[len(f.split('_'))-1].split('.')

suf = '_' + suf
ext = '.' + ext

item = models.Item.objects.all()

irend = models.ImageProfile.objects.filter(sufix=suf, file_extension=ext)
print irend
vrend = models.ImageRendition.objects.get(item=item[0], image_profile=irend)
vrend.file_name = f
vrend.status = 'F'
vrend.save()



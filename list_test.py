#
# Stand alone script
#
from django.core.management import setup_environ
from Packager import settings
setup_environ(settings)
import re

#
# Modelo de la aplicacion
#
from Packager_app import models


f = 'trolita_PIH01.png'

# Agregar una expresion Regular    

suf, ext = f.split('_')[len(f.split('_'))-1].split('.')


x = re.match("(.+)_(PI[S|H][0-9][0-9]).([a-z][a-z][a-z])",f)
if x:
    print x.group(1)
    print x.group(2)
    print x.group(3)
else:
    print "File Invalido"

suf = '_' + suf
ext = '.' + ext

item = models.Item.objects.all()

irend = models.ImageProfile.objects.filter(sufix=suf, file_extension=ext)
print irend
vrend = models.ImageRendition.objects.get(item=item[0], image_profile=irend)
vrend.file_name = f
vrend.status = 'F'
vrend.save()



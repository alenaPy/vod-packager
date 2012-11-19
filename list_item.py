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

it = models.Item.objects.all()

for i in it:
    print i.name

iq = models.ImportQueue.objects.all()

for i in iq:
    print i.file_name
    print i.item.name
    
    
    
                                                                        
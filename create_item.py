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

item = models.Item()
item.name     = "Trolita"
item.format   = "HD"
item.save()


iq = models.ImportQueue()
iq.item = item
iq.file_name = "racing.mov"
iq.queue_status = 'Q'
iq.svc_path	   = "\\\\10.3.0.166\\home\\"
iq.save()




                                                                        
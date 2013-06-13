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


for Item in models.Item.objects.all():
    try:
	InternalBrand = models.InternalBrand.objects.get(name=Item.brand)
    except:
	print "Creando Internal Brand: " + Item.brand
	InternalBrand = models.InternalBrand()
	
	InternalBrand.name = Item.brand
	if Item.brand == 'Venus' or Item.brand == 'Playboy' or Item.brand == 'Penthouse' or Item.brand == 'Hot Shots':
	    InternalBrand.format = 'HD'
	else:
	    InternalBrand.format = 'SD'
	InternalBrand.save()
	
	
    Item.internal_brand = InternalBrand
    Item.save()
    
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Stand alone script
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned 
from django.core.management import setup_environ
from Packager import settings
setup_environ(settings)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Modelo de la aplicacion
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from Packager_app import models

from datetime import datetime, timedelta
from Lib.daemon import Daemon

import string
import os, time, sys, re
import logging
import Settings

def PrePackageToPackages(PrePackage=None):

    if PrePackage is not None:
	#
	# Trae todos los items Done y cuyo grupo sea el grupo de exportacion pedido
        #
        Items = models.Item.objects.filter(status='D', group=PrePackage.item_group)

	try:
	    logging.info("")
	    PackageGroup = models.PackageGroup.objects.get(name=PrePackage.item_group.key)
	    logging.info
	except ObjectDoesNotExist:
	    logging.info("")
	    PackageGroup = models.PackageGroup()
	    PackageGroup.name = PrePackage.item_group.key
	    PackageGroup.description = PrePackage.item_group.name
	    PackageGroup.save()

        print Items

        for item in Items:
    	    #
    	    # Establece en que formato tiene que exportar
    	    #
    	    if item.format == item.internal_brand.format:
    		format = item.format
    	    elif item.internal_brand.format == 'SD' and item.format == 'HD':
    		format = 'SD'
    	    elif item.internal_brand.format == 'HD' and item.format == 'SD':
    		format = 'SD'
	    #
	    # Por Cada item trae todos los clientes que tienen la internal brand de ese item
	    #
	    Customers = models.Customer.objects.filter(internal_brand=item.internal_brand, export_zone=PrePackage.export_zone)
	    for customer in Customers:
		export_format = customer.export_format
		
		    
		if export_format == 'OSD':
		    if format == 'SD' or format == 'HD':
			try:
			    Package = models.Package.objects.get(item=item, customer=customer, group=PackageGroup, format='SD')
			    continue
			except MultipleObjectsReturned:
			    continue
			except ObjectDoesNotExist:
			    Package = models.Package()
			
			Package.customer = customer
			Package.format   = 'SD'
			Package.item     = item
			Package.group    = PackageGroup
			Package.status   = 'Q'
			Package.save()		
		
		elif export_format == 'OHD':
		    if format == 'HD':
		    
			try:
			    Package = models.Package.objects.get(item=item, customer=customer, group=PackageGroup, format='HD')
			    continue
			except MultipleObjectsReturned:
			    continue
			except ObjectDoesNotExist:
			    Package = models.Package()
			
			Package.customer = customer
			Package.format   = 'HD'
			Package.item     = item
			Package.group    = PackageGroup
			Package.status   = 'Q'
			Package.save()
		
		elif export_format == 'BOTH':
	
		
		    try:
		        Package = models.Package.objects.get(item=item, customer=customer, group=PackageGroup, format='SD')
		        continue
		    except MultipleObjectsReturned:
		        continue
		    except ObjectDoesNotExist:
		        Package = models.Package()
		    Package.customer = customer
		    Package.format   = 'SD'
		    Package.item     = item
		    Package.group    = PackageGroup
		    Package.status   = 'Q'
		    Package.save()	
		    
		    if format == 'HD':		
			try:
			    Package = models.Package.objects.get(item=item, customer=customer, group=PackageGroup, format='HD')
			    continue
			except MultipleObjectsReturned:
			    continue
			except ObjectDoesNotExist:
			    Package = models.Package()
			Package.customer = customer
			Package.format   = 'HD'
			Package.item     = item
			Package.group    = PackageGroup
			Package.status   = 'Q'
			Package.save()	

		elif export_format == 'HD':

		    if format == 'HD':
			try:
			    Package = models.Package.objects.get(item=item, customer=customer, group=PackageGroup, format='HD')
			    continue
			except MultipleObjectsReturned:
			    continue
			except ObjectDoesNotExist:
			    Package = models.Package()
			Package.customer = customer
			Package.format   = 'HD'
			Package.item     = item
			Package.group    = PackageGroup
			Package.status   = 'Q'
			Package.save()	
		    
		    elif format == 'SD':		    
			try:
			    Package = models.Package.objects.get(item=item, customer=customer, group=PackageGroup, format='HD')
			    continue
			except MultipleObjectsReturned:
			    continue
			except ObjectDoesNotExist:
			    Package = models.Package()
			
			Package.customer = customer
			Package.format   = 'SD'
			Package.item     = item
			Package.group    = PackageGroup
			Package.status   = 'Q'
			Package.save()	
	    
	    print Customers	
		
	PrePackage.status = 'D'
	PrePackage.save()
		
		
def Main():
    #
    # Trae todos los Pre-Paquetes que pertenecen a la zona
    #
    logging.basicConfig(format='%(asctime)s - QPrePackager.py -[%(levelname)s]: %(message)s', filename='./log/QPrePackager.log',level=logging.INFO)

    while True:
	Zone        = models.ExportZone.objects.get(zone_name=Settings.ZONE)
        PrePackages = models.PrePackage.objects.filter(status='Q', export_zone=Zone)
    
	print PrePackages
	for PPackage in PrePackages:
	    PrePackageToPackages(PPackage)
    
	time.sleep(Settings.QPREPACKAGER_SLEEP)
    
    
class main_daemon(Daemon):
    def run(self):
        try:
    	    Main()
	except KeyboardInterrupt:
	    sys.exit()	    

if __name__ == "__main__":
    daemon = main_daemon('./pid/QPrePackager.pid', stdout='./log/QPrePackager.err', stderr='./log/QPrePackager.err')
    if len(sys.argv) == 2:
    	if 'start'     == sys.argv[1]:
	    daemon.start()
	elif 'stop'    == sys.argv[1]:
	    daemon.stop()
	elif 'restart' == sys.argv[1]:
	    daemon.restart()
	elif 'run'     == sys.argv[1]:
	    daemon.run()
	elif 'status'  == sys.argv[1]:
	    daemon.status()
	else:
	    print "Unknown command"
	    sys.exit(2)
	    sys.exit(0)
    else:
    	print "usage: %s start|stop|restart|run" % sys.argv[0]
	sys.exit(2)
	
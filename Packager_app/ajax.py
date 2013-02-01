from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajaxice.core import dajaxice_functions
import urlparse
import json
import logging
import models
import sys
import re
import traceback

@dajaxice_register
def dajaxice_example(request):
	return simplejson.dumps({'message':'Hello from Python modified!'})
#dajaxice_functions.register(dajaxice_example)

@dajaxice_register
def args_example(request, text):
	return simplejson.dumps({'message':'Your message is %s!' % text})
#dajaxice_functions.register(args_example)

@dajaxice_register
def bulk_export(request, data):
    try:
	ddata = urlparse.parse_qs(data)
	#file = open('/opt/packager/app/vod-packager/log/ajax.py', 'w')
	#file.write(str(ddata.keys()))
	#file.close()
	item_group = ddata['item_group'][0]
	for checkbox in ddata.keys():
	    match 		= re.match("it_(.+)_cr_(.+)", checkbox)
	    if match:
		item_id 	= int(match.group(1))
		customer_id	= int(match.group(2))
		item 		= models.Item.objects.get(id=item_id)
		customer 	= models.Customer.objects.get(id=customer_id)
		package_group 	= models.PackageGroup.objects.get(name=item_group)
		try:
		    models.Package.objects.get(item=item, customer=customer)
		except:
		    package = models.Package()
		    package.customer = customer
		    package.item = item
		    package.status = "Q"
		    package.group = package_group
		    package.error = ""
		    package.save()

	return simplejson.dumps({'message': 'La exportacion masiva se ha procesado con exito.'})
    except Exception, e:
	return simplejson.dumps({'message': 'Hubo inconvenientes creando el grupo de paquetes:  %s' % e})
	
@dajaxice_register
def force_to_be_done(request, item_id):
	try:
	        item = models.Item.objects.get(id=int(item_id))
		item.status = 'D'
		item.save()
		return simplejson.dumps({'message': " *** ATENCION *** \n " + item.name + " fue forzado a status Done \n POSIBLES ERRORES"})
	except:
		return simplejson.dumps({'message': "No se pudo cambiar el status a Done"})
	

@dajaxice_register
def export_item(request, item_id, selected_customers, package_group):

	try:
		item 			= models.Item.objects.get(id=int(item_id))
		package_group 		= models.PackageGroup.objects.get(id=int(package_group))
#		logging.basicConfig(format='%(asctime)s - ajax.py -[%(levelname)s]: %(message)s', filename='../log/Ajax.log',level=logging.INFO)
#		logging.info("Esto es un log!")
		if selected_customers is not None:
			i = 0
			for c in selected_customers:
				customer = models.Customer.objects.get(id=int(c))
				try:
					package = models.Package.objects.get(customer=customer, item=item, group=package_group)
					# Agregar a futuro que no deje exportar algo que este packaged
					msg = 'Se han modificado '
				except:
					package 			= models.Package()
					package.customer 	= customer
					package.item     	= item
					package.group		= package_group
					msg = 'Se han creado '
				package.status = 'Q'
				package.error = ''
				package.save()
				i = i + 1
			return simplejson.dumps({'message': msg + str(i) + ' paquetes.'})		
		else:
			return simplejson.dumps({'message':'Por favor seleccione al menos un cliente.'})
	except ObjectDoesNotExist:
		return simplejson.dumps({'message':'No encontre el item!'})
	#except IntegrityError, e:
	#	return simplejson.dumps({'message':'Error: bla'})
	except:
		return simplejson.dumps({'message':'Error: ' + str(sys.exc_info()[1])})

@dajaxice_register
def package_group_save(request, data):
	try:
		ddata = urlparse.parse_qs(data)
		if ddata['name'] != "":
			package_group 			= models.PackageGroup()
			package_group.name 		= ddata['name'][0]
			package_group.description 	= ddata['description'][0]
			package_group.save()
			json_string = json.dumps(package_group, default=lambda o: o.__dict__)
			return simplejson.dumps(json_string)
		else:
			return simplejson.dumps({'message': 'Hubo inconvenientes creando el grupo de paquetes.'})
	except:
		return simplejson.dumps({'message': 'Hubo inconvenientes creando el grupo de paquetes.'})

from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from dajaxice.core import dajaxice_functions
import urlparse
import json
import logging
import models

@dajaxice_register
def dajaxice_example(request):
	return simplejson.dumps({'message':'Hello from Python modified!'})
#dajaxice_functions.register(dajaxice_example)

@dajaxice_register
def args_example(request, text):
	return simplejson.dumps({'message':'Your message is %s!' % text})
#dajaxice_functions.register(args_example)

@dajaxice_register
def export_item(request, item_id, selected_customers, package_group):

	try:
		item 		= models.Item.objects.get(id=int(item_id))
		package_group 	= models.PackageGroup.objects.get(id=int(package_group))
#		logging.basicConfig(format='%(asctime)s - ajax.py -[%(levelname)s]: %(message)s', filename='../log/Ajax.log',level=logging.INFO)
#		logging.info("Esto es un log!")
		if selected_customers is not None:
			i = 0
			for c in selected_customers:
				customer = models.Customer.objects.get(id=int(c))
				try:
					package = models.Package.objects.get(customer=customer, item=item, package_group=package_group)
				except:
					package 		= models.Package()
					package.customer 	= customer
					package.item     	= item
					package_group		= package_group
				package.status = 'Q'
				package.error = ''
				package.save()
				i = i + 1
			return simplejson.dumps({'message': 'Se han creado ' + str(i) + ' paquetes.'})		
		else:
			return simplejson.dumps({'message':'Por favor seleccione al menos un cliente.'})
	except ObjectDoesNotExist:
		return simplejson.dumps({'message':'No encontre el item!'})
	except:
		return simplejson.dumps({'message':'No se que paso!'})

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

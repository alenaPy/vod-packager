from django.http import HttpResponse
from django.shortcuts import redirect, render, render_to_response, get_object_or_404
from django.template import RequestContext
import models

def index(request):
	items = models.Item.objects.order_by('name')
	return render_to_response('view.html', {'items': items}, context_instance=RequestContext(request))

def items(request):
	return HttpResponse("Items index.")

def customer(request, customer_id):
	try:
		customer = models.Customer.objects.get(id=customer_id)
		resp = customer.name
	except:
		resp = 'No ta!'
	
	return HttpResponse("You're looking at customer %s." % resp)

def item(request, item_id):
	try:
		item = models.Item.objects.get(id=item_id)
		resp = item.name
		return render_to_response('item.html', {'item': item}, context_instance=RequestContext(request)) 
	except:
		resp = 'No ta!'
		return HttpResponse("You're looking at item %s." % resp)

def package(request, package_id):
	try:
		package = models.Package.objects.get(id=package_id)
		resp = package.item
	except:
		resp = 'No ta!'
	
	return HttpResponse("You're looking at package %s." % resp)
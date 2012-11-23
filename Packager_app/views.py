from django.http import HttpResponse
from django.shortcuts import render
import models

def index(request):
	return render(request, 'item.html')

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
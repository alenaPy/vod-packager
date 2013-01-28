from django.http import HttpResponse
from django.shortcuts import redirect, render, render_to_response, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from os import listdir
from os.path import isfile, join

import json
import models
import os

from Packager_app.search import *

@csrf_protect
def login_user(request):

	if request.user.is_authenticated():
		return HttpResponseRedirect("/vod/items")
	else:
		# Do something for anonymous users.
		
		state = "Please log in below..."
		username = password = ''
		if request.GET:
			next = request.GET.get('next', '')
		else:
			next = '/vod/items'
		if request.POST:
			username = request.POST.get('username')
			password = request.POST.get('password')
			next = request.POST.get('next')
			
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					state = "You're successfully logged in!"
					return HttpResponseRedirect(next)
				else:
					state = "Your account is not active, please contact the site admin."
			else:
				state = "Your username and/or password were incorrect."
		
		return render_to_response('registration/login.html', {'state':state, 'username': username, 'next': next}, context_instance=RequestContext(request))

@login_required
@csrf_protect
def index(request):

	return render_to_response('index.html', context_instance=RequestContext(request))

@login_required
@csrf_protect
def items(request):

	items_list = models.Item.objects.all()
	paginator = Paginator(items_list, 10)
	
	page = request.GET.get('page')
	try:
		items = paginator.page(page)
	except PageNotAnInteger:
		items = paginator.page(1)
	except EmptyPage:
		items = paginator.page(paginator.num_pages)
	
	return render_to_response('view_items.html', {'items': items}, context_instance=RequestContext(request))

@login_required
@csrf_protect
def customers(request):

	customer_list = models.Customer.objects.all()
	paginator = Paginator(customer_list, 10)
	
	page = request.GET.get('page')
	try:
		customers = paginator.page(page)
	except PageNotAnInteger:
		customers = paginator.page(1)
	except EmptyPage:
		customers = paginator.page(paginator.num_pages)
	
	return render_to_response('view_customers.html', {'customers': customers}, context_instance=RequestContext(request))

@login_required
@csrf_protect
def packages(request):
	
	packages_list = models.Package.objects.all()
	paginator = Paginator(packages_list, 10)
	
	page = request.GET.get('page')
	try:
		packages = paginator.page(page)
	except PageNotAnInteger:
		packages = paginator.page(1)
	except EmptyPage:
		packages = paginator.page(paginator.num_pages)
	
	return render_to_response('view_packages.html', {'packages': packages}, context_instance=RequestContext(request))

@login_required
@csrf_protect
def package_group(request, package_group_id):

    #try:
	packages_groups = models.PackageGroup.objects.all().order_by('-name')
	package_group = models.PackageGroup.objects.get(id=package_group_id)
	item_group = models.ItemGroup.objects.get(key=package_group.name)
	items = models.Item.objects.filter(group=item_group).order_by('brand')
	customers = models.Customer.objects.all().order_by('name') 
	try:
	    packages = models.Package.objects.filter(group=package_group.id).order_by('item', 'customer')
	except:
	    packages = []
	
	matriz = []
	item_id = 0
	contItems = -1
	for pkg in packages:
		if item_id != pkg.item.id:
			contItems = contItems + 1
			litem = [int(pkg.item.id), str(pkg.item.name), pkg.item.brand]
			matriz.append((litem, []))
		item_id = pkg.item.id
		while item_id == pkg.item.id:
			lpkg = [int(pkg.id), int(pkg.customer.id), str(pkg.status), str(pkg.error)]
			matriz[contItems][1].append(lpkg)
			break

	return render_to_response('view_package_group.html', {'items': items, 'packages_groups': packages_groups, 'package_group': package_group, 'packages': packages, 'customers': customers, 'matriz': matriz}, context_instance=RequestContext(request))
    #except:
#	error_msg = "Ha surgido un error mientras se intentaba desplegar la vista package_group. Por favor contacte al administrador del sistema."
#	return render_to_response('view_custom_error.html', {'error_msg': error_msg}, context_instance=RequestContext(request))

@login_required
@csrf_protect
def delivery(request, item_group_id):

    try:
	item_group = models.ItemGroup.objects.get(id=item_group_id)
	item_groups = models.ItemGroup.objects.all().order_by('-key')
	items = models.Item.objects.filter(group=item_group).order_by('brand')
	customers = models.Customer.objects.all().order_by('name')
	try:
	    package_group = models.PackageGroup.objects.get(name=item_group.key)
	except:
	    package_group = models.PackageGroup()
	    package_group.name = item_group.key
	    package_group.description = item_group.name
	    package_group.save()
	packages = models.Package.objects.filter(group=package_group)
	return render_to_response('view_delivery.html', {'item_groups': item_groups, 'item_group': item_group, 'customers': customers, 'items': items, 'package_group': package_group, 'packages': packages}, context_instance=RequestContext(request))
    except:
	error_msg = "Ha surgido un error mientras se intentaba desplegar la vista delivery. Por favor contacte al administrador del sistema."                                                                               
	return render_to_response('view_custom_error.html', {'error_msg': error_msg}, context_instance=RequestContext(request))

@login_required
@csrf_protect
def bulk_delivery(request):

    try:
	item_group = models.ItemGroup.objects.latest('key')
        item_groups = models.ItemGroup.objects.all().order_by('-key')
        items = models.Item.objects.filter(group=item_group).order_by('brand')
        customers = models.Customer.objects.all().order_by('name')
        try:
    	    package_group = models.PackageGroup.objects.get(name=item_group.key)
        except:
    	    package_group = models.PackageGroup()
    	    package_group.name = item_group.key
    	    package_group.description = item_group.name
    	    package_group.save()
        packages = models.Package.objects.filter(group=package_group)
        return render_to_response('view_bulk_delivery.html', {'item_groups': item_groups, 'customers': customers, 'items': items, 'package_group': package_group, 'packages': packages}, context_instance=RequestContext(request))
    except:
	error_msg = "Ha surgido un error mientras se intentaba desplegar la vista bulk_delivery. Por favor contacte al administrador del sistema."
	return render_to_response('view_custom_error.html', {'error_msg': error_msg}, context_instance=RequestContext(request))

@login_required
@csrf_protect
def dashboard(request):

    try:
	packages_groups_list = models.PackageGroup.objects.all().order_by('-name')
	paginator = Paginator(packages_groups_list, 1)
	page = request.GET.get('page')
	try:
		packages_groups = paginator.page(page)
	except PageNotAnInteger:
		packages_groups = paginator.page(1)
	except EmptyPage:
		packages_groups = paginator.page(paginator.num_pages)
	
	customers = models.Customer.objects.all().order_by('name')
	try:
	    packages = models.Package.objects.filter(group=packages_groups[0].id).order_by('item', 'customer')
	except:
	    packages = []
		    
	matriz = []
	item_id = 0
	contItems = -1
	for pkg in packages:
		if item_id != pkg.item.id:
			contItems = contItems + 1
			litem = [int(pkg.item.id), str(pkg.item.name), pkg.item.brand]
			matriz.append((litem, []))
		item_id = pkg.item.id
		while item_id == pkg.item.id:
			lpkg = [int(pkg.id), int(pkg.customer.id), str(pkg.status), str(pkg.error)]
			matriz[contItems][1].append(lpkg)
			break

	return render_to_response('view_dashboard.html', {'packages_group_list': packages_groups_list, 'packages_groups': packages_groups, 'packages': packages, 'customers': customers, 'matriz': matriz}, context_instance=RequestContext(request))
    except:
	error_msg = "Ha surgido un error mientras se intentaba desplegar la vista dashboard. Por favor contacte al administrador del sistema."
	return render_to_response('view_custom_error.html', {'error_msg': error_msg}, context_instance=RequestContext(request))


@login_required
@csrf_protect
def daemons(request):

	pidpath = '/opt/packager/app/vod-packager/pid'

	DaemonList = [ 'QChecker', 'QImport', 'QPackager', 'VPApiServer' ]
        DaemonStatus = { 'QChecker_status'    : 'N', 
			 'QImport_status'     : 'N',
			 'QPackager_status'   : 'N',
			 'VPApiServer_status' : 'N' }

	for daemon in DaemonList:
		pidfile =pidpath + '/' + daemon + '.pid'

		# Get the pid from the pidfile
		try:
			pf = file(pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None
	
		if pid:
			if os.path.exists('/proc/'+ str(pid)):
				if daemon == 'QChecker':
				        DaemonStatus['QChecker_status']   = 'R'
				elif daemon == 'QImport':
					DaemonStatus['QImport_status']     = 'R'
				elif daemon == 'QPackager': 
					DaemonStatus['QPackager_status']   = 'R'
				elif daemon == 'VPApiServer': 
					DaemonStatus['VPApiServer_status'] = 'R'
	
	return render_to_response('view_daemons.html', DaemonStatus, context_instance=RequestContext(request))		
	    

@login_required
@csrf_protect
def logs(request):

	logs = []
	mypath = '/opt/packager/app/vod-packager/log'
	onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
	
        return render_to_response('view_logs.html', {'onlyfiles': onlyfiles}, context_instance=RequestContext(request))

@login_required
@csrf_protect
def item(request, item_id):
	
#	try:
		item = models.Item.objects.get(id=item_id)
		resp = item.name
		image_renditions = models.ImageRendition.objects.filter(item=item_id)
		video_renditions = models.VideoRendition.objects.filter(item=item_id)
		packages_groups = models.PackageGroup.objects.all()
		customers_for_export = models.GetCustomersForExport(item)
		return render_to_response('item.html', {'item': item, 'video_renditions': video_renditions, 'image_renditions': image_renditions, 'customers_for_export': customers_for_export, 'packages_groups': packages_groups}, context_instance=RequestContext(request)) 
#	except:
#		resp = 'No ta!'
#		return HttpResponse("You're looking at item %s." % resp)

@login_required
@csrf_protect
def customer(request, customer_id):
	
	try:
		customer = models.Customer.objects.get(id=customer_id)
		return render_to_response('customer.html', {'customer': customer}, context_instance=RequestContext(request))
	except:
		resp = 'No ta!'
		return HttpResponse("You're looking at customer %s." % resp)

@login_required
@csrf_protect
def package(request, package_id):
	
	try:
		package = models.Package.objects.get(id=package_id)
		return render_to_response('package.html', {'package': package}, context_instance=RequestContext(request))
	except:
		resp = 'No ta!'
		return HttpResponse("You're looking at package %s." % resp)

@login_required
@csrf_protect
def image_rendition(request, image_rendition_id):

	try:
		image_rendition = models.ImageRendition.objects.get(id=image_rendition_id)
		return render_to_response('image_rendition.html', {'image_rendition': image_rendition}, context_instance=RequestContext(request))
	except:
		resp = 'No ta!'
		return HttpResponse("You're looking at image rendition %s." % resp)

@login_required
@csrf_protect
def image_renditions_upload(request, item_id):

#       try:
                item = models.Item.objects.get(id=item_id)
                image_renditions = models.ImageRendition.objects.filter(item=item_id)
                video_renditions = models.VideoRendition.objects.filter(item=item_id)
                return render_to_response('image_renditions_upload.html', {'item': item}, context_instance=RequestContext(request))
#       except:
#               resp = 'No ta!'
#               return HttpResponse("You're looking at item %s." % resp)

@login_required
@csrf_protect
def new_package_group(request):

	return render_to_response('new_package_group.html', context_instance=RequestContext(request))

@login_required
@csrf_protect
def search(request):

	query_string = ''
	found_entries = None
	if ('q' in request.GET) and request.GET['q'].strip():
		query_string = request.GET['q']
		entry_query = get_query(query_string, ['name', 'year',])
		found_entries = models.Item.objects.filter(entry_query).order_by('id')

	return render_to_response('search_results.html',
						{ 'query_string': query_string, 'found_entries': found_entries },
						context_instance=RequestContext(request))

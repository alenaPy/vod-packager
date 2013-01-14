from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# dajaxice
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.conf import settings
dajaxice_autodiscover()

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Login / logout
from Packager.views import *
from django.conf.urls.defaults import *

urlpatterns = patterns('',
	# Examples:
	#url(r'^$', include('Packager_app.urls')),
	# url(r'^Packager/', include('Packager.foo.urls')),
	
	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	(r'^$', main_page),
	url(r'^vod/', include('Packager_app.urls')),
	# Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
	url(r'^uploadify/', include('uploadify.urls')),
	url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),

	# Login / logout.
	(r'^login/$', 'Packager_app.views.login_user'),
	#(r'^logout/$', "logout.html"),
	(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
)

urlpatterns += staticfiles_urlpatterns()

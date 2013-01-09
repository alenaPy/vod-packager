from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# dajaxice
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.conf import settings
dajaxice_autodiscover()

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', include('Packager_app.urls')),
    # url(r'^Packager/', include('Packager.foo.urls')),
	
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	
    url(r'^vod/', include('Packager_app.urls')),
	
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	
    url(r'^uploadify/', include('uploadify.urls')),
	
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
    #url(r'^dajaxice/', include('dajaxice.urls')),
    #url(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
)

urlpatterns += staticfiles_urlpatterns()

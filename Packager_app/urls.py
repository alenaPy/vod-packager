from django.conf.urls import patterns, url

from Packager_app import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^customer/(?P<customer_id>\d+)/$', views.customer, name='customer'),
    url(r'^item/(?P<item_id>\d+)/$', views.item, name='item'),
    url(r'^package/(?P<package_id>\d+)/$', views.package, name='package'),
)

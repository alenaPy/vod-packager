from django.db import models
from datetime import *
# importar User y DateTime

# Create your models here.

ACTIVE_STATUS = (
	('E', 'Enabled'),
	('D', 'Disabled'),
)

FORMAT = (
	('SD', 'SD'),
	('HD', 'HD'),
	('3D', '3D'),
)	





class Country(models.Model):
	code						= models.CharField(max_length=2)
	country						= models.CharField(max_length=255)

	def __unicode__(self):
	    return self.country


class Language(models.Model):
	code 						= models.CharField(max_length=2)
        name 						= models.CharField(max_length=20)

	def __unicode__(self):
	    return self.name


class Rating(models.Model):
	name						= models.CharField(max_length=6)

	def __unicode__(self):
	    return self.name


class Customer(models.Model):

	PRODUCT_TYPE = (
		('SVOD', 'Subscription Video On Demand'),
		('MOD', 'Movie On Demand'),
	)

	RUNTIME_DISPLAY = (
		('T', 'Time Format: HH:MM:SS'),
		('S', 'Number of seconds'),
	)
	
	EXPORT_CUSTOMER_FORMAT = (
		('OSD', 'Only SD Format'),
		('OHD', 'Only HD Format'),
		('BOTH','Both Format'),
		('HD', 'HD Preferably'),
	)

	LICENSE_DATE_FORMAT = (
		('DT', 'Date + Time'),
		('DO', 'Only Date'),
	)


	name 						= models.CharField(max_length=256)
	vod_active 					= models.BooleanField(default=True)
	image_type 					= models.CharField(max_length=128)
	video_profile 					= models.ManyToManyField('VideoProfile')
	image_profile 					= models.ManyToManyField('ImageProfile')
	metadata_profile 				= models.ForeignKey('MetadataProfile')
	export_language					= models.ForeignKey('Language')
	export_format					= models.CharField(max_length=4, choices=EXPORT_CUSTOMER_FORMAT)
	export_folder					= models.CharField(max_length=256)
	runtype_display					= models.CharField(max_length=1, choices=RUNTIME_DISPLAY)
	license_date_format				= models.CharField(max_length=2, choices=LICENSE_DATE_FORMAT)
	rating_display					= models.ForeignKey('Rating')
	product_type					= models.CharField(max_length=4, choices=PRODUCT_TYPE)
	sugested_price_longform_sd			= models.CharField(max_length=10)
	sugested_price_longform_hd			= models.CharField(max_length=10)
	sugested_price_shortform_sd			= models.CharField(max_length=10)
	sugested_price_shortform_hd			= models.CharField(max_length=10)
	rental_period_shortform				= models.CharField(max_length=10)
	rental_period_longform				= models.CharField(max_length=10)
	license_window					= models.CharField(max_length=3, default='90')
	preview_period					= models.CharField(max_length=4, default='0', blank=True)
	maximum_viewing_length				= models.CharField(max_length=8, default='00:24:00', blank=True)
	extended_video_information			= models.CharField(max_length=1, default='Y', choices=(('Y', 'Yes'),('N', 'No')))
	
	def __unicode__(self):
		return self.name


class MetadataLanguage(models.Model):

	language					= models.ForeignKey('Language')
	item						= models.ForeignKey('Item')
	title_sort_name 				= models.CharField(max_length=22)
	title_brief 					= models.CharField(max_length=19)
	title 						= models.CharField(max_length=128)
	episode_name					= models.CharField(max_length=256)
	summary_long 					= models.CharField(max_length=4096)
	summary_medium 					= models.CharField(max_length=1024)
	summary_short	 				= models.CharField(max_length=256)

	def __unicode__(self):
		return self.language.name


class Item(models.Model):
	ITEM_STATUS = (
		('N', 'New'),
		('P', 'Processing'),
		('D', 'Done'),
		('W', 'Warning'),
	)
	name						= models.CharField(max_length=256)
	creation_date 					= models.DateTimeField(auto_now_add=True)
	modification_date 				= models.DateTimeField(auto_now=True)	
	kill_date 					= models.DateTimeField(default=datetime.now()+timedelta(days=45))
	format						= models.CharField(max_length=2, choices=FORMAT)
	status 						= models.CharField(max_length=2, choices=ITEM_STATUS)
	content_language				= models.ForeignKey('Language')
	content_duration				= models.CharField(max_length=10)
	episode_name					= models.CharField(max_length=255, blank=True)
	episode_id					= models.CharField(max_length=60, blank=True)
	category					= models.ForeignKey('Category')
	audience					= models.CharField(max_length=32, blank=True, default='Adult')
	show_type					= models.CharField(max_length=32, default='Movie')
	rating 						= models.CharField(max_length=32)
	genres 						= models.CharField(max_length=32)
	actors 						= models.CharField(max_length=512)
	country_of_origin				= models.ForeignKey('Country')
	year 						= models.CharField(max_length=4)
	director 					= models.CharField(max_length=128)
	studio						= models.CharField(max_length=64)
	studio_name 					= models.CharField(max_length=128)
	mam_id 						= models.CharField(max_length=64)


	def __unicode__(self):
		return self.name

class RenditionQueue(models.Model):
	RENDITION_QUEUE_STATUS = (
		('Q', 'Queued'),
		('D', 'Dequeued'),
		('E', 'Error'),
	)
	item	          			= models.ForeignKey('Item')
	file_name         			= models.CharField(max_length=256)
	svc_path          			= models.CharField(max_length=256)
	queue_status				= models.CharField(max_length=1,choices=RENDITION_QUEUE_STATUS)
	creation_date				= models.DateTimeField(auto_now_add=True)
	modification_date 			= models.DateTimeField(auto_now=True)
	

	error					= models.CharField(max_length=512, blank=True)

	def __unicode__(self):
		return self.file_name 
	
class VideoRendition(models.Model):
	VIDEO_RENDITION_STATUS = (
		('Q', 'Queued'),
		('F', 'Finished'),
		('E', 'Error'),
	)
	file_name				= models.CharField(max_length=256)
	video_profile				= models.ForeignKey('VideoProfile')
	transcoding_server			= models.ForeignKey('TranscodingServer')
	transcoding_job_guid			= models.CharField(max_length=256)
	status 					= models.CharField(max_length=1, choices=VIDEO_RENDITION_STATUS)
	item 					= models.ForeignKey('Item')
	file_size 				= models.BigIntegerField(default=0)
	checksum 				= models.CharField(max_length=32)
	
	error					= models.CharField(max_length=512)
	screen_format				= models.CharField(max_length=64)

	def __unicode__(self):
		return self.file_name

class ImageRendition(models.Model):
	IMAGE_RENDITION_STATUS = (
		('U', 'Unfilled'),
		('F', 'Filled'),
		('D', 'Done'),
		('E', 'Error'),
	)
	file_name 					= models.CharField(max_length=256)
	file_size 					= models.BigIntegerField(default=0)
	checksum 					= models.CharField(max_length=32)
	image_profile 					= models.ForeignKey('ImageProfile')
	item 						= models.ForeignKey('Item')
	status						= models.CharField(max_length=2, choices=IMAGE_RENDITION_STATUS)
	
	error						= models.CharField(max_length=512, blank=True)
	#
	# idiomas
	#
	def __unicode__(self):
		return self.file_name
	def filteredItems(self, item):
		return self.objects.filter(item=item)

class Provider(models.Model):
	provider					= models.CharField(max_length=20)
	provider_id					= models.CharField(max_length=20)
	provider_content_tier				= models.CharField(max_length=20)


class PackageGroup(models.Model):
	name 						= models.CharField(max_length=32)
	description					= models.CharField(max_length=128)
	def __unicode__(self):
		return self.name

class Package(models.Model):
	PACKAGE_STATUS = (
		('Q', 'Queued'),
		('P', 'Packaged'),
		('E', 'Error'),
	)

	customer					= models.ForeignKey('Customer')
	item						= models.ForeignKey('Item')
	date_published 					= models.DateField(auto_now_add=True)
	status						= models.CharField(max_length=2, choices=PACKAGE_STATUS)
	group 						= models.ForeignKey('PackageGroup')
	error						= models.CharField(max_length=512, blank=True)
	
	def __unicode__(self):
		return str(self.date_published)

class TranscodingServer(models.Model):
	
	host_name 					= models.CharField(max_length=256)
	ip_address 					= models.CharField(max_length=15)
	status 						= models.CharField(max_length=1, choices=ACTIVE_STATUS)
	
	def __unicode__(self):
		return self.ip_address

class Path(models.Model):
	
	key 						= models.CharField(max_length=24,unique=True)
	location 					= models.CharField(max_length=256)
	description 					= models.CharField(max_length=256)
	
	def __unicode__(self):
		return self.key

class VideoProfile(models.Model):
	
	name 						= models.CharField(unique=True, max_length=32)
	guid 						= models.CharField(max_length=256)
	file_extension 					= models.CharField(max_length=64)
	status 						= models.CharField(max_length=1, choices=ACTIVE_STATUS)
	sufix 						= models.CharField(max_length=32)
	format 						= models.CharField(max_length=2, choices=FORMAT)
	notes 						= models.CharField(max_length=512)

	#
	# Cablelabs Metadata for Movie Item
	#
	audio_type					= models.CharField(max_length=64)
	resolution					= models.CharField(max_length=5)
	frame_rate					= models.CharField(max_length=2)
	codec						= models.CharField(max_length=64)
	bit_rate					= models.CharField(max_length=64)

	def __unicode__(self):
		return self.name

class ImageProfile(models.Model):
	IMAGE_TYPE = (
		('S', 'Soft'),
		('H', 'Hard'),
	)
	name 						= models.CharField(max_length=256)
	description 					= models.CharField(max_length=512, blank=True)
	sufix 						= models.CharField(max_length=32)
	file_extension 					= models.CharField(max_length=32)
	status 						= models.CharField(max_length=1, choices=ACTIVE_STATUS)
	regex 						= models.CharField(max_length=512, blank=True)
	image_aspect_ratio				= models.CharField(max_length=24)
	type 						= models.CharField(max_length=1, choices=IMAGE_TYPE)
	
	def __unicode__(self):
		return self.name

class MetadataProfile(models.Model):
	
	key 						= models.CharField(max_length=32)
	name 						= models.CharField(max_length=64)
	status 						= models.CharField(max_length=1, choices=ACTIVE_STATUS)
	description 					= models.CharField(max_length=512)
	
	def __unicode__(self):
		return self.name

class Category(models.Model):
	
	name 						= models.CharField(max_length=256)
	def __unicode__(self):
		return self.name

class CustomCategory(models.Model):
	
	name 						= models.CharField(max_length=256)
	def __unicode__(self):
		return self.name

class CategoryRelation(models.Model):
	
	category 					= models.ForeignKey('Category')
	custom_category 				= models.ForeignKey('CustomCategory')
	customer 					= models.ForeignKey('Customer')

	def __unicode__(self):
		return self.customer.name


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Funciones - GET
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def GetVideoProfiles(format='ALL'):
    if format == 'ALL':
	vp_list = VideoProfile.objects.filter(status='E')
    elif format == 'SD':
	vp_list = VideoProfile.objects.filter(status='E',format='SD')
    elif format == 'HD':
	vp_list = VideoProfile.objects.filter(status='E',format='HD')
    return vp_list


def GetImageProfile():
    return ImageProfile.objects.filter(status='E')

def GetTranscodingServer():
    return TranscodingServer.objects.filter(status='E')

def GetRenditionQueue():
    return RenditionQueue.objects.filter(queue_status='Q')

def GetPath(path=None):
    if path is not None:
	try:
	    return Path.objects.get(key=path).location
	except:
	    return None
    return None

def GetVideoRenditionQueue():
    return VideoRendition.objects.filter(status='Q')

def GetImageRenditionQueue():
    return ImageRendition.objects.filter(status='F') 

def GetProcessingItems():
    return Item.objects.filter(status='P')

def GetPackageQueue():
    return Package.objects.filter(status='Q')




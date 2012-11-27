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

IMAGE_TYPE = (
	('S', 'Soft'),
	('H', 'Hard'),
)










class Language(models.Model):
	code 						= models.CharField(max_length=2)
        name 						= models.CharField(max_length=20)

	def __unicode__(self):
	    return name


class Customer(models.Model):

	PRODUCT_TYPE = (
		('VOD', 'Video On Demand'),
		('MOD', 'Movie On Demand'),
	)

	RATING_DISPLAY = (
		('X',  'X'),
		('XXX','XXX'),
		('18', '18'),
		('R',  'R'),
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
	rating_display					= models.CharField(max_length=3, choices=RATING_DISPLAY)
	product_type					= models.CharField(max_length=3, choices=PRODUCT_TYPE)
	sugested_price_sd				= models.CharField(max_length=10)
	sugested_price_hd				= models.CharField(max_length=10)


	def __unicode__(self):
		return self.name


class MetadataLanguage(models.Model):

	language					= models.ForeignKey('Language')
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
	format						= models.CharField(max_length=1, choices=FORMAT)
	status 						= models.CharField(max_length=2, choices=ITEM_STATUS)
	#asset_id 					= models.CharField(max_length=20) # autogenerar
    
	content_language				= models.ForeignKey('Language')
	metadata_language				= models.ManyToManyField('MetadataLanguage')
	episode_id					= models.CharField(max_length=10)
	category					= models.CharField(max_length=32)
	rating 						= models.CharField(max_length=32)
	genres 						= models.CharField(max_length=32)
	actors 						= models.CharField(max_length=512)
	country_of_origin				= models.CharField(max_length=2)
	year 						= models.CharField(max_length=4)
	director 					= models.CharField(max_length=128)
	studio_name 					= models.CharField(max_length=128)
	mam_id 						= models.CharField(max_length=64)


	def __unicode__(self):
		return self.name

class ImportQueue(models.Model):
	IMPORT_QUEUE_STATUS = (
		('Q', 'Queued'),
		('D', 'Dequeued'),
	)
	item	          			= models.ForeignKey('Item')
	file_name         			= models.CharField(max_length=256)
	svc_path          			= models.CharField(max_length=256)
	queue_status				= models.CharField(max_length=1,choices=IMPORT_QUEUE_STATUS)
	creation_date				= models.DateTimeField(auto_now_add=True)
	modification_date 			= models.DateTimeField(auto_now=True)
	

	error					= models.CharField(max_length=512)

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
		('E', 'Empty'),
		('F', 'Filled'),
	)
	file_name 					= models.CharField(max_length=256)
	file_size 					= models.BigIntegerField(default=0)
	checksum 					= models.CharField(max_length=32)
	image_profile 					= models.ForeignKey('ImageProfile')
	item 						= models.ForeignKey('Item')
	status						= models.CharField(max_length=2, choices=IMAGE_RENDITION_STATUS)
	#
	# idiomas
	#
	def __unicode__(self):
		return self.file_name



class PackageGroup(models.Model):
	name 						= models.CharField(max_length=32)
	
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
	date_published 					= models.DateTimeField(auto_now_add=True)
	status						= models.CharField(max_length=2, choices=PACKAGE_STATUS)
	group 						= models.ForeignKey('PackageGroup')
	error						= models.CharField(max_length=512)
	
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
	
	name 						= models.CharField(max_length=256)
	description 					= models.CharField(max_length=512)
	sufix 						= models.CharField(max_length=32)
	file_extension 					= models.CharField(max_length=32)
	status 						= models.CharField(max_length=1, choices=ACTIVE_STATUS)
	regex 						= models.CharField(max_length=512)
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
		return self.customer


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

def GetImportQueue():
    return ImportQueue.objects.filter(queue_status='Q')


def GetPath(path=None):
    if path is not None:
	return Path.objects.get(key=path).location
    return None


def GetVideoRenditionQueue():
    return VideoRendition.objects.filter(status='Q')
    

def GetProcessingItems():
    return Item.objects.filter(status='P')
    

def GetPackageQueue():
    return Package.objects.filter(status='Q')




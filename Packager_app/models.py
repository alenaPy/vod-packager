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

LANGUAGE = (
	('SP', 'Spanish'),
	('EN', 'English'),
	('PO', 'Portuguesse'),
)

IMAGE_TYPE = (
	('S', 'Soft'),
	('H', 'Hard'),
)

ITEM_STATUS = (
	('N', 'New'),
	('P', 'Processing'),
	('D', 'Done'),
	('W', 'Warning'),
)

IMPORT_QUEUE_STATUS = (
	('Q', 'Queued'),
	('D', 'Dequeued'),
)

IMAGE_RENDITION_STATUS = (
	('E', 'Empty'),
	('F', 'Filled'),
)

VIDEO_RENDITION_STATUS = (
	('Q', 'Queued'),
	('F', 'Finished'),
	('E', 'Error'),
)

PACKAGE_STATUS = (
	('Q', 'Queued'),
	('P', 'Packaged'),
	('E', 'Error'),
)
	
class Customer(models.Model):

	name 						= models.CharField(max_length=256)
	vod_active 					= models.BooleanField(default=True)
	# xxx review
	#rental_period_start_date 	= models.DateField()
	#rental_period_end_date 		= models.DateField()
	
	# notificaciones email

	image_type 					= models.CharField(max_length=128)
	video_profile 				= models.ForeignKey('VideoProfile')
	image_profile 				= models.ManyToManyField('ImageProfile')
	metadata_profile 			= models.ForeignKey('MetadataProfile')
	language 					= models.CharField(max_length=2, choices=LANGUAGE)
	cost_HD 					= models.IntegerField()
	cost_SD 					= models.IntegerField()

	def __unicode__(self):
		return self.name

class Item(models.Model):
	    
	name						= models.CharField(max_length=256)
	creation_date 				= models.DateTimeField(auto_now_add=True)
	modification_date 			= models.DateTimeField(auto_now=True)	
	kill_date 					= models.DateTimeField(default=datetime.now()+timedelta(days=45))
	format						= models.CharField(max_length=1, choices=FORMAT)
	status 						= models.CharField(max_length=2, choices=ITEM_STATUS)
	asset_id 					= models.CharField(max_length=20) # autogenerar
	title_sort_name_sp 			= models.CharField(max_length=22)
	title_brief_sp 				= models.CharField(max_length=19)
	title_sp 					= models.CharField(max_length=128)
	title_sort_name_en 			= models.CharField(max_length=22)
	title_brief_en 				= models.CharField(max_length=19)
	title_en					= models.CharField(max_length=128)
	title_sort_name_po			= models.CharField(max_length=22)
	title_brief_po 				= models.CharField(max_length=19)
	title_po 					= models.CharField(max_length=128)
	summary_long_sp 			= models.CharField(max_length=4096)
	summary_medium_sp 			= models.CharField(max_length=1024)
	summary_short_sp 			= models.CharField(max_length=256)
	summary_long_en 			= models.CharField(max_length=4096)
	summary_medium_en 			= models.CharField(max_length=1024)
	summary_short_en 			= models.CharField(max_length=256)
	summary_long_po				= models.CharField(max_length=4096)
	summary_medium_po			= models.CharField(max_length=1024)
	summary_short_po			= models.CharField(max_length=256)
	episode_number				= models.CharField(max_length=256)
	episode_title_sp			= models.CharField(max_length=256)
	episode_title_en 			= models.CharField(max_length=256)
	episode_title_po 			= models.CharField(max_length=256)
	rating 						= models.CharField(max_length=128)
	genre 						= models.CharField(max_length=32)
	actors 						= models.CharField(max_length=512)
	origin_country 				= models.CharField(max_length=2)
	year 						= models.CharField(max_length=4)
	director 					= models.CharField(max_length=128)
	studio_name 				= models.CharField(max_length=128)
	format 						= models.CharField(max_length=2, choices=FORMAT)
	mam_id 						= models.CharField(max_length=64)

	def __unicode__(self):
		return self.name

class ImportQueue(models.Model):
	
	item	          			= models.ForeignKey('Item')
	file_name         			= models.CharField(max_length=256)
	svc_path          			= models.CharField(max_length=256)
	queue_status				= models.CharField(max_length=1,choices=IMPORT_QUEUE_STATUS)
	creation_date				= models.DateTimeField(auto_now_add=True)
	modification_date 			= models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return self.file_name 
	
class VideoRendition(models.Model):
	
	file_name					= models.CharField(max_length=256)
	video_profile				= models.ForeignKey('VideoProfile')
	transcoding_server			= models.ForeignKey('TranscodingServer')
	transcoding_job_guid		= models.CharField(max_length=256)
	# xxx review
	#transcoding_job			= models.ForeignKey('TranscodingJob')
	status 						= models.CharField(max_length=1, choices=VIDEO_RENDITION_STATUS)
	#error_id					= models.ForeignKey('AppError')
	item 						= models.ForeignKey('Item')
	file_size 					= models.BigIntegerField(default=0)
	checksum 					= models.CharField(max_length=32)
	
	def __unicode__(self):
		return self.file_name

class ImageRendition(models.Model):
	
	file_name 					= models.CharField(max_length=256)
	file_size 					= models.BigIntegerField(default=0)
	checksum 					= models.CharField(max_length=32)
	image_profile 				= models.ForeignKey('ImageProfile')
	item 						= models.ForeignKey('Item')

	def __unicode__(self):
		return self.file_name
                
class PackageGroup(models.Model):
	name 						= models.CharField(max_length=32)
	
	def __unicode__(self):
		return self.name

class Package(models.Model):
	
	customer					= models.ForeignKey('Customer')
	item						= models.ForeignKey('Item')
	date_published 				= models.DateField()
	# xxx review
	#user 						= models.ForeignKey('User') # descomentar
	#status 					= models.ForeignKey(Status)
	group 						= models.ForeignKey('PackageGroup')
	
	def __unicode__(self):
		return self.date_published

class TranscodingServer(models.Model):
	
	host_name 					= models.CharField(max_length=256)
	ip_address 					= models.CharField(max_length=15)
	status 						= models.CharField(max_length=1, choices=ACTIVE_STATUS)
	
	def __unicode__(self):
		return self.ip_address

class Path(models.Model):
	
	key 						= models.CharField(max_length=24,unique=True)
	location 					= models.CharField(max_length=256)
	description 				= models.CharField(max_length=256)
	
	def __unicode__(self):
		return self.key

class Daemon(models.Model):
	
	name 						= models.CharField(max_length=256)
	description 				= models.CharField(max_length=256)
	status 						= models.ForeignKey('Status')
	last_run 					= models.DateField()
	action 						= models.CharField(max_length=512)
	
	def __unicode__(self):
		return self.name

class VideoProfile(models.Model):
	
	name 						= models.CharField(unique=True, max_length=256)
	guid 						= models.CharField(max_length=256)
	file_extension 				= models.CharField(max_length=64)
	status 						= models.CharField(max_length=1, choices=ACTIVE_STATUS)
	bit_rate 					= models.CharField(max_length=64)
	sufix 						= models.CharField(max_length=32)
	format 						= models.CharField(max_length=2, choices=FORMAT)
	# xxx review
	#fps 						= models.DecimalField() #descomentar
	notes 						= models.CharField(max_length=512)
	
	def __unicode__(self):
		return self.name

class ImageProfile(models.Model):
	
	name 						= models.CharField(max_length=256)
	description 				= models.CharField(max_length=512)
	sufix 						= models.CharField(max_length=32)
	# xxx review
	#prefix 					= models.CharField(max_length=32)
	file_extension 				= models.CharField(max_length=32)
	status 						= models.CharField(max_length=1, choices=ACTIVE_STATUS)
	regex 						= models.CharField(max_length=512)
	content_aspect 				= models.CharField(max_length=24)
	type 						= models.CharField(max_length=1, choices=IMAGE_TYPE)
	
	def __unicode__(self):
		return self.name

class MetadataProfile(models.Model):
	
	key 						= models.CharField(max_length=32)
	name 						= models.CharField(max_length=64)
	status 						= models.CharField(max_length=1, choices=ACTIVE_STATUS)
	description 				= models.CharField(max_length=512)
	
	def __unicode__(self):
		return self.name

class Status(models.Model):
	
	key 						= models.CharField(max_length=32)
	name 						= models.CharField(max_length=64)
	description 				= models.CharField(max_length=512)

	def __unicode__(self):
		return self.name

class AppError(models.Model):

	key 						= models.CharField(max_length=32)
	name 						= models.CharField(max_length=64)
	description 				= models.CharField(max_length=512)

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
	custom_category 			= models.ForeignKey('CustomCategory')
	customer 					= models.ForeignKey('Customer')

	def __unicode__(self):
		return self.customer

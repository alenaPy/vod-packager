from django.db import models
from datetime import *
# importar User y DateTime

# Create your models here.


ACTIVE_STATUS = (
	('E', 'Enable'),
	('D', 'Disable'),
)

FORMAT = (
	('SD', 'SD'),
	('HD', 'HD'),
	('3D', '3D'),
)	

#
# INCOMPLETA
#
class Customer(models.Model):
	name = models.CharField(max_length=256)
#	path_id = models.ForeignKey(Path)
	vod_active = models.BooleanField(default=True)
	video_profile_id = models.ForeignKey('VideoProfile')
	image_profile_id = models.ForeignKey('ImageProfile')
	metadata_profile_id = models.ForeignKey('MetadataProfile')
	rental_period_start_date = models.DateField()
	rental_period_end_date = models.DateField()
	cost_HD = models.IntegerField()
	cost_SD = models.IntegerField()
	# notificaciones email
	def __unicode__(self):
		return self.name

#
# INCOMPLETA
#
class Item(models.Model):
	ITEM_STATUS = (
	    ('N', 'New'),
	    ('P', 'Processing'),
	    ('D', 'Done'),
	    ('W', 'Warning'),
	)
	    
	name          	  = models.CharField(max_length=256)
	creation_date	  = models.DateTimeField(auto_now_add=True)
	modification_date = models.DateTimeField(auto_now=True)	
	kill_date         = models.DateTimeField(default=datetime.now()+timedelta(days=45))
	format		  = models.CharField(max_length=1, choices=FORMAT)
	status		  = models.CharField(max_length=2, choices=ITEM_STATUS)

	def __unicode__(self):
		return self.name

class ImportQueue(models.Model):
	IMPORT_QUEUE_STATUS = (
	    ('Q', 'Queued'),
	    ('D', 'Dequeued'),
	)
	item	          = models.ForeignKey('Item')
	file_name         = models.CharField(max_length=256)
	svc_path          = models.CharField(max_length=256)
	queue_status      = models.CharField(max_length=1,choices=IMPORT_QUEUE_STATUS)
	creation_date     = models.DateTimeField(auto_now_add=True)
	modification_date = models.DateTimeField(auto_now=True)


class VideoRendition(models.Model):
	VIDEO_RENDITION_STATUS = (
	    ('Q', 'Queued'),
	    ('F', 'Finished'),
	    ('E', 'Error'),
	)
	file_name             = models.CharField(max_length=256)
	#path_id              = models.ForeignKey(Path)
	video_profile         = models.ForeignKey('VideoProfile')
	transcoding_server    = models.ForeignKey('TranscodingServer')
	transcoding_job_guid  = models.CharField(max_length=256)
	#transcoding_job  = models.ForeignKey('TranscodingJob')
	status                = models.CharField(max_length=1, choices=VIDEO_RENDITION_STATUS)
	#status_id = models.ForeignKey(Status)
	#error_id              = models.ForeignKey('AppError')
	item                  = models.ForeignKey('Item')
	file_size             = models.BigIntegerField(default=0)
	checksum              = models.CharField(max_length=32)
	def __unicode__(self):
		return self.file_name

class ImageRendition(models.Model):
	IMAGE_RENDITION_STATUS = (
	    ('E', 'Empty'),
	    ('F', 'Filled'),
	)
	file_name        = models.CharField(max_length=256)
	#path_id         = models.ForeignKey(Path)
	file_size        = models.BigIntegerField(default=0)
	checksum         = models.CharField(max_length=32)
	image_profile    = models.ForeignKey('ImageProfile')
	item             = models.ForeignKey('Item')
	def __unicode__(self):
                return self.file_name
                


class PackageGroup(models.Model):
	name = models.CharField(max_length=32)
	
	def __unicode__(self):
		return self.name


class Package(models.Model):
	PACKAGE_STATUS = (
	    ('Q', 'Queued'),
	    ('P', 'Packaged'),
	    ('E', 'Error'),
	)
	customer       = models.ForeignKey('Customer')
	item           = models.ForeignKey('Item')
	date_published = models.DateField()
	#user           = models.ForeignKey('User') # descomentar
	#status         = models.ForeignKey(Status)
	group	       = models.ForeignKey('PackageGroup')
	def __unicode__(self):
                return self.media_id

class TranscodingServer(models.Model):
	host_name  = models.CharField(max_length=256)
	ip_address = models.IPAddressField()
	status     = models.CharField(max_length=1, choices=ACTIVE_STATUS)
	def __unicode__(self):
                return self.host_name

class Path(models.Model):
	key = models.CharField(max_length=24,unique=True)
	location = models.CharField(max_length=256)
	description = models.CharField(max_length=256)
	def __unicode__(self):
                return self.key

class Daemon(models.Model):
	name = models.CharField(max_length=256)
	description = models.CharField(max_length=256)
	status_id = models.ForeignKey('Status')
	last_run = models.DateField()
	action = models.CharField(max_length=512)
	def __unicode__(self):
		return self.file_name

class VideoProfile(models.Model):
	name           = models.CharField(unique=True, max_length=256)
	guid           = models.CharField(max_length=256)
	file_extension = models.CharField(max_length=64)
	#status_id = models.ForeignKey(Status)
	status         = models.CharField(max_length=1, choices=ACTIVE_STATUS)
	bit_rate       = models.CharField(max_length=64)
	sufix	       = models.CharField(max_length=32)
	format         = models.CharField(max_length=2, choices=FORMAT)
	#fps            = models.DecimalField() #descomentar
	notes          = models.CharField(max_length=512)
	def __unicode__(self):
                return self.name

class ImageProfile(models.Model):
	name = models.CharField(max_length=256)
	description    = models.CharField(max_length=512)
	sufix  	       = models.CharField(max_length=32)
	#prefix = models.CharField(max_length=32)
	file_extension = models.CharField(max_length=32)
	status         = models.CharField(max_length=1, choices=ACTIVE_STATUS)
	regex          = models.CharField(max_length=512)
	def __unicode__(self):
                return self.name

class MetadataProfile(models.Model):
	key            = models.CharField(max_length=32)
	name           = models.CharField(max_length=64)
	status         = models.CharField(max_length=1, choices=ACTIVE_STATUS)
	description    = models.CharField(max_length=512)
	def __unicode__(self):
                return self.name

class Status(models.Model):
	key = models.CharField(max_length=32)
        name = models.CharField(max_length=64)
        description = models.CharField(max_length=512)
        def __unicode__(self):
                return self.name

class AppError(models.Model):
        key = models.CharField(max_length=32)
        name = models.CharField(max_length=64)
        description = models.CharField(max_length=512)
        def __unicode__(self):
                return self.name


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
	('', 'Empty'),
)

BRAND_FORMAT = (
	('SD', 'SD'),
	('HD', 'HD'),
	('3D', '3D'),
)


class ItemGroup(models.Model):
	key						= models.CharField(max_length=6)
	name						= models.CharField(max_length=50)

	def __unicode__(self):
	    return self.name
	

class Country(models.Model):
	code						= models.CharField(max_length=2)
	code_three_chars				= models.CharField(max_length=3, blank=True)
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


#
# Descomentar luego de cambiar el modelo
#
class CustomMetadata(models.Model):
	customer					= models.ForeignKey('Customer')
	apply_to					= models.CharField(max_length=1, default='T', choices=(('I', 'Image'),('T', 'Title'),('V', 'Video')))
	name						= models.CharField(max_length=256)
	brand_condition					= models.CharField(max_length=30, blank=True)
	SHOW_TYPE = (('Ad', 'Advertisement'),
		     ('Events', 'Events'),
		     ('Kids', 'Kids'),
		     ('Lifestyle', 'Lifestyle'),
		     ('Movie', 'Movie'),
		     ('Music', 'Music'),
		     ('Series', 'Series'),
		     ('Sports', 'Sports'))
	show_type					= models.CharField(max_length=10, choices=SHOW_TYPE,default='Movie')
	format_condition				= models.CharField(max_length=2, choices=FORMAT, blank=True, default='')
	value						= models.CharField(max_length=256)


class Customer(models.Model):

	PRODUCT_TYPE = (
		('TVOD', 'True Video on Demand'),
		('SVOD', 'Subscription Video On Demand'),
		('MOD', 'Movie On Demand'),
		('MODADULT', 'Mod Adult'),
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
	IMAGE_TYPE = (
		('poster', 'Poster'),
		('box cover', 'Box Cover'),
	)

	PATH_STYLE = (
		('PEP', 'Plain Export Path'),
		('APC', 'Adultos / Brand / Category'),
		('DLA', 'DLA Style'),
		('BFC', 'Brand Format / Category'),
		('BPC', 'Brand / Category'),
		('FPC', 'Format / Category'),
		('AM',  'Adultos / Brand'),
		('CA',  'Adultos / Category'),
		('ZA',  'Zona Adultos / Format / Category'),
		('SHO', 'SHOWRUNNER/ADULTO +18/'),
	)
	
	name 						= models.CharField(max_length=256)
	vod_active 					= models.BooleanField(default=True)
	
	image_type 					= models.CharField(max_length=128)
	video_profile 					= models.ManyToManyField('VideoProfile')
	image_profile 					= models.ManyToManyField('ImageProfile')
	internal_brand					= models.ManyToManyField('InternalBrand')
	metadata_profile 				= models.ForeignKey('MetadataProfile')
	export_language					= models.ForeignKey('Language')
	export_format					= models.CharField(max_length=4, choices=EXPORT_CUSTOMER_FORMAT)
	export_folder					= models.CharField(max_length=256)
	runtype_display					= models.CharField(max_length=1, choices=RUNTIME_DISPLAY)
	license_date_format				= models.CharField(max_length=2, choices=LICENSE_DATE_FORMAT)
	rating_display					= models.ForeignKey('Rating')
	product_type					= models.CharField(max_length=10, choices=PRODUCT_TYPE)
	viewing_can_be_resumed				= models.CharField(max_length=1, choices=(('Y', 'Yes'),('N', 'No')), default='N')
	suggested_price_longform_sd			= models.CharField(max_length=10, default='0')
	suggested_price_longform_hd			= models.CharField(max_length=10, default='0')
	suggested_price_shortform_sd			= models.CharField(max_length=10, default='0')
	suggested_price_shortform_hd			= models.CharField(max_length=10, default='0')
#
#	Quitar rental period del siguiente cambio de la base de datos
#
	billing_id					= models.CharField(max_length=10, blank=True)
	license_window					= models.CharField(max_length=3, default='90')
	preview_period					= models.CharField(max_length=4, default='0', blank=True)
	maximum_viewing_length				= models.CharField(max_length=8, default='00:24:00', blank=True)
	extended_video_information			= models.CharField(max_length=1, default='Y', choices=(('Y', 'Yes'),('N', 'No')))
	category_with_spaces				= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	category_path_style				= models.CharField(max_length=3, default='DLA', choices=PATH_STYLE)
	titles_in_capital_letter			= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	use_hdcontent_var				= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	doctype						= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	summary_long					= models.CharField(max_length=1, default='Y', choices=(('Y', 'Yes'),('N', 'No')))
	image_aspect_ratio				= models.CharField(max_length=1, default='Y', choices=(('Y', 'Yes'),('N', 'No')))
	actor_display					= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No'),('B','Both')))
	limit_content_value				= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	id_len_reduced					= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	use_genres_category				= models.CharField(max_length=1, default='Y', choices=(('Y', 'Yes'),('N', 'No')))
	custom_genres					= models.CharField(max_length=20, default='',  blank=True) 
	empty_product_type				= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	use_xml_adi_filename				= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	use_three_chars_country				= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	provider_id_with_brand				= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	provider_id					= models.CharField(max_length=20, blank=True)
	provider_qa_contact				= models.CharField(max_length=100, blank=True)
	brand_in_synopsis				= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	export_complete_package				= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	use_preview					= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))	
	use_dtd_file					= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	id_special_prefix				= models.CharField(max_length=4, default='', blank=True)
	uppercase_adi					= models.CharField(max_length=1, default='N', choices=(('Y', 'Yes'),('N', 'No')))
	special_product_type				= models.CharField(max_length=20, default='', blank=True)
		
	def __unicode__(self):
		return self.name


class MetadataLanguage(models.Model):

	language					= models.ForeignKey('Language')
	item						= models.ForeignKey('Item')
	title_sort_name 				= models.CharField(max_length=22)
	title_brief 					= models.CharField(max_length=30)
	title 						= models.CharField(max_length=128)
	episode_name					= models.CharField(max_length=256, blank=True)
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
		('E', 'Error'),
	)
	name				= models.CharField(max_length=256)
	creation_date			= models.DateTimeField(auto_now_add=True)
	modification_date		= models.DateTimeField(auto_now=True)	
	kill_date 			= models.DateTimeField(default=datetime.now()+timedelta(days=60))
	format				= models.CharField(max_length=2, choices=FORMAT)
	status 				= models.CharField(max_length=2, choices=ITEM_STATUS)
	content_language		= models.ForeignKey('Language')
	
	#
	# Si es Short form o long form!
	#
	material_type			= models.CharField(max_length=2, choices=(('SF', 'Short Form'), ('LF', 'Long Form')))

	'''
	A string representing a period of time and 
	the maximum number of views over the 
	period of time.
	The separator shall be a "," between the 
	period start date, period end date and 
	maximum views.
	'''
	subscriber_view_limit		= models.CharField(max_length=30, blank=True)

	'''
	Digital Object Identifier (DOI) from the 
	Entertainment ID Registry [EIDR]
	'''
	eidr				= models.CharField(max_length=30, blank=True)

	'''
	International Standard Audiovisual Number 
	(ISAN)
	'''
	isan				= models.CharField(max_length=30, blank=True)

	closed_captioning		= models.CharField(max_length=1, choices=(('Y', 'Yes'),('N', 'No')), default='N')
	run_time			= models.CharField(max_length=8)
	display_run_time		= models.CharField(max_length=5)
	year 				= models.CharField(max_length=4)
	country_of_origin		= models.ForeignKey('Country')
	#
	# Hacer las modificaciones
	#
	actors				= models.CharField(max_length=35, blank=True)
	actors_display			= models.CharField(max_length=512, blank=True)		

	episode_name			= models.CharField(max_length=255, blank=True)
	episode_id			= models.CharField(max_length=60, blank=True)
	especial			= models.CharField(max_length=1, choices=(('Y', 'Yes'),('N', 'No')), default='N')
	category			= models.ForeignKey('Category')
	audience			= models.CharField(max_length=32, blank=True, default='Adult')

	SHOW_TYPE = (('Ad', 'Advertisement'),
		     ('Events', 'Events'),
		     ('Kids', 'Kids'),
		     ('Lifestyle', 'Lifestyle'),
		     ('Movie', 'Movie'),
		     ('Music', 'Music'),
		     ('Series', 'Series'),
		     ('Sports', 'Sports'))
	show_type			= models.CharField(max_length=10, choices=SHOW_TYPE,default='Movie')
	rating				= models.CharField(max_length=32)
	genres				= models.CharField(max_length=32)
	director 			= models.CharField(max_length=128)

	group				= models.ForeignKey('ItemGroup')
	brand				= models.CharField(max_length=64, blank=True)
	internal_brand			= models.ForeignKey('InternalBrand')
	studio				= models.CharField(max_length=64)
	studio_name 			= models.CharField(max_length=128)
	mam_id 				= models.CharField(max_length=64)

	def __unicode__(self):
		return self.name


class RenditionQueue(models.Model):
	RENDITION_QUEUE_STATUS = (
		('W', 'Waiting'),
		('P', 'Pulling'),
		('Q', 'Queued'),
		('D', 'Dequeued'),
		('E', 'Error'),
	)
	item	          			= models.ForeignKey('Item')
	file_name         			= models.CharField(max_length=256)
	local_file				= models.CharField(max_length=1, choices=(('Y', 'Yes'), ('N', 'No')))
	queue_status				= models.CharField(max_length=1,choices=RENDITION_QUEUE_STATUS)
	creation_date				= models.DateTimeField(auto_now_add=True)
	modification_date 			= models.DateTimeField(auto_now=True)
	
	error					= models.CharField(max_length=512, blank=True)

	def __unicode__(self):
		return self.file_name 

class InternalBrand(models.Model):
	name					= models.CharField(max_length=20)
	format					= models.CharField(max_length=2, choices=BRAND_FORMAT)
	

	def __unicode__(self):
		return self.name

class PreviewRenditions(models.Model):
        file_name                               = models.CharField(max_length=256)
        video_profile                           = models.ForeignKey('VideoProfile')
        run_time                                = models.CharField(max_length=8)
        file_size                               = models.BigIntegerField(default=0)
        checksum                                = models.CharField(max_length=32)
                                        
        def __unicode__(self):
            return self.file_name
                                                                


class VideoRendition(models.Model):
	VIDEO_RENDITION_STATUS = (
		('Q', 'Queued'),
		('F', 'Finished'),
		('U', 'Unasigned'),
		('E', 'Error'),
		('C', 'Cancel'),
	)
	file_name				= models.CharField(max_length=256)
	video_profile				= models.ForeignKey('VideoProfile')
	transcoding_server			= models.ForeignKey('TranscodingServer', blank=True, null=True)
	transcoding_job_guid			= models.CharField(max_length=256, blank=True)
	status 					= models.CharField(max_length=1, choices=VIDEO_RENDITION_STATUS)
	item 					= models.ForeignKey('Item')
	src_file_name         			= models.CharField(max_length=256)
	src_svc_path          			= models.CharField(max_length=256)
	file_size 				= models.BigIntegerField(default=0)
	checksum 				= models.CharField(max_length=32)
	error					= models.CharField(max_length=512, blank=True)
	screen_format				= models.CharField(max_length=64)
	speed					= models.CharField(max_length=25, blank=True)
	progress				= models.CharField(max_length=10, blank=True)
	
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
	name	 					= models.CharField(max_length=256)
	ip_address 					= models.CharField(max_length=15)
	status 						= models.CharField(max_length=1, choices=ACTIVE_STATUS)

	
	def __unicode__(self):
		return self.ip_address

class Path(models.Model):
	
	key 						= models.CharField(max_length=24)
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
	need_to_be_checked				= models.CharField(max_length=1, choices=(('T', 'True'),('F', 'False')))
	cloud_duplicate					= models.CharField(max_length=1, choices= (('Y', 'Yes'), ('N', 'No')), default='N', blank= False)
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
	format 						= models.CharField(max_length=2, choices=FORMAT)
	regex 						= models.CharField(max_length=512, blank=True)
	image_aspect_ratio				= models.CharField(max_length=24)
	type 						= models.CharField(max_length=1, choices=IMAGE_TYPE)
	cloud_duplicate					= models.CharField(max_length=1, choices= (('Y', 'Yes'), ('N', 'No')), default='N', blank= False)
	
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
	    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Trae todos los Video Profiles
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def GetVideoProfiles(format='ALL'):
    if format == 'ALL':
	vp_list = VideoProfile.objects.filter(status='E')
    elif format == 'SD':
	vp_list = VideoProfile.objects.filter(status='E',format='SD')
    elif format == 'HD':
	vp_list = VideoProfile.objects.filter(status='E',format='HD')
    return vp_list

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Trae todos los Image Profiles
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def GetImageProfile(format='ALL'):
    if format == 'ALL':
	return ImageProfile.objects.filter(status='E')
    elif format == 'SD':
	return ImageProfile.objects.filter(status='E', format='SD')
    elif format == 'HD':
	return ImageProfile.objects.filter(status='E', format='HD')
	
	
def GetImageProfilesBrand(IBrand=None):
    ImageProfiles = []
    if IBrand is not None:
	try:
	    Customers = Customer.objects.filter(internal_brand=IBrand)
	    for customer in Customers:
		if IBrand.format == 'HD':
		    IProfiles = customer.image_profile.filter(status='E')
		elif IBrand.format == 'SD':
		    IProfiles = customer.image_profile.filter(status='E', format='SD')
		elif IBrand.format == '3D':
		    IProfiles = customer.image_profile.filter(status='E', format='3D')   

		for iprofile in IProfiles:
		    if iprofile not in ImageProfiles:
			ImageProfiles.append(iprofile)
	except:
	    pass
    return ImageProfiles


def GetVideoProfilesBrand(IBrand=None):
    
    VideoProfiles = []
    
    if IBrand is not None:
	try:
	    Customers = Customer.objects.filter(internal_brand=IBrand)
	    for customer in Customers:
		if IBrand.format == 'HD':
		    VProfiles = customer.video_profile.filter(status='E')
		elif IBrand.format == 'SD':
		    VProfiles = customer.video_profile.filter(status='E', format='SD')
		elif IBrand.format == '3D':
		    VProfiles = customer.video_profile.filter(status='E', format='3D')   
		
		for vprofile in VProfiles:
		    if vprofile not in VideoProfiles:
			VideoProfiles.append(vprofile)
	except:
	    pass	
    
    return VideoProfiles	
	
	
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Trae todo los Transcoding Servers Habilitados
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def GetTranscodingServer():
    return TranscodingServer.objects.filter(status='E')

def GetWaitingRenditionQueue():
    return RenditionQueue.objects.filter(queue_status='W').order_by('id')

def GetRenditionQueue():
    return RenditionQueue.objects.filter(queue_status='Q')

def GetPath(path=None):
    if path is not None:
	try:
	    return Path.objects.get(key=path).location
	except:
	    return None
    return None

def GetVideoRenditionUnassigned():
    return VideoRendition.objects.filter(status='U')

def GetVideoRenditionQueue():
    return VideoRendition.objects.filter(status='Q')

def GetImageRenditionQueue():
    return ImageRendition.objects.filter(status='F') 

def GetNewItems():
    return Item.objects.filter(status='N')        

def GetProcessingItems():
    return Item.objects.filter(status='P')

def GetPackageQueue():
    return Package.objects.filter(status='Q')

def GetCustomersForExport(it):
	customers_for_export = []
	customers_vod_active = Customer.objects.filter(vod_active=True)
	for c in customers_vod_active:
		x = 0
		ips = c.image_profile.all()
		for ip in ips:
			irs = ImageRendition.objects.filter(item=it, image_profile=ip.id)
			for ir in irs:
				if ir.image_profile == ip and ir.status == "D":
					x = x + 1

		if len(ips) == x and x != 0:
			imagesOK = True
		else:
			imagesOK = False
	
		y = 0
		vps = c.video_profile.all()
		for vp in vps:
			vrs = VideoRendition.objects.filter(item=it, video_profile=vp.id)
			for vr in vrs:
				if vr.video_profile == vp and vr.status == "F":
					y = y + 1

		if len(vps) == y and y != 0:
			videosOK = True
		else:
			videosOK = False

		mdl = MetadataLanguage.objects.filter(item_id = it.id, language = c.export_language)
		if len(mdl) == 0:
			metadataOK = False
		else:
			metadataOK = True

		if imagesOK and videosOK and metadataOK:
			customers_for_export.append(c)

	return customers_for_export

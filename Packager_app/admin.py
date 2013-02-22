from django.contrib import admin
from Packager_app.models import *

class CustomMetadataAdmin(admin.ModelAdmin):
	list_display = ('customer', 'name', 'value')

class CustomerAdmin(admin.ModelAdmin):
	list_display = ('name', 'id', 'vod_active')
	fieldsets = [
	    ('General info',    {'fields': ['name','vod_active', 'product_type']}),
	    ('Rental period',   {'fields': ['suggested_price_longform_sd', 'suggested_price_longform_hd', 'suggested_price_shortform_sd', 'suggested_price_shortform_hd', 'billing_id', 'license_window', 'preview_period', 'maximum_viewing_length']}),
	    ('Media and Metadata Profile',   {'fields': ['video_profile', 'image_profile', 'image_type', 'metadata_profile', 'runtype_display', 'license_date_format', 'rating_display', 'viewing_can_be_resumed', 'extended_video_information', 'category_with_spaces', 'category_path_style','titles_in_capital_letter', 'use_hdcontent_var', 'doctype', 'summary_long', 'image_aspect_ratio', 'actor_display', 'limit_content_value', 'id_len_reduced', 'use_genres_category', 'custom_genres']}),
	    ('Exportation rules',    {'fields': ['export_language','export_format', 'export_folder']}), 
	]
	

class ItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'format', 'status')
	fieldsets = [
	    ('General info',	{'fields': ['name', 'status', 'group', 'format']}),
	    ('Rental period',	{'fields': ['kill_date', 'subscriber_view_limit']}),
	    ('Metadata info',	{'fields': ['content_language', 'material_type', 'eidr', 'isan', 'closed_captioning', 'run_time', 'display_run_time', 'year', 'country_of_origin', 'actors', 'actors_display', 'episode_name', 'episode_id', 'category', 'audience', 'show_type', 'rating', 'genres', 'director', 'brand', 'studio', 'studio_name', 'mam_id']}),
	]

class ItemGroupAdmin(admin.ModelAdmin):
        list_display = ('id', 'key',  'name')

class RenditionQueueAdmin(admin.ModelAdmin):
	list_display = ('file_name', 'item', 'queue_status')

class VideoRenditionAdmin(admin.ModelAdmin):
	list_display = ('id', 'file_name', 'item', 'video_profile', 'transcoding_server', 'status')

class ImageRenditionAdmin(admin.ModelAdmin):
	list_display = ('id', 'file_name', 'item', 'image_profile', 'status')

class PackageGroupAdmin(admin.ModelAdmin):
	list_display = ('id', 'name',  'description')

class PackageAdmin(admin.ModelAdmin):
	list_display = ('date_published', 'item', 'customer', 'group', 'status')

class TranscodingServerAdmin(admin.ModelAdmin):
	list_display = ('name', 'ip_address', 'status')

class PathAdmin(admin.ModelAdmin):
	list_display = ('key', 'location', 'description')

class VideoProfileAdmin(admin.ModelAdmin):
	list_display = ('name', 'file_extension', 'status', 'bit_rate', 'format', 'notes')

class ImageProfileAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'file_extension', 'image_aspect_ratio', 'type')

class MetadataProfileAdmin(admin.ModelAdmin):
	list_display = ('key', 'name', 'status', 'description')

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)

class CustomCategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)

class CategoryRelationAdmin(admin.ModelAdmin):
	list_display = ('category', 'custom_category', 'customer')

class MetadataLanguageAdmin(admin.ModelAdmin):
	list_display = ('item', 'title_brief', 'language')

class LanguageAdmin(admin.ModelAdmin):
	list_display = ('name', 'code') 

class CountryAdmin(admin.ModelAdmin):
	list_display = ('country', 'code') 

class RatingAdmin(admin.ModelAdmin):
	list_display = ('name',)


admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomMetadata, CustomMetadataAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemGroup, ItemGroupAdmin)
admin.site.register(RenditionQueue, RenditionQueueAdmin)
admin.site.register(VideoRendition, VideoRenditionAdmin)
admin.site.register(ImageRendition, ImageRenditionAdmin)
admin.site.register(PackageGroup, PackageGroupAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(TranscodingServer, TranscodingServerAdmin)
admin.site.register(Path, PathAdmin)
admin.site.register(VideoProfile, VideoProfileAdmin)
admin.site.register(ImageProfile, ImageProfileAdmin)
admin.site.register(MetadataProfile, MetadataProfileAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CustomCategory, CustomCategoryAdmin)
admin.site.register(CategoryRelation, CategoryRelationAdmin)
admin.site.register(MetadataLanguage, MetadataLanguageAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Country, CountryAdmin)

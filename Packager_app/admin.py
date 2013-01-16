from django.contrib import admin
from Packager_app.models import *

class CustomMetadataAdmin(admin.ModelAdmin):
	list_display = ('customer', 'name', 'value')

class CustomerAdmin(admin.ModelAdmin):
	list_display = ('name', 'id', 'vod_active')

class ItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'format', 'status')

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
	list_display = ('host_name', 'ip_address', 'status')

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
'''
admin.site.register(Customer)
admin.site.register(Item)
admin.site.register(ImportQueue)
admin.site.register(VideoRendition)
admin.site.register(ImageRendition)
admin.site.register(PackageGroup)
admin.site.register(Package)
admin.site.register(TranscodingServer)
admin.site.register(Path)
admin.site.register(Daemon)
admin.site.register(VideoProfile)
admin.site.register(ImageProfile)
admin.site.register(MetadataProfile)
admin.site.register(AppError)
admin.site.register(Category)
admin.site.register(CustomCategory)
admin.site.register(CategoryRelation)
'''

from django.contrib import admin
from Packager_app.models import *

class CustomerAdmin(admin.ModelAdmin):
	list_display = ('name', 'vod_active')

class ItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'format', 'status')

class ImportQueueAdmin(admin.ModelAdmin):
	list_display = ('file_name', 'item', 'queue_status')

class VideoRenditionAdmin(admin.ModelAdmin):
	list_display = ('file_name', 'video_profile', 'transcoding_server', 'status')

class ImageRenditionAdmin(admin.ModelAdmin):
	list_display = ('id', 'file_name', 'image_profile')

class PackageGroupAdmin(admin.ModelAdmin):
	list_display = ('name',)

class PackageAdmin(admin.ModelAdmin):
	list_display = ('date_published', 'item', 'customer')

class TranscodingServerAdmin(admin.ModelAdmin):
	list_display = ('host_name', 'ip_address', 'status')

class PathAdmin(admin.ModelAdmin):
	list_display = ('key', 'location', 'description')

class DaemonAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'last_run')

class VideoProfileAdmin(admin.ModelAdmin):
	list_display = ('name', 'file_extension', 'status', 'bit_rate', 'format', 'notes')

class ImageProfileAdmin(admin.ModelAdmin):
	list_display = ('name', 'description', 'file_extension', 'content_aspect', 'type')

class MetadataProfileAdmin(admin.ModelAdmin):
	list_display = ('key', 'name', 'status', 'description')

class AppErrorAdmin(admin.ModelAdmin):
	list_display = ('key', 'name', 'description')

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)

class CustomCategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)

class CategoryRelationAdmin(admin.ModelAdmin):
	list_display = ('category', 'custom_category', 'customer')

class MetadataLanguageAdmin(admin.ModelAdmin):
	lsit_display = ('language', 'title_brief')

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ImportQueue, ImportQueueAdmin)
admin.site.register(VideoRendition, VideoRenditionAdmin)
admin.site.register(ImageRendition, ImageRenditionAdmin)
admin.site.register(PackageGroup, PackageGroupAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(TranscodingServer, TranscodingServerAdmin)
admin.site.register(Path, PathAdmin)
admin.site.register(Daemon, DaemonAdmin)
admin.site.register(VideoProfile, VideoProfileAdmin)
admin.site.register(ImageProfile, ImageProfileAdmin)
admin.site.register(MetadataProfile, MetadataProfileAdmin)
admin.site.register(AppError, AppErrorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CustomCategory, CustomCategoryAdmin)
admin.site.register(CategoryRelation, CategoryRelationAdmin)
admin.site.register(MetadataLanguage, MetadataLanguageAdmin)
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
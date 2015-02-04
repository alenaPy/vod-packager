#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import logging
import os
import time
from datetime import datetime, timedelta

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Stand alone script
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from django.core.management import setup_environ
from Packager import settings
setup_environ(settings)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Modelo de la aplicacion
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from Packager_app import models

import Settings

def CheckImagenRendition(Item=None, IProfile=None):
    IRlist = models.ImageRendition.objects.filter(item=Item, image_profile=IProfile)
    if len(IRlist) > 0:
	return False
    return True



def MakeImageRenditions(Item):
    print Item
    if Settings.OPTIMIZE_PROFILES_WITH_BRAND:
	IProfileList_pre = models.GetImageProfilesBrand(Item.internal_brand)
	print Item.internal_brand
	print IProfileList_pre
	if Item.internal_brand == 'HD' and Item.format == 'SD':
	    print "MakeImageRenditions(): Internal Brand is HD but Item format is SD -> Eliminate HD Profiles"
	    #
	    # Hay que eliminar los HD
	    #
	    IProfileList = []
	    for IProfile in IProfileList_pre:
		if IProfile.format == 'SD':
		    IProfileList.add(IProfile)
	else:
	    IProfileList = IProfileList_pre	    
    else:
	#
        # Trae la lista de profiles activos
        #
	if Item.format == 'HD':
    	    IProfileList = models.GetImageProfile()
	else:
	    IProfileList = models.GetImageProfile('SD')
    #
    # Por cada image profile debe crear el image rendition
    #
    for IProfile in IProfileList:
	if not CheckImagenRendition(Item, IProfile):
	    print "MakeImagenRendition(): Image Profile exist-> Continue. [IP: %s]" % IProfile.name 
	    continue
	IRendition               = models.ImageRendition()
	IRendition.image_profile = IProfile
	IRendition.item          = Item
	IRendition.status        = 'U'
	print "MakeImageRendition(): Creating Image rendition for Item: " + Item.name + " [IP: " + IProfile.name + "]"
	IRendition.save()

    return True

group = models.ItemGroup.objects.get(id=28)

print group.key
Items = models.Item.objects.filter(group=group)
for item in Items:
    MakeImageRenditions(item)




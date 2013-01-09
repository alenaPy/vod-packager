import xmlrpclib

def ItemMetadata():
    return dict([('name', ''),
		 ('format', ''),
		 ('episode_number', ''),
		 ('rating', ''),
		 ('genre', ''),
		 ('actors', ''),
		 ('origin_country', ''),
		 ('year', ''),
		 ('director', ''),
		 ('studio_name', ''),
		 ('mam_id', '')])


def ItemMetadataLanguage():
    return dict([('language', ''),
		 ('title_sort_name', ''),
		 ('title_brief', ''),
		 ('title', ''),
		 ('episode_tile', ''),
		 ('summary_long', ''),
		 ('summary_medium', ''),
		 ('summary_short', '')])


def VodPackagerAddItem(SmbPath = None, FileName = None, IMetadata = None, IMetadataLanguage = []):
    if FileName is not None and SmbPath is not None and IMetadata is not None:
	s = xmlrpclib.ServerProxy('http://localhost:8000')
	return s.VPAddItem(SmbPath, FileName, IMetadata, IMetadataLanguage)


#I = ItemMetadata()
#I['name'] = 'Putin'

#L = ItemMetadataLanguage()
#L['language'] = 'esp'
#VodPackagerAddItem('\\\\aca\\', 'Gran Trolo.mov', I, [L] )

def main():
	print "Hola!"
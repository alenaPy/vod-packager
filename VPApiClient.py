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


def VpAddItem():
    s = xmlrpclib.ServerProxy('http://localhost:8000')
    print s.system.listMethods()
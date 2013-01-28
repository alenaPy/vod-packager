import xmlrpclib
import ApiSettings


API_VERSION = '1.0.0'

def ItemMetadata():
    return dict([('name', ''),
		 ('format', ''),
		 ('content_language', ''),
		 ('material_type', ''),
		 ('run_time', ''),
		 ('display_runtime', ''),
		 ('episode_name', ''),
		 ('episode_id', ''),
		 ('category', ''),
		 ('show_type', ''),
		 ('rating', ''),
		 ('genres', ''),
		 ('actors', ''),
		 ('country_of_origin', ''),
		 ('year', ''),
		 ('director', ''),
		 ('studio_name', ''),
		 ('group', ''),
		 ('mam_id', '')])


def ItemMetadataLanguage():
    return dict([('language', ''),
		 ('title_sort_name', ''),
		 ('title_brief', ''),
		 ('title', ''),
		 ('episode_title', ''),
		 ('summary_long', ''),
		 ('summary_medium', ''),
		 ('summary_short', '')])


def VodPackagerAddItem(SmbPath = None, FileName = None, IMetadata = None, IMetadataLanguage = []):
    if FileName is not None and SmbPath is not None and IMetadata is not None:
	s = xmlrpclib.ServerProxy('http://'+ ApiSettings.SERVER_HOST + ':' + ApiSettings.SERVER_PORT, allow_none=True)
	ret = s.TestApiVersion(API_VERSION)
	if ret:
	    return s.VPAddItem(SmbPath, FileName, IMetadata, IMetadataLanguage)
	else:
	    return False

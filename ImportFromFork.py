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

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# VPApiClient
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from VPApiClient import ItemMetadata, ItemMetadataLanguage, VodPackagerAddItem

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Others
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import xml.etree.ElementTree as xml
import sys

def main():
	#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	# Archivo XML
	#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	xml_file_path = sys.argv[1]
	video_file_name = sys.argv[2]
	tree = xml.parse(xml_file_path)
	smb_path = ""
	rootElement = tree.getroot()
	#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	# Diccionarios
	#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	I = ItemMetadata()
	for clip in rootElement.getiterator(tag="clip"):
		for child in clip.getchildren():
			if child.text:
				if ("title" == child.tag) and (child.attrib['lang'] == "original"):
					I["name"] = child.text
				elif "format" == child.tag:
					I["format"] = child.text
				elif "episode_number" == child.tag:
					I["episode_number"] = child.text
				elif "genre" == child.tag:
					I["genres"] = child.text
				elif "actors" == child.tag:
					I["actors_display"] = child.text
				elif "origins" == child.tag:
					I["origin_country"] = child.text
				elif "director" == child.tag:
					I["director"] = child.text
				elif "mam_id" == child.tag:
					I["mam_id"] = "NO"	#xxx
				elif "original_language" == child.tag:
					I["content_language"] = child.text
				elif "duration" == child.tag:
					str_duration = child.text
					str_duration = str_duration[:-3]
					I["run_time"] = str_duration
					I["display_runtime"] = str_duration[:-3]
					str_duration = str_duration[:-3]
					str_duration = str_duration[3:]
					duration = int(str_duration)
					if duration > 30:
						I["material_type"] = "LF"
					else:
						I["material_type"] = "SF"
				elif "production_date" == child.tag:
					I["year"] = child.text[-4:]
				elif "origins" == child.tag:
					I["country_of_origin"] = child.text
				elif "material_type" == child.tag:
					for e in tree.iterfind('branch[@lang="original"]'):
						episode_title = e.text
					for e in tree.iter(tag='episode_number'):
						episode_id = e.text
					if child.text == "series":
						I["episode_name"] = episode_title
						I["episode_id"] = episode_id
				elif "category" == child.tag:
					I["category"] = child.text
				elif "producer" == child.tag:
					I["studio"] = child.text
					I["studio_name"] = child.text
				elif "material_type" == child.tag:
					I["show_type"] = child.text
				I["rating"] = "xxx"
					
	print I
	
	#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	# Metadata Language
	#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	L = []
	#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	# Metadata Language: ES
	#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	auxDictES = ItemMetadataLanguage()
	auxDictES['language'] = 'es'
	for e in tree.findall('.//*[@lang="es"]'):
		if "vod_title" == e.tag:
			auxDictES["title_sort_name"] = e.text
			auxDictES["title_brief"] = e.text
			auxDictES["title"] = e.text
		elif "episode_title" == e.tag:
			auxDictES["episode_title"] = e.text
		elif "synopsis" == e.tag:
			if e.attrib['format'] == "short":
				auxDictES["summary_short"] = e.text
			elif e.attrib['format'] == "medium":
				auxDictES["summary_medium"] = e.text
			elif e.attrib['format'] == "long":
				auxDictES["summary_long"] = e.text
	L.append(auxDictES)
	#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	# Metadata Language: EN
	#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	auxDictEN = ItemMetadataLanguage()
	auxDictEN['language'] = 'en'
	for e in tree.findall('.//*[@lang="en"]'):
		if "vod_title" == e.tag:
			auxDictEN["title_sort_name"] = e.text
			auxDictEN["title_brief"] = e.text
			auxDictEN["title"] = e.text
		elif "episode_title" == e.tag:
			auxDictEN["episode_title"] = e.text
		elif "synopsis" == e.tag:
			if e.attrib['format'] == "short":
				auxDictEN["summary_short"] = e.text
			elif e.attrib['format'] == "medium":
				auxDictEN["summary_medium"] = e.text
			elif e.attrib['format'] == "long":
				auxDictEN["summary_long"] = e.text
	L.append(auxDictEN)
	#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	# Metadata Language: PT
	#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	auxDictPT = ItemMetadataLanguage()
	auxDictPT['language'] = 'pt'
	for e in tree.findall('.//*[@lang="pt"]'):
		if "vod_title" == e.tag:
			auxDictPT["title_sort_name"] = e.text
			auxDictPT["title_brief"] = e.text
			auxDictPT["title"] = e.text
		elif "episode_title" == e.tag:
			auxDictPT["episode_title"] = e.text
		elif "synopsis" == e.tag:
			if e.attrib['format'] == "short":
				auxDictPT["summary_short"] = e.text
			elif e.attrib['format'] == "medium":
				auxDictPT["summary_medium"] = e.text
			elif e.attrib['format'] == "long":
				auxDictPT["summary_long"] = e.text
	L.append(auxDictPT)
	
	print L
	
	VodPackagerAddItem(smb_path, xml_file_path, I, L)

main()
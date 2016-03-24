#!/usr/bin/env python
from pymongo import *
import re
import collections
import json
from point_in_polygon_with_shapely import *

key = []
key.append('Photo/video_identifier')
key.append('User_NSID')
key.append('User_nickname')
key.append('Date_taken')
key.append('Date_uploaded')
key.append('Capture_device')
key.append('title')
key.append('Description')
key.append('User_tags')
key.append('Machine_tags')
key.append('Longitude')
key.append('Latitude')
key.append('Accuracy')
key.append('Photo/video_page_URL')
key.append('Photo/video_download_URL')
key.append('License_name')
key.append('License_URL')
key.append('Photo/video_server_identifier')
key.append('Photo/video_farm_identifier')
key.append('Photo/video_secret')
key.append('Photo/video_secret_original')
key.append('Photo/video_extension_original')
key.append('Photos/video_Smarker')
key.append('Country')

def InsertDataToMongodbFromDataset():
	bbox_dict =	Get_area_list()

	print 'Linking to MongoDB...'
	client = MongoClient('localhost', 27017)
	db = client['YFCC100M']
	collection_with_geo_tag_and_user_tag = db['dataset_with_geo_tag']
	collection_without_geo_tag_and_user_tag = db['dataset_without_geo_tag']

	print 'Reading YFCC100M dataset and Writing documents to MongoDB...'
	for dataset_num in xrange(0,10):
		dataset_name = "../data/yfcc100m_dataset-%d" % dataset_num
		dataset = open(dataset_name)
		line_num = 1;
		line = dataset.readline()

		while line:
			user_tag = False
			geo_tag = False

			doc = collections.OrderedDict()
			value = line.split('\t')
			value.append('')
			# split user tages
			if value[8] != '':
				value[8] = value[8].split(',')
				user_tag = True
			# split machine tags
			if value[9] != '':
				value[9] = value[9].split(',')
			# reverse geocode
			if (value[10] != '') & (value[11] != ''):
				lon = value[10] = float(value[10])
				lat = value[11] = float(value[11])

				area_name = point_in_polygon_with_shapely(bbox_dict, lon, lat)
				if area_name != None:
					value[23] = area_name
					geo_tag = True

			if user_tag & geo_tag:
				for i in range(0, 24):
					doc[key[i]] = value[i]
				collection_with_geo_tag_and_user_tag.insert(doc)
			else:
				for i in range(0, 24):
					doc[key[i]] = value[i]
				collection_without_geo_tag_and_user_tag.insert(doc)

			print " Line : %d in dataset : %d is inserted." % (line_num, dataset_num)
			line_num = line_num + 1
			line = dataset.readline()

		dataset.close()
	print "Data insert mission compeleted!"
	print "Creating descending index on User_tags in collection_with_geo_tag_and_user_tag..."
	collection_with_geo_tag_and_user_tag.creat_index([('User_tags', 1)])
	print "Creating descending index on Country in collection_with_geo_tag_and_user_tag..."
	collection_with_geo_tag_and_user_tag.creat_index([('Country', 1)])
	print collection_with_geo_tag_and_user_tag.index_information()

	return

if __name__ == "__main__": 
	InsertDataToMongodbFromDataset()
	pass
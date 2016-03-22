#!/usr/bin/env python
'''
request Google maps API and get country's bounding box with lng. & lat.
'''

import urllib2
import json
import time

def GetBbox():
	country_file = open('country')
	country_with_bbox_file = open('country_with_bbox','w')

	url = 'https://maps.googleapis.com/maps/api/geocode/json?'
	address = 'address='
	key = '&key=AIzaSyAv5MP0JyVLrjqC_7hoQ_3hA-xE6ZNsPQw'

	line = country_file.readline()
	line_num = 1
	print line_num,

	while line:
		s = line.split('\"')
		country =  "".join(s[1].split(' ')) #remove 'space'
		
		#print url+address+country+key
		
		response = urllib2.urlopen(url+address+country+key)
		data = json.loads(response.read())
		if data['status'] != 'OK':
			print country
			line = country_file.readline()
			line_num += 1
			print line_num,
			continue

		print country,
		lat_max = data['results'][0]['geometry']['bounds']['northeast']['lat']
		lng_max = data['results'][0]['geometry']['bounds']['northeast']['lng']
		lat_min = data['results'][0]['geometry']['bounds']['southwest']['lat']
		lng_min = data['results'][0]['geometry']['bounds']['southwest']['lng']
		if lat_max < lat_min:
			temp = lat_max
			lat_max = lat_min
			lat_min = temp
		if lng_max < lng_min:
			temp = lng_max
			lng_max = lng_min
			lng_min = lng_max
		print lat_max,lat_min,lng_max,lng_min

		country_dict = {
			s[1]:{
				"lat":{
				"min":lat_min,
				"max":lat_max
				},
				"lng":{
				"min":lng_min,
				"max":lng_max
				}
			}
		}
		country_with_bbox_file.write(json.dumps(country_dict)+'\n')
		#return
		line = country_file.readline()
		line_num += 1
		print line_num,

	country_file.close()
	country_with_bbox_file.close()

if __name__ == "__main__":
	GetBbox()
	pass
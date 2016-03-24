#!/usr/bin/env python
# coding:utf-8

import json
from shapely.geometry import asShape, Point


class Area:
	def __init__():
		self.name = ''
		self.boundary = None	
		self.next_level_list = []
	def __init__(self, name, boundary, next_level_list):
		self.name = name
		self.boundary = boundary	
		self.next_level_list = next_level_list

	
def Get_area_list():
	print "Reading OSM data(admin_level=country) and Creating list of countries..."

	area_list = []
	bbox_dict = {}

	with open('admin_level_2.geojson') as json_f:
		f = json.load(json_f)

	error_count = 0

	for feature in f['features']:
		try:
			polygon = asShape(feature["geometry"])
		except KeyError, e:
			error_count += 1
			continue
		try:
			if feature['osm_type'] == "relation":
				admin_area = Area(feature['properties']['name:en'], polygon, [])
				area_list.append(admin_area)

		except KeyError, e:
			error_count += 1

	for area in area_list:
		bbox_dict[area.boundary.bounds] = area

	print "List of countrys'boundary has been created."
	return bbox_dict

def point_in_polygon_with_shapely(bbox_dict, lon, lat):
	point = Point(lon, lat)
	candidate_area_list = []

	for bounds, area in bbox_dict.iteritems():
		if  (lon >= bounds[0]) & (lon <= bounds[2]) & (lat >= bounds[1]) & (lat <= bounds[3]):
			candidate_area_list.append(area)

	for area in candidate_area_list:
		# contains() or crosses() or equals() or touches() or within()
		if area.boundary.intersects(point):
			return area.name
	return None

if __name__ == '__main__':
	bbox_dict = Get_area_list()

	while True:
		lon = input("Input longitude:")
		lat = input('Input latitude:')
		
		print point_in_polygon_with_shapely(bbox_dict, lon, lat)

	'''
	point_in_polygon_with_shapely(bbox_dict, 116.3579936, 39.9587666)  # china
	point_in_polygon_with_shapely(bbox_dict, -87.3857493, 12.8596198)  # nicaragua
	point_in_polygon_with_shapely(bbox_dict, 10.4234469, 51.0834196)  # germany
	point_in_polygon_with_shapely(bbox_dict, -4.0239568, 39.8560679)  # spain
	point_in_polygon_with_shapely(bbox_dict, -2.2900239, 16.3700359)  # mali
	point_in_polygon_with_shapely(bbox_dict, 2.3514992, 48.8566101)  # france
	point_in_polygon_with_shapely(bbox_dict, -73.9865812, 40.7305991)  #United State of America
	'''
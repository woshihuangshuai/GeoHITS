#!/usr/bin/env python
'''
    GeoHITS with tag frequency
'''

from pymongo import MongoClient
import numpy as np
from prettytable import PrettyTable
import os
from point_in_polygon_with_shapely import *


def SearchByKeyword(keyword):
    print '=>Search by keyword: %s' % keyword
    client = MongoClient('localhost', 27017)
    db = client['YFCC100M']
    collection = db['dataset_with_tag']

    query = {'$and':[
                {'User_tags':{'$in':[keyword]}}, 
                {'Longitude':{'$ne':''}},
                {'Latitude':{'$ne':''}}
            ]}

    fields = {}
    fields['User_tags'] = True
    fields['Longitude'] = True
    fields['Latitude'] = True

    cursor = collection.find(query, fields)

    print "There is %d documents about %s."%(cursor.count(), keyword)
    print

    print '=>Run point_in_polygon...' 
    bbox_dict = Get_area_list()

    user_tags_list = []
    locations_list = []

    for doc in cursor:
        lon = doc['Longitude']
        lat = doc['Latitude']
        user_tags = doc['User_tags']

        country = point_in_polygon_with_shapely(bbox_dict, lon, lat)

        if country != None:
            user_tags_list.append(user_tags)
            locations_list.append(country)

    return user_tags_list, locations_list


def DataProcess(user_tags_list, locations_list):
    print '=>Do data process...'

    if os.path.exists('GeoHITS_tf result') == False:
        os.mkdir('GeoHITS_tf result')

    #list of locations' and tags'name 
    locations = []
    tags = []

    #represent locations in 2-D matrix
    #len(matrix_locations) = len(locations),len(matrix_locations[j]) = len(tags)
    #if location_i contains tag_j,locations[j] = 1;else locations[j] = 0
    matrix_locations = []

    print '=>Creat locations-tags matrix...'
    for i in xrange(0, len(locations_list)):
        user_tags = user_tags_list[i]
        country = locations_list[i]

        if country not in locations:
            locations.append(country)

        for tag in user_tags:
            if tag not in tags:
                tags.append(tag)

    for i in xrange(0, len(locations)):
        location = []
        for j in xrange(0,len(tags)):
            location.append(0.0)

        matrix_locations.append(location)

    tags_of_each_location = []
    for i in xrange(0, len(locations)):
        tags_of_each_location.append([])

    for i in xrange(0, len(locations_list)):
        user_tags = user_tags_list[i]
        country = locations_list[i]

        for tag in user_tags:
            if tag not in tags_of_each_location[locations.index(country)]:
                tags_of_each_location[locations.index(country)].append(tag)

        for tag in user_tags:
                matrix_locations[locations.index(country)][tags.index(tag)] += 1.0    # tag frequency
   
    # if the number of locations contain tag_i <2,remove tag_i
    del_items = []
    for i in xrange(0, len(tags)):
        locations_contain_tag_i = 0
        for arr in matrix_locations:
            if arr[i] != 0:
                locations_contain_tag_i += 1
        if locations_contain_tag_i < 2:  # threshold
            del_items.append(i)
 
    index_drift = 0
    for i in del_items:
        del tags[i-index_drift]
        for arr in matrix_locations:
            del arr[i-index_drift]
        index_drift += 1

    '''
    print len(locations),len(tags)
    print len(locations) == len(matrix_locations)
    print len(tags) == len(matrix_locations[len(locations)-1])
    '''

    print '=>print GeoHITS_tf result and write GeoHITS_tf result to file...'
    num_list_of_each_location_contains_tags = []
    num_list_of_each_tag_occur_in_locations = []

    for i in xrange(0, len(tags)):
        num_of_each_tag_occur_in_locations = 0
        for tags_of_location in matrix_locations:
            if tags_of_location[i] != 0:
                num_of_each_tag_occur_in_locations += 1

        num_list_of_each_tag_occur_in_locations.append(num_of_each_tag_occur_in_locations)

    for tags_of_location in matrix_locations:
        num_of_location_contains_tags = 0
        for tag in tags_of_location:
            if tag != 0:
                num_of_location_contains_tags += 1

        num_list_of_each_location_contains_tags.append(num_of_location_contains_tags)

    print "<<TABLE OF EACH LOCATION CONTAINS TAGS>>"
    t = PrettyTable(["Location", 'Number','Occurrence number'])

    for i in xrange(0, len(locations)):
        t.add_row([locations[i], 
            num_list_of_each_location_contains_tags[i], 
            locations_list.count(locations[i])])

    t.sortby = "Number"
    t.reversesort = True
    print t
    print 'Total of locations: ', len(locations)

    f = open("GeoHITS_tf result/%s_TABLE_OF_EACH_LOCATION_CONTAINS_TAGS" % keyword,'w+')
    f.write(t.get_string())
    f.write('\n')
    f.write('Total of locations: %s' % len(locations))
    f.close()

    print '<<TABLE OF EACH TAG OCCURS IN LOCATIONS>>'
    t = PrettyTable(['Tags', 'Number'])

    for i in xrange(0, len(tags)):
        t.add_row([tags[i],num_list_of_each_tag_occur_in_locations[i]])

    t.sortby = "Number"
    t.reversesort = True
    print t
    print 'Total of tags: ', len(tags)

    f = open("GeoHITS_tf result/%s_TABLE_OF_EACH_TAG_OCCURS_IN_LOCATIONS" % keyword,'w+')
    f.write(t.get_string())
    f.write('\n')
    f.write('Total of tags: %s' % len(tags))
    f.close()
    # --------------print over---------------------

    print '=>Calcalate Tag frequency for each tag in each location...'
    matrix_locations_tf = matrix_locations[:]

    for i in xrange(0, len(locations)):
        denominator = max(matrix_locations_tf[i])
        for j in xrange(0, len(tags)):
            numerator = matrix_locations_tf[i][j]
            matrix_locations_tf[i][j] = numerator / denominator
           
    return locations, tags, matrix_locations, matrix_locations_tf


def GeoHITS(locations, tags, matrix_locations, matrix_locations_tf):
    print '=>Runing GeoHITS with tag similarity...'

    locations_mat = np.mat(np.ones([1, len(locations)]), dtype='float64')
    tags_mat = np.mat(np.ones([1, len(tags)]), dtype='float64')
    adjacency_mat = np.mat(matrix_locations, dtype='float64')
    adjacency_mat_tf = np.mat(matrix_locations_tf, dtype='float64')

    last_locations_mat = locations_mat

    v = 10e-15  # threshold
    k = 0  # num of iterations

    while (k==0) or (np.linalg.norm(last_locations_mat-locations_mat) >= v):
        if k == 0:
            last_locations_mat = locations_mat/np.linalg.norm(locations_mat)
        else:
            last_locations_mat = locations_mat

        tags_mat = locations_mat*adjacency_mat_tf
        locations_mat = tags_mat*adjacency_mat_tf.T

        #normalize
        tags_mat = tags_mat/np.linalg.norm(tags_mat)
        locations_mat = locations_mat/np.linalg.norm(locations_mat)

        k += 1
        
    return locations_mat.tolist()[0], k


def Printresult(rank_list, k):
    print "=>Print rank GeoHITS_tf result and log to file..."
    if os.path.exists('GeoHITS_tf result') == False:
        os.mkdir('GeoHITS_tf result')

    print '<<TABLE OF RANK GeoHITS_tf result>>'
    t = PrettyTable(['Location', 'Value'])
    for i in xrange(0, len(locations)): 
    # for i in xrange(0, 10):  # print top-10 countries
        t.add_row([locations[i], rank_list[i]])
    t.sortby = "Value"
    t.reversesort = True
    print t
    print "Number of iterations = ",k

    f = open("GeoHITS_tf result/%s_TABLE_OF_RANK_RESULT" % keyword,'w+')
    f.write(t.get_string())
    f.write('\n')
    f.write("Number of iterations = %s" % k)
    f.close()
    print '*'*20, 'OVER', '*'*20


if __name__ == '__main__':
    print '*'*55
    keyword = raw_input("=>Please input keyword:\t")
    print

    user_tags_list, locations_list = SearchByKeyword(keyword)
    locations, tags, matrix_locations, matrix_locations_tf = DataProcess(user_tags_list, locations_list)
    rank_list, k = GeoHITS(locations, tags, matrix_locations, matrix_locations_tf)
    Printresult(rank_list, k)
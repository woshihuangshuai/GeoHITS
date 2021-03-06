#!/usr/bin/env python
'''
    GeoHITS with tag frequency
'''

import os

import numpy as np
from pymongo import MongoClient

from point_in_polygon_with_shapely import *
from prettytable import PrettyTable
from progressive.bar import Bar


def SearchByKeyword(keyword):
    print '=>Search by keyword: %s' % keyword
    client = MongoClient('localhost', 27017)
    db = client['YFCC100M']
    collection = db['dataset_with_tag']

    query = {'$and': [
        {'User_tags': {'$in': [keyword]}},
        {'Longitude': {'$ne': ''}},
        {'Latitude': {'$ne': ''}}
    ]}

    fields = {}
    fields['User_tags'] = True
    fields['Longitude'] = True
    fields['Latitude'] = True

    cursor = collection.find(query, fields)

    total = cursor.count()
    print "There is %d documents about %s." % (total, keyword)
    print
    print '=>Runing point_in_polygon:'

    bbox_dict = Get_area_list()
    print
    user_tags_list = []
    locations_list = []

    now = 0  # progress
    bar = Bar(max_value=total)
    bar.cursor.clear_lines(2)
    bar.cursor.save()

    for doc in cursor:
        lon = doc['Longitude']
        lat = doc['Latitude']
        user_tags = doc['User_tags']

        country = point_in_polygon_with_shapely(bbox_dict, lon, lat)
        now += 1
        bar.cursor.restore()
        bar.draw(value=now)

        if country != None:
            user_tags_list.append(user_tags)
            locations_list.append(country)

    return user_tags_list, locations_list


def DataProcess(user_tags_list, locations_list):
    print '=>Doing data process:'

    if os.path.exists('GeoHITS_tf result') == False:
        os.mkdir('GeoHITS_tf result')

    # list of locations' and tags'name
    locations = []
    tags = []

    # represent locations in 2-D matrix
    # len(matrix_locations) = len(locations),len(matrix_locations[j]) = len(tags)
    # if location_i contains tag_j,locations[j] = 1;else locations[j] = 0
    matrix_locations = []

    print 'Creat list of locations and tags...'
    for i in xrange(0, len(locations_list)):
        user_tags = user_tags_list[i]
        country = locations_list[i]

        if country not in locations:
            locations.append(country)

        for tag in user_tags:
            if tag not in tags:
                tags.append(tag)

    print 'Creat locations-tags matrix...'
    for i in xrange(0, len(locations)):
        location = []
        for j in xrange(0, len(tags)):
            location.append(0.0)

        matrix_locations.append(location)

    for i in xrange(0, len(locations_list)):
        user_tags = user_tags_list[i]
        country = locations_list[i]

        for tag in user_tags:
            matrix_locations[locations.index(country)][
                tags.index(tag)] += 1.0    # tag frequency

    print 'Get common tag...'
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
        del tags[i - index_drift]
        for arr in matrix_locations:
            del arr[i - index_drift]
        index_drift += 1

    print 'print GeoHITS_tf result and write GeoHITS_tf result to file...'
    list_of_num_of_locations_contains_each_tag = []
    list_of_num_of_tags_belong_to_each_location = []
    list_of_num_of_each_tags_occurrence = []

    for i in xrange(0, len(tags)):
        num_of_locations_contains_tag_i = 0
        num_of_tags_i_occurrence = 0
        for tags_of_location in matrix_locations:
            if tags_of_location[i] != 0:
                num_of_locations_contains_tag_i += 1
                num_of_tags_i_occurrence += tags_of_location[i]
        list_of_num_of_locations_contains_each_tag.append(
            num_of_locations_contains_tag_i)
        list_of_num_of_each_tags_occurrence.append(num_of_tags_i_occurrence)

    for tags_of_location in matrix_locations:
        num_of_tags_belong_to_location_i = 0
        for tag in tags_of_location:
            if tag != 0:
                num_of_tags_belong_to_location_i += 1
        list_of_num_of_tags_belong_to_each_location.append(
            num_of_tags_belong_to_location_i)

    print "<<TABLE OF EACH LOCATION CONTAINS TAGS>>"
    t = PrettyTable(["Location", 'Number of tags', 'Number of Occurrence'])

    for i in xrange(0, len(locations)):
        t.add_row([locations[i],
                   list_of_num_of_tags_belong_to_each_location[i],
                   locations_list.count(locations[i])])

    t.sortby = "Number of tags"
    t.reversesort = True
    print t
    print 'Total of locations: ', len(locations)

    f = open("GeoHITS_tf result/%s_TABLE_OF_EACH_LOCATION_CONTAINS_TAGS" %
             keyword, 'w+')
    f.write(t.get_string())
    f.write('\n')
    f.write('Total of locations: %s' % len(locations))
    f.close()

    print '<<TABLE OF EACH TAG OCCURS IN LOCATIONS>>'
    t = PrettyTable(['Tags', 'Number of locations', 'Number of Occurrence'])

    for i in xrange(0, len(tags)):
        t.add_row([tags[i],
                   list_of_num_of_locations_contains_each_tag[i],
                   list_of_num_of_each_tags_occurrence[i]])

    t.sortby = "Number of locations"
    t.reversesort = True
    print t
    print 'Total of tags: ', len(tags)

    f = open("GeoHITS_tf result/%s_TABLE_OF_EACH_TAG_OCCURS_IN_LOCATIONS" %
             keyword, 'w+')
    f.write(t.get_string())
    f.write('\n')
    f.write('Total of tags: %s' % len(tags))
    f.close()
    # --------------print over---------------------

    print 'Calcalate Tag frequency for each tag in each location...'
    matrix_locations_tf = matrix_locations[:]
    '''
    for i in xrange(0, len(locations)):
        max_i = max(matrix_locations_tf[i])
        for j in xrange(0, len(tags)):
            matrix_locations_tf[i][j] = matrix_locations_tf[i][j] / max_i

    '''
    max_of_each_tags_occurrence = []
    for i in xrange(0, len(tags)):
        max = 0
        for j in xrange(0, len(locations)):
            if matrix_locations_tf[j][i] > max:
                max = matrix_locations_tf[j][i]

        max_of_each_tags_occurrence.append(max)

    for i in xrange(0, len(tags)):
        for j in xrange(0, len(locations)):
            matrix_locations_tf[j][i] = matrix_locations_tf[
                j][i] / max_of_each_tags_occurrence[i]
            #matrix_locations_tf[j][i] = matrix_locations_tf[j][i] * list_of_num_of_locations_contains_each_tag[i]

    return locations, tags, matrix_locations, matrix_locations_tf


def GeoHITS(locations, tags, matrix_locations, matrix_locations_tf):
    locations_mat = np.mat(np.ones([1, len(locations)]), dtype='float64')
    tags_mat = np.mat(np.ones([1, len(tags)]), dtype='float64')

    adjacency_mat = np.mat(matrix_locations, dtype='float64')
    adjacency_mat_tf = np.mat(matrix_locations_tf, dtype='float64')

    last_locations_mat = locations_mat

    v = 10e-8  # threshold
    k = 0  # num of iterations
    print '=>Runing GeoHITS with tag frequency, threshold = %d' % v

    while (k == 0) or (np.linalg.norm(last_locations_mat - locations_mat) >= v):
        if k == 0:
            last_locations_mat = locations_mat / np.linalg.norm(locations_mat)
        else:
            last_locations_mat = locations_mat

        print 'Number of iterations: %d' % k

        tags_mat = locations_mat * adjacency_mat_tf
        locations_mat = tags_mat * adjacency_mat_tf.T

        # normalize
        tags_mat = tags_mat / np.linalg.norm(tags_mat)
        locations_mat = locations_mat / np.linalg.norm(locations_mat)

        k += 1

    return locations_mat.tolist()[0], k


def Printresult(locations, rank_list, k):
    print "=>Print rank GeoHITS_tf result and log to file..."

    if os.path.exists('GeoHITS_tf result') == False:
        os.mkdir('GeoHITS_tf result')

    print '<<TABLE OF RANK GeoHITS_tf result>>'
    t = PrettyTable(['Location', 'Value'])
    for i in xrange(0, len(locations)):
        t.add_row([locations[i], rank_list[i]])

    t.sortby = "Value"
    t.reversesort = True
    print t
    print "Number of iterations = ", k

    f = open("GeoHITS_tf result/%s_TABLE_OF_RANK_RESULT" % keyword, 'w+')
    f.write(t.get_string())
    f.write('\n')
    f.write("Number of iterations = %s" % k)
    f.close()

    print '*' * 20, 'OVER', '*' * 20


if __name__ == '__main__':
    print '*' * 55
    keyword = raw_input("=>Please input keyword: ")
    print

    user_tags_list, locations_list = SearchByKeyword(keyword)
    locations, tags, matrix_locations, matrix_locations_tf \
        = DataProcess(user_tags_list, locations_list)
    rank_list, k = GeoHITS(
        locations, tags, matrix_locations, matrix_locations_tf)
    Printresult(locations, rank_list, k)

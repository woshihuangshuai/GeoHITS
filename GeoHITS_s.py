#!/usr/bin/env python
'''
    GeoHITS with tag similarity
'''

from pymongo import MongoClient
import numpy as np
from prettytable import PrettyTable
import os

def SearchByKeyword(keyword):
    print '*'*19, 'SEARCH BY KEYWORD', '*'*19
    client = MongoClient('localhost', 27017)
    db = client['YFCC100M']
    collection = db['dataset_with_tag']

    query = {'$and':[
                {'User_tags':{'$in':[keyword]}}, 
                {'Country':{'$ne':""}}
            ]}

    fields = {}
    fields['User_tags'] = True
    fields['Country'] = True

    cursor = collection.find(query, fields)
    print "There is %d documents about %s."%(cursor.count(), keyword)
    print
    return cursor


def DataProcess(cursor):
    if os.path.exists('result') == False:
        os.mkdir('result')
    #list of locations' and tags'name 
    locations = []
    tags = []

    #represent locations in 2-D matrix
    #len(matrix_locations) = len(locations),len(matrix_location[j]) = len(tags)
    #if location_i contains tag_j,locations[j] = 1;else locations[j] = 0
    matrix_locations = []

    for doc in cursor:
        user_tags = doc['User_tags']
        country = doc['Country']

        if country not in locations:
            locations.append(country)

        for tag in user_tags:
            if tag not in tags:
                tags.append(tag)

    for i in xrange(0,len(locations)):
        location = []
        for j in xrange(0,len(tags)):
            location.append(0.0)
        matrix_locations.append(location)

    '''
    print len(locations),len(tags)
    print len(locations) == len(matrix_locations)
    print len(tags) == len(matrix_locations[len(locations)-1])
    '''

    cursor.rewind()       # reset cursor

    for doc in cursor:
        user_tags = doc['User_tags']
        country = doc['Country']

        for i in xrange(0, len(tags)-1):
            if tags[i] in user_tags:
                matrix_locations[locations.index(country)][i] = 1.0
                # matrix_locations[locations.index(country)][i] += 1.0  # tag frequency

    # if locations contain tag_i <2,remove tag_i
    del_items = []
    for i in xrange(0, len(tags)):
        locations_contain_tag_i = 0
        for j in xrange(0, len(locations)):
            locations_contain_tag_i += matrix_locations[j][i]
        if locations_contain_tag_i < 5:  # threshold
            del_items.append(i)
 
    index_drift = 0
    for i in del_items:
        del tags[i-index_drift]
        for j in xrange(0, len(locations)):
            del matrix_locations[j][i-index_drift]
        index_drift += 1

    num_list_of_each_location_contains_tags = []
    num_list_of_each_tag_occur_in_locations = []
    for i in xrange(0, len(tags)):
        num_of_each_tag_occur_in_locations = 0.0
        for j in matrix_locations:
            num_of_each_tag_occur_in_locations += j[i]
        num_list_of_each_tag_occur_in_locations.append(num_of_each_tag_occur_in_locations)
    for j in matrix_locations:
        num_list_of_each_location_contains_tags.append(sum(j))

    #print result and write result to file
    print '*'*10, "TABLE OF EACH LOCATION CONTAINS TAGS", '*'*10
    t = PrettyTable(["Location", 'Number'])
    for i in xrange(0, len(locations)):
        t.add_row([locations[i], num_list_of_each_location_contains_tags[i]])
    t.sortby = "Number"
    t.reversesort = True
    print t
    print 'Total of locations: ', len(locations)

    f = open("result/%s_TABLE_OF_EACH_LOCATION_CONTAINS_TAGS" % keyword,'w+')
    f.write(t.get_string())
    f.write('\n')
    f.write('Total of locations: %s' % len(locations))
    f.close()

    print '*'*10, 'TABLE OF EACH TAG OCCURS IN LOCATIONS', '*'*10
    t = PrettyTable(['Tags', 'Number'])
    for i in xrange(0, len(tags)):
    	t.add_row([tags[i],num_list_of_each_tag_occur_in_locations[i]])
    t.sortby = "Number"
    t.reversesort = True
    print t
    print 'Total of tags: ', len(tags)
    f = open("result/%s_TABLE_OF_EACH_TAG_OCCURS_IN_LOCATIONS" % keyword,'w+')
    f.write(t.get_string())
    f.write('\n')
    f.write('Total of tags: %s' % len(tags))
    f.close()

    return locations, tags, matrix_locations

def GeoHITS(locations, tags, matrix_locations):
    # -----------------GeoHITS------------------
    locations_mat = np.mat(np.ones([1, len(locations)]), dtype='float64')
    tags_mat = np.mat(np.ones([1, len(tags)]), dtype='float64')
    adjacency_mat = np.mat(matrix_locations, dtype='float64')

    last_locations_mat = locations_mat

    v = 10e-8  # threshold
    k = 0  # num of iterations

    while (k==0) or (np.linalg.norm(last_locations_mat-locations_mat) >= v):
        if k == 0:
            last_locations_mat = locations_mat/np.linalg.norm(locations_mat)
        else:
            last_locations_mat = locations_mat

        locations_mat = tags_mat*adjacency_mat.T
        tags_mat = locations_mat*adjacency_mat

        #normalize
        tags_mat = tags_mat/np.linalg.norm(tags_mat)
        locations_mat = locations_mat/np.linalg.norm(locations_mat)

        k += 1
    return locations_mat.tolist(), k


def PrintResult(rank_list, k):
    if os.path.exists('result') == False:
        os.mkdir('result')
    print '*'*10, 'TABLE OF RANK RESULT', '*'*10
    t = PrettyTable(['Location', 'Value'])
    for i in xrange(0, len(locations)):
        t.add_row([locations[i], rank_list[0][i]])

    t.sortby = "Value"
    t.reversesort = True
    print t
    print "Number of iterations = ",k

    f = open("result/%s_TABLE_OF_RANK_RESULT" % keyword,'w+')
    f.write(t.get_string())
    f.write('\n')
    f.write("Number of iterations = %s" % k)
    f.close()
    print '*'*20, 'OVER', '*'*20


if __name__ == '__main__':
    print '*'*55
    keyword = raw_input("Please input keyword:\t")
    print
    cursor = SearchByKeyword(keyword)
    locations, tags, matrix_locations = DataProcess(cursor)
    rank_list, k = GeoHITS(locations, tags, matrix_locations)
    PrintResult(rank_list, k)
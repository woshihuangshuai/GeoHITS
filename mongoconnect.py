#!/usr/bin/env python
from pymongo import MongoClient
import re
client = MongoClient('localhost',27017)
db = client['test']
collection = db['dataset-1']

item = {"text" : "Hello Mongo!"}
collection.insert(item)
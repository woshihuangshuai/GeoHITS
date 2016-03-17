#!/usr/bin/env python
import re
file1 = open("yfcc100m_dataset-0")
line = file1.readline()
items = line.split("\t")
for  item in items:
	print item
print len(items)

AIzaSyAv5MP0JyVLrjqC_7hoQ_3hA-xE6ZNsPQw
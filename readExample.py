#!/opt/local/bin/python
#-*- coding: utf-8 -*-

import json
import io

data = []
input_file  = file("example", "r")
for line in input_file:
	data.append(json.loads(line))

print "Topic id: %s" %(data[0]['tid'])
print "Name: %s" %(data[0]['name'])
print "Author: %s" %(data[0]['author'])
print "Story: %s" %(data[0]['story'])
print "AllEmo: %s" %(data[0]['emotions'])
print "Like: %s" %(data[0]['emotions']['like'])
print "TagList: %s" %(data[0]['tagList'])
print "First Tag: %s" %(data[0]['tagList'][0])
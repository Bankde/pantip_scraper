#!/opt/local/bin/python
#-*- coding: utf-8 -*-

# Created by DarkDrag0nite

###################
# Another Example #
###################

import json
import io

data = []
input_file  = file("pantip_storage/ptopic35100", "r")
for line in input_file:
	data.append(json.loads(line))

for line in data:
	print "Topic id: %s" %(line['tid'])
	print "Name: %s" %(line['name'])
	print "Author: %s" %(line['author'])
	print "LikeCount: %s" %(line['likeCount'])
	print "CommentCount: %s" %(line['commentCount'])
	print "Emotions: "
	for emo in line['emotions']:
		print "\t" + emo + ": " + line['emotions'][emo]
	print "Tag-items: " ,
	for tag in line['tagList']:
		print tag + " ",
	print ""
	print "Date: %s" %(line['dateTime'])
	print ""
	print ""
#!/opt/local/bin/python
#-*- coding: utf-8 -*-

# Created by DarkDrag0nite

###################
# Another Example #
###################

import json
import io

data = []
input_file  = file("example_result", "r")
for line in input_file:
	data.append(json.loads(line))

line = data[2]
print "Comment 103 message: %s" %(line['comments'][102])
import json
import io

data = []
input_file  = file("ptopic34940", "r")
for line in input_file:
	data.append(json.loads(line))

print "Name: %s" %(data[0]['name'])
print "Author: %s" %(data[0]['author'])
print "Story: %s" %(data[0]['story'])
print "Like: %s" %(data[0]['emotions']['like'])
import json
import io

data = []
input_file  = file("ptopic33924", "r")
for line in input_file:
	data.append(json.loads(line))

print data[0]['story']
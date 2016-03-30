#!/opt/local/bin/python

# Created by DarkDrag0nite


class FullGraph:

	def __init__(self):
		self.nodeList = []
		self.edgeWeight = {}
		self.frequencyList = []

	def addNode(self, newNode):
		if newNode not in self.nodeList:
			self.nodeList.append(newNode)
			self.frequencyList.append(0)
			index = 0
			newNodeIndex = len(self.nodeList) - 1
			for node in self.nodeList:
				if index != newNodeIndex:
					key = str(index) + "-" + str(newNodeIndex)
					self.edgeWeight[key] = 0
				index += 1
			return 1
		else:
			# already exists
			ind = self.nodeList.index(newNode)
			self.frequencyList[ind] += 1
			return 0

	def incWeight(self, node1, node2):
		self.addWeight(node1, node2, 1)

	def addWeight(self, node1, node2, weight):
		if node1 == node2:
			return "Error: you can't have connection in same node"
		if node1 in self.nodeList and node2 in self.nodeList:
			node1Index = self.nodeList.index(node1)
			node2Index = self.nodeList.index(node2)
			key = str(min(node1Index, node2Index)) + "-" + str(max(node1Index, node2Index))
			self.edgeWeight[key] += 1
		else:
			return "Error: input nodes not in graph"

	def getWeight(self, node1, node2):
		if node1 == node2:
			return -1
		if node1 in self.nodeList and node2 in self.nodeList:
			node1Index = self.nodeList.index(node1)
			node2Index = self.nodeList.index(node2)
			key = str(min(node1Index, node2Index)) + "-" + str(max(node1Index, node2Index))
			return self.edgeWeight[key]
		else:
			return -1

	def getAllNodes(self):
		return self.nodeList

	def getAllEdges(self):
		return self.edgeWeight

	def getNodeKey(self, node):
		return self.nodeList.index(node);

	def getEdgeKey(self, node1, node2):
		if node1 == node2:
			return "Error: you can't have edge in same node"
		if node1 in self.nodeList and node2 in self.nodeList:
			node1Index = self.nodeList.index(node1)
			node2Index = self.nodeList.index(node2)
			key = str(min(node1Index, node2Index)) + "-" + str(max(node1Index, node2Index))
			return key
		else:
			return "Error: input nodes not in graph"

	def saveGraph(self, path='GraphFile.txt'):
		import os, json, codecs
		fpath = path
		data = self.edgeWeight.copy()
		data['__nodeList__'] = self.nodeList	
		data['__frequencyList__'] = self.frequencyList		
		json.dump(data, open(path, 'w'), ensure_ascii=False)		
		print('Saved FullGraph to:' + path)

	def loadGraph(self,  path='GraphFile.txt'):
		import json, sys	
		data = json.load(open(path, 'r'))
		self.nodeList = data['__nodeList__']
		self.frequencyList = data['__frequencyList__']
		data.pop('__nodeList__', None)
		self.edgeWeight = data
		MBFACTOR = float(1<<20)
		print "Loaded FullGraph from: %s (%sMB)" % (path,  "{0:.2f}".format(sys.getsizeof(data)/MBFACTOR))		
		count = 0
		print data
		# for item in self.nodeList:
		# 	print item.decode('utf-8')
		# for key,value in data:
		# 	count += 1
		# 	if count > 10:
		# 		break
		# 	print key + ':' + value

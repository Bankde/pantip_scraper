import numpy as np

# run pantip_make_graph.py: PantipGraph.create_ptag_dataset first to get this file.
# or just: python pantip_make_graph.py
PTAGS_DATASET_PATH = 'ptags_dataset.txt'

# To use in auto-select minimum support value as it depends on size of the dataset.
# This value will select the value as percent of occurence of nth most frequent data
# eg. TOP_NTH_MIN_SUPPORT = 30
# 		- means that we select 30th most frequent item in the dataset
#		- then find its frequency in the dataset, suppose 0.005
#		- so use 0.005 as minimum support, to have 30 candidates at first layer
TOP_NTH_MIN_SUPPORT = 240

MINIMUM_CONFIDENCE = 0.4

class Apriori(object):

	"""Compute Association rules with Apriori. 
		Basically for finding out which items are likely to go together.
		Minimum support must be chosen with care, too low will give high
		number of possible subsets, and that means it will HANG.
		Uses: 
			ap = Apriori(0.003)  # custom minimum support 0.003
			ap.compute(data_path)
		Tips:
			"Choosing Minimum Support" 
			ap.compute(data_path, auto_minimum_support=True)

			will print out percent of occurence of 20th most frequent item 
			in this dataset. You may get a grip of reasonable minimum support
			value for computation.
		Resources:
			Heavily based on http://aimotion.blogspot.com/2013/01/machine-learning-and-data-mining.html

	"""

	# Relevant Functions
	# - computeFrequentList: createC1 -> loop(pruneD -> aprioriGen)
	# 	-> generateRules: loop(pruneRules -> rules_from_conseq)

	def __init__(self, minimum_support=0.3):
		super(Apriori, self).__init__()
		self.minimum_support = minimum_support
		# TODO: may optimize by using this to map text<->index, and compute with integers instead.
		self.tagList = []
		self.frequencyList = []
		self.totalDataCount = -1
		self.totalTagCount = -1
		self.topNthTags = []


	def generateRules(self, L, support_data, min_confidence=0.7):
		"""Create the association rules
		L: list of frequent item sets
		support_data: support data for those itemsets
		min_confidence: minimum confidence threshold
		"""
		rules = []
		# K layers: (k -> 0), (k-1 -> 1), (k-2 -> 2), ...
		for i in range(1, len(L)):
			for freqSet in L[i]:
				# start with one item at the right ( P1 -> H1 ), ...
				H1 = [frozenset([item]) for item in freqSet]
				# print "freqSet", freqSet, 'H1', H1	            
				if (i > 1):
					# k >= 2
					self.rules_from_conseq(freqSet, H1, support_data, rules, min_confidence)
				else:	           
					# k = 1 	
					self.pruneRules(freqSet, H1, support_data, rules, min_confidence)
		return rules


	def pruneRules(self, freqSet, H, support_data, rules, min_confidence=0.7):
		"Evaluate the rule generated"
		# support = frequency of occurences of these sets in original dataset
		# P + H = union of P and H
		# freqSet - H = P
		# confidence P -> H = support(P+H)/support(P)
		pruned_H = []
		for conseq in H:			
			conf = support_data[freqSet] / support_data[freqSet - conseq]
			if conf >= min_confidence:
				# print freqSet - conseq, '--->', conseq, 'conf:', conf
				# add rules that it's confident of
				rules.append((freqSet - conseq, conseq, conf))
				pruned_H.append(conseq)
		return pruned_H


	def rules_from_conseq(self, freqSet, H, support_data, rules, min_confidence=0.7):
		"Generate a set of candidate rules"
		m = len(H[0])
		if (len(freqSet) > (m + 1)):
			# make next sets of H (all combinations of previous layer H)
			Hmp1 = self.aprioriGen(H, m + 1)
			# determine and prune what's not meet confidence
			Hmp1 = self.pruneRules(freqSet, Hmp1,  support_data, rules, min_confidence)
			# do it for all possible partitions
			# K layers: (k -> 0), (k-1 -> 1), (k-2 -> 2), ...
			if len(Hmp1) > 1:
				self.rules_from_conseq(freqSet, Hmp1, support_data, rules, min_confidence)


	def loadData(self, dataset_path):
		"""Load tags data into memory"""
		dataset = []
		self.tagList = []
		self.frequencyList = []
		self.topNthTags = []
		with open(PTAGS_DATASET_PATH, 'r') as f:
			count = 0
			count_tag = 0
			for line in f:
				tags = line.replace('\n', '').replace('\r', '').split(',')
				for tag in tags:
					if tag not in self.tagList:
						self.tagList.append(tag)
						count_tag += 1
						self.frequencyList.append(1)
					else:
						ind = self.tagList.index(tag)
						self.frequencyList[ind] += 1
				dataset.append(tags)
				count += 1
				# if count == 1000:
				# 	break

			if count == 0:
				print('Error: no dataset loaded.')			
			else:
				print('Loaded: ' + str(count))
				print('Tag Lists: ' + str(count_tag))	
		self.totalDataCount = count
		self.totalTagCount = count_tag
		total = len(dataset)
		# topList = sorted(range(len(self.frequencyList)), key=lambda i:self.frequencyList[i], reverse=True)[:TOP_NTH_MIN_SUPPORT]
		topList = sorted(range(len(self.frequencyList)), key=lambda i: self.frequencyList[i], reverse=True)[:TOP_NTH_MIN_SUPPORT]		
		print('\nTOP %s TAGS' % str(TOP_NTH_MIN_SUPPORT))
		self.topNthTags = [self.tagList[item] for item in topList]
		for item in self.topNthTags:
			print item + ' ',
		print '\n'
		auto_minimum_support = float(self.frequencyList[self.tagList.index(self.topNthTags[TOP_NTH_MIN_SUPPORT-1])])/float(total)
		return dataset, auto_minimum_support


	def createC1(self, dataset):
		"""Create a list of candidate item sets of size one."""
		c1 = []
		for topic_tags in dataset:
			for tag in topic_tags:
				if [tag] not in c1:
					c1.append([tag])
		c1.sort()
		# frozenset because it will be a ket of a dictionary.
		return map(frozenset, c1)


	def pruneD(self, dataset, candidates, minimum_support):
		"""Return all candidates that meets a minimum support level."""		
		sscnt = {}
		for topic_tags in dataset:
			for can in candidates:				
				if can.issubset(topic_tags):
					sscnt.setdefault(can, 0)
					sscnt[can] += 1
		print('Pruning ... : finished counting subset')
		num_items = float(len(dataset))		
		retlist = []
		support_data = {}
		for key in sscnt:
			support = sscnt[key] / num_items			
			if support >= minimum_support:				
				retlist.insert(0, key)
				support_data[key] = support
		return retlist, support_data


	def aprioriGen(self, freq_sets, k):
		"""Generate Joint Items from candidate sets"""
		jointItems = []
		lenF = len(freq_sets)
		for i1 in range(0, lenF):
			for i2 in range(i1+1, lenF): 
				L1 = list(freq_sets[i1])[:k-2]
				L2 = list(freq_sets[i2])[:k-2]
				L1.sort()
				L2.sort()
				if L1 == L2:
					jointItems.append(freq_sets[i1]|freq_sets[i2])
		return jointItems


	def computeFrequentList(self, dataset, min_support):
		"Generate a list of candidate item sets"				
		if not dataset:
			raise ValueError('No data to process.')

		C1 = self.createC1(dataset)
		print('Generated C1:' + str(len(C1)))
		# use set for subset computations
		D = map(set, dataset)				
		L1, support_data = self.pruneD(D, C1, min_support)
		print('Finished Pruning C1, removed ' + str(len(D)-len(L1)) + ', left ' + str(len(L1)) + '\n')
		L = [L1]		
		k = 2
		while(len(L[k-2]) > 0):
			Ck = self.aprioriGen(L[k-2], k)
			print('Generated C' + str(k) + ': ' + str(len(Ck)))
			Lk, supK = self.pruneD(D, Ck, min_support)			
			support_data.update(supK)
			print('Finished Pruning C' + str(k) + ', removed ' + str(len(Ck)-len(Lk)) + ', left ' + str(len(Lk)) + '\n')
			# print(support_data)
			L.append(Lk)			
			k+=1
		# delete last empty candidate set
		del L[k-2]

		return L, support_data


	def compute(self, dataset_path, auto_minimum_support=True, saves_result_to_file=False):
		import time
		start_time = time.time()
		print('Starting Apriori ...\n\n')
		dataset, autoMinimumSupport = self.loadData(dataset_path)
		# automatically choose 20th most frequent item's as minimum support
		if auto_minimum_support:
			min_sup = autoMinimumSupport
			print('Use auto minimum support: ' + str(min_sup))
		else:
			min_sup = self.minimum_support
			print('Use custom minimum support: ' + str(min_sup))

		print('=======Computing Frequent List ...')
		L, support_data = self.computeFrequentList(dataset, min_sup)
		print('')
		
		print('=======Generating Rules ...')
		rules = self.generateRules(L, support_data, MINIMUM_CONFIDENCE)

		if saves_result_to_file:
			print('Saving to ptags_AprioriResults.txt ... ')
			self.savesResult(L, support_data, rules, min_sup, MINIMUM_CONFIDENCE)		
		end_time = time.time()
		print('\nDone (%s).' % str(end_time - start_time))
		return rules


	def savesResult(self, L, support_data, rules, min_support, min_confidence):
		# L = [L1, L2, L3, ...]
		# L1 = [frozenset, frozenset, ...]

		# Rule = (frozenset (P), frozenset (H), float (con))
		# P --> H
		
		out = open('ptags_AprioriResults.txt', 'w')
		out.write('Total Data Count: %s\n' % str(self.totalDataCount))
		out.write('Total Tag Count: %s\n' % str(self.totalTagCount))
		out.write('Top %s Tags:\n' % TOP_NTH_MIN_SUPPORT)
		for item in self.topNthTags:			
			out.write('%s (%s) ' % (item, str(self.frequencyList[self.tagList.index(item)])))			
		out.write('\n')
		out.write('Minimum support: %s\n' % str(min_support))
		out.write('Minimum confidence: %s\n' % str(min_confidence))
		out.write('\n\n=======Frequent Lists=======\n')
		k = 0

		import collections

		for Lk in L:
			k += 1
			out.write('---(K = %s)----\n' % str(k))
			#sort first
			Lkdict = {}	
			for can in Lk:
				item_str = ""
				for item in can:
					item_str += item + ' '
				Lkdict[support_data[can]] = item_str
			od = collections.OrderedDict(sorted(Lkdict.items(), reverse=True))
			for key, v in od.iteritems():
				out.write('%s (%s)\n' % (v, key))

		out.write('\n\n=======Association Rules========\n')

		RulesDict = {}
		for rule in rules:
			rule_str = ""
			for item in rule[0]:
				rule_str += item + ' '
			rule_str += ' --> '
			for item in rule[1]:
				rule_str += item + ' '			
			RulesDict[rule[2]] = rule_str
		od = collections.OrderedDict(sorted(RulesDict.items(), reverse=True))
		for key, v in od.iteritems():
			out.write('%s (%s)\n' % (v, key))
		out.close()



if __name__ == '__main__':
	ap = Apriori(0.009)
	rules = ap.compute(PTAGS_DATASET_PATH, auto_minimum_support=True, saves_result_to_file=True)
	# for rule in rules:
	# 	print rule

	#L, support_data = ap.compute(PTAGS_DATASET_PATH, False)
	# k = 1	
	# for Lk in L:
	# 	print '========%d Item(s)==========' % k
	# 	k += 1
	# 	for joint in Lk:
	# 		for item in joint:
	# 			print item,
	# 		print ''	




		

		

#!/usr/bin/python

import os
import fullgraph as fg

THAI_ENCODING = 'utf-8'
DATASET_PATH = "dataset"

class PantipGraph(object):

    @staticmethod
    def tags_graph_from_ptopic_dataset(path):

        count = 0
        fgraph = fg.FullGraph()

        for root, dirs, files in os.walk(path, topdown=False):
            # go into each dataset files
            print files
            for name in files:
                # get full path
                fname = os.path.join(root, name)
                print('Reading File:' + fname)
                # read file
                with open(fname, 'r') as ins:
                    for line in ins:
                        if line.startswith('Tag-item: '):
                            if len(line) <= 12:
                                continue
                            tags = line.replace('Tag-item: ', '').replace('\n', '').replace('\r', '').split(',')
                            # for tag in tags:                                
                            #     print tag +'\n---'
                            # add all nodes
                            for tag in tags:                                   
                            	fgraph.addNode(tag)                            	
                            # add weight to every pairs
                            for i in range(0, len(tags)):
                            	for j in range(i+1, len(tags)):
                            		fgraph.addWeight(tags[i], tags[j], 1)
                            count = count + 1   
        print('Saving...')    
        fgraph.saveGraph()
        print('Total topics in dataset = ' + str(count))
        print('Total nodes = ' + str(len(fgraph.nodeList)))
        m = max(fgraph.frequencyList)
        maxlist = [i for i, j in enumerate(fgraph.frequencyList) if j == m]
        print('Most Frequent Tag = ' + fgraph.nodeList[maxlist[0]] + ', Value = ' + str(fgraph.frequencyList[maxlist[0]]))
        topList = sorted(range(len(fgraph.frequencyList)), key=lambda i:fgraph.frequencyList[i], reverse=True)[:10]
        print('Top 10 Tags:')
        for ind in topList:
            print(fgraph.nodeList[ind] + ': ' + str(fgraph.frequencyList[ind]))
        # for node in fgraph.getAllNodes():
        # 	print node.decode('utf-8').encode('tis620')


if __name__ == '__main__':
    PantipGraph.tags_graph_from_ptopic_dataset(DATASET_PATH)
    # fgraph = fg.FullGraph()
    # fgraph.loadGraph()


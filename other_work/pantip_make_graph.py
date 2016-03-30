#!/usr/bin/python

import os
import fullgraph as fg

THAI_ENCODING = 'utf-8'
DATASET_PATH = "pantip_storage"

class PantipGraph(object):

    @staticmethod
    def create_ptag_dataset(dataset_path, save_path='ptags_dataset.txt'):
        import os
        count = 0
        print('Creating ptags_dataset...')
        out = open(save_path, 'w')      
        for root, dirs, files in os.walk(dataset_path, topdown=False):
            # go into each dataset files
            print files
            for name in files:
                # get full path
                fname = os.path.join(root, name)
                if 'ptopic' not in name:
                    print('Skipping File:' + fname)
                    continue
                print('Reading File:' + fname)
                # read file
                with open(fname, 'r') as ins:
                    for line in ins:                        
                        if line.startswith('Tag-item: '):
                            # len including new line symbol
                            if len(line) <= 12:
                                continue
                            tags = line.replace('Tag-item: ', '').replace('\n', '').replace('\r', '') + '\n'
                            out.write(tags) 
                            count += 1
        out.close()
        print('Saved ptags_dataset to: ' + save_path)
        print('Total topics in dataset = ' + str(count))

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
    PantipGraph.create_ptag_dataset(DATASET_PATH)
    # PantipGraph.tags_graph_from_ptopic_dataset(DATASET_PATH)
    # fgraph = fg.FullGraph()
    # fgraph.loadGraph()


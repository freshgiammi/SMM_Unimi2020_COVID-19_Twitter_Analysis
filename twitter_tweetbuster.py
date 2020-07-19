import json
import sys
import networkx as nx
import numpy as np

#Load dataset
#TODO: Merge all datasets, build a base of unique users containing own tweets
dataset = json.load(open('datasets/dataset.json'))

handle =sys.argv[1]
links = list()

for i in dataset:
  for j in i.get("tweets",""):
      if list(j.get("retweeted_from","").keys())[0] == handle:
          linkGenerator = "https://twitter.com/"+handle+"/status/"+str(j.get("retweeted_from","")[handle])
          links.append(linkGenerator)
uniquetweets = list(set(links))
for i in uniquetweets:
    num = 0
    for j in links:
        if j == i:
            num += 1 
    print("{}, retweeted {} times.".format(i,num))



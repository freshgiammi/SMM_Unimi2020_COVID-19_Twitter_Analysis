import json
import time
import twitter
import pandas as pd
import random
import datetime

from statsmodels.distributions.empirical_distribution import ECDF
import networkx as nx
from statsmodels.distributions.empirical_distribution import ECDF
import numpy as np
import matplotlib.pyplot as plt

#Load dataset
#TODO: Merge all datasets, build a base of unique users containing own tweets
dataset = json.load(open('datasets/dataset.json'))
 
totaltweets = 0
totalusers = len(dataset)
totalrt = 0
userlist = list()
realusers = list()
for t in dataset:
    userlist.append(list(t.keys())[0])
    realusers.append(list(t.keys())[0])
    totaltweets = totaltweets + len(t.get('tweets',''))
    for tweet in t.get('tweets',''):
        totalrt = totalrt + len(tweet.get('retweeted_from',''))
        if len(tweet.get('retweeted_from','')) != 0:
            for rt in tweet.get('retweeted_from',''):
                realusers.append(rt)
            
        #TODO: Check for oldest tweet, compare first one to current time

print("Are there user duplicates in the list? "+str(len(userlist) != len(set(userlist))))
print("We have a total of "+str(totalusers)+" users and "+str(totaltweets)+" tweets.")
print("Out of "+str(totaltweets)+" tweets, "+str(totalrt)+" are retweets.")
print("We calculate around "+str(totaltweets/totalusers)+" tweets per user.")

realusers = list(dict.fromkeys(realusers))
print("Total unique users (OC+RT) detected: "+str(len(realusers)))

print("Generating edge list...", end=" ")
edgelist = list()
for user in dataset:
    username = list(user.keys())[0]
    for tweet in user.get('tweets',''):
        if len(tweet.get('retweeted_from','')) == 0:
            continue
        else: 
            rt_oc_user = list(tweet.get('retweeted_from','').keys())[0]
            link = (username,rt_oc_user)
            if username == rt_oc_user:
                continue
            if link not in edgelist:
                edgelist.append(link)

twitter_d = nx.DiGraph()
for tuple in edgelist:
    twitter_d.add_edge(tuple[0], tuple[1])
print("Edge list generated. Length: "+str(len(edgelist)))

print('Preformatted nodes: {}'.format(twitter_d.order()))
print("Removing nodes with out-degree less than 10...", end=" ")
to_be_removed = [x for  x in twitter_d.nodes() if twitter_d.degree(x) <= 9]
for x in to_be_removed:
    twitter_d.remove_node(x)
print("Done.")
print("Removing isolates...", end=" ")
to_be_removed = list(nx.isolates(twitter_d))
for x in to_be_removed:
    twitter_d.remove_node(x)
print("Done.")

print('Number of nodes: {}'.format(twitter_d.order()))
print('Number of links: {}'.format(twitter_d.size()))
density = nx.density(twitter_d)
print('Density: {}'.format(density))

nx.write_gexf(twitter_d, "dataset.gexf")
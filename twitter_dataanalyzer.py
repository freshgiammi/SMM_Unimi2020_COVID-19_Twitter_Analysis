import json
import networkx as nx
import numpy as np

#Load dataset
#TODO: Merge all datasets, build a base of unique users containing own tweets
dataset = json.load(open('datasets/dataset.json'))
 
totaltweets = 0
totalusers = len(dataset)
totalrt = 0
userlist = list()
realusers = list()

usernames = list()
for user in dataset:
    userlist.append(user['handle'])
    realusers.append(user['handle'])
    totaltweets = totaltweets + len(user['tweets'])
    for tweet in user['tweets']:
        realusers.append(list(tweet['retweeted_from'].keys())[0])

print("Are there user duplicates in the list? "+str(len(userlist) != len(set(userlist))))
print("We have a total of "+str(totalusers)+" users and "+str(totaltweets)+" retweets.")
print("We calculate around "+str(totaltweets/totalusers)+" tweets per user.")

realusers = list(dict.fromkeys(realusers))
print("Total unique users (OC+RT) detected: "+str(len(realusers)))


print("Generating edge list...", end=" ")
twitter_d = nx.DiGraph()
for user in dataset:
    username = user['handle']
    for tweet in user['tweets']:
        rt_oc_user = list(tweet['retweeted_from'].keys())[0]
        link = (username,rt_oc_user)
        if username == rt_oc_user:
            continue #User is retweeting himself; avoid self-loops
        if (twitter_d.has_edge(username, rt_oc_user) != True):
            twitter_d.add_edge(username, rt_oc_user)
print("Edge list generated.")

print('Preformatted nodes: {}'.format(twitter_d.order()))

print('Removing nodes outside of Giant Component...', end='')
weak_nodes = max(nx.weakly_connected_components(twitter_d), key=len)
nodelist = list()
for n in twitter_d.nodes():
    if n not in weak_nodes:
      nodelist.append(n)
twitter_d.remove_nodes_from(nodelist)
print(' '+str(len(nodelist))+ ' nodes removed.')

print('Number of nodes: {}'.format(twitter_d.order()))
print('Number of links: {}'.format(twitter_d.size()))
density = nx.density(twitter_d)
print('Density: {}'.format(density))

#nx.write_gexf(twitter_d, "dataset.gexf")
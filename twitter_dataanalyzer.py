import json
import time
import twitter
import pandas as pd
import random
import datetime

#Twitter API Initialization
keys = json.load(open('keys.json'))['twitter']
bearer_token = twitter.oauth2_dance(consumer_key = keys['consumer_key'], consumer_secret = keys['consumer_secret'])
twitter_api = twitter.Twitter(auth=twitter.OAuth2(bearer_token = bearer_token))

#Load dataset
#TODO: Merge all datasets, build a base of unique users containing own tweets
dataset = json.load(open('datasets/Twitter_Dataset_20200424-011336.json'))
 
totaltweets = 0
totalusers = len(dataset)
totalrt = 0
for t in dataset:
    totaltweets = totaltweets + len(t.get('tweets',''))
    for tweet in t.get('tweets',''):
        totalrt = totalrt + len(tweet.get('retweeted_from',''))
        #TODO: Check for oldest tweet, compare first one to current time

print("We have a total of "+str(totalusers)+" users and "+str(totaltweets)+" tweets.")
print("Out of "+str(totaltweets)+" tweets, "+str(totalrt)+" are retweets.")
print("We calculate around "+str(totaltweets/totalusers)+" tweets per user.")



        
#print("Gathered "+str(len(dataset))+" tweets from a set of "+str(len(unique_users))+" unique users.", sep="")
#print("Most retweeted tweet is: "+str(dataset[max(max_retweets, key=max_retweets.get)]))
#print("Most liked tweet is: "+str(dataset[max(max_favorites, key=max_favorites.get)]))



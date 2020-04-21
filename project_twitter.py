import json
import time
import twitter
import pandas as pd
import random

# ---------------- FUNCTION DEFINITIONS  ---------------- #

## randomTweetID(search_result)
# Takes in query result and returns a random tweet id.
def randomTweetID(search_result):
    t = random.choice(search_result)
    tid = t.get('id','')
    print(tid)
    return tid

# ---------------- FUNCTION DEFINITIONS  ---------------- #

#Twitter API Initialization
keys = json.load(open('keys.json'))['twitter']
bearer_token = twitter.oauth2_dance(consumer_key = keys['consumer_key'], consumer_secret = keys['consumer_secret'])
twitter_api = twitter.Twitter(auth=twitter.OAuth2(bearer_token = bearer_token))

#Query composition and request
query = '#COVID19'
print("Indexing request 1 ..." ,end=" ")
response = twitter_api.search.tweets(q=query,count=100, lang='it')
print("Request completed.")
tweets = response['statuses']

#Ask more tweets range(n) times, if they are available. (n+1 return values)
for i in range(149):
    print("Indexing request",i+2,"..." ,end=" ")
    if 'next_results' in response['search_metadata']:
        max_id = dict([tuple(tok.split('=')) for tok in response['search_metadata']['next_results'][1:].split('&')])['max_id']
        print("Request completed.")
        #print(response['search_metadata']['next_results'])
        response = twitter_api.search.tweets(q=query,count=100, lang='it', max_id = max_id)
        tweets.extend(response['statuses'])
    else:
        #TODO: RATE LIMITING CASE HANDLING
        break

# ---------------- JSON PREFORMATTING  ---------------- #
print("Preformatting tweets into JSON tweetlist...", end=" ")
tweetlist = list()
for t in tweets:
    tweetinfo_container = {} #Builds main tweet.
    tweet = {} #First section: tweet specific information
    user = {} #Second section: user specific information

    #TODO: CHECK IF truncated == true, ADD CASE FOR full_text
    tweet['text'] = t['text']#field 'id' is another possible node candidate
    tweet['created_at'] = t['created_at']
    tweet['hashtags'] = t.get('entities','')['hashtags']
    
    #TODO: Should we add a field for verified users and narrow down possible hubs?
    user['username'] = t.get('user','')['screen_name'] #field 'id' is another possible node attribute, candidate for pseudo-anonymity.
    user['followers'] = t.get('user','')['followers_count']
    user['following'] = t.get('user','')['friends_count']
    user['location'] = t.get('user','')['location']

    #Generate item and append to tweetlist
    tweetinfo_container['tweet'] = tweet
    tweetinfo_container['user'] = user
    tweetinfo_container['retweets'] = t['retweet_count']
    tweetinfo_container['favorites'] = t['favorite_count']
    tweetlist.append(tweetinfo_container)
# ---------------- JSON PREFORMATTING  ---------------- #
print("Preformatting completed. Saving to file...")

with open("datasets/Twitter_Dataset_"+time.strftime("%Y%m%d-%H%M%S")+".json", 'x') as outfile:
    json.dump(tweetlist, outfile, indent=1)

print("JSON tweetlist generated. Happy analysis!")
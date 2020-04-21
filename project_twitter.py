import json
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
response = twitter_api.search.tweets(q=query,count=100, lang='it')
tweets = response['statuses']

#Ask more tweets range(n) times, if they are available. (n+1 return values)
for i in range(1):
    if 'next_results' in response['search_metadata']:
        max_id = dict([tuple(tok.split('=')) for tok in response['search_metadata']['next_results'][1:].split('&')])['max_id']
        #print(response['search_metadata']['next_results'])
        response = twitter_api.search.tweets(q=query,count=100, lang='it', max_id = max_id)
        tweets.extend(response['statuses'])
    else:
        break
#print(len({t['id_str'] for t in tweets}))

tweet_id = randomTweetID(tweets)
hydrated_tweet = twitter_api.statuses.show(_id=tweet_id, tweet_mode='extended')
#print(json.dumps(hydrated_tweet,indent=1)) #Prints single tweet info

#TODO: If returnet tweet is a RT, full_text will be truncated in the output. Fix?
print('@',hydrated_tweet.get('user','')['screen_name'],': ',hydrated_tweet['full_text'],sep='')
print('Numero di favorite: {}'.format(hydrated_tweet['favorite_count']))
print('Numero di retweet: {}'.format(hydrated_tweet['retweet_count']))

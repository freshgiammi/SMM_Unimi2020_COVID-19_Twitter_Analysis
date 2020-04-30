import json
import time
import datetime
import twitter
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
twitter_api = twitter.Twitter(auth=twitter.OAuth2(bearer_token = bearer_token), retry=True)

tweetlist = json.load(open('datasets/dataset.json'))
#tweetlist = list()

#Query composition and request
query = 'covid OR coronavirus OR covid19 OR covid-19 OR novel OR coronavirus OR covid19italia'
print("Indexing request 1 ..." ,end=" ")
response = twitter_api.search.tweets(q=query,count=100, lang='it', tweet_mode='extended')
print("Request completed.")
tweets = response['statuses']

#Ask more tweets range(n) times, if they are available. (n+1 return values)
for i in range(449):
    print("Indexing request",i+2,"..." ,end=" ")
    if 'next_results' in response['search_metadata']:
        max_id = dict([tuple(tok.split('=')) for tok in response['search_metadata']['next_results'][1:].split('&')])['max_id']
        response = twitter_api.search.tweets(q=query, count=100, lang='it', tweet_mode='extended', max_id = max_id)
        tweets.extend(response['statuses'])
        print("Request completed.")
    else:
        print("Bedrock found. No more tweets to see here!")
        break

# ---------------- JSON PREFORMATTING  ---------------- #
print("Preformatting tweets into JSON tweetlist...")
for t in tweets:
    flag = 0 #Sets flag for multiple tweets in a user.
    #This block defines an ACTIVE USER. 
    user_time = datetime.datetime.strptime(t.get('user','')['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
    current_time = datetime.datetime.now()
    if (current_time-user_time).days < 2:
        print("Trashing tweet, reason: [AGE_LESS_THAN_TWO]")
        continue
    if(t.get('user','')['followers_count']) == 0:
        print("Trashing tweet, reason: [NO_FOLLOWERS]")
        continue
    if(t.get('user','')['friends_count']) == 0:
        print("Trashing tweet, reason: [NO_FOLLOWING]")
        continue

    user = {} #Builds user key.
    userinfo = {} #Builds user value
    tweet = {} #Builds unique tweet.

    tweet['text'] = t['full_text']#field 'id' is another possible node candidate
    tweet['id'] = t['id']
    tweet['created_at'] = t['created_at']
    tweet['hashtags'] = t.get('entities','')['hashtags']
    tweet['retweets'] = t['retweet_count']
    tweet['favorites'] = t['favorite_count']

    userinfo['followers'] = t.get('user','')['followers_count']
    userinfo['following'] = t.get('user','')['friends_count']
    userinfo['location'] = t.get('user','')['location']

    #Flows in if the tweet is OC.
    if 'retweeted_status' in t:
        tweet['retweeted_from'] = {t.get('retweeted_status','').get('user','')['screen_name']:t.get('retweeted_status','')['id']}
    else:
        tweet['retweeted_from'] = list() #Needed for singlet detection 

    #If user ir already in the list, just add the tweet to the list. Otherwise, create a user.
    #TODO: This shit is "a bit less" fugly
    for currentuser in tweetlist:
        if list(currentuser.keys())[0] == t.get('user','')['screen_name']:
            if any(t['id'] not in currenttweets for currenttweets in currentuser.get('tweets','')): 
                currentuser.get('tweets','').append(tweet)  #Add tweet to user
                flag = 1 #TODO: Check if we can refactor, instead of flagging
                break

    if flag == 0:
        tweets = list() #Builds tweetlist.
        tweets.append(tweet)
        user[t.get('user','')['screen_name']] = userinfo
        user['tweets'] = tweets
        tweetlist.append(user)
        
# ---------------- JSON PREFORMATTING  ---------------- #
print("Preformatting completed. Saving to file...")

#with open("datasets/Twitter_Dataset_"+time.strftime("%Y%m%d-%H%M%S")+".json", 'x') as outfile:
#    json.dump(tweetlist, outfile, indent=1)
with open("datasets/dataset.json", 'w') as outfile:
    json.dump(tweetlist, outfile, indent=1)

print("JSON tweetlist generated. Happy analysis!")
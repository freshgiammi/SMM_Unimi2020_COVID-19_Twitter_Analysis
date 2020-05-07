import json
import time
import datetime
import twitter
import random

#Twitter API Initialization
keys = json.load(open('keys.json'))['twitter']
bearer_token = twitter.oauth2_dance(consumer_key = keys['consumer_key'], consumer_secret = keys['consumer_secret'])
twitter_api = twitter.Twitter(auth=twitter.OAuth2(bearer_token = bearer_token), retry=True)

userlist = json.load(open('datasets/dataset.json'))
#userlist = list()

#Query composition and request
query = 'covid OR coronavirus OR covid19 OR covid-19 OR novel coronavirus OR covid19italia'
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
for nt in tweets:
    #This block defines an ACTIVE USER. 
    user_time = datetime.datetime.strptime(nt.get('user','')['created_at'],'%a %b %d %H:%M:%S +0000 %Y')
    current_time = datetime.datetime.now()
    if (current_time-user_time).days < 14:
        print("Trashing tweet, reason: [AGE_LESS_THAN_TWO_WEEKS]")
        continue
    if(nt.get('user','')['followers_count']) == 0:
        print("Trashing tweet, reason: [NO_FOLLOWERS]")
        continue
    if(nt.get('user','')['friends_count']) == 0:
        print("Trashing tweet, reason: [NO_FOLLOWING]")
        continue
    if 'retweeted_status' not in nt:
        print("Trashing tweet, reason: [NOT_A_RETWEET]")
        continue

    #Check if userlist already contains the user we're analyzing. Retrieve index, otherwise set variable as None (null)
    currentuser = next((i for i,u in enumerate(userlist) if nt.get('user','')['screen_name'] in u['handle']), None)
    if currentuser != None: 
        if not any(t['id'] == nt['id'] for t in userlist[currentuser]['tweets']):
            newtweet = {} #Builds unique tweet.
            # FULL_TEXT is truncated even in extended mode for retweets. Since we only get retweets, fetch from original post...
            # https://stackoverflow.com/questions/38717816/twitter-api-text-field-value-is-truncated
            newtweet['text'] = nt['retweeted_status']['full_text']
            newtweet['id'] = nt['id']
            newtweet['hashtags'] = nt.get('entities','')['hashtags']
            newtweet['retweets'] = nt['retweet_count']
            newtweet['favorites'] = nt['favorite_count']
            newtweet['retweeted_from'] = {nt.get('retweeted_status','').get('user','')['screen_name']:nt.get('retweeted_status','')['id']}
            userlist[currentuser]['tweets'].append(newtweet)
        else:
            pass #We're indexing a tweet that's already in the list. Skip over.
        
    else:
        tweetlist = list()
        newtweet = {} #Builds unique tweet.
        # FULL_TEXT is truncated even in extended mode for retweets. Since we only get retweets, fetch from original post...
        # https://stackoverflow.com/questions/38717816/twitter-api-text-field-value-is-truncated
        newtweet['text'] = nt['retweeted_status']['full_text']
        newtweet['id'] = nt['id']
        newtweet['hashtags'] = nt.get('entities','')['hashtags']
        newtweet['retweets'] = nt['retweet_count']
        newtweet['favorites'] = nt['favorite_count']
        newtweet['retweeted_from'] = {nt.get('retweeted_status','').get('user','')['screen_name']:nt.get('retweeted_status','')['id']}
        tweetlist.append(newtweet)

        newuser = {} #Builds user key.
        newuser['handle'] = nt.get('user','')['screen_name']
        newuser['followers'] = nt.get('user','')['followers_count']
        newuser['following'] = nt.get('user','')['friends_count']
        newuser['tweets'] = tweetlist

        userlist.append(newuser)
        
# ---------------- JSON PREFORMATTING  ---------------- #
print("Preformatting completed. Saving to file...")

#with open("datasets/Twitter_Dataset_"+time.strftime("%Y%m%d-%H%M%S")+".json", 'x') as outfile:
#    json.dump(tweetlist, outfile, indent=1)
with open("datasets/dataset.json", 'w') as outfile:
    json.dump(userlist, outfile, indent=1)

print("JSON tweetlist generated. Happy analysis!")
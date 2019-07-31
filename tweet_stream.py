import tweepy as tw

consumer_key = ""
consumer_secret = ""

access_token = ""
access_token_secret = ""

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

search_words = "Rafael Correa Mashi"
date_since = "2018-11-16"

tweets = tw.Cursor(api.search,
              q=search_words,
              since=date_since).items(10)

# Iterate on tweets
for tweet in tweets:
    print('******')
    user=tweet.user.id
    print("username:", str(tweet.user.screen_name).encode('utf-8'))
    print("followers:", int(str(tweet.user.followers_count).encode('utf-8')))
    print("friends:", int(str(tweet.user.friends_count).encode('utf-8')))
    print(str(tweet.text).encode('utf-8'))
    print('******')
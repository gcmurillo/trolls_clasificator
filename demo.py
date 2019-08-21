import tweepy
import credentials

# Tweepy api credentials config
consumer_key = credentials.consumer_key
consumer_secret = credentials.consumer_secret

access_token = credentials.access_token
access_token_secret = credentials.access_token_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

tweet = api.get_status(1163622449252110336)
content = str(tweet.text)
followers = tweet.user.followers_count
following = tweet.user.friends_count
retweet = 1 if hasattr(tweet, 'retweeted_status') else 0
line = content.replace(',', ';').replace('\n', ' ') + "," + str(followers) + "," + str(following) + "," + str(retweet)
print(line)

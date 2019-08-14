import tweepy as tw
import credentials

consumer_key = credentials.consumer_key
consumer_secret = credentials.consumer_secret

access_token = credentials.access_token
access_token_secret = credentials.access_token_secret

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

# Getting timeline for user
for status in tw.Cursor(api.user_timeline, screen_name='Fabrici85278757', tweet_mode="extended").items():
    print(status.full_text)
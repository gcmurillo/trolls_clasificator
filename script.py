# import stuff
import argparse
import tweepy
import credentials
from dateutil import tz

# Define functions
def time_analysis(date):
    """
    Return weekday (0-6) and interval (0-3)
    """
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    utc = date
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    day = central.weekday()
    hour = central.hour
    if 0 <= hour < 6:
        return day, 0
    elif 6 <= hour < 12:
        return day, 1
    elif 12 <= hour < 18:
        return day, 2
    elif 18 <= hour < 24:
        return day, 3

# Tweepy api credentials config
consumer_key = credentials.consumer_key
consumer_secret = credentials.consumer_secret

access_token = credentials.access_token
access_token_secret = credentials.access_token_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# create arguments for script
parser = argparse.ArgumentParser()
# -t y-f trolls_list.csv -o dataset.csv
parser.add_argument("-t", "--troll", help="Is troll file", default="n", dest="troll")
parser.add_argument("-f", "--userfile", help="csv file direction")

args = parser.parse_args()

# setting if file is for trolls or not
troll_file = False
if args.troll != "n":
    troll_file = True

# option to create dataset
n_tweets = 0
users_filename = args.userfile
if users_filename:
    header = "content,followers,following,retweet,created_at,troll\n"
    with open(users_filename) as f:
        with open("dataset.csv", "w", encoding='utf-8') as output_file:
            output_file.write(header)
            for user in f:
                try: 
                    for status in tweepy.Cursor(api.user_timeline, screen_name=user.strip("\n"), tweet_mode="extended").items():
                        content = status.full_text
                        followers = status.user.followers_count
                        following = status.user.friends_count
                        retweeted = True if hasattr(status, 'retweeted_status') else False
                        created_at = status.created_at
                        is_troll = troll_file
                        line = content.replace(',', ';').replace('\n', ' ') + "," + str(followers) + "," + str(following) + "," + str(retweeted) + "," + str(created_at) + "," + str(is_troll) + "\n"
                        output_file.write(line)
                        n_tweets += 1
                        print("Tweets: ", n_tweets)
                    print("End user: ", user)
                except:
                    print("Error:", user)
                    pass
else:
    print("sin crear")
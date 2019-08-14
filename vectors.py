# import stuff
import tweepy as tw
import credentials
from sentic import SenticPhrase
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import requests, json
from dateutil import tz

# Tweepy api credentials config
consumer_key = credentials.consumer_key
consumer_secret = credentials.consumer_secret

access_token = credentials.access_token
access_token_secret = credentials.access_token_secret

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

def parrot_emotion_model(text):
    sp = SenticPhrase(text, "es")
    emotions = {"fear": 0, "anger": 0, "sadness": 0, "love": 0, "surprise": 0, "joy": 0}
    # Parrot emotion model
    if sp.get_sentics():
        sentic_dict = sp.get_sentics()
        emotions["fear"] += 1 if -0.3 > sentic_dict["sensitivity"] >= -0.6 else 0
        emotions["anger"] += 1 if 0.6 >= sentic_dict["sensitivity"] > 0.3 else 0
        emotions["sadness"] +=1  if -0.3 > sentic_dict["pleasantness"] >= -0.6 else 0
        emotions["love"] +=1  if sentic_dict["pleasantness"] > 0 and sentic_dict["aptitude"] > 0 else 0
        emotions["surprise"] += 1 if -0.3 > sentic_dict["attention"] >= -0.6 else 0
        emotions["joy"] += 1 if 0.6 >= sentic_dict["pleasantness"] > 0.3 else 0
    return emotions


def vader_sentiment(text):
    """
        Return 1 if positive, -1 to negative and 0 to neutral
    """
    # Vader Sentiment analyzer and languages for translator
    sid_obj = SentimentIntensityAnalyzer()
    to_lang="en"  
    from_lang="es"
    # please note usage limits for My Memory Translation Service:   http://mymemory.translated.net/doc/usagelimits.php
    # using   MY MEMORY NET   http://mymemory.translated.net
    api_url = "http://mymemory.translated.net/api/get?q={}&langpair={}|{}".format(text, from_lang, to_lang)
    hdrs ={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    response = requests.get(api_url, headers=hdrs)
    response_json = json.loads(response.text)
    translation = response_json["responseData"]["translatedText"]
    translator_name = "MemoryNet Translation Service"
    
    # polarity_scores method of SentimentIntensityAnalyzer 
    # oject gives a sentiment dictionary. 
    # which contains pos, neg, neu, and compound scores. 
    sentiment_dict = sid_obj.polarity_scores(translation) 
      
    print("Overall sentiment dictionary is : ", sentiment_dict) 
    print("sentence was rated as ", sentiment_dict['neg']*100, "% Negative") 
    print("sentence was rated as ", sentiment_dict['neu']*100, "% Neutral") 
    print("sentence was rated as ", sentiment_dict['pos']*100, "% Positive") 
  
    print("Sentence Overall Rated As", end = " ")
    if sentiment_dict['compound'] >= 0.05 : 
        print("Positive") 
        return 1
    elif sentiment_dict['compound'] <= - 0.05 : 
        print("Negative") 
        return -1
    else : 
        print("Neutral")
        return 0


# Getting timeline for user
counter = 0
for status in tw.Cursor(api.user_timeline, screen_name='Fabrici85278757', tweet_mode="extended").items():
    print(status.full_text)
    text = status.full_text
    
    parrot = parrot_emotion_model(text)

    # VADER SENTIMENTAL ANALYSIS (positive & negative)
    vader_sentiment(text)
  
    
    # Time analysis
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    utc = status.created_at
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    print("day: ", central.weekday())
    hour = central.hour
    print("interval:", end=" ")
    if 0 <= hour < 6:
        print(1)
    elif 6 <= hour < 12:
        print(2)
    elif 12 <= hour < 18:
        print(3)
    elif 18 <= hour < 24:
        print(4)
    
    print("***********")
    if counter > 10:
        break
    else: 
        counter += 1
    

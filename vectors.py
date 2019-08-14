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

# Vader Sentiment analyzer and languages for translator
sid_obj = SentimentIntensityAnalyzer()
to_lang="en"  
from_lang="es"

# Getting timeline for user
counter = 0
for status in tw.Cursor(api.user_timeline, screen_name='Fabrici85278757', tweet_mode="extended").items():
    print(status.full_text)
    text = status.full_text
    sp = SenticPhrase(text, "es")
    
    # Parrot emotion model
    if sp.get_sentics():
        sentic_dict = sp.get_sentics()
        if -0.3 > sentic_dict["sensitivity"] >= -0.6:  # fear    
            print("Fear")
        if 0.6 >= sentic_dict["sensitivity"] > 0.3:  # Anger
            print("Anger")
        if -0.3 > sentic_dict["pleasantness"] >= -0.6:  # sadness
            print("Sadness")
        if sentic_dict["pleasantness"] > 0 and sentic_dict["aptitude"] > 0: # Love
            print("Love")
        if -0.3 > sentic_dict["attention"] >= -0.6:  # surprise
            print("Surprise")
        if 0.6 >= sentic_dict["pleasantness"] > 0.3:  # Joy
            print("Joy")
    
    # VADER SENTIMENTAL ANALYSIS (positive & negative)
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
  
    # decide sentiment as positive, negative and neutral 
    if sentiment_dict['compound'] >= 0.05 : 
        print("Positive") 
  
    elif sentiment_dict['compound'] <= - 0.05 : 
        print("Negative") 
  
    else : 
        print("Neutral")

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
    
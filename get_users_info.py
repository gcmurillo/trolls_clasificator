import os
import json
import sys

rootdir = '/media/geancarlo/OS_Install/Users/geancarlo/Desktop/tweets/'  # carpeta con subcarpetas de tweets
'''
> tweets
    > guayaquil_1
    > quito_1
    > cuenca_1
'''

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

users = []
file = open('users_dataset.csv', 'w')
file.write('screen_name,following,followers,favourites_count,verified\n')

tweets_file = open('tweets_dataset.csv', 'w', encoding='utf-8-sig')
tweets_file.write('screen_name,tweet,favorite_count,retweet_count,reply_to,n_user_mentions,n_hashtags,n_urls,user_mentions,hashtags\n')

cities = ['Guayaquil', 'Quito', 'Cuenca']
n_tweets = 0

for root, dirs, files in os.walk(rootdir):
    for name in files:
        if name.endswith((".json")):
            full_path = os.path.join(root, name)
            with open(full_path) as f:
                data = json.load(f)
            # get tweets from the json file
            tweets = data['data']
            for t in tweets:
                """ if t['place']['name'] in cities:
                    user = t['user']['screen_name']
                    if user not in users:  # for user dataset
                        users.append(user)
                        file.write(user + ',' + str(t['user']['friends_count']) + ',' +  str(t['user']['followers_count']) + ',' +
                                    str(t['user']['favourites_count']) + ',' + str(t['user']['verified']) + '\n')

                    if 'extended_tweet' in t.keys():  # for tweets dataset
                        tweet = str('\"' + t['extended_tweet']['full_text'] + '\"').replace('\n', ' ').replace(',', ';').encode('utf-8')
                    else:
                        tweet = str('\"' + t['text'] + '\"').replace('\n', ' ').replace(',', ';').encode('utf-8')
                    reply = t['in_reply_to_screen_name'] if t['in_reply_to_screen_name'] is not None else ''
                    user_mentioned = ';'.join(i['screen_name'] for i in t['entities']['user_mentions'])
                    hashtags = ';'.join(i['text'] for i in t['entities']['hashtags'])
                    tweets_file.write(user + ',' + tweet.decode('utf-8') + ',' + str(t['favorite_count']) + ',' + str(t['retweet_count']) + ',' + reply + ',' + 
                    str(len(t['entities']['user_mentions'])) + ',' + str(len(t['entities']['hashtags'])) + ',' + str(len(t['entities']['urls'])) + ',"' + 
                    user_mentioned + '","' + hashtags + '",' +  t['place']['name'] + '\n')
                    n_tweets += 1 """
                user = t['user']['screen_name']
                if user not in users:  # for user dataset
                    users.append(user)
                    file.write(user + ',' + str(t['user']['friends_count']) + ',' +  str(t['user']['followers_count']) + ',' +
                                str(t['user']['favourites_count']) + ',' + str(t['user']['verified']) + '\n')

                if 'extended_tweet' in t.keys():  # for tweets dataset
                    tweet = str('\"' + t['extended_tweet']['full_text'] + '\"').replace('\n', ' ').replace(',', ';').encode('utf-8')
                else:
                    tweet = str('\"' + t['text'] + '\"').replace('\n', ' ').replace(',', ';').encode('utf-8')
                reply = t['in_reply_to_screen_name'] if t['in_reply_to_screen_name'] is not None else ''
                user_mentioned = ';'.join(i['screen_name'] for i in t['entities']['user_mentions'])
                hashtags = ';'.join(i['text'] for i in t['entities']['hashtags'])
                tweets_file.write(user + ',' + tweet.decode('utf-8') + ',' + str(t['favorite_count']) + ',' + str(t['retweet_count']) + ',' + reply + ',' + 
                str(len(t['entities']['user_mentions'])) + ',' + str(len(t['entities']['hashtags'])) + ',' + str(len(t['entities']['urls'])) + ',"' + 
                user_mentioned + '","' + hashtags + '"' + '\n')
            n_tweets += len(tweets)
            print('file_name: ', name, '| tweets:', len(tweets))
            print('users:', len(users), '| tweets:', n_tweets)  
    print('Complete', root)
print('Complete')
file.close()
tweets_file.close()

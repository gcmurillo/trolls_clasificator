#!/usr/bin/env python
# coding: utf-8

# import stuff
print("Importing stuff --------")
import pandas as pd

import numpy as np
from sklearn import feature_extraction
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
from nltk.stem.snowball import SnowballStemmer
from nltk import collocations
import re, string
import matplotlib
import matplotlib.pyplot as plt
from sklearn import preprocessing
from scipy import sparse
from sklearn import linear_model
plt.rcParams['figure.figsize'] = [16, 6]
print("End importations")

# Function to get datasets from s to f
def getxy(row_s, row_f, feature_cols=['content', 'followers', 'following', 'retweet'], label_col=['troll']):
    return df[feature_cols][row_s:row_f], df[label_col][row_s:row_f]

# reading trolls dataset and non-trolls dataset, and concat
print("reading datasets")
df_trolls = pd.read_csv("dataset_troll_all.csv")
df_users = pd.read_csv("dataset_users_trial.csv")
df = pd.concat([df_trolls, df_users])

# dropping Nan
df = df.dropna()

# creating set of stopwords in spanish and english
stopwords_set = stopwords.words('spanish')
stopwords_set.extend(stopwords.words('english'))
stopwords_set = set(stopwords_set)

tweets_hashtags = set([])
tweets_full_lemmas = set([])

def limpieza_tweet(tweets):
    # without icons
    tweet = tweets["content"].lower()
    sin_icons = re.sub(r'\$\w*','',tweet)
    # getting words
    tw_Tokenizer = TweetTokenizer(strip_handles=True, reduce_len=True)
    temp_tweet_list = tw_Tokenizer.tokenize(sin_icons)
    # without urls/direcciones
    sin_https = [re.sub(r'https?:\/\/.*\/\w*|t.co\/\w*','',i) for i in temp_tweet_list]
    # without hashtags
    tweets_hashtags.update(sin_https)
    sin_hashtags = [re.sub(r'#|https', '', i) for i in sin_https]
    # without punctations 
    sin_puntuacion = [re.sub(r'[' + string.punctuation + ']+', ' ', i) for i in sin_hashtags]
    sin_puntuacion = [re.sub(r'[“’—‘”–…]+', ' ', i) for i in sin_puntuacion]
    
    new_tweet = ' '.join(sin_puntuacion)
    filtrada_palabras = tw_Tokenizer.tokenize(new_tweet)
    filtrada_palabras = [re.sub(r'^\w\w?$', '', i) for i in filtrada_palabras]
    
    filtrada =' '.join(filtrada_palabras)
    tweet_final = re.sub(r'\s\s+', ' ', filtrada)
    # without stopwords
    tweet_final = tweet_final.strip(' ').split(' ')
    sin_stopwords = [i for i in tweet_final if (i.lower() not in stopwords_set and len(i)>1 and not i.isdigit())]
    # getting emojis
    emoticones = [i for i in tweet_final if (i.lower() not in stopwords_set and len(i)==1) ]
    # getting sentences
    tweets_full_lemmas.update(sin_stopwords)
    tweets["emoticones"] = ' '.join(emoticones)
    tweets["sin_stopwords"] = ' '.join(sin_stopwords)
    return tweets

# cleaning tweets
print("cleaning tweets")
df = df.apply(limpieza_tweet, axis=1)

print("Creating column content without stopwords")
texto = df["sin_stopwords"].str.lower().str.replace(r'\|', ' ').str.cat(sep=' ')
palabras = nltk.tokenize.word_tokenize(texto, language="spanish")
distribucion = nltk.FreqDist(palabras)
frecuencia = pd.DataFrame(distribucion.most_common(20),columns=['Palabra', 'Frequencia']).set_index('Palabra')

# shuffling the dataframe
df = df.sample(frac=1)

print("Getting training and testing sets")
X_train, y_train = getxy(0,136448)   # 136448 examples for training
X_test, y_test = getxy(136449,191400)  # 54951 examples for testing
print("Training examples: ", X_train.shape)
print("Testing examples: ", X_test.shape)

# Tokenizing words (text analysis)
print("Getting word tokenizer")
vocab_size=5000
tokenizer=feature_extraction.text.CountVectorizer(stop_words=stopwords_set, max_features=vocab_size)
tokenizer=tokenizer.fit(df['sin_stopwords'])

# Getting a matrix from words tokenized with tweets content
print("Getting matrix of tokenized words")
X_train_tok=tokenizer.transform(X_train['content']) 
X_test_tok=tokenizer.transform(X_test['content'])

# Normalizing followers and following
print("Normalize followers/following")
scaler_training = preprocessing.StandardScaler().fit(X_train[['followers','following']])
scaler_testing = preprocessing.StandardScaler().fit(X_test[['followers','following']])
print('Training followers/following means and scales: {}, {}'.format(scaler_training.mean_, scaler_training.scale_))

col_to_std = ['followers', 'following']
X_train[col_to_std]=scaler_training.transform(X_train[col_to_std])
X_test[col_to_std]=scaler_testing.transform(X_test[col_to_std])

print(X_train[col_to_std].head(), X_test[col_to_std])

# binarize outputs
bool_to_bin = lambda x: 1 if x else 0
print("Binarize outputs")
y_train['troll'] = y_train['troll'].apply(bool_to_bin)
y_test['troll'] = y_test['troll'].apply(bool_to_bin)

# binarize retweet colum
print("Binarize retweet column")
X_train['retweet'] = X_train['retweet'].apply(bool_to_bin)
X_test['retweet'] = X_test['retweet'].apply(bool_to_bin)


def concatenate_features(tok_matrix, data_df):
    """ concatenate the tokenized matrix (scipy.sparse) with other features """
    sparse_cols = sparse.csr_matrix(data_df[['followers', 'following', 'retweet']])
    combined = sparse.hstack([tok_matrix, sparse_cols])
    return combined

print("Combine features")
X_train_combined = concatenate_features(X_train_tok, X_train)
X_test_combined = concatenate_features(X_test_tok, X_test)

print("Training matrix dimensions: ", X_train_combined.shape)


# Training the model - Logistic Regresion
print("Logistic")
logic_model = linear_model.LogisticRegression().fit(X_train_combined, y_train['troll'])
print("Training Score:", logic_model.score(X_train_combined, y_train['troll']))
print("Testing Score:", logic_model.score(X_test_combined, y_test['troll']))

# Creating Neural Net
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation

# Configuring Neural Net
model = Sequential()  # 5003 inputs
model.add(Dense(1024, activation='relu', input_shape=X_train_combined.shape[1:])) # first layer
model.add(Dropout(0.7))
model.add(Dense(512, activation='relu'))  # second layer 1024 inputs
model.add(Dropout(0.5))
model.add(Dense(128, activation='relu'))  # third layer  512 inputs
model.add(Dense(1, activation='sigmoid'))  # last layer


print(model.summary())
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Converting to a numpy matrix
X_test_matrix = X_test_combined.todense()
X_train_matrix = X_train_combined.todense()

score = model.evaluate(X_test_matrix, y_test['troll'], verbose=0)
accuracy = 100*score[1]

print('Precisión en el conjunto de prueba: %.4f%%' % accuracy)

from keras.callbacks import ModelCheckpoint

checkpointer = ModelCheckpoint(filepath='trolls.model.best.hdf5', verbose=1, save_best_only=True)
hist = model.fit(X_train_matrix, y_train['troll'], batch_size=1024, nb_epoch=15, validation_split=0.2, callbacks=[checkpointer], verbose=1, shuffle=True)

model.load_weights('trolls.model.best.hdf5')
score = model.evaluate(X_test_matrix, y_test['troll'], verbose=0)
accuracy = 100*score[1]

# mostrar la precisión en prubea
print('Precisión durante la prueba: %.4f%%' % accuracy)


print('DEMO')
import tweepy
consumer_key = "fxGZYoJGBTtK8H2E8WO4eKdis"
consumer_secret = "Q3YY6ZJbURAopG7TmtY430XkfsUUa5qykeJhEfSNNqHEs1aP6E"
 
access_token = "227449172-qnfQfv9Rob8XaYgbfKyz1UccdHhwLZPCBa1EYsYU"
access_token_secret = "Uldgr5rzvuGaC77RVafaG86UlijFDrsebOpHrHYVD7TKk"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

tweets = {
    "Amparit65838995": 1119006511399952384,
    "geanmurillo": 1119488493053521921
}

for user, id in tweets.items():
    print(user)
    mini_df = {}
    tweet = api.get_status(id)
    mini_df['content'] = [str(tweet.text)]
    print("Tweet:", mini_df['content'])
    mini_df['followers'] = [tweet.user.followers_count]
    mini_df['following'] = [tweet.user.friends_count]
    mini_df['retweet'] = [1 if hasattr(tweet, 'retweeted_status') else 0]
    mini_df = pd.DataFrame.from_dict(mini_df)
    print("Getting matrix of tokenized words")
    tweet_tok=tokenizer.transform(mini_df['content']) 
    mini_df[col_to_std]=scaler_training.transform(mini_df[col_to_std])  # normalize followers/following
    mini_df_combined = concatenate_features(tweet_tok, mini_df)
    mini_df_numpy_vector = mini_df_combined.todense()
    pred = model.predict(mini_df_numpy_vector)
    # Prepare and send the response.
    digit = np.argmax(pred)
    print("Prediction:", digit)
    print(pred)
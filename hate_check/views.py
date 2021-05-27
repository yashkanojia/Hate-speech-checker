
from django.shortcuts import render, redirect
from django.urls import path
from django.http import HttpResponse
import re
import numpy as np
import pickle
from string import punctuation
import nltk
nltk.download('punkt')
from nltk.corpus import stopwords
from textblob import TextBlob
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import tweepy as tw
nltk.download('stopwords')


def index(request):
    if request.method == 'POST':
        url = request.POST.get('username')
        b = check_validtweet(url)
        if(b):
            text = get_tweet_text(url)
            pred = predict(text)
            keywords = ""
            print(pred)
            if(pred == "HATE"):
                pred=pred+" : Please don't share this further."
                l1 = find_characteristics(text)
                keywords += "keywords from tweets are:";
                for i in l1:
                    keywords += " " + i
                print(l1)
            if(pred == "NOT HATE"):
                pred=pred+" : you can share this tweet further."
            return render(request, "page.html", {'username': pred, 'text': text, 'keywords': keywords})
        else:
            return HttpResponse("inavlid url..sorry")
    else:
        return render(request, "index.html")


def page(request):
    return render(request, "page.html")


def find_characteristics(text):
    l1 = set()
    parameters = 0
    with open('hate_check/parameters.pickle', 'rb') as read:
        parameters = pickle.load(read)
    text = text.split(" ")
    for i in text:
        if(i.lower() in parameters):
            l1.add(i)
    for j in text:
        b = TextBlob(j.lower())
        if(b.sentiment.subjectivity > 0 and b.sentiment.polarity < 0):
            l1.add(j.lower())
    return list(l1)


def check_validtweet(url):
    pattern = "^https://twitter.com/"
    x = re.findall(pattern, url)
    if x:
        file = url.split("/")
        if(len(file) == 6):
            return True
        else:
            return False
    else:
        return False


def get_tweet_text(url):
    consumer_key = "FvquxZOzpY8T4J0Q01XQFhaeI"
    consumer_secret = 'TRwUZ7zLOVl2aNDTNEjB3LYQo0jTv6jdPV7vZnNHETmkOtGuPS'
    access_token = '1802379589-oN2X9Fc85KNoOIpLbv7RNayqbsw8dvXkXGk6gXi'
    access_token_secret = 'snwKx7pfBF0Tlww1ONxjFVBVzTjpr9PW1x95femY6cTaW'
    auth = tw.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tw.API(auth, wait_on_rate_limit=True)
    url = url.split("/")
    tweetid = np.uint64(url[-1])
    text = api.get_status(tweetid, tweet_mode='extended').full_text
    return text


def stringtolist(text, parameters):
    text = text.lower()
    text = word_tokenize(text)
    text = ' '.join([c for c in text if c not in punctuation])
    Words = text.split()
    ps = PorterStemmer()
    root_sent = ""
    for w in Words:
        rootWord = ps.stem(w)
        root_sent += " "
        root_sent += rootWord
    Words = rootWord.split()
    Words = [word for word in Words if word not in stopwords.words(
        'english') and "'" not in word]
    Words = " ".join([c for c in Words if sum(TextBlob(c).sentiment) != 0])
    text = text.split(" ")
    l = []
    for j in range(len(parameters)):
        if parameters[j] in text:
            l.append(1)
        else:
            l.append(0)
    return l


def predict(text):
    #loaded_model = pickle.load(open("predict.sav", 'rb'))
    loaded_model = pickle.load(open("hate_check/rf_model.sav", 'rb'))
    parameters = 0
    with open('hate_check/parameters.pickle', 'rb') as read:
        parameters = pickle.load(read)
    test = stringtolist(text, parameters)
    pred = (loaded_model.predict([test]))[0]
    if(pred > 0):
        return "HATE"
    return "NOT HATE"

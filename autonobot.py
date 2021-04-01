# Database access imports
from twitter.req import getTweets
from database.access import Database
from viz.sentiment import getSentiment, plotSentiment

from datetime import datetime, timezone, timedelta
import tweepy
import os
import requests as r
from dotenv import load_dotenv
from gensim.summarization import summarize


import nltk
from nltk import sent_tokenize
nltk.download('punkt')
SQL_DB = './database/trending.db'

# =============================================================================
# Notes:
#     Do sentiment analysis of popular tweets about that topic
#     Some sort of visualization over time
#     Check rate-limit status
#     Add state popularity of topic
#     Function for checking if relevant summary can be found
#     Include topic of conversation - maybe use this to filter unrelated news
# https://towardsdatascience.com/real-time-twitter-sentiment-analysis-for-brand-improvement-and-topic-tracking-chapter-2-3-1caf05346721
# =============================================================================

# Twitter API info
load_dotenv()
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_KEY = os.getenv('ACCESS_KEY')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
RAPID_KEY = os.getenv('RAPID_KEY')

# Using tweepy for trends
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# Using twitter API for v2 search features


# Set recency for tweets
recency = 6  # 6 hours
lastStamp = datetime.now(timezone.utc) - timedelta(hours=recency)
recentTime = lastStamp.astimezone().isoformat()

# Connect to SQL database
conn = Database.sqlConnect(SQL_DB)
Database.createTable(conn)
currentTrends = Database.loadDb(conn)

queue = []
links = set()
summaries = set()
scores = []


def manageTrends():
    global currentTrends, queue

    # Tweet volume threshold is currently set to 100,000
    tweet_volume = 100000

    trends = [trend['name']
              for trend in api.trends_place(id=2352824)[0]['trends']
              if type(trend['tweet_volume']) == int
              and trend['tweet_volume'] >= tweet_volume
              and trend['promoted_content'] is None
              and '#' not in trend['name']]

    for obj in trends:
        if obj not in currentTrends:
            queue.append(obj)

    return trends


def getInfo(trend, page):
    global links
    global summaries
    global recentTime
    global scores
    global RAPID_KEY

    url = "https://rapidapi.p.rapidapi.com/v1/search"
    querystring = {"q": trend,
                   "sort_by": "relevancy",
                   "lang": "en",
                   'page_size': 5,
                   "page": page,
                   'country': 'US',
                   'from': recentTime}

    headers = {
        'x-rapidapi-key': RAPID_KEY,
        'x-rapidapi-host': "newscatcher.p.rapidapi.com"
        }

    re = r.request("GET", url, headers=headers, params=querystring)

    for item in re.json()['articles']:
        if item['link'] not in links:
            links.add(item['link'])
            summaries.add(item['summary'])
            scores.append([item['summary'], item['_score']])

    return


def getSummary(group):
    ranked = sent_tokenize(summarize(' '.join(group), ratio=0.1))

    for i, sent in enumerate(ranked):
        if len(sent) <= 280:
            return sent

    return ranked[0]


def aggTweets(topic):

    tweets = []
    next_token = ''

    for i in range(10):  # CHANGE THIS
        data = getTweets(topic, next_token)
        next_token = f'next_token={data[1]}'

        for tweet, user in zip(data[0], data[2]):
            tweets.append([tweet, user])

    return tweets


def siftTweets(tweets):
    text = []
    locations = []

    for i, tweet in enumerate(tweets):

        retweets = tweet[0]['public_metrics']['retweet_count']
        words = tweet[0]['text']

        if retweets == 0:
            mult = 1
        else:
            mult = retweets

        for j in range(mult):
            text.append(words)

    return text, locations


def postTweet(status, path):

    api.update_with_media(path,
                          status=status)


def main():

    trends = manageTrends()  # Get trends
    print(trends, queue)
    try:
        top = queue.pop(0)  # Pull top trend from queue
    except IndexError:
        print('No new trends')
        return
    rem = list(set(queue) ^ set(trends))  # Update rep. trends

    # Refresh database
    Database.deleteAll(conn)

    # Write new trends to database
    Database.writeDb(conn, rem)
    conn.commit()
    conn.close()

    [getInfo(top, i) for i in range(1, 6)]

    summary = getSummary(summaries)

    tweet_text = f'TRENDING – {top}\n\n{summary}'
    print(tweet_text)

    tweets = aggTweets(top)
    text = siftTweets(tweets)[0]
    data = [getSentiment(tweet) for tweet in text]

    plotSentiment(data, top)

    postTweet(tweet_text, './viz/plots/sentPlot.png')

    print('Success!')

    return tweet_text


if __name__ == '__main__':
    # est = temp('Kobe')
    main()

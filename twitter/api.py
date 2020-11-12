import requests
from autonobot import recentTime, BEARER_TOKEN
recentTime = recentTime
BEARER_TOKEN = BEARER_TOKEN


class Twitter:

    def create_url(topic, next_token):
        global recentTime

        query = topic + ' -is:retweet -is:quote lang:en'
        max_results = 'max_results=100'
        tweet_fields = "tweet.fields=lang,public_metrics"
        expansions = 'expansions=author_id'
        user_fields = 'user.fields=location,username'
        start_time = f'start_time={recentTime}'

        if next_token != '':
            url = ('https://api.twitter.com/2/tweets/search/recent?'
                   'query={}&{}&{}&{}&{}&{}&{}').format(
                       query, tweet_fields, max_results,
                       start_time, next_token, user_fields, expansions
                       )

        else:
            url = ('https://api.twitter.com/2/tweets/search/recent?'
                   'query={}&{}&{}&{}&{}&{}').format(
                       query, tweet_fields, max_results, start_time,
                       user_fields, expansions
                       )

        return url

    def create_headers(bearer_token):
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
        return headers

    def connect_to_endpoint(url, headers):
        response = requests.request("GET", url, headers=headers)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

    def getTweets(topic, next_token):
        global BEARER_TOKEN
        url = Twitter.create_url(topic, next_token)
        headers = Twitter.create_headers(BEARER_TOKEN)
        json_response = Twitter.connect_to_endpoint(url, headers)
        res = (json_response['data'],
               json_response['meta']['next_token'],
               json_response['includes']['users'])
        return res

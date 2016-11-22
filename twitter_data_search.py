import tweepy
from tweepy import OAuthHandler
from tweepy.parsers import JSONParser
import json
import private_tokens
import custom_stream_listener
import util_constants as uc
from datetime import datetime


class TwitterDataSearcher:

    def search_and_collect_tweets(self, params):
        searched_tweets = []
        last_id = -1
        tweets_count = 0
        call_count = 0
        call_count_max = 50
        file_name = 'historical_tweets.json'

        print('Collecting tweets')
        #authentication
        auth = OAuthHandler(private_tokens.consumer_key, private_tokens.consumer_secret)
        auth.set_access_token(private_tokens.access_token, private_tokens.access_secret)
        api = tweepy.API(auth)

        last_id = self.find_last_id(file_name)
        last_saved_id = last_id

        with open(file_name, 'a') as f:

            while call_count < call_count_max:
                try:
                    new_tweets = api.search(q=search_params['q'], \
                                            geocode=search_params['geocode'],\
                                            count=200, max_id=str(last_id - 1),\
                                            since_id=24012619984051000)

                    call_count += 1

                    print('call count: {0}'.format(call_count))

                    if not new_tweets:
                        print('Exiting because of no new tweets')
                        break

                    else:
                        last_id = new_tweets[-1].id

                        for tweet in new_tweets:
                            if self.is_dengue_tweet(tweet) and self.has_location_data(tweet) and tweet.id > last_saved_id:
                                # print(tweet.place)
                                # print(tweet.coordinates)
                                f.write(json.dumps(tweet._json)+ '\n')
                                tweets_count += 1

                                if tweets_count % 10 == 0:
                                    print('Collected {0} tweets'.format(tweets_count))

                except tweepy.TweepError as e:
                    # depending on TweepError.code, one may want to retry or wait
                    # to keep things simple, we will give up on an error
                    print(e)
                    break

    def find_last_id(self, file_name):
        max_id = -1
        with open(file_name, 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if tweet['id'] > max_id:
                    max_id = tweet['id']

        print('Last saved tweet id in {0} is {1}'.format(file_name, max_id))
        return max_id

    def is_dengue_tweet(self, tweet):
        keywords = ['dengue', 'Dengue', 'dengosa', 'Dengosa']
        for k in keywords:
            if k in tweet.text:
                return True

        return False

    def has_location_data(self, tweet):
        # return True
        return tweet.place != None or tweet.coordinates != None

if __name__== '__main__':
    #not sure if search query is case sensitive
    search_params = {'q' : 'dengue OR Dengue OR dengosa or Dengosa',
                     'geocode' : '-10,-56,5000km'}

    tds = TwitterDataSearcher()
    tds.search_and_collect_tweets(search_params)

#!/usr/bin/python
# Tatsiana Maskalevich
import tweepy
import time


""" inspired by http://peter-hoffmann.com/2012/simple-twitter-streaming-api-access-with-python-and-oauth.html"""
# your twitter credentials
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""

class CustomStreamListener(tweepy.StreamListener):
    def on_status(self, status):
    	try: 
        	print status.text
        except Exception, e:
            # Catch any unicode errors while printing to console
            # and just ignore them to avoid breaking application.
            pass
    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream
    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

stream_api = tweepy.streaming.Stream(auth, CustomStreamListener()) 
#random sample of tweets
stream_api.sample()

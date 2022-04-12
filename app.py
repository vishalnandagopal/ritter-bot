from time import ctime
from os import getenv
from tweepy import Client
from dotenv import load_dotenv
import feedparser as fp

load_dotenv(r"owasp-tweet-bot.env")

# get the necessary tokens from .env file
BT = getenv("Bearer_Token")
AK = getenv("API_Key")
AKS = getenv("API_KEY_SECRET")
AT = getenv("Access_Token")
ATS = getenv("Access_Token_Secret")

list_of_rss_feeds = []

def feed_to_json(url: str):
    # converts feedparser output to a json file for better readability
    from json import dumps
    feed = fp.parse(url)
    to_dump = dumps(feed, indent=1, sort_keys=True)
    f = open("feed.json", "a")
    f.write(to_dump)
    f.close()

def dict_for_tweets(tweet_details: list) -> dict:
    # creates a dictionary of details containing text, readable time and epoch time
    sub_dict_for_tweet = {}
    sub_dict_for_tweet["text"] = tweet_details[0]
    sub_dict_for_tweet["time"] = tweet_details[1]
    return sub_dict_for_tweet

def shorten_tweet_text(text: str) -> str:
    # shortens the text to 276 characters and appends '...' at the end. (Twitter's character limit is 280)
    return text[0:276] + "..."


class TwitterUser:
    def __init__(self, bearer_token=None, api_key=None, api_key_secret=None, access_token=None, access_token_secret=None) -> None:
        self.BEARER_TOKEN = bearer_token
        self.API_KEY = api_key
        self.API_KEY_SECRET = api_key_secret
        self.ACCESS_TOKEN = access_token
        self.ACCESS_TOKEN_SECRET = access_token_secret
        self.authenticated_user = Client(self.BEARER_TOKEN, self.API_KEY, self.API_KEY_SECRET, self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET)

    def tweet_out(self, tweet_text=None):
        if (0 < len(tweet_text) <= 280):
            tweeting = self.authenticated_user.create_tweet(text=tweet_text)
            f = open("tweet-ids.txt", "a")
            f.write(tweeting[0]["id"] + "\n")
            f.close()
            g = open("tweet-details.txt", "a")
            dict_to_write = {tweeting[0]["id"]: dict_for_tweets([tweet_text, ctime()])}
            g.write(str(dict_to_write) + "\n")
            g.close()
        else:
            return self.tweet_out(shorten_tweet_text(tweet_text))

    def search_query(self, query="") -> dict:
        search_results = self.authenticated_user.search_recent_tweets(query, sort_order="relevancy", max_results=20)
        return search_results

    def read_rss_and_tweet(self, url: str):
        # read rss feed and return details to tweet out
        feed = fp.parse(url)
        if (feed["status"] == 200):
            # dict > list > dict > ['title']
           #for i in range(len(feed["entries"])):
            for i in range(2):
                # runs loop for first range() articles in the feed
                text_to_tweet_out = ( (feed["entries"][i]["title"]) + " " + feed["entries"][i]["link"] )
                self.tweet_out(text_to_tweet_out)
        else:
            pass

user = TwitterUser(BT, AK, AKS, AT, ATS)

for feed_url in list_of_rss_feeds:
    user.read_rss_and_tweet(feed_url)
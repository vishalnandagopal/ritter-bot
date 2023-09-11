from .os_functions import *
import tweepy

class TwitterUser:
    def __init__(self) -> None:
        bearer_token, api_key, api_key_secret, access_token, access_token_secret = get_api_keys()
        self.authenticated_user = tweepy.Client(bearer_token, api_key, api_key_secret, access_token, access_token_secret,wait_on_rate_limit=True)
    
    # All the below functions are tied to a user. They're supposed to be accessed by an authenticated user ( user.function() ), and are twitter specific.
    def tweet_out(self, tweet_text: str = '', in_reply_to_id:int = 0) -> tuple:
        if 0 < len(tweet_text) <= 280:
            if not variables.testing_mode:
                try:
                    if not in_reply_to_id:
                        tweeting = self.authenticated_user.create_tweet(text=tweet_text)
                    else:
                        tweeting = self.authenticated_user.create_tweet(text=tweet_text, in_reply_to_tweet_id=in_reply_to_id)
                    variables.tweet_count += 1
                except Exception as e:
                    if "duplicate content" in str(e):
                        tweeting = (
                            {
                                'id': 0,
                                'text': tweet_text
                                },
                                ["duplicate_content"]
                                )
                    else:
                        tweeting = (
                            {
                                'id': 0,
                                'text': tweet_text
                                },
                                [str(e)]
                                )
                        write_to_file(str(e) + "\n",'important-errors.txt')
                        raise e
            else:
                '''
                tweeting is a list of lists returned by Client.create_tweet().
                Replicating same format here when testing_mode==False
                example format: Response(data={"id": "1517736731571007488", "text": "Researcher Releases PoC for Recent Java Cryptographic Vulnerability https://t.co/uOOs0awlIU"}, includes={}, errors=[], meta={})
                '''
                tweeting = (
                    {
                        'id': 0,
                        'text': tweet_text,
                    },
                    ["testing_mode=True"]
                )
            return tweeting
        else:
            return self.tweet_out(shorten_tweet_text(tweet_text),in_reply_to_id)
    
    
    def tweet_feed(self, feed, description_from_html:bool = False):

        if variables.testing_mode:
            if len(feed['entries']) > 2:
                urls_to_tweet = 2
            else:
                urls_to_tweet = 1
        else:
            # runs loop for first range() articles in the feed
            urls_to_tweet = len(feed['entries'])
        
        for i in range(urls_to_tweet):
            # # When feedparser parses a RSS feed, the output is in the format dict > list > dict > ["title"]
            
            url = feed['entries'][i]['link']
            if new_link_validator(url):
                entry = feed['entries'][i]
                (url, sentences_to_tweet, type_of_tweet,read_more) = what_to_tweet(entry, description_from_html)
                tweet_ids=[0]
                for sentence in sentences_to_tweet:
                    tweeting = self.tweet_out(sentence,in_reply_to_id=tweet_ids[-1])
                    tweet_ids.append(tweeting[0]['id'])
                if read_more:
                    tweeting = self.tweet_out("Read more at " + url,in_reply_to_id=tweet_ids[-1])
                    tweet_ids.append(tweeting[0]['id'])
                print(f"{tweeting[0]['id']} is the tweet ID for {url}")
                log_to_file(tweet_ids, url, type_of_tweet, sentences_to_tweet)
                
                time.sleep(variables.time_to_wait_after_tweeting_a_url_in_seconds)
            else:
                #print(f"Already been tweeted about - {url}")
                # Can also break, if the feed is sorted chronologically. If one URL has already been tweeted out, it means the all the next URLs in the feed have also been tweeted out
                pass
    
    
    def search_query(self, query="") -> dict:
        # searches the given query on twitter
        search_results = self.authenticated_user.search_recent_tweets(query, sort_order='relevancy', max_results=100)
        return search_results
    
    
    def delete_tweet(self, to_delete=None, all_ids_in_log_files:bool = False):
        # can provide a list or tuple of tweet_ids, a single tweet_id:int or ask it to delete all tweet_ids in 'log_files\tweet-ids.txt' (can be used for deleting all tweets easily)
        if isinstance(to_delete,int):
            # deletes the tweet corresponding to the tweet_id given to the function as to_delete
            time.sleep(1)
            return ( self.authenticated_user.delete_tweet(to_delete) )
        elif isinstance(to_delete,list) or isinstance(to_delete,tuple):
            # deletes every tweet in the list to_delete supplied to the function
            for tweet_id in to_delete:
                self.authenticated_user.delete_tweet(tweet_id)
        elif ( (all_ids_in_log_files) and (to_delete==None) ):
            list_of_tweet_ids = read_file_and_ignore_comments('tweet-ids.txt','log_files')
            self.delete_tweet(to_delete=list_of_tweet_ids)
        else:
            print(f"Wrong type of argument passed to delete_tweet(). to_delete must be an int or a list, but it currently is of type {type(to_delete)}")

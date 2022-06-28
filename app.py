import tweepy
import feedparser
import time
import os
import json

# Functions defined from the next line up to the TwitterUser class are generic and not specific to Twitter. They're made for the project but can be used anywhere else.

def read_and_check_config(config_error_count:int=0) -> tuple[bool,tuple[bool,bool,bool,bool,bool,bool,bool,bool,bool,int,int,int,bool,dict,list,bool]]:
    print("Reading config file")
    with open("config.json", "r") as f:
            config = json.load(f)
    
    try:
        config_values = (
            config["run_program"], # -------------------------------- 0
            config["cron_job_mode"], # -------------------------------1
            config["testing_mode"], # --------------------------------2
            config["tweet_only_link"], # -----------------------------3
            config["tweet_description"], # ---------------------------4 
            config["tweet_summarized_article"], # --------------------5
            config["move_log_files"], # ------------------------------6
            config["delete_old_log_files"], # ------------------------7
            config["delete_important_errors"], # ---------------------8
            config["time_to_wait_after_a_tweet_in_seconds"], # -------9
            config["run_program_every_x_seconds"], # ----------------10
            config["time_to_wait_when_not_running_in_seconds"], # ---11
            config["ignore_https"], # -------------------------------12
            config["rss_feeds_to_fetch"], # -------------------------13
            config["dont_summarize_these_urls"], # ------------------14
            config["reset_config_to_default"] # ---------------------15
            )
    except (KeyError,FileNotFoundError,json.JSONDecodeError):
        (valid_config,config_error_count) = config_error(config_error_count)
        read_and_check_config(config_error_count)
    
    # Checks if the important properties in the config.json file are valid by seeing if their types are appropriate
    if not ( (isinstance(config_values[0],bool)) and (isinstance(config_values[1],bool)) and (isinstance(config_values[2],bool)) and (isinstance(config_values[3],bool)) and (isinstance(config_values[4],bool)) and (isinstance(config_values[5],bool)) ):
        valid_config = False
    elif not ( (isinstance(config_values[10],int)) and (isinstance(config_values[11],int)) ):
        valid_config = False
    elif not ( (isinstance(config_values[13],dict))):
        valid_config = False
    else:
        valid_config = True
    
    return (valid_config, config_values)


def write_to_file(stuff_to_write: str, file_name: str, directory:str = '', mode :str = 'a', set_pointer_position_from_end_and_truncate:int=0):
    # Writes stuff_to_write string to file_name, defaults to append mode. Directory can also be a sub-directories (even if parent directory does not exist). Eg: old_log_files\log_files
    try:
        if directory:
            file_path = directory + "\\" + file_name
        else:
            file_path = file_name
        with open(file_path, mode) as f:
            if set_pointer_position_from_end_and_truncate > 0:
                #This sets the pointer to 1 character from the end. Here, 2 is the whence meaning end of file.
                f.seek(-set_pointer_position_from_end_and_truncate,2)
                f.truncate()
            f.write(stuff_to_write)
    except FileNotFoundError:
        make_dir(directory)
        write_to_file(stuff_to_write,file_name,directory,mode,set_pointer_position_from_end_and_truncate)


def read_file_and_ignore_comments(file_name: str, directory:str = '') -> list:
    # reads the file in the given file path and returns a list of all lines that do not start with "#" in the file
    l1 = []
    try:
        if directory:
            file_path = directory + "\\" + file_name
        else:
            file_path = file_name
        with open(file_path,'r') as f:
            l = f.readlines()
        for line in l:
            if not line.startswith("#"):
                line1 = line.rstrip("\n")
                l1.append(line1)
    except FileNotFoundError:
        write_to_file("",file_name,directory,'x')
    return l1


def make_value_false_in_config(key_to_make_false:str):
    # sets the value of the given key as false again. Used to prevent the program from getting stuck in a loop where it keeps deleting old_log_files or keeps reloading api_keys 
    with open('config.json', "r") as f:
        config = json.load(f)
        config[key_to_make_false] = False
        to_dump = json.dumps(config,indent=4)
        write_to_file(to_dump,'config.json','',mode='w')
        print("Changed config.json")


def make_dir(dir_name:str):
    # Makes a directory with the given name in the root directory.
    try:
        # os.makedirs can create parent directories too, if they don't exist when creating a sub directory.
        os.makedirs(dir_name)
    except FileExistsError:
        print(f"Tried making {dir_name} directory, but it already exists")


def move_file_or_dir(current_name:str, dir_to_move_to:str, add_ctime_to_name_after_moving:bool = False):
    try:
        if add_ctime_to_name_after_moving:
            new_name = dir_to_move_to + '\\' + current_name + (f" at {time.ctime()}").replace(":","-",3)
            os.rename(current_name, new_name)
        else:
            new_name = dir_to_move_to + '\\' + current_name
            os.rename(current_name, new_name)
    except FileNotFoundError:
        make_dir(current_name)
        make_dir(dir_to_move_to)
        move_file_or_dir(current_name, dir_to_move_to,add_ctime_to_name_after_moving)


def delete_file_or_folder(path:str):
    try:
        os.remove(path)
        print(f"Deleted {path}")
    except FileNotFoundError:
        print(f"Tried to delete {path} but it does not exist")
    except PermissionError:
        try:
            import shutil
            shutil.rmtree(path)
            print(f"Deleted contents of {path}")
        except NotADirectoryError:
            delete_file_or_folder(path)
        except FileNotFoundError:
            print(f"Tried to delete {path} but it does not exist")


def check_if_exists_in_directory(file_name:str,directory:str='') -> bool:
    current_working_dir =  os.getcwd()
    try:
        if directory:
            os.chdir(directory)
        return file_name in os.listdir()
    finally:
        os.chdir(current_working_dir)


def check_if_file_is_empty(file_name:str,directory:str='') -> bool:
    if directory:
        file_path = directory + "\\" + file_name
    else:
        file_path = file_name
    try:
        return os.path.getsize(file_path) == 0
    except FileNotFoundError:
        return True


def move_or_clear_files(delete_old_log_files:bool = False, move_log_files:bool = False, move_config:bool = False, delete_important_errors:bool = False) -> str:
    if move_config:
        if check_if_exists_in_directory('config.json'):
            move_file_or_dir('config.json','old_log_files')
            reset_config()
    else:
        if delete_old_log_files:
            delete_file_or_folder('old_log_files')
            make_value_false_in_config('delete_old_log_files')
        if delete_important_errors:
            delete_file_or_folder('important-errors.txt')
            make_value_false_in_config('delete_important_errors')
        if move_log_files:
            if check_if_exists_in_directory('log_files'):
                move_file_or_dir('log_files','old_log_files',True)
                make_value_false_in_config('move_log_files')


class GlobalVariables:
    def __init__(self) -> None:
        # Settings for the bot (flags). Assigns the values from config.json
        self.read_config_and_set_variables() 

    def read_config_and_set_variables(self):

                (
            self.valid_config,
            
            (
                self.run_program,
                self.cron_job_mode,
                self.testing_mode,
                self.tweet_only_link,
                self.tweet_description,
                self.tweet_summarized_article,
                self.move_log_files,
                self.delete_old_log_files,
                self.delete_important_errors,
                self.time_to_wait_after_a_tweet_in_seconds,
                self.run_program_every_x_seconds,
                self.time_to_wait_when_not_running_in_seconds,
                self.ignore_https,
                self.rss_feeds_to_fetch,
                self.dont_summarize_these_urls,
                self.reset_config_to_default
                )

            ) = read_and_check_config()


variables = GlobalVariables()

def reset_config():
    default_config = read_file_and_ignore_comments('default-config.json')
    delete_file_or_folder('config.json')
    for line in default_config:
        write_to_file(line + "\n",'config.json')
    print("config.json has been reset")


def config_error(config_error_count:int) -> tuple[bool,int]:
    # Runs when the config.json file has some error or is not properly formatted. Sets run_program and config_valid to false.
    error = f"config.json does not seem to be a valid json file. Time of error is {time.ctime()}"
    print(error)
    
    write_to_file( (error + "\n"),'important-errors.txt')
    
    if config_error_count == 9:
        error = f"Read invalid config too many times. Will reset config if it is invalid after reading it once again. Time of error is {time.ctime()}"
        print(error)
        write_to_file( (error + "\n"),'important-errors.txt')
    
    if config_error_count == 10:
        reset_config()
        error =  f"Reset config.json because of invalid config too many times. Time of error is {time.ctime()}"
        print(error)
        write_to_file( (error + "\n"),'important-errors.txt')
        return [False,0]
    
    print(f"Waiting for 10 minutes before reading config.json again. Have read invalid config {config_error_count} time(s) now")

    config_error_count += 1

    try:
        time.sleep(variables.time_to_wait_when_not_running_in_seconds)
    except NameError:
        time.sleep(21600)
    config_error(config_error_count)


def new_link_validator(url: str) -> bool:
    # Checks if the url has already been tweeted out by reading all lines in 'log_files\tweeted-urls.txt'
    already_tweeted_urls = read_file_and_ignore_comments('tweeted-urls.txt','log_files')
    return not url in already_tweeted_urls


def dict_for_tweets(ids :list, type_of_tweet: str, tweet_text) -> dict:
    # creates a dictionary of details containing text, readable time and epoch time
    tweeted_out_time = time.ctime() # Not the exact tweeted out time since this is the time when the dict_for_tweets is called, and not when the text is tweeted out. But good enough

    sub_dict_for_tweet = {}
    sub_dict_for_tweet['id'] = str(ids)
    sub_dict_for_tweet['text'] = str(tweet_text)
    sub_dict_for_tweet['time'] = tweeted_out_time
    sub_dict_for_tweet['type'] = type_of_tweet
    return sub_dict_for_tweet


def get_tag_data(html_text: str, tag: str) -> str:
    # This gets the data of the provided tag from the html text. Separate function to ensure can easily add more tags other than meta tag
    tag_string = ""
    length = len(html_text)
    for i in range(length):
        if (html_text[i : (i + (len(tag)))]) == tag:
            for j in range(i, length):
                if html_text[j] == ">":
                    tag_string = html_text[i : j + 1]
                    break
    if tag_string == "":
        print(f"{tag} not found, try another tag")
    return tag_string


def get_url_description_from_html(url:str) -> str:
    # Fetches description of a url from by parsing it's html. To be used in case the description is not included in the RSS feeds.

    # This works only for meta tags where the data is stored in content="". Can change it easily
    # Could have done this using beautifulsoup4 but wanted to do it on my own. bs4 code included below
    """
    from bs4 import BeautifulSoup
    import requests
    
    html_text = requests.get("https://www.scrapingbee.com/blog_to_json/python-web-scraping-beautiful-soup/").content
    
    soup = BeautifulSoup(html_text, 'html.parser')
    
    description = soup.find('meta', attrs={"name": "description"})
    print(description['content'])
    
    # The description of the page
    description = soup.find("meta", property="description")
    
    # The text of the page
    print(description.get_text())
    """
    import requests
    try:
        response = requests.get(url)
        html_text = response.text
        if response.status_code != 200:
            print("Error fetching page")
        else:
            tag_string = get_tag_data(html_text, "<meta name=\"description\"")
            if tag_string == "":
                tag_string = get_tag_data(html_text, "<meta property=\"twitter:description\"")
                if tag_string == "":
                    tag_string = get_tag_data(html_text, "<meta property=\"og:description\"")
                    print(f"{url} does not have a description meta tag")
            tag_content = ""
            for i in range(len(tag_string)):
                if (tag_string[i : (i + 7)]) == "content":
                    for j in range(i + 9, len(tag_string)):
                        if tag_string[j] == '"' or tag_string[j] == "'":
                            tag_content = tag_string[i + 9 : j]
                            break
            return tag_content
    except Exception as e:
        if ("NewConnectionError" in str(e)) or ("ConnectionError" in str(e)):
            print("Prolly not connected to the internet")
            return tag_content
        else:
            print("Connected to the internet but some other exception exception")


def summarize_article(url: str) -> tuple[str]:
    # Uses the newspaper module to generate a summary of the article. Fetches the article, parses it and then summarises it with the help of nltk. Returns a tuple of sentences in the summarized verion
    # not perfect but pretty good

    from newspaper import Article

    article = Article(url)
    article.download()
    article.parse()
    try:
        article.nlp()
    except LookupError:
        import nltk
        nltk.download("punkt",quiet=True)
        article.nlp()
    summarized_text = article.summary
    return summarized_text


def split_into_sentences(summarized_text: str) -> list:
    import nltk
    nltk.download("punkt",quiet=True)
    single_sentences = nltk.tokenize.sent_tokenize(summarized_text)
    already_added,sentences_to_tweet = [],[]
    for i in range(len(single_sentences)):
        if (i not in already_added):
            (already_added,sentences_to_tweet) = check_merge_sentences(single_sentences, i, already_added, sentences_to_tweet)
    return sentences_to_tweet


def check_merge_sentences(single_sentences: list, index: int, already_added: list, sentences_to_tweet:list, count: int = 2) -> tuple[list,list]:
    length = 0
    for i in range(count):
        try:
            length += len(single_sentences[index+i]) + 1
        except IndexError:
            length = 276
    if length < 275:
        check_merge_sentences(single_sentences, index, already_added,sentences_to_tweet,count+1)
    else:
        sentence = single_sentences[index]
        if (len(sentence) > 280) and (count == 2):
            sentences_to_tweet.append(sentence[:277] + "...")
            single_sentences[index] = sentence[277:]
            check_merge_sentences(single_sentences, index, already_added,sentences_to_tweet,count)
        else:
            sentences_to_tweet.append(sentence)
        already_added.append(index)
        for i in range(count-2):
                sentence += " " + single_sentences[index+i+1]
                already_added.append(index+i+1)
        sentences_to_tweet.append(sentence)
    return (already_added, sentences_to_tweet)

def tld(url:str) -> str:
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    return domain

def what_to_tweet(entry:dict, description_from_html:bool) -> tuple[str,list,str]:
    # Default mode is to tweet the title + URL of the article. To change default, edit config.json

    url = entry['link']

    if variables.tweet_only_link:
        sentences_to_tweet = (url)
        type_of_tweet = 'link'
        
    elif variables.tweet_description:
        if description_from_html:
                description_text = get_url_description_from_html(url)
        else:
            try:
                description_text = entry['description']
            except KeyError:
                # Description of the article isn't present in the the RSS feed
                description_text = get_url_description_from_html(url)
        sentences_to_tweet = split_into_sentences(description_text)
        sentences_to_tweet.insert(0,entry['title'])
        type_of_tweet = 'description'
         
    elif variables.tweet_summarized_article:
        if tld(url) not in variables.dont_summarize_these_urls:
            sentences_to_tweet =  split_into_sentences(summarize_article(url))
        else:
            description_text = get_url_description_from_html(url)
            sentences_to_tweet = split_into_sentences(description_text)
        sentences_to_tweet.insert(0,entry['title'])
        type_of_tweet = 'summary'
        
    else:
        sentences_to_tweet = entry['title']
        type_of_tweet = 'title'
    
    return (url, sentences_to_tweet, type_of_tweet)


def shorten_tweet_text(text: str) -> str:
    # Shortens the text to 276 characters and appends "..." at the end. (Twitter's character limit is 280)
    return text[0:276] + "..."


def log_to_file(ids: list, url: str, type_of_tweet: str, tweet_text):
    # takes care of logging the details of the tweet to text files for future use
    
    #removes the 1st 0 from the list of tweet_ids
    ids.pop(0)
    
    # log_to_jsons the IDs of the tweets to tweet-ids.txt
    for tweet_id in ids:
        write_to_file( (str(tweet_id) + "\n"), 'tweet-ids.txt','log_files')

    # log_to_jsons all the URLs that have been tweeted out
    write_to_file( (url + "\n"), 'tweeted-urls.txt','log_files')
    
    # log_to_jsons a json of tweet details to tweet-details.json
    # used to log_to_json a str(dictionary) but decided json is better
    dict_to_write = { url: dict_for_tweets(
        ids,
        type_of_tweet,
        tweet_text
        )
    }
    
    if check_if_file_is_empty('tweet-details.json','log_files'):
        to_dump = json.dumps(dict_to_write, sort_keys=True,indent=4)
        write_to_file((to_dump), 'tweet-details.json','log_files')
    else:
        to_dump = "," + json.dumps(dict_to_write, sort_keys=True,indent=4).lstrip("{")
        write_to_file((to_dump).encode('ascii') , 'tweet-details.json','log_files',mode='ab',set_pointer_position_from_end_and_truncate=2)


def feed_to_json(url: str):
    # converts feedparser output to a json file for better readability. To better understand what fields to parse and tweet out when testing
    from json import dumps
    feed = feedparser.parse(url)
    to_dump = dumps(feed, indent=1, sort_keys=True)
    write_to_file(to_dump, 'feed.json', 'log_files', 'w')


def get_api_keys() -> tuple[str,str,str,str,str]:
    from dotenv import load_dotenv
    try:
        # get the necessary tokens from .env file. To hardcode the API keys, substitute the os.getenv('') with a string of the API keys.
        if check_if_exists_in_directory("ritter-bot.env"):
            load_dotenv(r'ritter-bot.env')
        else:
            # loads the env keys when using hosting sites such as heroku, etc
            load_dotenv()
        bearer_token = os.getenv('Bearer_Token')
        api_key = os.getenv('API_Key')
        api_key_secret = os.getenv('API_Key_Secret')
        access_token = os.getenv('Access_Token')
        access_token_secret = os.getenv('Access_Token_Secret')
        
        return (bearer_token, api_key, api_key_secret,access_token,access_token_secret)

    except ValueError:
        print('Error with API Keys')


def read_rss_feed(feed_url: str) -> feedparser.util.FeedParserDict:
    # read rss feed and returns a dictionary of the entries in the feed details.
    feed = feedparser.parse(feed_url)
    try:
        if feed['status'] == 200:
            fetch_error = False
        else:
            fetch_error = True
    except KeyError:
        fetch_error = True
    try:
        if variables.ignore_https:
            if "certificate" in str(feed['bozo_exception']).lower():
                import requests
                print(f"{feed_url} has an SSL certificate issue. Trying to fetch without HTTPS")
                response = requests.get(feed_url, verify=False)
                html_text = response.text
                feed = feedparser.parse(html_text)
                if feed['bozo'] == False:
                    fetch_error = False
    except KeyError:
        pass
    if not fetch_error:
        return feed
    else:
        print(f"{feed_url} cannot be accessed.")
    
    
class TwitterUser:

    def __init__(self) -> None:
        bearer_token, api_key, api_key_secret, access_token, access_token_secret = get_api_keys()
        self.authenticated_user = tweepy.Client(bearer_token, api_key, api_key_secret, access_token, access_token_secret,wait_on_rate_limit=True)
    
    # All the below functions are tied to a user. They're supposed to be accessed by an authenticated user ( user.function() ), and are twitter specific.
    def tweet_out(self, tweet_text: str = '', url: str = '', in_reply_to_id:int = 0) -> list:
        if 0 < len(tweet_text) <= 280:
            if not variables.testing_mode:
                if not in_reply_to_id:
                    tweeting = self.authenticated_user.create_tweet(text=tweet_text)
                else:
                    tweeting = self.authenticated_user.create_tweet(text=tweet_text, in_reply_to_tweet_id=in_reply_to_id)
            else:
                '''
                tweeting is a list of lists returned by Client.create_tweet().
                Replicating same format here when testing_mode==False
                example format: Response(data={"id": "1517736731571007488", "text": "Researcher Releases PoC for Recent Java Cryptographic Vulnerability https://t.co/uOOs0awlIU"}, includes={}, errors=[], meta={})
                '''
                tweeting = [
                    {
                        'id': "#testing_mode=True",
                        'text': tweet_text,
                    }
                ]
            return tweeting
        else:
            return self.tweet_out(shorten_tweet_text(tweet_text),url)
    
    
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
                (url, sentences_to_tweet, type_of_tweet) = what_to_tweet(entry, description_from_html)
                tweet_ids=[0]
                for sentence in sentences_to_tweet:
                    tweeting = self.tweet_out(sentence, url,in_reply_to_id=tweet_ids[-1])
                    tweet_ids.append(tweeting[0]['id'])
                tweeting = self.tweet_out("Read more at " + url,url,in_reply_to_id=tweet_ids[-1])
                tweet_ids.append(tweeting[0]['id'])
                
                log_to_file(tweet_ids, url, type_of_tweet, sentences_to_tweet)
                
                time.sleep(variables.time_to_wait_after_a_tweet_in_seconds)
            else:
                #print(f"Already been tweeted about - {url}")
                # Can also break, if the feed is sorted chronologically. If one URL has already been tweeted out, it means the all the next URLs in the feed have also been tweeted out
                pass
    
    
    def search_query(self, query="") -> dict:
        # searches the given query on twitter
        search_results = self.authenticated_user.search_recent_tweets(query, sort_order='relevancy', max_results=20)
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


'''
import schedule

'''

def job():
    start_time = (time.ctime(),time.time())

    print("Running job()")
    if variables.reset_config_to_default:
        move_or_clear_files(move_config=True)
        
    elif variables.run_program:
        user = TwitterUser()
        for feed_url in variables.rss_feeds_to_fetch['description_from_rss_feed']:
                feed = read_rss_feed(feed_url)
                user.tweet_feed(feed)
        for feed_url in variables.rss_feeds_to_fetch['description_from_html']:
                feed = read_rss_feed(feed_url)
                user.tweet_feed(feed,description_from_html=True)
        
    else:
        print(f"Program not running. Waiting for {variables.time_to_wait_when_not_running_in_seconds} seconds")
        time.sleep(variables.time_to_wait_when_not_running_in_seconds)
    
    if variables.move_log_files or variables.delete_old_log_files or variables.delete_important_errors:
        move_or_clear_files(variables.delete_old_log_files,variables.move_log_files,variables.delete_important_errors)

    # user.delete_tweet(all_ids_in_log_files=True)
    '''
    Other useful functions
    user.delete_tweet(all_ids_in_log_files=True)
    feed_to_json("https://www.secureworks.com/rss?feed=research&category=threat-analysis")
    '''
    
    end_time = (time.ctime(),time.time())
    
    print(f"Job started at {start_time[0]} and finished in {end_time[1] - start_time[1]} seconds")


if variables.valid_config:
    job()

if not variables.cron_job_mode:
    while True:
        if variables.valid_config:
            job()
            time.sleep(variables.run_program_every_x_seconds)
        else:
            variables.time_to_wait_when_not_running_in_seconds()
        variables.read_config_and_set_variables()

'''
# Can also use schedule module instead of a cron job
import schedule
schedule.every(25).minutes.do.job()
time.sleep(2)
schedule.every(30).days.do(move_or_clear_files, move_log_files=True, delete_old_log_files=False)
schedule.every(90).days.do(move_or_clear_files, move_log_files=False, delete_old_log_files=True)
'''

# Simpler times: https://github.com/vishalnandagopal/ritter-bot/blob/c699e6d1814484ef64d8e5e7c3e562bad33ea90c/app.py

# This source code is licensed under the MIT license found in the LICENSE file in the root directory of this source tree.
# (Copyright (c) 2022 Vishal N)
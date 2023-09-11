import requests

def get_url_description_from_html(url: str) -> str:
    # Fetches description of a url from by parsing it's html using the beautifulsoup module
    from bs4 import BeautifulSoup
    import requests
    
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    
    description = soup.find("meta", attrs={"name": "description"})
    if not description:
        description = soup.find("meta", attrs={"property": "og:description"})
        if not description:
            description = soup.find("meta", attrs={"property": "twitter:description"})
    
    # Returns the content of the description
    return description["content"] if "content" in description else None


def get_api_respone(api_url:str = "https://api.meaningcloud.com/summarization-1.0",header_data:dict = None) -> dict:
    response = requests.post(url=api_url,data=header_data)
    respone_json = response.json()
    return respone_json


def summarize_with_meaning_cloud_api(article_text:str = '', url:str = '') -> str:
    # Text is the first parameter, so if you not specificy what the argument is, make sure it is etxt.
    # Summarizes a text or URL using https://learn.meaningcloud.com/developer/summarization/1.0/doc/what-is-summarization and returns a summary of it
    
    token = get_meaning_cloud_token()
    
    if article_text:
        header_data={
        'key': token,
        'txt': article_text,
        'sentences': '7'
        }
    elif url:
        header_data={
            'key': token,
            'url': url,
            'sentences': '7'
        }
    
    response_json = get_api_respone(header_data=header_data)
    if response_json["status"]["msg"] == '200':
        summarized_text = response_json["summary"]
        return summarized_text


def get_article_using_newspaper(url: str) -> object:
    # Uses the newspaper module to extract the actual text of the article. Fetches the article, parses it and then returns a string of the whole article text. Not perfect but pretty good
    import newspaper
    try:
        article_obj = newspaper.Article(url)
        article_obj.download()
        article_obj.parse()
        return article_obj
    except newspaper.article.ArticleException:
        return None

def summarize_article(url:str) -> str:
    # Summarizes article using the nlp() function and .summary attribute of the summarize article object.
    # Meant to be used as backup for the meaning cloud API, when it returns gibberish, isn't working or when it is inaccessible.
    
    article_obj = get_article_using_newspaper(url)
    
    if not article_obj:
        # Returns description in the case where article is inaccessible. Something better than nothing
        print(f"{url} is inaccessible using newspaper module")
        description_text = get_description_of_entry_or_url(url=url)
        return description_text
    summarized_text = summarize_with_meaning_cloud_api(article_text=article_obj.text)
    
    if not summarized_text:
        try:
            article_obj.nlp()
        except LookupError:
            #punkt resource not downloaded
            import nltk
            nltk.download("punkt",quiet=True)
            article_obj.nlp()
        summarized_text = article_obj.summary
    
    return summarized_text


def split_and_merge_sentences(summarized_text: str) -> list:
    single_sentences = split_into_sentences(summarized_text)
    already_added, sentences_to_tweet = [-1], []
    while already_added[-1] != (len(single_sentences)-1):
        for i in range(len(single_sentences)):
            if i not in already_added:
                num_of_sentences_that_can_be_merged = check_mergeability_of_sentences(single_sentences, i)
                for j in range(int(num_of_sentences_that_can_be_merged)):
                    sentences_to_tweet.append(single_sentences[i+j])
                    already_added.append(i + j)
                if isinstance(num_of_sentences_that_can_be_merged, float):
                    sentences_to_tweet.append(
                        (
                            single_sentences[
                                int(i + num_of_sentences_that_can_be_merged + 1)
                            ][:277]
                        )
                        + "..."
                    )
                    
                    single_sentences[
                                int(i + num_of_sentences_that_can_be_merged + 1)
                            ] = single_sentences[
                                int(i + num_of_sentences_that_can_be_merged + 1)
                            ][277:]
    return sentences_to_tweet

def get_meaning_cloud_token() -> str:
    if not variables.use_backup_meaning_cloud_token:
        meaning_cloud_token = os.getenv('Meaning_Cloud_Token')
    else:
        meaning_cloud_token = os.getenv('Meaning_Cloud_Backup_Token')
    return meaning_cloud_token

def switch_meaning_cloud_token():
    variables.use_backup_meaning_cloud_token = not variables.use_backup_meaning_cloud_token
    switch_bool_value_in_config("use_backup_meaning_cloud_token",False)


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


def get_api_keys() -> tuple[str,str,str,str,str]:
    from dotenv import load_dotenv
    try:
        # Get the necessary tokens from the ritter-bot.env file. To hardcode the API keys, substitute the os.getenv('') with a string of the API keys.
        if check_if_exists_in_directory("ritter-bot.env"):
            load_dotenv(r'ritter-bot.env')
        else:
            # Loads the env keys when using GitHub Actions, or hosting sites such as Heroku.
            load_dotenv()
        bearer_token = os.getenv('Bearer_Token')
        api_key = os.getenv('API_Key')
        api_key_secret = os.getenv('API_Key_Secret')
        access_token = os.getenv('Access_Token')
        access_token_secret = os.getenv('Access_Token_Secret')
        return (bearer_token, api_key, api_key_secret,access_token,access_token_secret)
    
    except ValueError:
        print('Error with API Keys')
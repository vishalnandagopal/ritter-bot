# Ritter Bot - A feature-rich Twitter bot that tweets out articles from any RSS Feed

A Python application that pulls data from RSS feeds, parses it and then tweets out the latest articles (their titles, a brief summary, a description or just the article links)

## Setup

### API Keys

Get the API keys for your Twitter account from the [Twitter Developer Dashboard](https://developer.twitter.com/en/portal/dashboard).

If you want to store the keys in a `.env` file, Create a file name `ritter-bot.env` in the root directory. Put your keys in the same file (preferably in the same format):

```
Bearer_Token=
API_Key=
API_Key_Secret=
Access_Token=
Access_Token_Secret=
```

If you are using a hosting provider that supports setting environmental variables globally to your project (like [Heroku](https://www.heroku.com)), add the five keys mentioned above as variables in your hosting provider's project/app settings.


**Your API keys must have "Elevated access"**. If you only have "Essential access", click [here](https://developer.twitter.com/en/portal/products/elevated).

<details>

<summary>
If you are facing problems with the API, or need a more thorough explanation, click here.
</summary>

1. You need to create a project on your [Twitter Developer Dashboard](https://developer.twitter.com/en/portal/dashboard). Next, create an app under the project, by filling in all the details Twitter has asked for.

2. You need to apply for "Elevated access", since this is neccessary for making tweets using the Twitter API. Only "Essential Access" is granted by default. You can apply [here](https://developer.twitter.com/en/portal/products/elevated). It might take 2 days to get approved.

3. Make sure your Access Token and Secret have "Read and Write" permissions. Only "Read" permission is granted by default when you create an Access Token.
    1. First, under "User authentication settings" in the app settings on the dashboard, make sure OAuth 1.0a and OAuth 2.0 are turned on.
    
    2. Check if OAuth 1.0 has "Read and Write permissions". If not, enable it and then regenerate the Authentication Tokens (access tokens and bearer token).

    3. "Created with Read and Write permissions" should be displayed under the "Access Token and Secret" section in the "Keys and Tokens" section of your app.

4. If you're still facing issues, regenerate *all* tokens and then run the program again.

##### If you do not want to use .env files, you can hardcode your keys into the program by changing the values in [app.py](app.py#L458)

</details>

### Configuration of features
Change the options available in [config.json](config.json) to your liking. Make sure it is a valid JSON file after you finish editing it.

The default mode is to tweet out the title of the article and a link to it. You can change it by changing the values of `tweet_only_link`, `tweet_description` or `tweet_summarized_article`.

**Make sure only one of those 3 values is `true`.** If multiple values are true, the bot only looks at the first value that is true.

The available options are:

- `testing_mode`:
    Prevents bot from actually tweeting. Useful for testing without spamming tweets from the twitter account. When `true`, it just just runs through 2 URLs in every rss feed and logs everything it was going to tweet in the log_files folder.
    
    Values: `true` or `false`

- `tweet_only_link`: When `true`, only the URL of every article in the RSS feed is tweeted out.
    
    Values: `true` or `false`

- `tweet_description`: When `true`, the title + description + URL is tweeted for every article in the RSS feed is tweeted out.
    
    Values: `true` or `false`

- `tweet_summarized_article`: When `true`, the title + summary + URL is tweeted for every article in the RSS feed is tweeted out.

    Article is summarized using the [newspaper3k](https://github.com/codelucas/newspaper/) and the [nltk](https://www.nltk.org) module.

    Values: `true` or `false`

- `run_program`: The program only runs when this value is `true`.

    Values: `true` or `false`

- `cron_job_mode`: When `true`, the program does not run continuously. It has to be triggered to run every time you want it. This can be done with the help of a cron job. When `false`, the program runs continuosly in a `while True` loop, till it is stopped or till an error is triggered. When program is running continuosly, you can stop it by changing the value of `run_program`.

    Values: `true` or `false`

-  `move_log_files`: When `true`, moves the entire `log_files` folder into a new `old_log_files` folder. Can be used for cleaning up and starting fresh.

    Values: `true` or `false`

-  `delete_old_log_files`: When `true`, deletes the entire `old_log_files` folder.
     
    Values: `true` or `false`

-  `delete_important_errors`: When `true`, deletes the `important-errors.txt` file.

    Values: `true` or `false`

- `time_to_wait_after_a_tweet_in_seconds`: Time (in seconds) to wait after a tweet. Tweepy has settings to prevent being rate limited by Twitter, but this is an additional setting to ensure your account doesn't tweet too many times in a minute.
    
    Values: `integer` > 0

- `run_program_every_x_seconds`: Time (in seconds) to wait after every time a program is run. Used only when `cron_job_mode` is false.
    
    Values: `integer` > 0

- `time_to_wait_when_not_running_in_seconds`: Time to wait when `run_program` and `cron_job_mode` are `false`, before reading the config file again.
    
    Values: `integer` > 0

- `ignore_https`: When `true`, it ignores certificate warnings that may arise when fetching the feed.
    
    Values: `integer` > 0

- `rss_feeds_to_fetch`: Dictionary/JSON with feeds to fetch. Feeds are to be put in `description_from_rss_feed` or `description_from_html`. This decides where their description is fetched (For feeds under`description_from_html`, the description is fetched by fetching the html and getting the data from the `<meta>` tags).
    
    Values: ```{"description_from_rss_feed": ["https://exaample.com/feed1"], "description_from_html": ["https://exaample.com/feed2","https://exaample.com/feed3"]}```

- `dont_summarize_these_urls`: List of domains for which the summary should not be generated because it is buggy. Example: Content in GitHub READMEs mess the summary up by popping up randomly.
    
    Values: ["github.com","reddit.com","youtube.com"]


- `reset_config_to_default`: When `true`, the settings in `config.json` are deleted and replaced with whatever is present in the `default-config.json` file.


This bot mainly uses the [tweepy](https://www.tweepy.org) and the [feedparser](https://github.com/kurtmckee/feedparser) modules.

This source code is licensed under the MIT license found in the LICENSE file in the root directory of this source tree. (Copyright (c) 2022 Vishal N)
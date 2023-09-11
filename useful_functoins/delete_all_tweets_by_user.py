import tweepy,time
class TwitterUser:
    def __init__(self) -> None:
        bearer_token, api_key, api_key_secret, access_token, access_token_secret = get_api_keys()
        self.authenticated_user = tweepy.Client(bearer_token, api_key, api_key_secret, access_token, access_token_secret,wait_on_rate_limit=True)
 
    
    def delete_tweet(self, to_delete=None, all_ids_in_log_files:bool = False):
        # can provide a list or tuple of tweet_ids, a single tweet_id:int or ask it to delete all tweet_ids in 'log_files\tweet-ids.txt' (can be used for deleting all tweets easily)
        if isinstance(to_delete,int):
            # deletes the tweet corresponding to the tweet_id given to the function as to_delete
            time.sleep(1)
            try:
                return ( self.authenticated_user.delete_tweet(to_delete) )
            except Exception as e:
                print(str(e))
        elif isinstance(to_delete,list) or isinstance(to_delete,tuple):
            # deletes every tweet in the list to_delete supplied to the function
            for tweet_id in to_delete:
                self.authenticated_user.delete_tweet(tweet_id)
        else:
            print(f"Wrong type of argument passed to delete_tweet(). to_delete must be an int or a list, but it currently is of type {type(to_delete)}")


def get_api_keys() -> tuple[str,str,str,str,str]:
    import os
    from dotenv import load_dotenv
    try:
        # Get the necessary tokens from the ritter-bot.env file. To hardcode the API keys, substitute the os.getenv('') with a string of the API keys
        load_dotenv(r'ritter-bot.env')
        bearer_token = os.getenv('Bearer_Token')
        api_key = os.getenv('API_Key')
        api_key_secret = os.getenv('API_Key_Secret')
        access_token = os.getenv('Access_Token')
        access_token_secret = os.getenv('Access_Token_Secret')
        return (bearer_token, api_key, api_key_secret,access_token,access_token_secret)

    except ValueError:
        print('Error with API Keys')

api = TwitterUser()

def write_to_file(stuff_to_write: str, file_name: str, directory:str = '', mode :str = 'a', set_pointer_position_from_end_and_truncate:int=0):
    # Writes stuff_to_write string to file_name, defaults to append mode. Directory can also be a sub-directories (even if parent directory does not exist). Eg: old_log_files\log_files
    try:
        if directory:
            file_path = directory + "/" + file_name
        else:
            file_path = file_name
        with open(file_path, mode) as f:
            if set_pointer_position_from_end_and_truncate > 0:
                #This sets the pointer to 1 character from the end. Here, 2 is the whence meaning end of file.
                f.seek(-set_pointer_position_from_end_and_truncate,2)
                f.truncate()
            f.write(stuff_to_write)
    except FileNotFoundError:
        write_to_file(stuff_to_write,file_name,directory,mode,set_pointer_position_from_end_and_truncate)
        
def check_if_exists_in_directory(file_name:str,directory:str='') -> bool:
    current_working_dir =  os.getcwd()
    try:
        if directory:
            os.chdir(directory)
        return file_name in os.listdir()
    except FileNotFoundError:
        return False
    finally:
        os.chdir(current_working_dir)
import os

api.delete_tweet(1543359574018859013)

""" while True:
    for status in (api.authenticated_user.get_users_tweets(id=1540770667766812672))[0]:
        api.delete_tweet(status.id)
        print(f"Deleted {status.id}")
        time.sleep(1) """
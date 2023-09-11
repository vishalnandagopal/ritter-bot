import os, json, time
from .get_config import variables

def read_and_check_config(config_error_count:int=0) -> tuple[bool,bool,bool,bool,bool,bool,bool,bool,bool,bool,int,int,int,bool,dict,list,bool]:
    print("Reading config file")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        config_values = (
            config['run_program'], # ---------------------------------- 0
            config['cron_job_mode'], # ---------------------------------1
            config['testing_mode'], # ----------------------------------2
            config['tweet_only_link'], # -------------------------------3
            config['tweet_description'], # -----------------------------4 
            config['tweet_summarized_article'], # ----------------------5
            config['move_log_files'], # --------------------------------6
            config['delete_old_log_files'], # --------------------------7
            config['delete_important_errors'], # -----------------------8
            config['use_backup_meaning_cloud_token'], # --------------------9
            config['time_to_wait_after_tweeting_a_url_in_seconds'], #--10
            config['run_program_every_x_seconds'], # ------------------11
            config['time_to_wait_when_not_running_in_seconds'], # -----12
            config['ignore_https'], # ---------------------------------13
            config['rss_feeds_to_fetch'], # ---------------------------14
            config['dont_summarize_these_urls'], # --------------------15
            config['reset_config_to_default'], # ----------------------16
            )
    except (KeyError,FileNotFoundError,json.JSONDecodeError):
        (valid_config,config_error_count) = config_error(config_error_count)
        read_and_check_config(config_error_count)
    
    # Checks if the important properties in the config.json file are valid by seeing if their types are appropriate
    if not ( (isinstance(config['run_program'],bool)) and (isinstance(config['cron_job_mode'],bool)) and (isinstance(config['testing_mode'],bool)) and (isinstance(config['tweet_only_link'],bool)) and (isinstance(config['tweet_description'],bool)) and (isinstance(config['tweet_summarized_article'],bool)) ):
        valid_config = False
    elif not ( (isinstance(config['time_to_wait_after_tweeting_a_url_in_seconds'],int)) and (isinstance(config['run_program_every_x_seconds'],int)) ):
        valid_config = False
    elif not ( (isinstance(config['rss_feeds_to_fetch'],dict))):
        valid_config = False
    else:
        valid_config = True
    if valid_config:
        return config_values
    else:
        return None

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
        make_dir(directory)
        write_to_file(stuff_to_write,file_name,directory,mode,set_pointer_position_from_end_and_truncate)


def read_file_and_ignore_comments(file_name: str, directory:str = '') -> list:
    # reads the file in the given file path and returns a list of all lines that do not start with "#" in the file
    l1 = []
    try:
        if directory:
            file_path = directory + "/" + file_name
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


def switch_bool_value_in_config(key_to_make_false:str,always_set_this_key_to_false:bool = True):
    # sets the value of the given key as false again. Used to prevent the program from getting stuck in a loop where it keeps deleting old_log_files or keeps reloading api_keys
    
    variables.changed_config = True
    
    with open('config.json', "r") as f:
        config = json.load(f)
        if always_set_this_key_to_false:
            config[key_to_make_false] = False
        else:
            config[key_to_make_false] = not config[key_to_make_false]
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
            new_name = dir_to_move_to + "/" + current_name + (f" at {time.ctime()}").replace(":","-",3)
            os.rename(current_name, new_name)
        else:
            new_name = dir_to_move_to + "/" + current_name
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


def check_if_exists_in_directory(file_or_folder_name:str,directory:str='') -> bool:
    current_working_dir =  os.getcwd()
    try:
        if directory:
            os.chdir(directory)
        return file_or_folder_name in os.listdir()
    except FileNotFoundError:
        return False
    finally:
        os.chdir(current_working_dir)


def check_if_file_is_empty(file_name:str,directory:str='') -> bool:
    if directory:
        file_path = directory + "/" + file_name
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
            switch_bool_value_in_config('delete_old_log_files')
        if delete_important_errors:
            delete_file_or_folder('important-errors.txt')
            switch_bool_value_in_config('delete_important_errors')
        if move_log_files:
            if check_if_exists_in_directory('log_files'):
                move_file_or_dir('log_files','old_log_files',True)
                switch_bool_value_in_config('move_log_files')


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

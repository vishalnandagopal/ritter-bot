from .os_functions import read_and_check_config

class GlobalVariables:
    def __init__(self) -> None:
        # Settings for the bot (flags). Assigns the values from config.json
        self.set_variables()
    
    def set_variables(self):
        config_values = read_and_check_config()
        if config_values:
            self.valid_config = True
            self.tweet_count = 0
            self.changed_config = False
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
                self.use_backup_meaning_cloud_token,
                self.time_to_wait_after_tweeting_a_url_in_seconds,
                self.run_program_every_x_seconds,
                self.time_to_wait_when_not_running_in_seconds,
                self.ignore_https,
                self.rss_feeds_to_fetch,
                self.dont_summarize_these_urls,
                self.reset_config_to_default,
                ) = config_values
        else:
            self.valid_config = False

variables = GlobalVariables()
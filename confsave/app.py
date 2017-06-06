from os.path import abspath
from os.path import expanduser
from os.path import join
from datetime import datetime

from confsave.repo import LocalRepo


class Application(object):

    class Settings(object):
        REPO_PATH = '~/.confsave'
        HOME_PATH = '~'
        BACKUP_NAME = 'backup'
        CONFIG_FILENAME = '.confsave.yaml'
        GIT_IGNORE = '.gitignore'
        CS_IGNORE = '.cs_ignore'

    def __init__(self):
        self.settings = self.Settings()
        self.repo = LocalRepo(self)

    def get_repo_path(self):
        """
        path to a local repo
        """
        return abspath(expanduser(self.settings.REPO_PATH))

    def get_home_path(self):
        """
        path to a user home directory
        """
        return abspath(expanduser(self.settings.HOME_PATH))

    def get_config_path(self):
        """
        path to a config file in local repo
        """
        return join(self.get_repo_path(), self.settings.CONFIG_FILENAME)

    def get_backup_path(self):
        """
        path to a backup dir
        """
        name = self.settings.BACKUP_NAME + '_' + datetime.now().strftime('%y_%m_%d')
        return join(self.get_repo_path(), name)

    def get_gitignore_path(self):
        """
        path to .gitignore file
        """
        return join(self.get_repo_path(), self.settings.GIT_IGNORE)

    def get_cs_ignore_path(self):
        """
        path to "ignore listing of not added files" file.
        """
        return join(self.get_repo_path(), self.settings.CS_IGNORE)

    def update_settings(self, repo_path=None, home_path=None, config_filename=None, backup_name=None):
        """
        Update settings values.
        """
        if repo_path:
            self.settings.REPO_PATH = repo_path

        if home_path:
            self.settings.HOME_PATH = home_path

        if config_filename:
            self.settings.CONFIG_FILENAME = config_filename

        if backup_name:
            self.settings.BACKUP_NAME = backup_name



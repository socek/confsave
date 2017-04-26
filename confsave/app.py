from os.path import expanduser
from os.path import join

from confsave.repo import LocalRepo


class Application(object):

    class Settings(object):
        REPO_PATH = '~/.confsave'
        CONFIG_FILENAME = '.confsave.yaml'

    def __init__(self):
        self.settings = self.Settings()
        self.repo = LocalRepo(self)

    def get_repo_path(self):
        """
        path to a local repo
        """
        return expanduser(self.settings.REPO_PATH)

    def get_config_path(self):
        """
        path to a config file in local repo
        """
        return join(self.get_repo_path(), self.settings.CONFIG_FILENAME)

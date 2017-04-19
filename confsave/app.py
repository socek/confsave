from os.path import expanduser


class Application(object):

    class Settings(object):
        REPO_PATH = '~/.confsave'

    def __init__(self):
        self.settings = self.Settings()

    def get_repo_path(self):
        """
        path to a local repo
        """
        return expanduser(self.settings.REPO_PATH)

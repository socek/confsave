from os.path import expanduser


class Settings(object):
    REPO_PATH = '~/.confsave'

    def get_repo_path(self):
        return expanduser(self.REPO_PATH)

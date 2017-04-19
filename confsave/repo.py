from os.path import exists

from git import Repo


class LocalRepo(object):

    def __init__(self, app):
        self.app = app
        self.git = None

    def is_created(self):
        """
        Is this repo created and ready?
        """
        if exists(self.app.get_repo_path()):
            try:
                Repo(self.app.get_repo_path())
                return True
            except:
                return False
        else:
            return False

    def init_git_repo(self):
        """
        Initalize git repo.
        """
        if self.is_created():
            self.git = Repo(self.app.get_repo_path())
        else:
            self.git = Repo()
            self.git.init(self.app.get_repo_path(), mkdir=True)

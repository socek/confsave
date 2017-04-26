from os.path import exists
from yaml import dump
from yaml import load

from git import Repo


class LocalRepo(object):

    def __init__(self, app):
        self.app = app
        self.git = None
        self.config = {'files': []}

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
        if not self.is_created():
            Repo.init(self.app.get_repo_path(), mkdir=True)
        self.git = Repo(self.app.get_repo_path())

    def read_config(self):
        """
        Read config file or flush the .config attribute if no file found.
        """
        if exists(self.app.get_config_path()):
            with open(self.app.get_config_path(), 'r') as file:
                self.config = load(file)
        else:
            self.config = {'files': []}

    def write_config(self):
        """
        Write config to a file in local repo.
        """
        with open(self.app.get_config_path(), 'w') as file:
            dump(self.config, file, default_flow_style=False)

    def add_endpoint_to_repo(self, endpoint):
        """
        Add path to repo and the config.
        """
        self.git.index.add([endpoint.get_repo_path()])
        self.config['files'].append(endpoint.path)

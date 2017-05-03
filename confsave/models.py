from os import mkdir
from os import sep
from os import symlink
from os import unlink
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import expanduser
from os.path import islink
from os.path import join
from shutil import copyfile


class Endpoint(object):

    def __init__(self, app, path):
        self.app = app
        self.path = abspath(expanduser(path))

    def is_existing(self):
        """
        is local file exisitng?
        """
        return exists(self.path)

    def is_link(self):
        """
        is local file already a symlink?
        """
        return islink(self.path)

    def get_repo_path(self):
        """
        get path for the file in the local repo
        """
        userpath = self._get_user_path()
        return join(self.app.get_repo_path(), self.path[len(userpath) + 1:])

    def get_folders_paths(self):
        """"
        get list of all paths that needs to be created in order to copy local
        file to local repo
        """
        userpath = self._get_user_path()
        head = dirname(self.path[len(userpath) + 1:])
        paths = []
        while head != '' and head != sep:
            paths.append(join(self.app.get_repo_path(), head))
            head = dirname(head)

        return reversed(paths)

    def make_folders(self):
        """
        create all needed folders for this file in the local
        """
        for path in self.get_folders_paths():
            mkdir(path)

    def _get_user_path(self):
        """
        get home path of the user
        """
        return expanduser(self.app.get_home_path())

    def add_to_repo(self):
        """
        copy local file to local repo and create a symlink in the old place
        """
        if not self.is_link():
            self.make_folders()
            copyfile(self.path, self.get_repo_path())
            unlink(self.path)
            symlink(self.get_repo_path(), self.path)
            self.app.repo.add_endpoint_to_repo(self)

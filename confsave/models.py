from os import mkdir
from os import sep
from os import symlink
from os.path import abspath
from os.path import dirname
from os.path import exists
from os.path import expanduser
from os.path import islink
from os.path import join
from shutil import move

from confsave.filematching import FilePatternMatching


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

    def is_in_user_path(self):
        """
        Is this path in the user path?
        """
        return self._get_user_path() in self.path

    def is_visible(self):
        """
        Is this endpoint visible for the show_list command?
        """
        return not (self.is_ignored() or self.is_link() or self.is_repo())

    def is_ignored(self):
        """
        Is this endpoint ignored?
        """
        return FilePatternMatching(self._get_relative_path(), self.app.repo.get_ignore_list()).is_matching()

    def is_repo(self):
        """
        Is this endpoint a path to confsave repo?
        """
        return self.path == self.app.get_repo_path()

    def get_repo_path(self):
        """
        get path for the file in the local repo
        """
        return join(self.app.get_repo_path(), self._get_relative_path())

    def get_backup_path(self):
        """
        get path for the file in the backup folder
        """
        return join(self.app.get_backup_path(), self._get_relative_path())

    def _get_relative_path(self):
        """
        get relative path for the file
        """
        userpath = self._get_user_path()
        return self.path[len(userpath) + 1:]

    def get_folders_paths(self, root=None):
        """"
        get list of all paths that needs to be created in order to copy local
        file to local repo
        """
        root = root or self.app.get_repo_path()
        userpath = self._get_user_path()
        head = dirname(self.path[len(userpath) + 1:])
        paths = []
        while head != '' and head != sep:
            paths.append(join(root, head))
            head = dirname(head)

        return reversed(paths)

    def make_folders(self, root=None):
        """
        create all needed folders for this file in the local
        """
        for path in self.get_folders_paths(root):
            if not exists(path):
                mkdir(path)

    def _get_user_path(self):
        """
        get home path of the user
        """
        return expanduser(self.app.get_home_path())

    def add_to_repo(self):
        """
        move local file to local repo and create a symlink in the old place
        """
        if not self.is_link():
            self.make_folders()
            move(self.path, self.get_repo_path())
            symlink(self.get_repo_path(), self.path)
            self.app.repo.add_endpoint_to_repo(self)

    def make_link(self):
        """
        Make symlink only and backup old data.
        """
        result = dict(populated=False, backuped=False)
        if not self.is_link():
            if self.is_existing():
                self._backup_local_file()
                result['backuped'] = True
            symlink(self.get_repo_path(), self.path)
            result['populated'] = True

        return result

    def _backup_local_file(self):
        """
        Backup local file.
        """
        self.app.repo.create_backup()
        self.make_folders(self.app.get_backup_path())
        move(self.path, self.get_backup_path())

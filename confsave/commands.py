from glob import glob
from os.path import abspath
from os.path import exists
from os.path import expanduser
from socket import gethostname
from getpass import getuser

from git import Repo

from confsave.models import Endpoint


class EmptyValue(object):
    pass


class PathNotInUserPath(Exception):
    pass


class Commands(object):

    def __init__(self, app):
        self.app = app

    def _init_repo(self):
        """
        Initialize the git repo if needed and read the confsave config.
        """
        self.app.repo.init_git_repo()
        self.app.repo.init_branch()
        self.app.repo.read_config()

    def add(self, filename):
        """
        Add file to the repo and change it to the symlink.
        """
        self._init_repo()
        endpoint = Endpoint(self.app, filename)
        if endpoint.is_in_user_path():
            endpoint.add_to_repo()
            self.app.repo.write_config()
        else:
            print('Path {0} is not in the user directory {1}'.format(
                filename,
                endpoint._get_user_path()
            ))

    def show_list(self):
        """
        Show list of files from home which are not yet added to the repo.
        """
        self._init_repo()
        for filename in glob(self.app.get_home_path() + '/.*'):
            endpoint = Endpoint(self.app, filename)
            if endpoint.is_visible():
                print(endpoint.path)

    def ignore(self, filename):
        """
        Add filename to ignore list.
        """
        self._init_repo()
        self.app.repo.hide_file(filename)

    def show_status(self):
        """
        Show status of tracked files.
        """
        self._init_repo()
        status = self.app.repo.git.git.status('-s')
        for line in status.split('\n'):
            if not line.endswith(self.app.settings.CONFIG_FILENAME):
                print(line)

    def commit(self, message=EmptyValue):
        """
        Commit files added to the index and push them to the repo.
        """
        self._init_repo()
        if message == EmptyValue:
            message = 'configuration stamp'
        self.app.repo.commit(message)

    def set_repo(self, remote):
        """
        Set remote url.
        """
        self._init_repo()
        self.app.repo.set_remote(remote)

    def populate(self):
        """
        Populate repo files into a user directory.
        """
        self._init_repo()
        for file in self.app.repo.config['files']:
            endpoint = Endpoint(self.app, file)
            result = endpoint.make_link()
            if result['populated']:
                print('Populated {}'.format(file))
            if result['backuped']:
                print('    * Backup stored in: {}'.format(endpoint.get_backup_path()))

    def create_repo(self, path):
        """
        Create repo for the
        """
        fullpath = abspath(expanduser(path))

        if exists(fullpath):
            print("Path {} already exists.".format(fullpath))
        else:
            Repo.init(fullpath, bare=True)
            print("Created repo at {}".format(fullpath))

        print('Possible remote url is: {0}@{1}:{2}'.format(
            getuser(),
            gethostname(),
            fullpath,
        ))

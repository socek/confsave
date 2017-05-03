from glob import glob

from confsave.models import Endpoint


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
        endpoint.add_to_repo()
        self.app.repo.write_config()

    def show_list(self):
        """
        Show list of files from home which are not yet added to the repo.
        """
        for filename in glob(self.app.get_home_path() + '/.*'):
            endpoint = Endpoint(self.app, filename)
            if not endpoint.is_link():
                print(endpoint.path)

    # TODO: will be implemented at 0.2v
    # def ignore(self, filename):
    #     pass

    def show_status(self):
        """
        Show status of tracked files.
        """
        self._init_repo()
        status = self.app.repo.git.git.status('-s')
        for line in status.split('\n'):
            if not line.endswith(self.app.settings.CONFIG_FILENAME):
                print(line)

    def commit(self, message=None):
        # todo: should also add config file
        # should make proper message
        # should push
        pass

    def set_repo(self, remote):
        self._init_repo()
        self.app.repo.set_remote(remote)

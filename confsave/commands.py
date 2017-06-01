from glob import glob

from confsave.models import Endpoint


class EmptyValue(object):
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

    # TODO: will be implemented at 0.3v
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

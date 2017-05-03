from glob import glob

from confsave.models import Endpoint


class Commands(object):

    def __init__(self, app):
        self.app = app

    def _init_repo(self):
        self.app.repo.init_git_repo()
        self.app.repo.read_config()

    def add(self, filename):
        self._init_repo()
        endpoint = Endpoint(self.app, filename)
        endpoint.add_to_repo()
        self.app.repo.write_config()

    def show_list(self):
        for filename in glob(self.app.get_home_path() + '/.*'):
            endpoint = Endpoint(self.app, filename)
            if not endpoint.is_link():
                print(endpoint.path)

    # TODO: will be implemented at 0.2v
    # def ignore(self, filename):
    #     pass

    def show_status(self):
        self._init_repo()
        status = self.app.repo.git.git.status('-s')
        for line in status.split('\n'):
            if not line.endswith(self.app.settings.CONFIG_FILENAME):
                print(line)

    def commit(self, message=None):
        # todo: should also add config file
        # should make proper message
        pass

    def push(self):
        pass

    def add_repo(self, remote):
        pass

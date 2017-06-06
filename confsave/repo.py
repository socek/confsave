from os import mkdir
from os.path import exists
from yaml import dump
from yaml import load

from git import Repo


class LocalRepo(object):
    REMOTE_NAME = 'origin'
    BRANCH_NAME = 'master'

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

    def set_remote(self, remote_path):
        """
        Connect with remote repo.
        """
        remote = self._get_remote(remote_path)
        remote.fetch()
        was_created = self._create_remote_branch(remote)
        self._set_remote_branch(remote)

        if not was_created:
            # if the branch was not created, then we need to pull changes from the upstream
            remote.pull()

    def _get_remote(self, remote_path):
        """
        Create link to the remote or use already existing one. Return None if it's not possible.
        """
        if self._get_remote_or_none() and remote_path:
            self._delete_remote()

        if (not self._get_remote_or_none()) and remote_path:
            self._create_remote(remote_path)

        return self._get_remote_or_none()

    def _get_remote_or_none(self):
        """
        Get remote or return None if remote does not exists.
        """
        try:
            return self.git.remotes[self.REMOTE_NAME]
        except (KeyError, IndexError):
            return None

    def _delete_remote(self):
        """
        Remove remote.
        """
        old_remote = self.git.remotes[self.REMOTE_NAME]
        self.git.delete_remote(old_remote)

    def _create_remote(self, remote_path):
        """
        Create remote with given remote_path.
        """
        self.git.create_remote(self.REMOTE_NAME, remote_path)

    def _create_remote_branch(self, remote):
        """
        Create remote branch if needed. Return status of creation.
        """
        if self.BRANCH_NAME not in [ref.name for ref in remote.refs]:
            remote.push('{0}:{0}'.format(self.BRANCH_NAME))
            return True
        return False

    def _set_remote_branch(self, remote):
        """
        Link local branch to a remote one.
        """
        local = self.git.heads[self.BRANCH_NAME]
        upstream = remote.refs[self.BRANCH_NAME]
        local.set_tracking_branch(upstream)

    def init_branch(self):
        """
        Make initial commit if needed.
        """
        if self.git.refs == []:
            self.write_config()
            index = self.git.index
            index.add([self.app.get_config_path()])
            index.commit('inital commit')
            self.git.active_branch.rename(self.BRANCH_NAME)

    def commit(self, message):
        """
        Commit files added to the index and push them to the repo if it is set.
        """
        changes = [diff.a_path for diff in self.git.index.diff(None)]
        self.git.index.add(changes)
        self.git.index.commit(message)

        remote = self._get_remote(None)
        if remote:
            remote.push()

    def add_ignore(self, path):
        """
        Add ignore path if not in the ignore file already.
        """
        ignored = open(self.app.get_gitignore_path()).readlines() if exists(self.app.get_gitignore_path()) else []
        ignored = [line.strip() for line in ignored]
        if path not in ignored:
            ignored.append(path)
            ignored.sort()
        with open(self.app.get_gitignore_path(), 'w') as file:
            file.write('\n'.join(ignored))
        self.git.index.add([self.app.get_gitignore_path()])

    def create_backup(self):
        """
        Create backup dir if it does not exists. Add backup to gitignore.
        """
        path = self.app.get_backup_path()
        if exists(path):
            return

        mkdir(path)
        self.add_ignore(self.app.settings.BACKUP_NAME + '_*')

    def hide_file(self, name):
        """
        Hide file for listing of not added files.
        """
        hidden_files = []
        if exists(self.app.get_cs_ignore_path()):
            hidden_files = self.get_ignore_list()

        if name not in hidden_files:
            hidden_files.append(name)
            hidden_files.sort()

            open(self.app.get_cs_ignore_path(), 'w').write('\n'.join(hidden_files))
            self.git.index.add([self.app.get_cs_ignore_path()])

    def get_ignore_list(self):
        """
        Get list of all hidden files for list command.
        """
        try:
            return [value.strip() for value in open(self.app.get_cs_ignore_path(), 'r').readlines()]
        except FileNotFoundError:
            return []

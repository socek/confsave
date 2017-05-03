from os import mkdir
from os.path import join
from tempfile import NamedTemporaryFile

from mock import MagicMock
from mock import patch
from mock import sentinel
from pytest import fixture
from pytest import yield_fixture
from yaml import dump
from yaml import load

from confsave.models import Endpoint
from confsave.repo import LocalRepo


class TestLocalRepo(object):

    @fixture
    def repo_path(self):
        return NamedTemporaryFile().name

    @fixture
    def existing_repo_path(self, repo_path, app):
        mkdir(repo_path)
        return repo_path

    @fixture
    def app(self, repo_path):
        mock = MagicMock()
        mock.get_repo_path.return_value = repo_path
        return mock

    @fixture
    def repo(self, app):
        return LocalRepo(app)

    @yield_fixture
    def mis_created(self, repo):
        with patch.object(repo, 'is_created') as mock:
            yield mock

    @yield_fixture
    def mrepo(self):
        with patch('confsave.repo.Repo') as mock:
            yield mock

    @fixture
    def remote(self):
        return MagicMock()

    @fixture
    def mgit(self, repo):
        repo.git = MagicMock()
        return repo.git

    @yield_fixture
    def mget_remote(self, repo, remote):
        with patch.object(repo, '_get_remote') as mock:
            mock.return_value = remote
            yield mock

    @yield_fixture
    def mcreate_remote_branch(self, repo):
        with patch.object(repo, '_create_remote_branch') as mock:
            yield mock

    @yield_fixture
    def mset_remote_branch(self, repo):
        with patch.object(repo, '_set_remote_branch') as mock:
            yield mock

    @yield_fixture
    def mwrite_config(self, repo):
        with patch.object(repo, 'write_config') as mock:
            yield mock

    def test_init(self, repo, app):
        """
        Repo should accept app
        """
        assert repo.app == app

    def test_is_created_when_path_not_exists(self, repo):
        """
        .is_created should return False if the folder is not existing
        """
        assert repo.is_created() is False

    def test_is_created_when_path_exists(self, repo):
        """
        .is_created should return False if the folder is existing, but it is
        not a git repo
        """
        mkdir(repo.app.get_repo_path())
        assert repo.is_created() is False

    def test_is_created_when_git_is_initalized(self, repo):
        """
        .is_created should return True if the folder is existing and the git
        is initalized
        """
        repo.init_git_repo()
        assert repo.is_created() is True

    def test_init_git_repo_when_created(self, repo, mis_created, mrepo, repo_path):
        """"
        .init_git_repo should do nothing if git repo is existing
        """
        mis_created.return_value = True

        repo.init_git_repo()

        assert repo.git == mrepo.return_value
        mrepo.assert_called_once_with(repo_path)

    def test_init_git_repo_when_not_created(self, repo, mis_created, mrepo, repo_path):
        """"
        .init_git_repo should init git repo if not existing
        """
        mis_created.return_value = False

        repo.init_git_repo()

        assert repo.git == mrepo.return_value
        mrepo.init.assert_called_once_with(repo_path, mkdir=True)
        mrepo.assert_called_once_with(repo_path)

    def test_read_config_if_not_existing(self, repo, existing_repo_path, app):
        """
        .read_config should only flush the .config field if no config file exists
        """
        conf_path = join(existing_repo_path, '.conf.yaml')
        app.get_config_path.return_value = conf_path
        repo.config = {'garbage': 10}

        repo.read_config()

        assert repo.config == {'files': []}

    def test_read_config_if_existing(self, repo, existing_repo_path, app):
        """
        .read_config should read the config if it exists
        """
        conf_path = join(existing_repo_path, '.conf.yaml')
        app.get_config_path.return_value = conf_path
        repo.config = {'garbage': 10}
        expected_data = {'true': 'data'}
        with open(conf_path, 'w') as file:
            dump(expected_data, file, default_flow_style=False)

        repo.read_config()

        assert repo.config == expected_data

    def test_write_config(self, repo, existing_repo_path, app):
        """
        .write_config should save config to a file
        """
        conf_path = join(existing_repo_path, '.conf.yaml')
        app.get_config_path.return_value = conf_path
        expected_data = {'true': 10}
        repo.config = expected_data

        repo.write_config()

        with open(conf_path, 'r') as file:
            assert load(file) == expected_data

    def test_add_endpoint_to_repo(self, existing_repo_path, repo, app):
        """
        .add_endpoint_to_repo should add file to the local repo git index
        and add user path to the config file
        """
        local_path = NamedTemporaryFile(delete=False).name
        app.get_home_path.return_value = '/tmp'
        conf_path = join(existing_repo_path, '.conf.yaml')
        app.get_config_path.return_value = conf_path
        endpoint = Endpoint(app, local_path)

        with open(endpoint.get_repo_path(), 'w') as file:
            file.write('now')

        repo.init_git_repo()
        repo.add_endpoint_to_repo(endpoint)

        assert repo.config['files'] == [local_path]

    def test_set_remote_branch(self, repo, remote, mgit):
        """
        ._set_remote_branch should link local branch to a remote one.
        """
        local = MagicMock()
        upstream = MagicMock()
        mgit.heads = {repo.BRANCH_NAME: local}
        remote.refs = {repo.BRANCH_NAME: upstream}

        repo._set_remote_branch(remote)

        local.set_tracking_branch.assert_called_once_with(upstream)

    def test_create_remote_branch_when_branch_not_existsing(self, repo, remote):
        """
        ._create_remote_branch should push branch to the remote
        """
        remote.refs = []
        assert repo._create_remote_branch(remote) is True
        remote.push.assert_called_once_with('{0}:{0}'.format(repo.BRANCH_NAME))

    def test_create_remote_branch_when_branch_existsing(self, repo, remote):
        """
        ._create_remote_branch should do nothing when the branch exists
        """
        ref = MagicMock()
        ref.name = repo.BRANCH_NAME
        remote.refs = [ref]
        assert repo._create_remote_branch(remote) is False

    def test_get_remote_when_not_existing(self, repo, mgit):
        """
        ._get_remote should create new remote when it is not existing
        """
        mgit.remotes = []

        assert repo._get_remote(sentinel.remote_path) == mgit.create_remote.return_value

        mgit.create_remote.assert_called_once_with(repo.REMOTE_NAME, sentinel.remote_path)

    def test_get_remote_when_existing(self, repo, mgit):
        """
        ._get_remote should get existing remote
        """
        repo.REMOTE_NAME = 0  # this trick is to use repo.git.remote as dict and as list.
        # repo.git.remote is an object which can be use like dict and like list.
        remote = MagicMock()
        remote.name = repo.REMOTE_NAME
        mgit.remotes = [remote]

        assert repo._get_remote(sentinel.remote_path) == remote

        assert not mgit.create_remote.called

    def test_set_remote_when_branch_not_created(
        self,
        repo,
        mget_remote,
        mcreate_remote_branch,
        mset_remote_branch,
        remote,
    ):
        """
        set_remote should pull the data from remote branch when the ._create_remote_branch has not created the branch
        """
        mcreate_remote_branch.return_value = False

        repo.set_remote(sentinel.remote_path)

        remote.pull.assert_called_once_with()

        # flow asserts
        mget_remote.assert_called_once_with(sentinel.remote_path)
        remote.fetch.assert_called_once_with()
        mcreate_remote_branch.assert_called_once_with(remote)
        mset_remote_branch.assert_called_once_with(remote)

    def test_set_remote_when_branch_created(
        self,
        repo,
        mget_remote,
        mcreate_remote_branch,
        mset_remote_branch,
        remote,
    ):
        """
        set_remote should not pull the data from remote branch when the ._create_remote_branch just created the branch
        """
        mcreate_remote_branch.return_value = True

        repo.set_remote(sentinel.remote_path)

        assert not remote.pull.called

        # flow asserts
        mget_remote.assert_called_once_with(sentinel.remote_path)
        remote.fetch.assert_called_once_with()
        mcreate_remote_branch.assert_called_once_with(remote)
        mset_remote_branch.assert_called_once_with(remote)

    def test_init_branch_when_branch_already_initalized(self, repo, mgit, mwrite_config):
        """
        .init_branch should do nothing when the branch is already initalized.
        """
        mgit.refs = [1]

        repo.init_branch()

        assert not mwrite_config.called

    def test_init_branch_when_branch_not_initalized(self, repo, mgit, mwrite_config, app):
        """
        .init_branch should initalize branch when non has been initalized
        """
        mgit.refs = []

        repo.init_branch()

        mwrite_config.assert_called_once_with()
        app.get_config_path.assert_called_once_with()

        index = mgit.index
        index.add.assert_called_once_with([app.get_config_path.return_value])
        index.commit.assert_called_once_with('inital commit')
        mgit.active_branch.rename.assert_called_once_with(repo.BRANCH_NAME)

    def test_commit(self, repo, mget_remote, mgit, remote):
        """
        .commit should commit files added to the index and push them to the remote repo
        """
        repo.commit(sentinel.message)

        mget_remote.assert_called_once_with(None)
        mgit.index.commit.assert_called_once_with(sentinel.message)
        remote.push.assert_called_once_with()

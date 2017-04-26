from os import mkdir
from os.path import join
from tempfile import NamedTemporaryFile

from mock import MagicMock
from mock import patch
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
        conf_path = join(existing_repo_path, '.conf.yaml')
        app.get_config_path.return_value = conf_path
        endpoint = Endpoint(app, local_path)

        with open(endpoint.get_repo_path(), 'w') as file:
            file.write('now')

        repo.init_git_repo()
        repo.add_endpoint_to_repo(endpoint)

        assert repo.config['files'] == [local_path]

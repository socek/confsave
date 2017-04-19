from os import mkdir
from tempfile import NamedTemporaryFile

from mock import MagicMock
from mock import patch
from pytest import fixture
from pytest import yield_fixture

from confsave.repo import LocalRepo


class TestRepo(object):

    @fixture
    def repo_path(self):
        return NamedTemporaryFile().name

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
        mrepo.assert_called_once_with()
        mrepo.return_value.init.assert_called_once_with(repo_path, mkdir=True)

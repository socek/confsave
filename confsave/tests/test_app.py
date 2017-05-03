from mock import patch
from pytest import yield_fixture

from confsave.app import Application


class SampleApplication(Application):

    class Settings(Application.Settings):
        REPO_PATH = '~/.creazyrepopath'
        HOME_PATH = '~'
        CONFIG_FILENAME = '.confsave-xxx.yaml'


class TestApplication(object):

    @yield_fixture
    def mexpanduser(self):
        with patch('confsave.app.expanduser') as mock:
            yield mock

    @yield_fixture
    def mget_repo_path(self):
        with patch.object(SampleApplication, 'get_repo_path') as mock:
            yield mock

    @yield_fixture
    def mjoin(self):
        with patch('confsave.app.join') as mock:
            yield mock

    def test_get_repo_path(self, mexpanduser):
        """
        .get_repo_path should return path to a local repo using path from settings
        """
        app = SampleApplication()
        assert app.get_repo_path() == mexpanduser.return_value
        mexpanduser.assert_called_once_with('~/.creazyrepopath')

    def test_get_config_path(self, mjoin, mget_repo_path):
        """
        .get_repo_path should return path to a config file in local repo using
        filename from settings
        """
        app = SampleApplication()
        assert app.get_config_path() == mjoin.return_value
        mjoin.assert_called_once_with(mget_repo_path.return_value, '.confsave-xxx.yaml')
        mget_repo_path.assert_called_once_with()

    def test_get_home_path(self, mexpanduser):
        """
        .get_home_path should return absolute home path to the home directory provided by settings
        """
        app = SampleApplication()

        assert app.get_home_path() == mexpanduser.return_value
        mexpanduser.assert_called_once_with('~')

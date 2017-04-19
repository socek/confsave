from mock import patch
from pytest import yield_fixture

from confsave.app import Application


class SampleApplication(Application):

    class Settings(Application.Settings):
        REPO_PATH = '~/.creazyrepopath'


class TestApplication(object):

    @yield_fixture
    def mexpanduser(self):
        with patch('confsave.app.expanduser') as mock:
            yield mock

    def test_get_repo_path(self, mexpanduser):
        """
        .get_repo_path should return path to a local repo using path in settings
        """
        app = SampleApplication()
        assert app.get_repo_path() == mexpanduser.return_value
        mexpanduser.assert_called_once_with('~/.creazyrepopath')

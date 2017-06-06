from datetime import datetime
from freezegun import freeze_time
from mock import patch
from pytest import mark
from pytest import yield_fixture

from confsave.app import Application


class SampleApplication(Application):

    class Settings(Application.Settings):
        REPO_PATH = '~/.creazyrepopath'
        HOME_PATH = '~'
        CONFIG_FILENAME = '.confsave-xxx.yaml'
        GIT_IGNORE = '.proper-git-ignore-file'
        CS_IGNORE = '.proper_cs_ignore'


class TestApplication(object):

    @yield_fixture
    def mexpanduser(self):
        with patch('confsave.app.expanduser') as mock:
            yield mock

    @yield_fixture
    def mabspath(self):
        with patch('confsave.app.abspath') as mock:
            yield mock

    @yield_fixture
    def mget_repo_path(self):
        with patch.object(SampleApplication, 'get_repo_path') as mock:
            yield mock

    @yield_fixture
    def mjoin(self):
        with patch('confsave.app.join') as mock:
            yield mock

    def test_get_repo_path(self, mexpanduser, mabspath):
        """
        .get_repo_path should return path to a local repo using path from settings
        """
        app = SampleApplication()
        assert app.get_repo_path() == mabspath.return_value
        mexpanduser.assert_called_once_with('~/.creazyrepopath')
        mabspath.assert_called_once_with(mexpanduser.return_value)

    def test_get_config_path(self, mjoin, mget_repo_path):
        """
        .get_repo_path should return path to a config file in local repo using
        filename from settings
        """
        app = SampleApplication()
        assert app.get_config_path() == mjoin.return_value
        mjoin.assert_called_once_with(mget_repo_path.return_value, '.confsave-xxx.yaml')
        mget_repo_path.assert_called_once_with()

    def test_get_home_path(self, mexpanduser, mabspath):
        """
        .get_home_path should return absolute home path to the home directory provided by settings
        """
        app = SampleApplication()

        assert app.get_home_path() == mabspath.return_value
        mexpanduser.assert_called_once_with('~')
        mabspath.assert_called_once_with(mexpanduser.return_value)

    @mark.parametrize(
        'repo_path, home_path, config_filename, backup_name',
        (
            [None, None, None, None, ],
            [True, None, None, None, ],
            [True, True, None, True, ],
            [True, None, True, True, ],
        )
    )
    def test_update_settings(self, repo_path, home_path, config_filename, backup_name):
        """
        .update_settings should update application settings when values are set
        """
        app = SampleApplication()

        app.update_settings(repo_path, home_path, config_filename, backup_name)

        # tese asserts are evil, isn't they?
        assert app.settings.REPO_PATH == repo_path if repo_path else app.settings.REPO_PATH != repo_path
        assert app.settings.HOME_PATH == home_path if home_path else app.settings.HOME_PATH != home_path
        assert (
            app.settings.CONFIG_FILENAME == config_filename
            if config_filename else
            app.settings.CONFIG_FILENAME != config_filename
        )
        assert app.settings.BACKUP_NAME == backup_name if backup_name else app.settings.BACKUP_NAME != backup_name

    def test_get_backup_path(self, mget_repo_path, mjoin):
        """
        .get_backup_path should return backup path with local date
        """
        app = SampleApplication()
        now = datetime(year=2012, month=5, day=3)
        with freeze_time(now):
            assert app.get_backup_path() == mjoin.return_value
            mjoin.assert_called_once_with(
                mget_repo_path.return_value,
                'backup_12_05_03',
            )

    def test_get_gitignore_path(self, mget_repo_path):
        """
        .get_gitignore_path should return proper path to a .gitignore file in main repository's path
        """
        app = SampleApplication()
        mget_repo_path.return_value = "something"

        assert app.get_gitignore_path() == 'something/.proper-git-ignore-file'

    def test_get_cs_ignore_path(self, mget_repo_path):
        """
        .get_cs_ignore_path should return proper path to a .cs_ignore file in main repository's path
        """
        app = SampleApplication()
        mget_repo_path.return_value = "something"

        assert app.get_cs_ignore_path() == 'something/.proper_cs_ignore'

from datetime import datetime
from os import mkdir
from os import symlink
from os.path import dirname
from os.path import exists
from os.path import join
from os.path import realpath
from tempfile import NamedTemporaryFile

from freezegun import freeze_time
from mock import MagicMock
from mock import patch
from pytest import fixture
from pytest import mark
from pytest import yield_fixture

from confsave.models import Endpoint


class TestEndpoint(object):

    @fixture
    def app(self):
        return MagicMock()

    @yield_fixture
    def mget_folders_paths(self):
        with patch.object(Endpoint, 'get_folders_paths') as mock:
            yield mock

    @yield_fixture
    def mexists(self):
        with patch('confsave.models.exists') as mock:
            yield mock

    @yield_fixture
    def mmkdir(self):
        with patch('confsave.models.mkdir') as mock:
            yield mock

    @yield_fixture
    def msymlink(self):
        with patch('confsave.models.symlink') as mock:
            yield mock

    @yield_fixture
    def mexpanduser(self):
        with patch('confsave.models.expanduser') as mock:
            yield mock

    @yield_fixture
    def mis_link(self):
        with patch.object(Endpoint, 'is_link') as mock:
            yield mock

    @yield_fixture
    def mis_ignored(self):
        with patch.object(Endpoint, 'is_ignored') as mock:
            yield mock

    @yield_fixture
    def mget_relative_path(self):
        with patch.object(Endpoint, '_get_relative_path') as mock:
            yield mock

    @yield_fixture
    def mis_existing(self):
        with patch.object(Endpoint, 'is_existing') as mock:
            yield mock

    @yield_fixture
    def mbackup_local_file(self):
        with patch.object(Endpoint, '_backup_local_file') as mock:
            yield mock

    @yield_fixture
    def mget_repo_path(self):
        with patch.object(Endpoint, 'get_repo_path') as mock:
            yield mock

    @yield_fixture
    def mget_user_path(self):
        with patch.object(Endpoint, '_get_user_path') as mock:
            yield mock

    @yield_fixture
    def mis_repo(self):
        with patch.object(Endpoint, 'is_repo') as mock:
            yield mock

    def test_init(self, app):
        """
        Endpoint should accept app and path to a file.
        """
        endpoint = Endpoint(app, '/path')
        assert endpoint.path == '/path'
        assert endpoint.app == app

    @mark.parametrize('delete', [True, False])
    def test_is_existing(self, delete, app):
        """
        .is_existing should give information about exsiting of a file
        """
        endpoint = Endpoint(app, NamedTemporaryFile(delete=delete).name)
        assert endpoint.is_existing() == (not delete)

    def test_is_link_when_file_not_exists(self, app):
        """
        .is_link should return False if file is not existing
        """
        endpoint = Endpoint(app, NamedTemporaryFile().name)
        assert not endpoint.is_link()

    def test_is_link_when_file_exists(self, app):
        """
        .is_link should return False if file is not a sysmlink
        """
        endpoint = Endpoint(app, NamedTemporaryFile(delete=True).name)
        assert not endpoint.is_link()

    def test_is_link_when_is_symlink(self, app):
        """
        .is_link should return True if file is a symlink
        """
        symlink_path = NamedTemporaryFile().name
        file_path = NamedTemporaryFile(delete=False).name
        symlink(file_path, symlink_path)
        endpoint = Endpoint(app, symlink_path)

        assert endpoint.is_link()

    def test_get_repo_path(self, app):
        """
        .get_repo_path should give path of the file in the local repo
        """
        app.get_repo_path.return_value = '/tmp/fake'
        app.get_home_path.return_value = '/home/socek'
        endpoint = Endpoint(app, '/home/socek/.config/chromium')

        assert endpoint.get_repo_path() == '/tmp/fake/.config/chromium'

    def test_get_folder_paths(self, app):
        """
        .get_folder_paths should return list of all paths that needs to be created
        in order to copy local file to local repo
        """
        app.get_repo_path.return_value = '/tmp/fake'
        app.get_home_path.return_value = '/home/socek'
        endpoint = Endpoint(app, '/home/socek/.config/chromium/end')

        assert list(endpoint.get_folders_paths()) == [
            '/tmp/fake/.config',
            '/tmp/fake/.config/chromium',
        ]

    def test_make_foleders(self, app, mget_user_path):
        """
        .make_foleders should create all needed folders for this file in the local
        repo
        """
        path = NamedTemporaryFile().name
        app.get_repo_path.return_value = path
        userdir = '/tmp/home'
        endpoint_path = join(userdir, '.config/chromium/end')
        repo_path = join(path, '.config/chromium/end')
        mkdir(path)

        assert not exists(dirname(repo_path))
        endpoint = Endpoint(app, endpoint_path)
        mget_user_path.return_value = '/tmp/home'
        endpoint.make_folders()
        assert exists(dirname(repo_path))

    def test_make_foleders_when_folder_exists(self, app, mget_folders_paths, mexists, mmkdir):
        """
        .make_foleders should do nothing when the folder is already existing
        """
        endpoint = Endpoint(app, 'path')
        mget_folders_paths.return_value = ['spath']
        mexists.return_value = True

        endpoint.make_folders('root')

        mget_folders_paths.assert_called_once_with('root')
        mexists.assert_called_once_with('spath')
        assert not mmkdir.called

    def test_add_to_repo(self, app, mget_user_path):
        """
        .add_to_repo should move local file to local repo and create a symlink
        in the old place
        """
        repo_path = NamedTemporaryFile().name
        user_path = NamedTemporaryFile().name
        local_file = '.testfile'
        local_file_path = join(user_path, local_file)

        app.get_repo_path.return_value = repo_path
        mkdir(user_path)
        mkdir(repo_path)
        with open(local_file_path, 'w') as localfile:
            localfile.write('testdata')

        endpoint = Endpoint(app, local_file_path)
        assert not endpoint.is_link()

        mget_user_path.return_value = user_path

        endpoint.add_to_repo()

        assert open(endpoint.get_repo_path()).read() == 'testdata'
        assert realpath(local_file_path) == endpoint.get_repo_path()
        assert endpoint.is_link()

    def test_add_to_repo_when_already_added_to_repo(self, app, msymlink, mis_link):
        """
        .add_to_repo should do nothing, if the symlink is already created
        """
        endpoint = Endpoint(app, NamedTemporaryFile().name)
        mis_link.return_value = True

        endpoint.add_to_repo()

        assert not msymlink.called

    def test_add_to_repo_directory(self, app, mget_user_path):
        """
        .add_to_repo should move local directory to local repo and create a symlink
        in the old place
        """
        repo_path = NamedTemporaryFile().name
        user_path = NamedTemporaryFile().name
        local_dir = '.testfile'
        local_dir_path = join(user_path, local_dir)
        local_file = 'file.txt'
        local_file_path = join(local_dir_path, local_file)

        app.get_repo_path.return_value = repo_path
        mkdir(user_path)
        mkdir(local_dir_path)
        mkdir(repo_path)
        with open(local_file_path, 'w') as localfile:
            localfile.write('testdata')

        endpoint = Endpoint(app, local_dir_path)
        assert not endpoint.is_link()

        mget_user_path.return_value = user_path

        endpoint.add_to_repo()

        assert open(local_file_path).read() == 'testdata'
        assert open(join(endpoint.get_repo_path(), local_file)).read() == 'testdata'
        assert realpath(local_dir_path) == endpoint.get_repo_path()
        assert endpoint.is_link()

    def test_backup_local_file(self, app, mget_user_path):
        """
        ._backup_local_file should make backup folder, and move the local file to the
        """
        now = datetime(year=2013, month=2, day=22)
        repo_path = NamedTemporaryFile().name
        user_path = NamedTemporaryFile().name
        backup_path = join(repo_path, 'backup')
        local_file = '.testfile'
        local_file_path = join(user_path, local_file)

        app.get_repo_path.return_value = repo_path
        app.get_backup_path.return_value = backup_path

        mkdir(user_path)
        mkdir(repo_path)
        mkdir(backup_path)
        with open(local_file_path, 'w') as localfile:
            localfile.write('testdata')

        endpoint = Endpoint(app, local_file_path)
        assert not endpoint.is_link()

        mget_user_path.return_value = user_path

        with freeze_time(now):
            endpoint._backup_local_file()

            app.repo.create_backup.assert_called_once_with()
            assert not exists(local_file_path)
            assert open(endpoint.get_backup_path()).read() == 'testdata'

    @mark.parametrize(
        'is_link, is_existing, should_backup, should_make_symlink',
        [
            (False, False, False, True),
            (False, True, True, True),
            (True, False, False, False),
            (True, True, False, False)
        ]
    )
    def test_make_link(
        self,
        app,
        is_link,
        is_existing,
        should_backup,
        should_make_symlink,
        mis_link,
        mis_existing,
        mbackup_local_file,
        msymlink,
        mget_repo_path,
    ):
        """
        .make_link should create symlink un user directory of a repo file.
        """
        mis_link.return_value = is_link
        mis_existing.return_value = is_existing

        endpoint = Endpoint(app, NamedTemporaryFile().name)

        result = endpoint.make_link()
        if should_backup:
            mbackup_local_file.assert_called_once_with()
            assert result['backuped']
        else:
            assert not mbackup_local_file.called
            assert not result['backuped']

        if should_make_symlink:
            msymlink.assert_called_once_with(mget_repo_path.return_value, endpoint.path)
            assert result['populated']
        else:
            assert not msymlink.called
            assert not result['populated']

    @mark.parametrize(
        'user_path, path, is_in_userpath',
        [
            ['/home/user', '/home/user/file.txt', True],
            ['/home/user/file.txt', '/home/user', False],
            ['/home/user', '/home/file.txt', False],
            ['/home/user', '~/file.txt', True],
        ]
    )
    def test_is_in_user_path(self, app, mget_user_path, mexpanduser, user_path, path, is_in_userpath):
        """
        .is_in_user_path should give the information if the endpoint has proper path, which is within user's directory
        """
        mget_user_path.return_value = user_path
        mexpanduser.side_effect = lambda obj: obj.replace('~', user_path)
        endpoint = Endpoint(app, path)

        assert endpoint.is_in_user_path() == is_in_userpath

    @mark.parametrize(
        'is_link, is_ignored, result',
        [
            [False, False, True],
            [True, False, False],
            [False, True, False],
            [True, True, False],
        ]
    )
    def test_is_visible(self, app, mis_link, mis_ignored, is_link, is_ignored, result):
        """
        .is_visible should return False if endpoint is a link or it is ignored.
        """
        path = '/home/user/file.txt'
        mis_ignored.return_value = is_ignored
        mis_link.return_value = is_link
        endpoint = Endpoint(app, path)

        assert endpoint.is_visible() is result

    @mark.parametrize(
        'path, result',
        [
            ['one', True],
            ['one/five', True],
            ['three', False],
            ['two', False],
            ['four', True],
            ['one.txt', False],
            ['seven', True],
            ['eight/nine/ten/eleven', True],
        ]
    )
    def test_is_ignored(self, app, mget_relative_path, mis_repo, path, result):
        """
        .is_ignored should return True if endpoint is in the ignore list.
        """
        app.repo.get_ignore_list.return_value = ['one', 'two/three', 'four', 'seve*', 'eight/nine/ten']
        mget_relative_path.return_value = path
        mis_repo.return_value = False

        assert Endpoint(app, path).is_ignored() is result

    @mark.parametrize(
        'path, result',
        [
            ['/home/mymegahome/.confsave', True],
            ['/home/mymegahome/somethingelse', False],
        ]
    )
    def test_is_repo(self, app, path, result):
        """
        .is_repo should return True if endpoint's path is a confsave's repo path.
        """
        app.get_repo_path.return_value = '/home/mymegahome/.confsave'

        assert Endpoint(app, path).is_repo() is result

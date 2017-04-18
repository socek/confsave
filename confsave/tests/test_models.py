from os import mkdir
from os import symlink
from os.path import dirname
from os.path import exists
from os.path import join
from tempfile import NamedTemporaryFile

from mock import MagicMock
from mock import patch
from pytest import fixture
from pytest import mark

from confsave.models import Endpoint


class TestEndpoint(object):

    @fixture
    def app(self):
        return MagicMock()

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
        endpoint = Endpoint(app, '/home/socek/.config/chromium')

        assert endpoint.get_repo_path() == '/tmp/fake/.config/chromium'

    def test_get_folder_paths(self, app):
        """
        .get_folder_paths should return list of all paths that needs to be created
        in order to copy local file to local repo
        """
        app.get_repo_path.return_value = '/tmp/fake'
        endpoint = Endpoint(app, '/home/socek/.config/chromium/end')

        assert list(endpoint.get_folders_paths()) == [
            '/tmp/fake/.config',
            '/tmp/fake/.config/chromium',
        ]

    def test_make_paths(self, app):
        """
        .make_paths should create all needed folders for this file in the local
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
        with patch.object(endpoint, '_get_user_path') as mock:
            mock.return_value = '/tmp/home'
            endpoint.make_folders()
        assert exists(dirname(repo_path))

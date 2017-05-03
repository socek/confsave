from mock import MagicMock
from mock import call
from mock import patch
from mock import sentinel
from pytest import fixture
from pytest import yield_fixture

from confsave.commands import Commands


class TestCommands(object):

    @fixture
    def app(self):
        return MagicMock()

    @fixture
    def commands(self, app):
        return Commands(app)

    @yield_fixture
    def minit_repo(self, commands):
        with patch.object(commands, '_init_repo') as mock:
            yield mock

    @yield_fixture
    def mendpoint(self):
        with patch('confsave.commands.Endpoint') as mock:
            yield mock

    @yield_fixture
    def mprint(self):
        with patch('confsave.commands.print') as mock:
            yield mock

    @yield_fixture
    def mglob(self):
        with patch('confsave.commands.glob') as mock:
            yield mock

    def test_init_repo(self, commands, app):
        """
        ._init_repo should initialize the git repo if needed and read the confsave config.
        """
        commands._init_repo()

        app.repo.init_git_repo.assert_called_once_with()
        app.repo.init_branch.assert_called_once_with()
        app.repo.read_config.assert_called_once_with()

    def test_add(self, commands, minit_repo, mendpoint, app):
        """
        .add should:
        1. initalize the repo
        2. create endpoint
        3. add endpoint to the repo
        4. write config
        """
        commands.add('filename')

        minit_repo.assert_called_once_with()  # 1
        mendpoint.assert_called_once_with(app, 'filename')  # 2
        mendpoint.return_value.add_to_repo.assert_called_once_with()  # 3
        app.repo.write_config.assert_called_once_with()  # 4

    def test_show_list_when_endpoint_is_a_link(self, commands, mglob, mendpoint, mprint, app):
        """
        .show_list should not show files that are in the homedir but are also a symlink
        """
        mglob.return_value = ['first']
        mendpoint.return_value.is_link.return_value = True

        commands.show_list()

        mendpoint.assert_called_once_with(app, 'first')
        assert not mprint.called

    def test_show_list_when_endpoint_is_not_a_link(self, commands, mglob, mendpoint, mprint, app):
        """
        .show_list should show files that are in the homedir but are not links
        """
        mglob.return_value = ['first']
        mendpoint.return_value.is_link.return_value = False
        commands.show_list()

        mendpoint.assert_called_once_with(app, 'first')
        mprint.assert_called_once_with(mendpoint.return_value.path)

    # TODO: will be implemented at 0.2v
    # def test_ignore(self, commands):
    #    """
    #    """
    #    commands.ignore('filename')

    def test_status(self, commands, app, mprint, minit_repo):
        """
        .show_status should:
        1. initalize the repo
        2. get status from git
        3. print proper line
        """
        app.repo.git.git.status.return_value = 'status1\nstatus2\n'
        app.settings.CONFIG_FILENAME = 'config'

        commands.show_status()

        minit_repo.assert_called_once_with()  # 1
        app.repo.git.git.status.assert_called_once_with('-s')  # 2
        assert mprint.call_args_list == [  # 3
            call('status1'),
            call('status2'),
            call(''),
        ]

    def test_status_with_config(self, commands, app, mprint, minit_repo):
        """
        .show_status should not print the config file
        """
        app.repo.git.git.status.return_value = 'status1\nconfig\nstatus2\n'
        app.settings.CONFIG_FILENAME = 'config'

        commands.show_status()

        minit_repo.assert_called_once_with()
        app.repo.git.git.status.assert_called_once_with('-s')
        assert mprint.call_args_list == [  # 3
            call('status1'),
            call('status2'),
            call(''),
        ]

    def test_commit_whit_no_message(self, commands, minit_repo, app):
        """
        .commit should create default message for commit if non was passed
        """
        commands.commit()

        minit_repo.assert_called_once_with()
        app.repo.commit.assert_called_once_with('configuration stamp')

    def test_commit_whit_message(self, commands, minit_repo, app):
        """
        .commit should use passed message for commit
        """
        commands.commit(sentinel.message)

        minit_repo.assert_called_once_with()
        app.repo.commit.assert_called_once_with(sentinel.message)

    def test_set_repo(self, commands, minit_repo, app):
        """
        .set_repo should set remote path repo
        """
        commands.set_repo(sentinel.repo_path)

        minit_repo.assert_called_once_with()
        app.repo.set_remote.assert_called_once_with(sentinel.repo_path)

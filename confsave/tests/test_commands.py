from mock import MagicMock
from mock import call
from mock import patch
from mock import sentinel
from pytest import fixture
from pytest import mark
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

    @yield_fixture
    def mrepo(self):
        with patch('confsave.commands.Repo') as mock:
            yield mock

    @yield_fixture
    def mgetuser(self):
        with patch('confsave.commands.getuser') as mock:
            yield mock

    @yield_fixture
    def mgethostname(self):
        with patch('confsave.commands.gethostname') as mock:
            yield mock

    @yield_fixture
    def mabspath(self):
        with patch('confsave.commands.abspath') as mock:
            yield mock

    @yield_fixture
    def mexpanduser(self):
        with patch('confsave.commands.expanduser') as mock:
            yield mock

    @yield_fixture
    def mexists(self):
        with patch('confsave.commands.exists') as mock:
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

    def test_add_on_error(self, commands, minit_repo, mendpoint, app, mprint):
        """
        .add should raise an error when endpoint is not within the user's directory
        """
        mendpoint.return_value.is_in_user_path.return_value = False

        commands.add('filename')

        minit_repo.assert_called_once_with()
        mendpoint.assert_called_once_with(app, 'filename')
        assert not mendpoint.return_value.add_to_repo.called
        assert not app.repo.write_config.called
        mprint.assert_called_once_with('Path {0} is not in the user directory {1}'.format(
            'filename',
            mendpoint.return_value._get_user_path.return_value,
        ))

    def test_show_list_when_endpoint_is_a_link(self, commands, mglob, mendpoint, mprint, app):
        """
        .show_list should not show files that are in the homedir but are also a symlink
        """
        mglob.return_value = ['first']
        mendpoint.return_value.is_visible.return_value = False

        commands.show_list()

        mendpoint.assert_called_once_with(app, 'first')
        assert not mprint.called

    def test_show_list_when_endpoint_is_not_a_link(self, commands, mglob, mendpoint, mprint, app):
        """
        .show_list should show files that are in the homedir but are not links
        """
        mglob.return_value = ['first']
        mendpoint.return_value.is_visible.return_value = True
        commands.show_list()

        mendpoint.assert_called_once_with(app, 'first')
        mprint.assert_called_once_with(mendpoint.return_value.path)

    def test_ignore(self, commands, app, minit_repo):
        """
        .ignore should add filename to ignore list
        """
        commands.ignore(sentinel.filename)

        minit_repo.assert_called_once_with()
        app.repo.hide_file(sentinel.filename)

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

    @mark.parametrize(
        'populated, backuped',
        [
            (False, False),
            (True, False),
            (False, True),
            (True, True),
        ]
    )
    def test_populate(self, commands, minit_repo, app, mendpoint, populated, backuped, mprint):
        """
        .populate should populate for all the files listed in the config, and print proper result.
        """
        path = '/tmp/this/is/sample'
        app.repo.config = dict(files=[path])
        mendpoint.return_value.make_link.return_value = dict(populated=populated, backuped=backuped)

        commands.populate()

        minit_repo.assert_called_once_with()
        mendpoint.assert_called_once_with(app, path)
        mendpoint.return_value.make_link.assert_called_once_with()
        calls = []
        if populated:
            calls.append(call('Populated ' + path))
        if backuped:
            calls.append(call('    * Backup stored in: {}'.format(mendpoint.return_value.get_backup_path.return_value)))

        assert mprint.call_args_list == calls

    def test_create_repo(self, commands, mrepo, mabspath, mexpanduser, mexists, mprint, mgetuser, mgethostname):
        """
        .create_repo should create repo and show url for the remote
        """
        mexists.return_value = False

        commands.create_repo('somepath')

        mexpanduser.assert_called_once_with('somepath')
        mabspath.assert_called_once_with(mexpanduser.return_value)
        mexists.assert_called_once_with(mabspath.return_value)
        mrepo.init.assert_called_once_with(mabspath.return_value, bare=True)
        mgethostname.assert_called_once_with()
        mgetuser.assert_called_once_with()

        assert mprint.call_args_list == [
            call("Created repo at {}".format(mabspath.return_value)),
            call('Possible remote url is: {0}@{1}:{2}'.format(
                mgetuser.return_value,
                mgethostname.return_value,
                mabspath.return_value,
            ))
        ]

    def test_create_repo_when_already_exists(
        self,
        commands,
        mrepo,
        mabspath,
        mexpanduser,
        mexists,
        mprint,
        mgetuser,
        mgethostname,
    ):
        """
        .create_repo should create repo and show url for the remote
        """
        mexists.return_value = True

        commands.create_repo('somepath')

        mexpanduser.assert_called_once_with('somepath')
        mabspath.assert_called_once_with(mexpanduser.return_value)
        mexists.assert_called_once_with(mabspath.return_value)
        assert not mrepo.init.called
        mgethostname.assert_called_once_with()
        mgetuser.assert_called_once_with()

        assert mprint.call_args_list == [
            call("Path {} already exists.".format(mabspath.return_value)),
            call('Possible remote url is: {0}@{1}:{2}'.format(
                mgetuser.return_value,
                mgethostname.return_value,
                mabspath.return_value,
            ))
        ]

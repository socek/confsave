from mock import MagicMock
from mock import call
from mock import patch
from mock import sentinel
from pytest import fixture
from pytest import mark
from pytest import raises
from pytest import yield_fixture

from confsave.cmd import CommandLine
from confsave.cmd import ValidationError
from confsave.cmd import run


class TestCommandParser(object):

    @yield_fixture
    def mcommands(self):
        with patch('confsave.cmd.Commands', autospec=True) as mock:
            yield mock

    @fixture
    def app(self):
        return MagicMock()

    @fixture
    def cmd(self, app, mcommands):
        return CommandLine(app)

    @yield_fixture
    def margument_parser(self):
        with patch('confsave.cmd.ArgumentParser') as mock:
            yield mock

    @yield_fixture
    def minitalize_parser(self, cmd):
        with patch.object(cmd, 'initalize_parser') as mock:
            yield mock

    @yield_fixture
    def mvalidate(self, cmd):
        with patch.object(cmd, 'validate') as mock:
            yield mock

    @yield_fixture
    def mrun_command(self, cmd):
        with patch.object(cmd, 'run_command') as mock:
            yield mock

    @yield_fixture
    def mexists(self):
        with patch('confsave.cmd.exists') as mock:
            yield mock

    @yield_fixture
    def mhas_conflicts(self, cmd):
        with patch.object(cmd, '_has_conflicts') as mock:
            yield mock

    @yield_fixture
    def mvalidate_conflicts(self, cmd):
        with patch.object(cmd, '_validate_conflicts') as mock:
            yield mock

    @yield_fixture
    def mvalidate_add(self, cmd):
        with patch.object(cmd, '_validate_add') as mock:
            yield mock

    @yield_fixture
    def mprint(self):
        with patch('confsave.cmd.print') as mock:
            yield mock

    @yield_fixture
    def mupdate_settings(self, cmd):
        with patch.object(cmd, 'update_settings') as mock:
            yield mock

    def test_parser_initalization(self, cmd, margument_parser):
        """
        .initalize_parser should create proper ArgumentParser.
        This test does not cover the configuration itself.
        """
        cmd.initalize_parser()

        margument_parser.assert_called_once()
        assert cmd.parser == margument_parser.return_value

    def test_running_with_no_errors(self, cmd, minitalize_parser, mvalidate, mrun_command, mupdate_settings):
        """
        .run should initalize parser, validate commands and where there is no errors there, run the command.
        """
        mvalidate.return_value = True
        cmd.parser = MagicMock()

        cmd.run()

        mupdate_settings.assert_called_once_with()
        minitalize_parser.assert_called_once_with()
        mvalidate.assert_called_once_with()
        mrun_command.assert_called_once_with()
        assert not cmd.parser.print_help.called

    def test_running_with_errors(self, cmd, minitalize_parser, mvalidate, mrun_command):
        """
        .run should initalize parser, validate commands and and print help on error
        """
        mvalidate.return_value = False
        cmd.parser = MagicMock()

        cmd.run()

        minitalize_parser.assert_called_once_with()
        mvalidate.assert_called_once_with()
        assert not mrun_command.called
        cmd.parser.print_help.assert_called_once_with()

    @mark.parametrize(
        'arg, command, args',
        [
            ('add', lambda commands: commands.add, lambda args: (args.add,)),
            ('list', lambda commands: commands.show_list, lambda args: ()),
            ('ignore', lambda commands: commands.ignore, lambda args: (args.ignore,)),
            ('status', lambda commands: commands.show_status, lambda args: ()),
            ('commit', lambda commands: commands.commit, lambda args: (args.commit,)),
            ('set_repo', lambda commands: commands.set_repo, lambda args: (args.set_repo,)),
            ('populate', lambda commands: commands.populate, lambda args: ()),
            ('create_repo', lambda commands: commands.create_repo, lambda args: (args.create_repo,)),
        ]
    )
    def test_run_command(self, cmd, mcommands, arg, command, args):
        """
        .run_command should run proper command.
        """
        cmd.args = MagicMock()
        cmd.args.add = None
        cmd.args.list = False
        cmd.args.ignore = None
        cmd.args.status = False
        cmd.args.commit = None
        cmd.args.set_repo = None
        cmd.args.populate = False
        cmd.args.create_repo = None

        setattr(cmd.args, arg, sentinel.value)

        cmd.run_command()

        command = command(mcommands.return_value)
        command.assert_called_once_with(*args(cmd.args))

    def test_run_command_loose_end(self, cmd):
        """
        .run_command should print help when it is unable to run proper command.
        """
        cmd.args = MagicMock()
        cmd.args.add = None
        cmd.args.list = False
        cmd.args.ignore = None
        cmd.args.status = False
        cmd.args.commit = None
        cmd.args.set_repo = None
        cmd.args.populate = False
        cmd.args.create_repo = None

        cmd.parser = MagicMock()

        cmd.run_command()

        cmd.parser.print_help.assert_called_once_with()

    def test_validate_add_when_add_command_was_not_triggered(self, cmd, mexists):
        """
        ._validate_add should do nothing when add command was not triggered
        """
        cmd.args = MagicMock()
        cmd.args.add = None

        cmd._validate_add()

        assert not mexists.called

    def test_validate_add_when_file_does_not_exists(self, cmd, mexists):
        """
        ._validate_add should raise an error when add command was triggered and file does not exists
        """
        cmd.args = MagicMock()
        mexists.return_value = False

        with raises(ValidationError):
            cmd._validate_add()

        mexists.assert_called_once_with(cmd.args.add)

    def test_validate_add_when_file_exists(self, cmd, mexists):
        """
        ._validate_add should do nothing when add command was triggered and file exists
        """
        cmd.args = MagicMock()
        mexists.return_value = True

        cmd._validate_add()

        mexists.assert_called_once_with(cmd.args.add)

    @mark.parametrize(
        'arguments, result',
        (
            ([False, False], False),
            ([True, False], False),
            ([True, True], True),
        )
    )
    def test_has_conflicts(self, cmd, arguments, result):
        """
        .should return True if the submited arguments count are larger then 1
        """
        assert cmd._has_conflicts(arguments) == result

    def test_validate_conflicts_when_no_conflict_found(self, cmd, mhas_conflicts):
        """
        ._validate_conflicts should do nothing when no conflict found
        """
        cmd.args = MagicMock()
        mhas_conflicts.return_value = False

        cmd._validate_conflicts()

        mhas_conflicts.assert_called_once_with([
            cmd.args.add,
            cmd.args.list,
            cmd.args.ignore,
            cmd.args.status,
            cmd.args.commit,
            cmd.args.set_repo,
            cmd.args.populate,
            cmd.args.create_repo,
        ])

    def test_validate_conflicts_when_conflict_found(self, cmd, mhas_conflicts):
        """
        ._validate_conflicts should raise ValidationError when conflics are found
        """
        cmd.args = MagicMock()
        mhas_conflicts.return_value = True

        with raises(ValidationError):
            cmd._validate_conflicts()

        mhas_conflicts.assert_called_once_with([
            cmd.args.add,
            cmd.args.list,
            cmd.args.ignore,
            cmd.args.status,
            cmd.args.commit,
            cmd.args.set_repo,
            cmd.args.populate,
            cmd.args.create_repo,
        ])

    def test_validate_when_no_errors(self, cmd, mvalidate_conflicts, mvalidate_add):
        """
        .validate should return True when no errors has been found
        """
        cmd.parser = MagicMock()

        assert cmd.validate() is True

    def test_validate_when_has_errors(self, cmd, mvalidate_conflicts, mvalidate_add, mprint):
        """
        .validate should print error statment when error has been found
        """
        mvalidate_add.side_effect = ValidationError('testing')
        cmd.parser = MagicMock()

        assert cmd.validate() is False

        assert mprint.call_args_list == [
            call('Error: testing'),
            call(),
        ]

    def test_update_settings(self, cmd, app):
        """
        .update_settings should pass the command line arguments to Application.update_settings
        """
        cmd.args = MagicMock()

        cmd.update_settings()

        app.update_settings.assert_called_once_with(
            repo_path=cmd.args.repo_path,
            home_path=cmd.args.home_path,
            config_filename=cmd.args.config_filename
        )


class TestRun(object):

    @yield_fixture
    def mapplication(self):
        with patch('confsave.cmd.Application') as mock:
            yield mock

    @yield_fixture
    def mcommand_line(self):
        with patch('confsave.cmd.CommandLine') as mock:
            yield mock

    def test_simple(self, mapplication, mcommand_line):
        """
        run function should initalize application and command line. After that it should run the command line.
        """
        run()

        mapplication.assert_called_once_with()
        mcommand_line.assert_called_once_with(mapplication.return_value)
        mcommand_line.return_value.run.assert_called_once_with()

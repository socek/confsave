from argparse import ArgumentParser
from os.path import exists

from confsave.app import Application
from confsave.commands import Commands
from confsave.commands import EmptyValue


class ValidationError(Exception):

    def __init__(self, message):
        self.message = message


class CommandLine(object):

    def __init__(self, app):
        self.app = app
        self.commands = Commands(app)

    def initalize_parser(self):
        """
        Create argument parser which will parse argument provided by command line.
        """
        self.parser = ArgumentParser(description='ConfSave cmd')
        self.parser.add_argument(
            '--add',
            '-a',
            help='add endpoint',
            dest='add')
        self.parser.add_argument(
            '--list',
            '-l',
            action='store_true',
            help='list untracked files',
            dest='list')
        self.parser.add_argument(
            '--ignore',
            '-i',
            help='add file to ignore list',
            dest='ignore')
        self.parser.add_argument(
            '--status',
            '-s',
            action='store_true',
            help='show status of tracked files',
            dest='status')
        self.parser.add_argument(
            '--commit',
            '-c',
            nargs='?',
            const=EmptyValue,
            help='commit changes to the repo',
            dest='commit')
        self.parser.add_argument(
            '--repo',
            '-r',
            help='set remote repo to push to',
            dest='set_repo'
        )

        self.parser.add_argument(
            '--repo-path',
            '-1',
            help='path to the config repository',
            dest='repo_path',
        )
        self.parser.add_argument(
            '--home-path',
            '-2',
            help='path to the home directory',
            dest='home_path',
        )
        self.parser.add_argument(
            '--config_filename',
            '-3',
            help='name of file to store the ConfSave config',
            dest='config_filename',
        )
        self.parser.add_argument(
            '--populate',
            '-p',
            help='populate repo files into a user directory',
            dest='populate',
            action='store_true',
        )
        self.parser.add_argument(
            '--create-repo',
            help='create repo for the configs',
            dest='create_repo',
        )

    def validate(self):
        """
        Validate if arguments provided by command line have any errors.
        """
        self.args = self.parser.parse_args()
        try:
            self._validate_conflicts()
            self._validate_add()
            return True
        except ValidationError as error:
            print('Error: {}'.format(error.message))
            print()
            return False

    def _validate_conflicts(self):
        conflicting_arguments = [
            self.args.add,
            self.args.list,
            self.args.ignore,
            self.args.status,
            self.args.commit,
            self.args.set_repo,
            self.args.populate,
            self.args.create_repo,
        ]
        if self._has_conflicts(conflicting_arguments):
            raise ValidationError('Two or more commands are in conflict')

    def _has_conflicts(self, conflicting_arguments):
        """
        is the provided list of arguments in conflict?
        """
        arguments = [bool(obj) for obj in conflicting_arguments]
        return arguments.count(True) > 1

    def _validate_add(self):
        filename = self.args.add
        if filename:
            if not exists(filename):
                raise ValidationError('Path "{}" does not exists'.format(filename))

    def run_command(self):
        """
        Run command choosed by the command line.
        """
        if self.args.add:
            self.commands.add(self.args.add)
            return

        if self.args.list:
            self.commands.show_list()
            return

        if self.args.ignore:
            self.commands.ignore(self.args.ignore)
            return

        if self.args.status:
            self.commands.show_status()
            return

        if self.args.commit:
            self.commands.commit(self.args.commit)
            return

        if self.args.set_repo:
            self.commands.set_repo(self.args.set_repo)
            return

        if self.args.populate:
            self.commands.populate()
            return

        if self.args.create_repo:
            self.commands.create_repo(self.args.create_repo)
            return

        self.parser.print_help()

    def update_settings(self):
        """
        Update settings from command line arguments.
        """
        self.app.update_settings(
            repo_path=self.args.repo_path,
            home_path=self.args.home_path,
            config_filename=self.args.config_filename)

    def run(self):
        """
        Run whole application with command line interface.
        """
        self.initalize_parser()
        if self.validate():
            self.update_settings()
            self.run_command()
        else:
            self.parser.print_help()


def run():
    app = Application()
    cmd = CommandLine(app)
    cmd.run()

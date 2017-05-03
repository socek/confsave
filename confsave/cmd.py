from argparse import ArgumentParser
from os.path import exists

from confsave.app import Application
from confsave.commands import Commands


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
        # TODO: will be implemented at 0.2v
        # self.parser.add_argument(
        #     '--ignore',
        #     '-i',
        #     help='add file to ignore list',
        #     dest='ignore')
        self.parser.add_argument(
            '--status',
            '-s',
            action='store_true',
            help='show status of tracked files',
            dest='status')

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

        self.parser.print_help()

    def run(self):
        """
        Run whole application with command line interface.
        """
        self.initalize_parser()
        if self.validate():
            self.run_command()
        else:
            self.parser.print_help()


def run():
    app = Application()
    cmd = CommandLine(app)
    cmd.run()

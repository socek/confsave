from argparse import ArgumentParser

from confsave.app import Application


class Commands(object):

    def __init__(self, app):
        self.app = app

    def add(self):
        pass


class CmdParser(object):

    def __init__(self, app):
        self.app = app
        self.commands = Commands(app)

    def initalize_parser(self):
        self.parser = ArgumentParser(description='ConfSave cmd')
        self.parser.add_argument(
            '--add', '-a', help='add endpoint', dest='add')

    def validate(self):
        self.args = self.parser.parse_args()
        if self.args.add:
            return True

        self.parser.print_help()

    def run_command(self):
        if self.args.add:
            self.commands.add(self.args.add)

    def run(self):
        self.initalize_parser()
        if self.validate():
            self.run_command()


def run():
    app = Application()
    cmd = CmdParser(app)
    cmd.run()

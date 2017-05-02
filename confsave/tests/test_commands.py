from mock import MagicMock
from pytest import fixture

from confsave.commands import Commands


class TestCommands(object):

    @fixture
    def app(self):
        return MagicMock()

    @fixture
    def commands(self, app):
        return Commands(app)

    def test_add(self, commands):
        """
        """
        commands.add('filename')

    def test_show_list(self, commands):
        """
        """
        commands.show_list()

    def test_ignore(self, commands):
        """
        """
        commands.ignore('filename')

    def test_status(self, commands):
        """
        """
        commands.show_status()

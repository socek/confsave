from fnmatch import fnmatchcase
from os.path import split


class FilePatternMatching(object):
    """
    Check if path is matching with list of patterns. Patterns are in form of Unix shell-style wildcards.
    """

    def __init__(self, path, patterns):
        self.path = path
        self.patterns = patterns

    def get_subpaths(self):
        """
        Get list of subpaths.
        """
        yield self.path
        root = self.path
        while True:
            root, name = split(root)
            if root in ['/', ''] or name == '':
                break
            else:
                yield root

    def _match_list(self):
        for ignore_path in self.patterns:
            for root in self.get_subpaths():
                yield root, ignore_path

    def is_matching(self, match=fnmatchcase):
        """
        Is the path match at least one of the patterns.
        """
        for root, ignore_path in self._match_list():
            if match(root, ignore_path):
                return True
        return False

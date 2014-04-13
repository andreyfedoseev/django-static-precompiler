from static_precompiler.management.commands.static_precompiler_watch import get_watched_dirs
from static_precompiler.settings import STATIC_ROOT
import os
import unittest


class StaticPrecompilerWatchTestCase(unittest.TestCase):

    def test_get_watched_dirs(self):

        self.assertEqual(get_watched_dirs(), sorted([
            os.path.join(os.path.dirname(__file__), "staticfiles_dir"),
            os.path.join(os.path.dirname(__file__), "staticfiles_dir_with_prefix"),
            STATIC_ROOT
        ]))


def suite():
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTest(loader.loadTestsFromTestCase(StaticPrecompilerWatchTestCase))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

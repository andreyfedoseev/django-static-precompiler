from static_precompiler.management.commands.compilestatic import get_scanned_dirs
from static_precompiler.settings import STATIC_ROOT
import os
import unittest


class CompileStaticTestCase(unittest.TestCase):

    def test_get_scanned_dirs(self):

        self.assertEqual(get_scanned_dirs(), sorted([
            os.path.join(os.path.dirname(__file__), "staticfiles_dir"),
            os.path.join(os.path.dirname(__file__), "staticfiles_dir_with_prefix"),
            STATIC_ROOT
        ]))


def suite():
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTest(loader.loadTestsFromTestCase(CompileStaticTestCase))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

import unittest


def suite():
    from static_precompiler.tests import test_base_compiler
    from static_precompiler.tests import test_url_converter
    from static_precompiler.tests import test_utils
    from static_precompiler.tests import test_less
    from static_precompiler.tests import test_coffeescript
    from static_precompiler.tests import test_scss
    from static_precompiler.tests import test_templatetags
    from static_precompiler.tests import test_management

    test_suite = unittest.TestSuite()
    test_suite.addTests(test_base_compiler.suite())
    test_suite.addTests(test_url_converter.suite())
    test_suite.addTests(test_utils.suite())
    test_suite.addTests(test_less.suite())
    test_suite.addTests(test_coffeescript.suite())
    test_suite.addTests(test_scss.suite())
    test_suite.addTests(test_templatetags.suite())
    test_suite.addTests(test_management.suite())
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

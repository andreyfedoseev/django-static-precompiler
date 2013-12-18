# coding: utf-8

def suite():
    import unittest
    import doctest
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'static_precompiler.tests.django_settings'
    suite = unittest.TestSuite()
    this_dir = os.path.dirname(__file__)
    package_tests = unittest.TestLoader().discover(start_dir=this_dir)
    suite.addTests(package_tests)
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

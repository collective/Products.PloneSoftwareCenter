""" Tests for Products.PloneSOftwareCenter.utils
"""
import unittest
from Products.PloneSoftwareCenter.utils import which_platform

class TestUtils(unittest.TestCase):

    def test_which_platform(self):
        u = 'http://pypi.python.org/pypi/simple/acme'
        files = (('Mac OS X', 
                  'iw.quality-0.1dev-r6420.macosx-10.3-fat.tar.gz'),
                 ('All platforms', 'iw.quality-0.1dev_r6420-py2.5.egg'),
                 ('All platforms', 'iw.quality-0.1dev-r6420.tar.gz'),
                 ('Mac OS X', 
                  '%s/iw.quality-0.1dev-r6420.macosx-10.3-fat.tar.gz' % u)
                )
        for wanted, name in files:
            self.assertEquals(which_platform(name), wanted)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUtils))
    return suite


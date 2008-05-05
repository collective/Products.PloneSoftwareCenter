from Products.PloneSoftwareCenter.tests.base import PSCTestCase
from Products.PloneSoftwareCenter.interfaces import IPSCFileStorage

from Products.PloneSoftwareCenter.storage import getFileStorage
from Products.PloneSoftwareCenter.storage import getFileStorageNames

class TestStorage(PSCTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        
        self.psc = self.portal.psc
        self.proj = self.portal.psc.proj
        releases = self.proj.releases 
        releases.invokeFactory('PSCRelease', '1.0')
        self.release = releases['1.0']

    def test_basic_storage(self):
        # try the registery
        wanted = ['zodb', ]
        for w in wanted:
            self.assert_(w in getFileStorageNames(self.release))

    def test_adapters(self):
        # try various storage
        for st_name in ('zodb',):
            for name, content in (('weird, name.tgz', 'xxx'), 
                                  ('regular.tgz', 'xxx'),):
                storage = getFileStorage(self.release, st_name)
                storage.setFileContent(content, name)
                self.assertEquals(storage.getFileContent(name), content)
            stored = storage.getFileNames()
            stored.sort()
            self.assertEquals(stored,  ['regular.tgz', 'weird, name.tgz'])
            

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestStorage))
    return suite


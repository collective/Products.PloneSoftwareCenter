from Products.PloneSoftwareCenter.tests.base import PSCTestCase
from Products.PloneSoftwareCenter.storage.interfaces import IPSCFileStorage
from Products.PloneSoftwareCenter.storage.archetype import ArchetypeStorage
from Products.PloneSoftwareCenter.storage import getFileStorageVocab
from Products.PloneSoftwareCenter.storage import DynamicStorage

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

    def test_adapters(self):
        # try various storage
        storage = DynamicStorage()
        self.assertEquals(storage.getName(), 'dynamic')
        
        pluggable_storage = storage._getStorage(self.psc)
        self.failUnless(pluggable_storage.__class__ is ArchetypeStorage)
        # name = pluggable_storage.getName()
        # self.assertEquals(name, 'archetype')

    def test_storage_vocab(self):
        """Test the test storage vocab"""
        vocab = getFileStorageVocab(self.release)
        self.failUnless(vocab[0][0] == u'archetype')
        self.failUnless(vocab[0][1].startswith('Archetypes'))
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestStorage))
    return suite


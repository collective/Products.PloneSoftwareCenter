from Products.PloneSoftwareCenter.tests.base import PSCTestCase
from Products.PloneSoftwareCenter.storage.interfaces import IPSCFileStorage
from Products.PloneSoftwareCenter.storage.archetype import ArchetypeStorage
from Products.PloneSoftwareCenter.storage import getFileStorageVocab
from Products.PloneSoftwareCenter.storage import DynamicStorage
from Products.PloneSoftwareCenter.storage import getFileStorageAdapters

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
        found = False
        for index, title in vocab:
            if index == u'archetype' and title == "Archetypes (stores releases via Archetype's AttributeStorage)":
                found = True
                break
        self.assert_(found)
       
    def test_storage_change(self):

        # what is the current storage strategy ? 
        ss = self.portal.psc.getStorageStrategy()
        self.assertEquals(ss, 'archetype')

        # let's add a file to our project
        self.release.invokeFactory('PSCFile', 'file')
        self.release.file.update(**{'title': 'my file'})

        # let's add a new strategy
        from zope.interface import implements
        class DummyStorage(object):
            title = u"Dummy"
            description = u"stores nothing"
            implements(IPSCFileStorage)
            storage = []

            def __init__(self, context):
                self.context = context

            def set(self, *args, **kw):
                self.storage.append('ok')

        from zope.component import getSiteManager
        from zope.interface import Interface
        sm = getSiteManager()
        sm.registerAdapter(factory=DummyStorage, 
                           provided=IPSCFileStorage,
                           required=(Interface,),
                           name='dummy')

        # let's see what kind of strategies are available
        strats = sorted([s for s, a in 
                  getFileStorageAdapters(self.portal.psc)])
        
        for s in ['archetype', 'dummy']:
            self.assert_(s in strats)

        # let's add some content in the file
        self.release.file.setDownloadableFile('xxxx')

        # let's change the strategy
        self.portal.psc.setStorageStrategy('dummy')

        # it should trigger an event that changes 
        # the storage for all files
        self.assert_(DummyStorage.storage, ['ok']) 
       
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestStorage))
    return suite


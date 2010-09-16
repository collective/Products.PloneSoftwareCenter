"""Tests for migration."""
from socket import gaierror
import os
from Products.PloneSoftwareCenter.tests.base import PSCTestCase
from Products.CMFCore.utils import getToolByName

from Products.PloneSoftwareCenter.setuphandlers import before_1_5
from Products.PloneSoftwareCenter.setuphandlers import extract_distutils_id 
from Products.PloneSoftwareCenter.setuphandlers import _pypi_certified_owner

curdir = os.path.dirname(__file__)

SOME_EGGS = (os.path.join(curdir, 'zope.size-3.4.0.tar.gz'),
             os.path.join(curdir, 'zope.event-3.4.0-py2.4.egg'),
             )

class TestMigration(PSCTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        
        self.psc = self.portal.psc
        self.proj = self.portal.psc.proj
        self.proj.setContactAddress('mailto:tarek@ziade.org')
        releases = self.proj.releases 
        releases.invokeFactory('PSCRelease', '1.0')
        self.release = releases['1.0']
        self.file = self.release.invokeFactory('PSCFile',
                                               'my.egg') 

    def test_pypi_synchro(self):
        pass

    def test_extract_distutils_id(self):
       
        class FakeField(object):
            def __init__(self, content, filename):
                self.content = content
                self.filename = filename
            def get_data(self):
                return self.content

        class FakeFile(object):
            def __init__(self, path):
                self.content = open(path).read()
                self.name = os.path.split(path)[-1]
            
            def getId(self):
                return self.name

            def getDownloadableFile(self):
                return FakeField(self.content, self.name) 

        for egg, wanted in zip(SOME_EGGS, 
                               ('zope.size', 'zope.event')):
            egg = FakeFile(egg)
            self.assertEquals(extract_distutils_id(egg), wanted)

    def test_pypi_certified_owner(self):
        # testing the real server
        # XXX this is not optimal 
        try:
            contacts = _pypi_certified_owner('Products.PloneSoftwareCenter')
        except gaierror:
            pass
        else:
            wanted = (None, 'aclark@aclark.net')
            self.assertEquals(contacts, wanted)

    def test_migration(self):
        # patching _pypi_certified_owner
        # so we don't query pypi for real here
        def _owner(id_):
            return 'tarek@ziade.org' 

        from Products.PloneSoftwareCenter import setuphandlers
        setuphandlers._pypi_certified_owner = _owner

        # let's add some files
        # without setting the distutils id
        for egg in SOME_EGGS:
            content = open(egg).read()
            name = os.path.split(egg)[-1]
            self.release.invokeFactory('PSCFile', name)
            f = getattr(self.release, name)
            f.setDownloadableFile(content, filename=name)
        self.release.reindexObject()

        # let's run the migration 
        portal_setup = getToolByName(self.portal, 'portal_setup')        
          
        before_1_5(portal_setup)
        
        # let's see what has been done to our proj
        self.assertEquals(self.proj.getDistutilsMainId(), 
                          'zope.event')
        self.assertEquals(self.proj.getDistutilsSecondaryIds(),
                          ('zope.size',))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigration))
    return suite


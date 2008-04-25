from base import PSCTestCase

from DateTime.DateTime import DateTime
import os
from cgi import FieldStorage
from tempfile import TemporaryFile

from ZPublisher.HTTPRequest import FileUpload

from Products.PloneSoftwareCenter.tests.utils import PACKAGE_HOME

from Testing import ZopeTestCase
try:
    from Products.Poi.interfaces import Tracker
    HAS_POI = True
    ZopeTestCase.installProduct('Poi')
except ImportError:
    HAS_POI = False

def createFileUpload(data, filename):
    fp = TemporaryFile('w+b')
    fp.write(data)
    fp.seek(0)
    env = {'REQUEST_METHOD':'PUT'}
    headers = {'content-type':'text/plain',
               'content-length': len(data),
               'content-disposition':'attachment; filename=%s' % \
                 filename}
    fs = FieldStorage(fp=fp, environ=env, headers=headers)
    result = FileUpload(fs)
    fp.close()
    
    return result

class TestProjectDOAPView(PSCTestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        self.proj = self.portal.psc.proj
        self.resetView()
    
    def resetView(self):
        self.view = self.proj.restrictedTraverse('@@project_doap_view')
        self.viewrdf = self.proj.restrictedTraverse('@@doap.rdf')
    
    def testViewLookup(self):
        self.failIf(self.view is None)
        self.failIf(self.viewrdf is None)
    
    def test_categories_url(self):
        self.portal.psc.setAvailableCategories([
          'cat1|Category 1|Projects of category 1',
          'cat2|Category 2|Projects of category 2',
          'cat3|Category 3|Projects of category 3',
          ])
        
        self.proj.setCategories(['cat1', 'cat3'])
        
        self.resetView()
        self.assertEqual(['http://nohost/plone/psc/by-category/cat1', 'http://nohost/plone/psc/by-category/cat3'],
          self.view.categories_url())
    
    def test_naked_description(self):
        self.proj.getField('text').set(self.proj, 'A full <b>description</b> for a PSCProject')
        self.proj.getField('text').setContentType(self.proj, 'text/html')
        
        self.resetView()
        self.assertEqual('A full description for a PSCProject',
          self.view.naked_description())
    
    def test_all_licenses(self):
        releases = self.proj.releases
        
        releases.invokeFactory('PSCRelease', '0.1')
        releases['0.1'].content_status_modify(workflow_action = 'release-alpha')
        releases['0.1'].reindexObject()
        
        releases.invokeFactory('PSCRelease', '0.2')
        releases['0.2'].content_status_modify(workflow_action = 'release-alpha')
        releases['0.2'].setLicense('BSD')
        releases['0.2'].reindexObject()
        
        releases.invokeFactory('PSCRelease', '0.9')
        releases['0.9'].content_status_modify(workflow_action = 'release-beta')
        releases['0.9'].setLicense('BSD')
        releases['0.9'].reindexObject()
        
        releases.invokeFactory('PSCRelease', '1.0')
        releases['1.0'].content_status_modify(workflow_action = 'release-final')
        releases['1.0'].setLicense('GPL')
        releases['1.0'].reindexObject()
        
        self.resetView()
        self.assertEqual(
            ['http://opensource.org/licenses/bsd-license',
             'http://creativecommons.org/licenses/GPL/2.0/'],
            self.view.all_licenses())
    
    def test_get_oses(self):
        releases = self.proj.releases
        
        releases.invokeFactory('PSCRelease', '0.9')
        releases['0.9'].content_status_modify(workflow_action = 'release-beta')
        releases['0.9'].reindexObject()
        releases['0.9'].invokeFactory('PSCFile', 'linux')
        releases['0.9'].linux.setPlatform('Linux')
        releases['0.9'].linux.reindexObject()
        releases['0.9'].invokeFactory('PSCFileLink', 'windows')
        releases['0.9'].windows.setPlatform('Windows')
        releases['0.9'].windows.reindexObject()
        
        releases.invokeFactory('PSCRelease', '1.0')
        releases['1.0'].content_status_modify(workflow_action = 'release-final')
        releases['1.0'].reindexObject()
        releases['1.0'].invokeFactory('PSCFile', 'linux')
        releases['1.0'].linux.setPlatform('Linux')
        releases['1.0'].linux.reindexObject()
        releases['1.0'].invokeFactory('PSCFile', 'macosx')
        releases['1.0'].macosx.setPlatform('Mac OS X')
        releases['1.0'].macosx.reindexObject()
        releases['1.0'].invokeFactory('PSCFileLink', 'windows')
        releases['1.0'].windows.setPlatform('Windows')
        releases['1.0'].windows.reindexObject()
        
        self.resetView()
        self.assertEqual(
            ['Linux',
             'Windows',
             'Mac OS X'],
            self.view.get_oses())
    
    def test_get_oses_all_platforms(self):
        releases = self.proj.releases
        
        self.portal.psc.setAvailablePlatforms(['Platform independent', 'Linux', 'Windows', 'Mac OS X'])
        
        releases.invokeFactory('PSCRelease', '0.9')
        releases['0.9'].content_status_modify(workflow_action = 'release-beta')
        releases['0.9'].reindexObject()
        releases['0.9'].invokeFactory('PSCFile', 'linux')
        releases['0.9'].linux.setPlatform('Linux')
        releases['0.9'].linux.reindexObject()
        releases['0.9'].invokeFactory('PSCFileLink', 'windows')
        releases['0.9'].windows.setPlatform('Windows')
        releases['0.9'].windows.reindexObject()
        
        releases.invokeFactory('PSCRelease', '1.0')
        releases['1.0'].content_status_modify(workflow_action = 'release-final')
        releases['1.0'].reindexObject()
        releases['1.0'].invokeFactory('PSCFile', 'all')
        releases['1.0'].all.setPlatform('Platform independent')
        platformVocab = releases['1.0'].all.getPlatformVocab()
        releases['1.0'].all.reindexObject()
        
        self.resetView()
        if len(self.view.get_oses()) != 0 and 'Platform independent' in platformVocab:
            self.fail('TODO: BUG?: When All Platforms is set, we should not display the os tag at all, since it would mean the project isn\'t OS specific. This would also mean All Platforms is somewhat standard and uneditable. If you don\'t know what I\'m talking about, contact me at shywolf9982@gmail.com')
    
    def test_get_releases(self):
        releases = self.proj.releases
        
        releases.invokeFactory('PSCRelease', '0.9')
        releases['0.9'].content_status_modify(workflow_action = 'release-beta')
        releases['0.9'].setCodename('sid')
        releases['0.9'].reindexObject()
        
        releases.invokeFactory('PSCRelease', '1.0')
        releases['1.0'].content_status_modify(workflow_action = 'release-final')
        releases['1.0'].setCodename('ummagumma')
        releases['1.0'].setExpectedReleaseDate(DateTime('1/12/2007'))
        releases['1.0'].reindexObject()
        
        releases['1.0'].invokeFactory('PSCFile', 'linux')
        releases['1.0'].linux.setPlatform('Linux')
        f = open(os.path.join(PACKAGE_HOME, 'input', 'pdb.txt')).read()
        releases['1.0'].linux.setDownloadableFile(createFileUpload(f, 'pdb.txt'))
        releases['1.0'].linux.reindexObject()
        
        releases['1.0'].invokeFactory('PSCFileLink', 'windows')
        releases['1.0'].windows.setPlatform('Windows')
        releases['1.0'].windows.setExternalURL('http://nohost')
        releases['1.0'].windows.reindexObject()
        
        self.resetView()
        self.assertEqual(
            [{ 'revision': '0.9', 'name': 'sid', 'date': '', 'files': [] },
             { 'revision': '1.0', 'name': 'ummagumma', 'date': '2007-01-12',
               'files': ['http://nohost/plone/psc/proj/releases/1.0/linux',
                         'http://nohost'] }],
            self.view.get_releases())

    def test_get_tracker(self):
        self.proj.setTracker('http://nohost/trac')
        self.resetView()
        self.assertEqual('http://nohost/trac', self.view.get_tracker())
        
        if HAS_POI:
            # note: here we are using Quickinstaller and this generates a lot of
            # warnings: but this depends a lot on Poi rather than us
            qi = self.portal.portal_quickinstaller              
            qi.installProduct('Poi')
            self.proj.invokeFactory('PoiPscTracker', 'issues')
            if self.view.get_tracker() != 'http://nohost/plone/psc/proj/issues':
                self.fail('Poi tracker should precedence over external one, returned %s' % (self.view.get_tracker()))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProjectDOAPView))
    return suite

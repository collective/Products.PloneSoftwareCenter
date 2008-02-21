from base import PSCTestCase

import os
from cgi import FieldStorage
from tempfile import TemporaryFile

from ZPublisher.HTTPRequest import FileUpload

from Products.PloneSoftwareCenter.tests.utils import PACKAGE_HOME

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

class TestPSCFile(PSCTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        self.portal.psc.proj.releases.invokeFactory('PSCRelease', '1.0')
        self.portal.psc.proj.releases['1.0'].invokeFactory('PSCFile', 'file')
        self.file = self.portal.psc.proj.releases['1.0'].file
    
    def testEditFields(self):
        self.file.setTitle('Custom Title')
        self.assertEqual('Custom Title', self.file.Title())
        
        f = open(os.path.join(PACKAGE_HOME, 'input', 'pdb.txt')).read()
        self.file.setDownloadableFile(createFileUpload(f, 'pdb.txt'))
        
        val = self.file.getDownloadableFile()
        self.assertEqual('pdb.txt', val.filename)
        self.assertEqual('text/plain', val.content_type)
        self.assertEqual(len(f), val.size)
        
        self.file.setPlatform('Platform 1')
        self.assertEqual('Platform 1', self.file.getPlatform())
    
    def test_cleanupFilename(self):
        self.assertEqual(self.file._cleanupFilename('file.tar.gz'),
          'file.tar.gz')
    
    def testGetPlatformVocab(self):
        self.portal.psc.setAvailablePlatforms(['Platform 1', 'Platform 2'])
        self.assertEqual((('Platform 1', 'Platform 1'), ('Platform 2',
          'Platform 2')), self.file.getPlatformVocab().items())
    
class TestPSCFileView(PSCTestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        self.portal.psc.proj.releases.invokeFactory('PSCRelease', '1.0')
        self.portal.psc.proj.releases['1.0'].invokeFactory('PSCFile', 'file')
        self.file = self.portal.psc.proj.releases['1.0'].file
        self.resetView()
    
    def resetView(self):
        self.view = self.file.restrictedTraverse('@@file_view')
        
    def testViewLookup(self):
        self.failIf(self.view is None)
        
    def test_downloadicon_name(self):
        self.file.setPlatform('Test OS')
        
        self.resetView()
        self.assertEqual('platform_test_os.gif',
          self.view.downloadicon_name())
    
    def test_file_size(self):
        f = open(os.path.join(PACKAGE_HOME, 'input', 'pdb.txt')).read()
        self.file.setDownloadableFile(createFileUpload(f, 'pdb.txt'))
        self.resetView()
        self.assertEqual('7.5 kB', self.view.file_size())
    
    def test_direct_url(self):
        self.assertEqual('http://nohost/plone/psc/proj/releases/1.0/file',
          self.view.direct_url())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPSCFile))
    suite.addTest(makeSuite(TestPSCFileView))
    return suite

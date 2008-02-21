from base import PSCTestCase

class TestReleaseFolder(PSCTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        
        self.psc = self.portal.psc
        self.proj = self.portal.psc.proj
        self.releases = self.psc.proj.releases
    
    def testEditFields(self):
        self.releases.setTitle('Custom Releases Title')
        self.assertEqual('Custom Releases Title', self.releases.Title())
        
        self.releases.setDescription('Custom Releases Description')
        self.assertEqual('Custom Releases Description',
          self.releases.Description())
    
    def test_renameAfterCreation(self):
        self.proj.manage_delObjects(['releases'])
        self.proj.invokeFactory('PSCReleaseFolder', 'foo')
        self.proj.foo._renameAfterCreation()
        self.failUnless('releases' in self.proj.objectIds())
    
    def testGenerateUniqueId(self):
        self.assertEqual('1.0', self.releases.generateUniqueId('PSCRelease'))
        
        self.releases.invokeFactory('PSCRelease', '1.0')
        self.assertEqual('1.1', self.releases.generateUniqueId('PSCRelease'))

class TestReleaseFolderView(PSCTestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        self.releases = self.portal.psc.proj.releases
        
        for ver in ['1.0', '2.0', '3.0', '4.0', '5.0']:
            self.releases.invokeFactory('PSCRelease', ver)
        
        self.releases['2.0'].content_status_modify(workflow_action = 'release-alpha')
        self.releases['3.0'].content_status_modify(workflow_action = 'release-final')
        self.releases['4.0'].content_status_modify(workflow_action = 'release-beta')
        self.releases['5.0'].content_status_modify(workflow_action = 'release-final')
        
        self.resetView()
    
    def resetView(self):
        self.view = self.releases.restrictedTraverse('@@releasefolder_view')
    
    def testViewLookup(self):
        self.failIf(self.view is None)
        
    def test_upcoming_releases(self):
        objs = self.view.upcoming_releases()
        #Alpha, beta, and relase-candidates come in order; then
        #pre-releases come at end
        self.assertEqual([self.releases['2.0'], self.releases['4.0'],
          self.releases['1.0']], objs)
    
    def test_previous_releases(self):
        objs = self.view.previous_releases()
        #Final releases come in reverse order
        self.assertEqual([self.releases['5.0'], self.releases['3.0']], objs)
            
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestReleaseFolder))
    suite.addTest(makeSuite(TestReleaseFolderView))
    return suite

from base import PSCTestCase

class TestProposalFolder(PSCTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        self.portal.psc.proj.invokeFactory('PSCImprovementProposalFolder',
          'roadmap')
        self.roadmap = self.portal.psc.proj.roadmap
    
    def testEditFields(self):
        self.roadmap.setTitle('Custom Title')
        self.assertEqual('Custom Title', self.roadmap.Title())
        
        self.roadmap.setDescription('Custom Description')
        self.assertEqual('Custom Description', self.roadmap.Description())
        
        self.roadmap.setProposalTypes(['Type 1', 'Type 2'])
        self.assertEqual(('Type 1', 'Type 2'),
          self.roadmap.getProposalTypes())
    
    def test_renameAfterCreation(self):
        proj = self.portal.psc.proj
        
        proj.manage_delObjects(['roadmap'])
        proj.invokeFactory('PSCImprovementProposalFolder', 'foo')
        proj.foo._renameAfterCreation()
        self.failUnless('roadmap' in proj.objectIds())
    
class TestProposalFolderView(PSCTestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        self.portal.psc.proj.invokeFactory('PSCImprovementProposalFolder',
          'roadmap')
        
        self.roadmap = self.portal.psc.proj.roadmap
        self.resetView()
        
    def resetView(self):
        self.view = self.roadmap.restrictedTraverse('@@roadmap_view')
    
    def testViewLookup(self):
        self.failIf(self.view is None)
        
    def test_state_title(self):
        self.assertEqual('Draft', self.view.state_title('draft'))
        self.assertEqual('In progress', self.view.state_title('in-progress'))
        self.assertEqual('Completed and merged',
          self.view.state_title('completed'))
        self.assertEqual('Rejected', self.view.state_title('rejected'))
        self.assertEqual('Deferred', self.view.state_title('deferred'))
        self.assertEqual('Ready for merge',
          self.view.state_title('ready-for-merge'))
        self.assertEqual('Being discussed',
          self.view.state_title('being-discussed'))
    
    def test_state_title_internationalized(self):
        self.warning("*** TODO: FUTURE - PloneSoftwareCenter is not "
          "internationalized yet. This method state_title actually is -- "
          "it's just not clear how to test it! Also need to "
          "internationalize PSCProject, method getCategoryTitles, among "
          "other methods.")
    
    def test_improvement_proposals(self):
        self.roadmap.invokeFactory('PSCImprovementProposal', '1')
        proposal1 = self.roadmap['1']
        proposal1.setTitle('Proposal 1')
        self.roadmap.invokeFactory('PSCImprovementProposal', '3')
        proposal3 = self.roadmap['3']
        proposal3.setTitle('Proposal 3')
        self.roadmap.invokeFactory('PSCImprovementProposal', '2')
        proposal2 = self.roadmap['2']
        proposal2.setTitle('Proposal 2')
        
        self.resetView()
        objs = [
          brain.getObject() for brain in self.view.improvement_proposals()
          ]
        
        self.assertEqual([proposal1, proposal2, proposal3], objs)
        
        proposal1.content_status_modify(workflow_action='propose')
        proposal2.content_status_modify(workflow_action='propose')
        proposal2.content_status_modify(workflow_action='begin')
        proposal3.content_status_modify(workflow_action='propose')
        proposal3.content_status_modify(workflow_action='begin')
        
        self.resetView()
        objs = [
          brain.getObject() for brain in self.view.improvement_proposals(
            review_state = ['being-discussed']
            )
          ]
        self.assertEqual([proposal1], objs)
        objs = [
          brain.getObject() for brain in self.view.improvement_proposals(
            review_state = ['in-progress']
            )
          ]
        self.assertEqual([proposal2, proposal3], objs)
    
    def test_upcoming_release(self):
        releases = self.portal.psc.proj.releases
        
        for ver in ['1.0', '2.0', '3.0', '4.0', '5.0']:
            releases.invokeFactory('PSCRelease', ver)
        
        releases['2.0'].content_status_modify(workflow_action = 'release-alpha')
        releases['3.0'].content_status_modify(workflow_action = 'release-final')
        releases['4.0'].content_status_modify(workflow_action = 'release-beta')
        releases['5.0'].content_status_modify(workflow_action = 'release-final')
        
        self.resetView()
        objs = self.view.upcoming_releases()
        #Alpha, beta, and relase-candidates come in order; then
        #pre-releases come at end
        self.assertEqual([releases['2.0'], releases['4.0'], releases['1.0']],
          objs)    

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProposalFolder))
    suite.addTest(makeSuite(TestProposalFolderView))
    return suite

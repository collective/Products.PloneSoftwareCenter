from base import PSCTestCase

class TestInstantiation(PSCTestCase):

    def testFullHierarchy(self):
        self.setRoles(('Manager',))
        
        try:
            self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        except:
            self.fail('Failed to instantiate a PloneSoftwareCenter')
        self.psc = self.portal.psc
        
        try:
            self.psc.invokeFactory('PSCProject', 'proj')
        except:
            self.fail('Failed to instantiate a PSCProject')
        self.proj = self.psc.proj
        
        self.failUnless('releases' in self.proj.objectIds())
        self.releases = self.proj.releases
        
        try:
            self.releases.invokeFactory('PSCRelease', '1.0')
        except:
            self.fail('Failed to instantiate a PSCRelease')
        self.release = self.releases['1.0']
        
        try:
            self.release.invokeFactory('PSCFile', 'file')
        except:
            self.fail('Failed to instantiate a PSCFile')
        try:
            self.release.invokeFactory('PSCFileLink', 'link')
        except:
            self.fail('Failed to instantiate a PSCFileLink')
        
        try:
            self.proj.invokeFactory('PSCImprovementProposalFolder',
              'proposal_folder')
        except:
            self.fail('Failed to instantiate a PSCImprovementProposalFolder')
        self.proposal_folder = self.proj.proposal_folder
        try:
            self.proposal_folder.invokeFactory('PSCImprovementProposal', '1')
        except:
            self.fail('Failed to instantiate a PSCImprovementProposal')
        self.proposal = self.proposal_folder['1']
        try:
            self.proposal.invokeFactory('File', 'file')
        except:
            self.fail('Failed to insantiate a file inside an improvement '
              'proposal')
        try:
            self.proposal.invokeFactory('Image', 'image')
        except:
            self.fail('Failed to insantiate an image inside an improvement '
              'proposal')
        
        try:
            self.proj.invokeFactory('PSCDocumentationFolder', 'docs')
        except:
            self.fail('Failed to instantiate a PSCDocumentationFolder')
            
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstantiation))
    return suite

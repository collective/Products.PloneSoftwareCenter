from base import PSCTestCase

from DateTime.DateTime import DateTime

TODAY_DT = DateTime()

class TestRelease(PSCTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        self.portal.psc.proj.releases.invokeFactory('PSCRelease', '1.0')
        self.release = self.portal.psc.proj.releases['1.0']
    
    def testEditFields(self):
        #id - see separate test method
        
        self.release.setReleaseNumber(10)
        self.assertEqual(10, self.release.getReleaseNumber())
        
        self.release.setCodename('barracuda')
        self.assertEqual('barracuda', self.release.getCodename())
        
        self.release.setDescription('A description for a PSCRelease')
        self.assertEqual('A description for a PSCRelease',
          self.release.Description())
        
        self.release.setText('Full description for a PSCRelease')
        self.assertEqual('Full description for a PSCRelease',
          self.release.getRawText())
        
        self.release.setChangelog('Added tests for PSCRelease\nRejoiced')
        self.assertEqual('Added tests for PSCRelease\nRejoiced',
          self.release.getRawChangelog())
        
        self.release.setReleaseManager('Alan Turing')
        self.assertEqual('Alan Turing', self.release.getReleaseManager())
        
        self.release.setReleaseManagerContact('turing@plone.org')
        self.assertEqual('turing@plone.org',
          self.release.getReleaseManagerContact())
        
        self.release.setImprovementProposalFreezeDate(TODAY_DT)
        self.assertEqual(TODAY_DT, self.release.getImprovementProposalFreezeDate())
        
        self.release.setFeatureFreezeDate(TODAY_DT)
        self.assertEqual(TODAY_DT, self.release.getFeatureFreezeDate())
        
        self.release.setExpectedReleaseDate(TODAY_DT)
        self.assertEqual(TODAY_DT, self.release.getExpectedReleaseDate())
        
        self.release.setLicense('license1')
        self.assertEqual('license1', self.release.getLicense())
        
        self.release.setCompatibility(['1.0', '2.0'])
        self.assertEqual(('1.0', '2.0'), self.release.getCompatibility())
        
        #relatedFeatures - see separate test method
        
        self.release.setRepository('http://localhost/repos1')
        self.assertEqual('http://localhost/repos1',
          self.release.getRepository())
    
    def testSetId(self):
        import transaction
        transaction.savepoint()
        self.release.setId('2.0')
        
        self.assertEqual('2.0', self.release.getId())
    
    def testTitle(self):
        self.portal.psc.proj.setTitle('MyProject')
        self.assertEqual('MyProject 1.0 (Unreleased)',
          self.release.Title())
        self.release.content_status_modify(workflow_action = 'release-alpha')
        self.assertEqual('MyProject 1.0 (Alpha release)',
          self.release.Title())
        self.release.content_status_modify(workflow_action = 're-release')
        self.assertEqual('MyProject 1.0 (Alpha release 2)',
          self.release.Title())
        self.release.content_status_modify(workflow_action = 'release-final')
        self.assertEqual('MyProject 1.0',
          self.release.Title())
    
    def testSetRepository(self):
        self.release.setRepository('http://localhost/repos1')
        self.assertEqual('http://localhost/repos1',
          self.release.getRepository())
        
        self.release.setRepository('http://localhost/repos2/')
        self.assertEqual('http://localhost/repos2',
          self.release.getRepository())
    
    def testGenerateTitle(self):
        self.portal.psc.proj.setTitle('MyProject')
        self.assertEqual('MyProject 1.0 (Unreleased)',
          self.release.generateTitle())
        self.release.content_status_modify(workflow_action = 'release-alpha')
        self.assertEqual('MyProject 1.0 (Alpha release)',
          self.release.generateTitle())
        self.release.content_status_modify(workflow_action = 're-release')
        self.assertEqual('MyProject 1.0 (Alpha release 2)',
          self.release.generateTitle())
        self.release.content_status_modify(workflow_action = 'release-final')
        self.assertEqual('MyProject 1.0',
          self.release.generateTitle())
    
    def testGetRelatedFeatures(self):
        proj = self.portal.psc.proj
        
        proj.invokeFactory('PSCImprovementProposalFolder', 'proposals')
        
        proj.proposals.invokeFactory('PSCImprovementProposal', '1')
        proposal1 = proj.proposals['1']
        proposal1.setTitle('Proposal 1')
        proj.proposals.invokeFactory('PSCImprovementProposal', '2')
        proposal2 = proj.proposals['2']
        proposal2.setTitle('Proposal 2')
        proj.proposals.invokeFactory('PSCImprovementProposal', '3')
        proposal3 = proj.proposals['3']
        proposal3.setTitle('Proposal 3')
        proj.proposals.invokeFactory('PSCImprovementProposal', '4')
        proposal4 = proj.proposals['4']
        proposal4.setTitle('Proposal 4')
        
        self.release.setRelatedFeatures([proposal3.UID(), proposal2.UID(),
          proposal1.UID()])
        self.assertEqual([proposal1, proposal2, proposal3],
          self.release.getRelatedFeatures())
        
        proposal1.content_status_modify(workflow_action='propose')
        proposal2.content_status_modify(workflow_action='propose')
        proposal2.content_status_modify(workflow_action='begin')
        proposal3.content_status_modify(workflow_action='propose')
        proposal3.content_status_modify(workflow_action='begin')
        self.assertEqual([proposal1], self.release.getRelatedFeatures(
          review_state = 'being-discussed'))
        self.assertEqual([proposal2, proposal3],
          self.release.getRelatedFeatures(review_state = 'in-progress'))
    
    def testGetMaturity(self):
        self.release.content_status_modify(workflow_action = 'release-beta')
        self.assertEqual('beta', self.release.getMaturity())
    
    def testGetLicenseVocab(self):
        self.portal.psc.proj.setAvailableLicenses([
          'lic1|License 1|http://localhost/license1',
          'lic2|License 2|http://localhost/license2',
          ])
        self.assertEqual((('lic1', 'License 1'), ('lic2', 'License 2')),
          self.release.getLicenseVocab().items())
    
    def testGetCompatibilityVocab(self):
        self.portal.psc.proj.setAvailableVersions([
          '2.0',
          '1.0',
          ])
        self.assertEqual(
          (('2.0', '2.0'), ('1.0', '1.0')),
          self.release.getCompatibilityVocab().items())
    
    def testGetRelatedFeaturesVocab(self):
        proj = self.portal.psc.proj
        
        proj.invokeFactory('PSCImprovementProposalFolder', 'proposals')
        
        proj.proposals.invokeFactory('PSCImprovementProposal', '1')
        proposal1 = proj.proposals['1']
        proposal1.setTitle('Proposal 1')
        proposal1.reindexObject()
        proj.proposals.invokeFactory('PSCImprovementProposal', '2')
        proposal2 = proj.proposals['2']
        proposal2.setTitle('Proposal 2')
        proposal2.reindexObject()
        
        self.assertEqual(((proposal1.UID(), 'Proposal 1'),
          (proposal2.UID(), 'Proposal 2')),
          self.release.getRelatedFeaturesVocab().items())
        
        proposal2.setTitle('Proposal 1')
        proposal2.reindexObject()
        try:
            self.assertEqual(((proposal1.UID(), 'Proposal 1'),
              (proposal2.UID(), 'Proposal 1')),
              self.release.getRelatedFeaturesVocab().items())
        except:
            self.warning('*** TODO: BUG: If two proposals have the same '
              'title, the Related Features Vocabulary only displays one.')
    
    def testShowReleaseNumber(self):
        #This method doesn't test the Archetypes integration that
        #'release number' will only be shown if showReleaseNumber evaluates
        #to true, but it does at least test that showReleaseNumber behaves
        #as expected
        
        self.failIf(self.release.showReleaseNumber())
        
        self.release.content_status_modify(workflow_action = 'release-alpha')
        self.failUnless(self.release.showReleaseNumber())
        
        self.release.content_status_modify(workflow_action = 're-release')
        self.failUnless(self.release.showReleaseNumber())
        
        self.release.content_status_modify(workflow_action = 'release-beta')
        self.failUnless(self.release.showReleaseNumber())
        
        self.release.content_status_modify(workflow_action = 'release-final')
        self.failIf(self.release.showReleaseNumber())
    
class TestReleaseView(PSCTestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        self.portal.psc.proj.releases.invokeFactory('PSCRelease', '1.0')
        self.release = self.portal.psc.proj.releases['1.0']
        self.resetView()
    
    def resetView(self):
        self.view = self.release.restrictedTraverse('@@release_view')
        
    def testViewLookup(self):
        self.failIf(self.view is None)
        
    def testStart(self):
        self.release.setExpectedReleaseDate(TODAY_DT)
        
        self.resetView()
        self.assertEqual(TODAY_DT, self.view.start())
    
    def testEnd(self):
        self.release.setExpectedReleaseDate(TODAY_DT)
        
        self.resetView()
        self.assertEqual(TODAY_DT, self.view.end())
    
    def test_compatibility_vocab(self):
        self.portal.psc.proj.setAvailableVersions([
          '2.0',
          '1.0',
          ])
        
        self.resetView()
        self.assertEqual(
          (('2.0', '2.0'), ('1.0', '1.0')),
          self.view.compatibility_vocab().items())
        
    def test_license_vocab(self):
        self.portal.psc.proj.setAvailableLicenses([
          'lic1|License 1|http://localhost/license1',
          'lic2|License 2|http://localhost/license2',
          ])
        
        self.resetView()
        self.assertEqual((('lic1', 'License 1'), ('lic2', 'License 2')),
          self.view.license_vocab().items())
    
    def test_related_features_vocab(self):
        proj = self.portal.psc.proj
        
        proj.invokeFactory('PSCImprovementProposalFolder', 'proposals')
        
        proj.proposals.invokeFactory('PSCImprovementProposal', '1')
        proposal1 = proj.proposals['1']
        proposal1.setTitle('Proposal 1')
        proposal1.reindexObject()
        proj.proposals.invokeFactory('PSCImprovementProposal', '2')
        proposal2 = proj.proposals['2']
        proposal2.setTitle('Proposal 2')
        proposal2.reindexObject()
        
        self.resetView()
        self.assertEqual(((proposal1.UID(), 'Proposal 1'),
          (proposal2.UID(), 'Proposal 2')),
          self.view.related_features_vocab().items())
        
        proposal2.setTitle('Proposal 1')
        proposal2.reindexObject()
        self.resetView()
        try:
            self.assertEqual(((proposal1.UID(), 'Proposal 1'),
              (proposal2.UID(), 'Proposal 1')),
              self.view.related_features_vocab().items())
        except:
            self.warning('*** TODO: If two proposals have the same '
              'title, the Related Features Vocabulary only displays one.')
    
    def test_validate_id(self):
        self.failIf(self.view.validate_id('abc1.2-3.4'))
        self.failIf(self.view.validate_id('1_2abc'))
        self.failUnless(self.view.validate_id(''))
        self.failUnless(self.view.validate_id('a b'))
        self.failUnless(self.view.validate_id('1 2'))
        self.failUnless(self.view.validate_id('!'))
    
    def test_is_outdated(self):
        self.portal.psc.proj.setAvailableVersions([
          '2.0',
          '1.0',
          ])
        self.resetView()
        self.failIf(self.view.is_outdated())
        
        self.portal.psc.proj.setUnsupportedVersions(['1.0'])
        self.resetView()
        try:
            self.failUnless(self.view.is_outdated())
        except:
            self.warning("*** TODO: BUG?: Right now is_outdated returns False "
              "if there are no up-to-date releases. Is this desired behavior?")
        
        self.portal.psc.proj.releases.invokeFactory('PSCRelease', '2.0')
        self.resetView()
        self.failUnless(self.view.is_outdated())
    
    def test_is_released(self):
        self.failIf(self.view.is_released())
        
        self.release.content_status_modify(workflow_action = 'release-alpha')
        self.resetView()
        self.failUnless(self.view.is_released())
    
    def test_release_date(self):
        self.release.setExpectedReleaseDate('1/1/2000')
        localtime = self.release.restrictedTraverse('@@plone').toLocalizedTime
        self.resetView()
        self.assertEqual(localtime('2000/01/01'), self.view.release_date())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRelease))
    suite.addTest(makeSuite(TestReleaseView))
    return suite

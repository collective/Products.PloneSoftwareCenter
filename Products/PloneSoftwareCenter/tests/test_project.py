from base import PSCTestCase
from base import developer_warning
from Testing import ZopeTestCase

from DateTime.DateTime import DateTime
import os

from Products.CMFCore.utils import getToolByName

from Products.PloneSoftwareCenter.tests.utils import PACKAGE_HOME
from Products.PloneSoftwareCenter.tests.utils import verifyURLWithRequestVars

from zExceptions import Unauthorized

def loadImage(name, size=0):
    """Load image from testing directory
    """
    path = os.path.join(PACKAGE_HOME, 'input', name)
    fd = open(path, 'rb')
    data = fd.read()
    fd.close()
    return data

SMALL_PNG = loadImage('blank-small.png')
LARGE_PNG = loadImage('blank-large.png')


class TestProject(PSCTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        
        self.psc = self.portal.psc
        self.proj = self.portal.psc.proj
    
    def testInitialization(self):
        self.failUnless('releases' in self.proj.objectIds('PSCReleaseFolder'))
    
    def testEditFields(self):
        self.proj.setDescription('A description for a PSCProject')
        self.assertEqual('A description for a PSCProject',
          self.proj.Description())
        
        self.proj.setText('A full description for a PSCProject')
        self.assertEqual('A full description for a PSCProject',
          self.proj.getRawText())
        
        self.proj.setCategories(['cat1', 'cat2'])
        self.assertEqual(('cat1', 'cat2'),
          self.proj.getCategories())
        
        self.proj.setSelfCertifiedCriteria(['crit1', 'crit2'])
        self.assertEqual(('crit1', 'crit2'),
          self.proj.getSelfCertifiedCriteria())
        
        self.proj.setIsApproved(True)
        self.assertEqual(True, self.proj.getIsApproved())
        
        self.proj.setReviewComment('Test review comment')
        self.assertEqual('Test review comment', self.proj.getReviewComment())
        
        self.proj.setUnsupportedVersions(['1.0', '2.0'])
        self.assertEqual(('1.0', '2.0'),
          self.proj.getUnsupportedVersions())
        
        self.proj.setContactAddress('mailto:test@plone.org')
        self.assertEqual('mailto:test@plone.org',
          self.proj.getContactAddress())
        
        self.proj.setHomepage('http://localhost/homepage')
        self.assertEqual('http://localhost/homepage',
          self.proj.getHomepage())
        
        self.proj.setDocumentationLink('http://localhost/docs')
        self.assertEqual('http://localhost/docs',
          self.proj.getDocumentationLink())
        
        self.proj.setRepository('http://localhost/repos')
        self.assertEqual('http://localhost/repos',
          self.proj.getRepository())
        
        self.proj.setTracker('http://localhost/tracker')
        self.assertEqual('http://localhost/tracker',
          self.proj.getTracker())
        
        self.proj.setMailingList('http://localhost/mailing-list')
        self.assertEqual('http://localhost/mailing-list',
          self.proj.getMailingList())
        
        # Any image will be re-converted, so we can't compare actual
        # data. But we can test that if the logo is set to a small image,
        # that the dimensions are as expected.
        self.proj.setLogo(SMALL_PNG, mimetype = 'image/png')
        self.assertEqual(16, self.proj.getLogo().width)
        self.assertEqual(16, self.proj.getLogo().height)
        
        # We can further test that if the logo is set to a large image,
        # that it is resized
        self.proj.setLogo(LARGE_PNG, mimetype = 'image/png')
        self.assertEqual(75, self.proj.getLogo().width)
        self.assertEqual(75, self.proj.getLogo().height)
        
        self.proj.setLogoURL('http://localhost/logo')
        self.assertEqual('http://localhost/logo',
          self.proj.getLogoURL())
        
        self.proj.setScreenshot(SMALL_PNG, mimetype='image/png')
        self.assertEqual(16, self.proj.getScreenshot().width)
        self.assertEqual(16, self.proj.getScreenshot().height)
        
        
        self.proj.setScreenshot(LARGE_PNG, mimetype='image/png')
        self.assertEqual(600, self.proj.getScreenshot().width)
        self.assertEqual(600, self.proj.getScreenshot().height)
    
    def testSetId(self):
        import transaction
        transaction.savepoint()
        self.proj.setId('foo')
        
        self.assertEqual('foo', self.proj.getId())
    
    def testSetCategories(self):
        releases = self.proj.releases
        releases.invokeFactory('PSCRelease', '1.0')
        release = releases['1.0']
        
        self.proj.invokeFactory('PSCImprovementProposalFolder', 'roadmap')
        self.proj.roadmap.invokeFactory('PSCImprovementProposal', '1')
        release.invokeFactory('PSCFile', 'file')
        release.invokeFactory('PSCFileLink', 'filelink')
        
        self.proj.setCategories(['cat1', 'cat2'])
        
        catalog = getToolByName(self.proj, 'portal_catalog')
        res = catalog.searchResults(
                          portal_type=['PSCRelease',
                                       'PSCFile',
                                       'PSCFileLink',
                                       'PSCImprovementProposal'],
                          path='/'.join(self.proj.getPhysicalPath()))
        for r in res:
            self.assertEqual(('cat1', 'cat2'), r.getCategories)
    
    def testGetCategoryTitles(self):
        self.psc.setAvailableCategories([
          'cat1|Category 1|Projects of category 1',
          'cat2|Category 2|Projects of category 2',
          'cat3|Category 3|Projects of category 3',
          ])
        
        self.proj.setCategories(['cat1', 'cat3'])
        
        self.assertEqual(['Category 1', 'Category 3'],
          self.proj.getCategoryTitles())
    
    def testGetCategoriesVocab(self):
        self.psc.setAvailableCategories([
          'cat1|Category 1|Projects of category 1',
          'cat2|Category 2|Projects of category 2',
          'cat3|Category 3|Projects of category 3',
          ])
        
        self.assertEqual((('cat1', 'Category 1'), ('cat2', 'Category 2'),
          ('cat3', 'Category 3'),), self.proj.getCategoriesVocab().items())
    
    def testGetSelfCertificationCriteriaVocab(self):
        self.psc.setAvailableSelfCertificationCriteria([
          'Criterion 1',
          'Criterion 2',
          ])
        
        self.assertEqual((('Criterion 1', 'Criterion 1'), ('Criterion 2',
          'Criterion 2')), self.proj.getSelfCertificationCriteriaVocab().items())
    
    def testGetReleaseFolder(self):
        self.assertEqual(self.proj.releases, self.proj.getReleaseFolder())
        
        self.proj.manage_delObjects(['releases'])
        self.failUnless(self.proj.getReleaseFolder() is None)
        
        self.proj.invokeFactory('PSCReleaseFolder', 'downloads')
        self.assertEqual(self.proj.downloads, self.proj.getReleaseFolder())
    
    def testGetRoadmapFolder(self):
        self.failUnless(self.proj.getRoadmapFolder() is None)
        
        self.proj.invokeFactory('PSCImprovementProposalFolder', 'proposals')
        self.assertEqual(self.proj.proposals, self.proj.getRoadmapFolder())
    
    def testGetNotAddableTypes(self):
        #When PloneHelpCenter is not installed, cannot add
        #PSCDocumentationFolder
        
        self.assertEqual(['PSCReleaseFolder', 'PSCDocumentationFolder'],
          self.proj.getNotAddableTypes())
        
        self.proj.manage_delObjects(['releases'])
        self.proj.invokeFactory('PSCImprovementProposalFolder', 'roadmap')
        
        self.assertEqual(['PSCImprovementProposalFolder',
          'PSCDocumentationFolder',], self.proj.getNotAddableTypes())
        
        self.proj.manage_delObjects(['roadmap'])
        self.proj.invokeFactory('PSCImprovementProposalFolder', 'proposals')
        
        try:
            self.assertEqual(['PSCImprovementProposalFolder',
              'PSCDocumentationFolder',], self.proj.getNotAddableTypes())
        except:
            self.warning('*** TODO: BUG? - If a roadmap folder exists but '
            'not named "roadmap", then currently a project folder allows '
            'adding another roadmap folder. Alternatively, if another '
            'item exists named "roadmap" that is not a roadmap folder, '
            'then one cannot add a roadmap folder. Is this desired '
            'behavior?')
    
    def testGetVersionsVocab(self):
        releases = self.proj.releases
        
        releases.invokeFactory('PSCRelease', '1.0')
        releases.invokeFactory('PSCRelease', '2.0')
        
        self.assertEqual(['1.0', '2.0'],
          self.proj.getVersionsVocab())
    
    def testGetCurrentVersions(self):
        releases = self.proj.releases
        
        releases.invokeFactory('PSCRelease', '1.0')
        releases.invokeFactory('PSCRelease', '2.0')
        releases.invokeFactory('PSCRelease', '3.0')
        
        releases.setUnsupportedVersions(['2.0'])
        
        self.assertEqual(['1.0', '3.0'],
          self.proj.getCurrentVersions())
    
    def testHaveHelpCenter(self):
        self.failIf(self.proj.haveHelpCenter())
    
    def testGetAvailableFeaturesAsDisplayList(self):
        self.proj.invokeFactory('PSCImprovementProposalFolder', 'proposals')
        
        self.proj.proposals.invokeFactory('PSCImprovementProposal', '1')
        proposal1 = self.proj.proposals['1']
        proposal1.setTitle('Proposal 1')
        proposal1.reindexObject()
        
        self.proj.proposals.invokeFactory('PSCImprovementProposal', '2')
        proposal2 = self.proj.proposals['2']
        proposal2.setTitle('Proposal 2')
        proposal2.reindexObject()
        
        self.assertEqual(((proposal1.UID(), 'Proposal 1'),
          (proposal2.UID(), 'Proposal 2')),
          self.proj.getAvailableFeaturesAsDisplayList().items())
        

    def testGetAvailableFeaturesAsDisplayListBlockDupes(self):
        """I test to see if you can change the title of a list item to match another list item.
            You are not supposed to be able to do this sort of action without Plone throwing a failure."""
        self.proj.invokeFactory('PSCImprovementProposalFolder', 'proposalDupes')

        self.proj.proposalDupes.invokeFactory('PSCImprovementProposal', '3')
        proposal3 = self.proj.proposalDupes['3']
        proposal3.setTitle('Proposal 3')
        proposal3.reindexObject()

        self.proj.proposalDupes.invokeFactory('PSCImprovementProposal', '4')
        proposal4 = self.proj.proposalDupes['4']
        proposal4.setTitle('Proposal 3')
        proposal4.reindexObject()
        
        try:
            self.assertEqual(((proposal4.UID(), proposal4.Title()),),
              self.proj.getAvailableFeaturesAsDisplayList().items())
        except:
            statement = '*** TODO: BUG: If two proposals have the same '
            statement += 'title, the Related Features Vocabulary only displays one.'
            #self.warning(statement)
            self.warning([((proposal4.UID(), proposal4.Title()),),
              self.proj.getAvailableFeaturesAsDisplayList().items()])

class TestProjectWithPloneHelpCenterIntegration(PSCTestCase):
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        
        self.psc = self.portal.psc
        self.proj = self.portal.psc.proj
        
        self.setRoles(('Manager',))
        qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        try:
            qi_tool.installProduct('PloneHelpCenter')
        except AttributeError:
            self.warning('PloneHelpCenter integration tests cannot be run '
              'because the product is not installed.')
        # At least in Plone 3 an AttributeError while installing
        # PloneHelpCenter is swallowed.  So we have to do a better
        # check.
        self.failIf(qi_tool.PloneHelpCenter.error)

    def testGetNotAddableTypes(self):
        self.failUnless('PSCDocumentationFolder' not in self.proj.getNotAddableTypes())
        self.proj.invokeFactory('PSCDocumentationFolder', 'documentation')
        self.failUnless('PSCDocumentationFolder' in self.proj.getNotAddableTypes())
    
    def testHaveHelpCenter(self):
        self.failUnless(self.proj.haveHelpCenter())

class TestProjectView(PSCTestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        self.proj = self.portal.psc.proj
        self.resetView()
    
    def resetView(self):
        self.view = self.proj.restrictedTraverse('@@project_view')
    
    def testViewLookup(self):
        self.failIf(self.view is None)
        
    def test_latest_release(self):
        releases = self.proj.releases
        
        releases.invokeFactory('PSCRelease', '1.0')
        releases['1.0'].content_status_modify(
          workflow_action = 'release-final')
        releases['1.0'].setEffectiveDate(DateTime('1/2/2000'))
        releases['1.0'].reindexObject()
        
        releases.invokeFactory('PSCRelease', '2.0')
        releases['2.0'].content_status_modify(
          workflow_action = 'release-final')
        releases['2.0'].setEffectiveDate(DateTime('1/1/2000'))
        releases['2.0'].reindexObject()
        
        self.resetView()
        self.assertEqual(releases['1.0'], self.view.latest_release())
    
    def test_latest_release_date(self):
        releases = self.proj.releases
        localtime = self.proj.restrictedTraverse('@@plone').toLocalizedTime
        
        releases.invokeFactory('PSCRelease', '1.0')
        releases['1.0'].content_status_modify(
          workflow_action = 'release-final')
        releases['1.0'].setEffectiveDate(DateTime('1/2/2000'))
        releases['1.0'].reindexObject()
        
        releases.invokeFactory('PSCRelease', '2.0')
        releases['2.0'].content_status_modify(
          workflow_action = 'release-final')
        releases['2.0'].setEffectiveDate(DateTime('1/1/2000'))
        releases['2.0'].reindexObject()

        self.resetView()
        self.assertEqual(localtime('2000/01/02'), self.view.latest_release_date())
    
    def test_upcoming_release(self):
        releases = self.proj.releases
        
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
    
    def test_release_rss_url(self):
        url = self.view.release_rss_url()
        # Removed review_state as it was removed in ProjectView @78203
        self.failUnless(verifyURLWithRequestVars(
          url, 
          'http://nohost/plone/psc/proj/search_rss',
          ['portal_type=PSCRelease', 'sort_on=Date', 'sort_order=reverse',
            'path=/plone/psc/proj']
          ))
    
    def test_display_categories(self):
        self.portal.psc.setAvailableCategories([
          'cat1|Category 1|Projects of category 1',
          'cat2|Category 2|Projects of category 2',
          'cat3|Category 3|Projects of category 3',
          ])
        
        self.proj.setCategories(['cat1', 'cat3'])
        
        self.resetView()
        self.assertEqual('Category 1, Category 3',
          self.view.display_categories())
    
    def test_similar_search_url(self):
        url = self.view.similar_search_url()
        self.assertEqual(url.count('?'), 1)
        url1, url2 = url.split('?')
        
        self.assertEqual('http://nohost/plone/search', url1)
        
        request_list = url2.split('&')
        for kw in ['portal_type%3Alist=PSCProject', 'Creator=test_user_1_',]:
            count = request_list.count(kw)
            self.failUnless(count)
            for i in range(count):
                request_list.remove(kw)
        
        self.failIf(request_list != [])
    
    def test_is_public(self):
        self.failIf(self.view.is_public())
        
        self.proj.content_status_modify(workflow_action = 'publish')
        self.failUnless(self.view.is_public())
    
    def test_release_folder_url(self):
        self.assertEqual('http://nohost/plone/psc/proj/releases',
           self.view.release_folder_url())
        
        self.proj.manage_delObjects(['releases'])
        self.resetView()
        self.failUnless(self.view.release_folder_url() is None)
    
    def test_roadmap_folder_url(self):
        self.failUnless(self.view.roadmap_folder_url() is None)
        self.proj.invokeFactory('PSCImprovementProposalFolder', 'roadmap')
        self.assertEqual('http://nohost/plone/psc/proj/roadmap',
           self.view.roadmap_folder_url())
    
    def test_has_documentation_link(self):
        self.failIf(self.view.has_documentation_link())
        
        self.proj.invokeFactory('PSCDocumentationFolder', 'documentation')
        self.resetView()
        self.failUnless(self.view.has_documentation_link())
        
        self.proj.manage_delObjects(['documentation',])
        self.proj.setDocumentationLink('http://otherhost/docs')
        self.resetView()
        self.failUnless(self.view.has_documentation_link())
        
    def test_documentation_url(self):
        self.failUnless(self.view.documentation_url() is None)
        
        self.proj.invokeFactory('PSCDocumentationFolder', 'documentation')
        self.resetView()
        self.assertEqual('http://nohost/plone/psc/proj/documentation',
          self.view.documentation_url())
        
        self.proj.manage_delObjects(['documentation',])
        self.proj.setDocumentationLink('http://otherhost/docs')
        self.resetView()
        self.assertEqual('http://otherhost/docs',
          self.view.documentation_url())
    
    def test_documentation_link_class(self):
        self.failUnless(self.view.documentation_link_class() is None)
        
        self.proj.invokeFactory('PSCDocumentationFolder', 'documentation')
        self.resetView()
        self.failUnless(self.view.documentation_link_class() is None)
        
        self.proj.manage_delObjects(['documentation',])
        self.proj.setDocumentationLink('http://otherhost/docs')
        self.resetView()
        self.assertEqual('link-plain', self.view.documentation_link_class())
    
    def test_additional_resources(self):
        self.proj.invokeFactory('PSCImprovementProposalFolder', 'roadmap')
        self.assertEqual(self.view.additional_resources(),
          [self.proj.releases, self.proj.roadmap])
    
    def test_criteria_info(self):
        self.portal.psc.setAvailableSelfCertificationCriteria([
          'Criterion 1',
          'Criterion 2',
          ])
        
        self.proj.setSelfCertifiedCriteria(['Criterion 2',])
        
        self.resetView()
        res = self.view.criteria_info()
        
        self.assertEqual(2, len(res))
        
        r = res[0]
        self.assertEqual(False, r['selected'])
        self.assertEqual('Criterion 1', r['text'])
        
        r = res[1]
        self.assertEqual(True, r['selected'])
        self.assertEqual('Criterion 2', r['text'])

    def test_distutils_ids(self):

        # each project holds distutils names
        main = self.proj.getDistutilsMainId()
        self.assertEquals(main, '')

        secondaries = self.proj.getDistutilsSecondaryIds()
        self.assertEquals(secondaries, ())

        # we can set them
        self.proj.setDistutilsMainId('my.egg')
        main = self.proj.getDistutilsMainId()
        self.assertEquals(main, 'my.egg')

        self.proj.setDistutilsSecondaryIds(['iw.recipe.one', 'iw.recipe.two'])
        secondaries = self.proj.getDistutilsSecondaryIds()
        self.assertEquals(secondaries, ('iw.recipe.one', 'iw.recipe.two'))


        self.portal.psc.invokeFactory('PSCProject', 'proj2')

        proj2 = self.portal.psc.proj2
        
        # Unrelated projects can be in the repository
        
        proj2.setDistutilsMainId('circulartriangle.recipe.two')
        main = proj2.getDistutilsMainId()
        self.assertEquals(main, 'circulartriangle.recipe.two')
        
        proj2.setDistutilsSecondaryIds(['circulartriangle.recipe.three',
                                        'circulartriangle.recipe.one'])
        secondaries = proj2.getDistutilsSecondaryIds()
        self.assertEquals(secondaries, ('circulartriangle.recipe.three',
                                        'circulartriangle.recipe.one'))

        # but if a name is already taken by someone else
        # it has to fail

        self.assertRaises(Unauthorized, proj2.setDistutilsMainId,
                          'iw.recipe.two')
        
        self.assertRaises(Unauthorized, proj2.setDistutilsSecondaryIds,
                          ['iw.recipe.three', 'iw.recipe.one'])


class TestProjectInternationalized(PSCTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        
        self.psc = self.portal.psc
        self.proj = self.portal.psc.proj
    
    def testGetCategoryTitles(self):
        self.warning('TODO: Internationalize product and write test.')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProject))
    suite.addTest(makeSuite(TestProjectView))
    if ZopeTestCase.hasProduct('PloneHelpCenter'):
        suite.addTest(makeSuite(TestProjectWithPloneHelpCenterIntegration))
    else:
        developer_warning("PloneHelpCenter integration tests ignored.")
    #suite.addTest(makeSuite(TestProjectInternationalized))
    return suite

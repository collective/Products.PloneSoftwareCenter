from base import PSCTestCase

from DateTime.DateTime import DateTime

from Products.PloneSoftwareCenter.tests.utils import verifyURLWithRequestVars

class TestSoftwareCenter(PSCTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.psc = self.portal.psc
    
    def testValidateAvailableCategories(self):
        self.psc.invokeFactory('PSCProject', 'p')
        
        dangerousCategory = ['p|products|Products']
        safeCategory = ['q|quick|Quick']
        
        self.assertEqual(None, self.psc.validate_availableCategories(safeCategory))
        self.assertNotEqual(None, self.psc.validate_availableCategories(dangerousCategory))
        self.assertNotEqual(None, self.psc.validate_availableCategories(safeCategory + dangerousCategory))
    
    def testEditFields(self):
        self.psc.setDescription('A description for a Software Center')
        self.assertEqual('A description for a Software Center', self.psc.Description())
        
        self.psc.setAvailableCategories([
          'cat1|Category 1|Projects of category 1',
          'cat2|Category 2|Projects of category 2',
          ])
        self.assertEqual((
          'cat1|Category 1|Projects of category 1',
          'cat2|Category 2|Projects of category 2',
          ),
          self.psc.getAvailableCategories())
        
        self.psc.setAvailableLicenses([
          'lic1|License 1|http://localhost/license1',
          'lic2|License 2|http://localhost/license2',
          ])
        self.assertEqual((
          'lic1|License 1|http://localhost/license1',
          'lic2|License 2|http://localhost/license2',
          ),
          self.psc.getAvailableLicenses())
        
        self.psc.setAvailableVersions([
          '2.0',
          '1.0',
          ])
        self.assertEqual((
          '2.0',
          '1.0',
          ),
          self.psc.getAvailableVersions())
        
        self.psc.setAvailablePlatforms([
          'Platform 2',
          'Platform 1',
          ])
        self.assertEqual((
          'Platform 2',
          'Platform 1',
          ),
          self.psc.getAvailablePlatforms())
        
        self.psc.setProjectEvaluators([
          'member1',
          'member2',
          ])
        self.assertEqual((
          'member1',
          'member2',
          ),
          self.psc.getProjectEvaluators())
        
        self.psc.setAvailableSelfCertificationCriteria([
          'Criterion 1',
          'Criterion 2',
          ])
        self.assertEqual((
          'Criterion 1',
          'Criterion 2',
          ),
          self.psc.getAvailableSelfCertificationCriteria())
        
        self.assertEqual(False, self.psc.getUseClassifiers())
        self.psc.setUseClassifiers(True)
        self.assertEqual(True, self.psc.getUseClassifiers())
         
    def testGetAvailableCategoriesAsDisplayList(self):
        self.psc.setAvailableCategories([
          'cat1|Category 1|Projects of category 1',
          'cat2|Category 2|Projects of category 2',
          ])
        self.assertEqual(
          (('cat1', 'Category 1'), ('cat2', 'Category 2')),
          self.psc.getAvailableCategoriesAsDisplayList().items()
          )
    
    def testGetAvailableLicensesAsDisplayList(self):
        self.psc.setAvailableLicenses([
          'lic1|License 1|http://localhost/license1',
          'lic2|License 2|http://localhost/license2',
          ])
        self.assertEqual(
          (('lic1', 'License 1'), ('lic2', 'License 2')),
          self.psc.getAvailableLicensesAsDisplayList().items()
          )
    
    def testGetAvailableVersionsAsDisplayList(self):
        self.psc.setAvailableVersions([
          '2.0',
          '1.0',
          ])
        self.assertEqual(
          (('2.0', '2.0'), ('1.0', '1.0')),
          self.psc.getAvailableVersionsAsDisplayList().items())
    
    def testGetAvailableSelfCertificationCriteriaAsDisplayList(self):
        self.psc.setAvailableSelfCertificationCriteria([
          'Criterion 1',
          'Criterion 2',
          ])
        self.assertEqual(
          (('Criterion 1', 'Criterion 1'), ('Criterion 2', 'Criterion 2')),
          self.psc.getAvailableSelfCertificationCriteriaAsDisplayList().items())

class TestSoftwareCenterRoles(PSCTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.psc = self.portal.psc
    
    def testProjectEvaluatorRole(self):
        self.failUnless('PSCEvaluator' in self.psc.validRoles())

class TestSoftwareCenterAsContainer(PSCTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.psc = self.portal.psc
        
        for id in ['proj4', 'proj3', 'proj2', 'proj1']: 
            self.psc.invokeFactory('PSCProject', id)
        
        self.psc.setCategories(self.psc.proj4, ['cat1'])
        self.psc.setCategories(self.psc.proj3, ['cat1'])
        self.psc.setCategories(self.psc.proj2, ['cat2'])
        self.psc.setCategories(self.psc.proj1, ['cat1','cat2'])
        
        self.psc.proj4.content_status_modify(workflow_action='publish')
        self.psc.proj3.content_status_modify(workflow_action='publish')
        self.psc.proj2.content_status_modify(workflow_action='publish')
    
    def testGetProjectsByCategory(self):
        objs = [brain.getObject() for brain in self.psc.getProjectsByCategory(
          'cat1')]
        self.assertEqual([self.psc.proj1, self.psc.proj3, self.psc.proj4],
          objs)
        
        objs = [brain.getObject() for brain in self.psc.getProjectsByCategory(
          'cat1', states=['published',])]
        self.assertEqual([self.psc.proj3, self.psc.proj4], objs)
        
        objs = [brain.getObject() for brain in self.psc.getProjectsByCategory(
          'cat1', limit=2)]
        self.assertEqual([self.psc.proj1, self.psc.proj3], objs)    
    
    def test_getContained(self):
        objs = [brain.getObject() for brain in self.psc._getContained(
          states=['published'], portal_type='PSCProject')]
        self.assertEqual([self.psc.proj2, self.psc.proj3, self.psc.proj4],
          objs)
        
        objs = [brain.getObject() for brain in self.psc._getContained(
          category='cat1', portal_type='PSCProject')]
        self.assertEqual([self.psc.proj1, self.psc.proj3, self.psc.proj4],
          objs)
        
        self.assertEqual([], self.psc._getContained(portal_type='DummyType'))
        
        objs = [brain.getObject() for brain in self.psc._getContained(
          portal_type='PSCProject', limit=2)]
        self.assertEqual([self.psc.proj1, self.psc.proj2],
          objs)
        
        objs = [brain.getObject() for brain in self.psc._getContained(
          portal_type='PSCProject', sort_on='sortable_title', sort_order='reverse')]
        self.assertEqual([self.psc.proj4, self.psc.proj3, self.psc.proj2,
          self.psc.proj1], objs)

class TestSoftwareCenterView(PSCTestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.psc = self.portal.psc
        self.resetView()
        
    def resetView(self):
        self.view = self.psc.restrictedTraverse('@@softwarecenter_view')
    
    def testViewLookup(self):
        self.failIf(self.view is None)
        
    def test_rss_url(self):
        self.failUnless(verifyURLWithRequestVars(
          self.view.rss_url(),
          'http://nohost/plone/psc/search_rss',
          ['portal_type=PSCRelease', 'sort_on=Date',
          'sort_order=reverse', 'review_state=alpha', 'review_state=beta',
          'review_state=release-candidate', 'review_state=final']
          ))
    
    def test_active_projects(self):
        for id in ['proj1', 'proj2', 'proj3', 'proj4']: 
            self.psc.invokeFactory('PSCProject', id)
            self.psc[id].content_status_modify(workflow_action = 'publish')
        self.psc.invokeFactory('PSCProject', 'proj5')
        
        for id in ['proj1', 'proj2', 'proj3']:
            self.psc[id].releases.invokeFactory('PSCRelease', '1.0')
        
        self.resetView()
        results = self.view.active_projects()
        self.assertEqual(0, len(results))
        
        self.psc.proj1.releases['1.0'].content_status_modify(
          workflow_action = 'release-alpha')
        self.psc.proj3.releases['1.0'].content_status_modify(
          workflow_action = 'release-candidate')
        
        self.resetView()
        results = self.view.active_projects()
        self.assertEqual(2, len(results))
        
        self.psc.proj1.releases['1.0'].content_status_modify(
          workflow_action = 'retract')
        
        self.resetView()
        results = self.view.active_projects()
        self.assertEqual(1, len(results))
    
    def test_can_add_project(self):
        self.psc.manage_permission('PloneSoftwareCenter: Add Project',
           roles=['Member'], acquire=0)
        
        self.setRoles(['Member'])
        self.failUnless(self.view.can_add_project())
        
        self.psc.manage_permission('PloneSoftwareCenter: Add Project',
           roles=['Manager'], acquire=0)
        
        self.failIf(self.view.can_add_project())
        self.setRoles(['Manager'])
        self.failUnless(self.view.can_add_project())
    
    def test_project_count(self):
        for id in ['proj1', 'proj2', 'proj3', 'proj4']: 
            self.psc.invokeFactory('PSCProject', id)
        
        self.resetView()
        self.assertEqual(4, self.view.project_count())
    
    def test_release_count(self):
        for i in range(1,5):
            proj_id = 'proj%s' % str(i)
            self.psc.invokeFactory('PSCProject', proj_id)
            for j in range(1,i+1):
                release_id = '%s.0' % str(j)
                self.psc[proj_id].releases.invokeFactory('PSCRelease',
                  release_id)
        
        self.resetView()
        self.assertEqual(10, self.view.release_count())
    
    def test_categories(self):
        self.psc.setAvailableCategories([
          'cat1|Category 1|Projects of category 1',
          'cat2|Category 2|Projects of category 2',
          'cat3|Category 3|Projects of category 3',
          ])
        self.psc.invokeFactory('PSCProject', 'proj1')
        self.psc.invokeFactory('PSCProject', 'proj2')
        self.psc.invokeFactory('PSCProject', 'proj3')
        
        self.psc.proj1.setCategories(['cat1'])
        self.psc.proj1.reindexObject()
        self.psc.proj2.setCategories(['cat1', 'cat2'])
        self.psc.proj2.reindexObject()
        
        self.psc.proj1.setTitle('Project A')
        self.psc.proj1.releases.invokeFactory('PSCRelease', '1.0')
        self.psc.proj1.releases['1.0'].setDescription('A release')
        self.psc.proj1.releases['1.0'].setEffectiveDate(DateTime('1/2/2000'))
        self.psc.proj1.releases['1.0'].reindexObject()
        self.psc.proj2.setTitle('Project B')
        self.psc.proj2.releases.invokeFactory('PSCRelease', '1.0')
        self.psc.proj2.releases['1.0'].setDescription('A release')
        self.psc.proj2.releases['1.0'].setEffectiveDate(DateTime('1/1/2000'))
        self.psc.proj2.releases['1.0'].reindexObject()
        
        self.resetView()
        categories = list(self.view.categories())
        
        #cat1, cat2 are stored in that order in self.psc
        #So, self.view.categories() should also return the category info
        #for cat1 first, and cat2 second
        
        self.assertEqual(2, len(categories))
        keys1, keys2 = categories[0].keys(), categories[1].keys()
        keys1.sort()
        keys2.sort()
        
        self.assertEqual(['description', 'id', 'name', 'num_projects',
          'releases', 'rss_url'], keys1)
        self.assertEqual(['description', 'id', 'name', 'num_projects',
          'releases', 'rss_url'], keys2)
        
        # verify description, id, name, num_projects
        self.assertEqual('Category 1', categories[0]['name'])
        self.assertEqual('Projects of category 1', categories[0]['description'])
        self.assertEqual(2, categories[0]['num_projects'])
        self.assertEqual('cat1', categories[0]['id'])
        
        self.assertEqual('Category 2', categories[1]['name'])
        self.assertEqual('Projects of category 2', categories[1]['description'])
        self.assertEqual(1, categories[1]['num_projects'])
        self.assertEqual('cat2', categories[1]['id'])
        
        # verify rss_url for cat1 (we skip the analogous test for cat2)
        self.failUnless(verifyURLWithRequestVars(
          categories[0]['rss_url'],
          'http://nohost/plone/search_rss',
          ['portal_type=PSCRelease', 'sort_on=Date',
          'sort_order=reverse', 'path=/plone/psc', 'getCategories=cat1',
          'review_state=alpha', 'review_state=beta',
          'review_state=release-candidate', 'review_state=final']
          ))
           
        #verify releases for cat1 (we skip the analogous test for cat2)
        #and only for the first release in the list, which is Project A 1.0
        #because it was released later
        self.assertEqual(2, len(categories[0]['releases']))
        releaseDict = categories[0]['releases'][0]
        keys = releaseDict.keys()
        keys.sort()
        self.assertEqual(['date', 'description', 'parent_url', 'review_state',
          'title'], keys)
        
        self.assert_(releaseDict['date'].startswith('2000-01-02'))
        self.assertEqual('A release', releaseDict['description'])
        self.assertEqual(
          'http://nohost/plone/psc/proj1', releaseDict['parent_url'])
        self.assertEqual('pre-release', releaseDict['review_state'])
        self.assertEqual('Project A 1.0 (Unreleased)', releaseDict['title'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSoftwareCenter))
    suite.addTest(makeSuite(TestSoftwareCenterRoles))
    suite.addTest(makeSuite(TestSoftwareCenterView))
    return suite

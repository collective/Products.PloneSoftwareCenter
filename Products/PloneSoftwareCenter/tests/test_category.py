from base import PSCTestCase


class TestCategoryView(PSCTestCase):

    def afterSetUp(self):

        self.setRoles(('Manager',))

        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')

        self.psc = self.portal.psc

        for id in ['proj4', 'proj3', 'proj2', 'proj1']: 

            self.psc.invokeFactory('PSCProject', id)

        self.psc.proj4.setCategories(['cat1'])
        self.psc.proj3.setCategories(['cat1'])
        self.psc.proj2.setCategories(['cat2'])
        self.psc.proj1.setCategories(['cat1','cat2'])
        self.psc.proj4.content_status_modify(workflow_action='publish')
        self.psc.proj3.content_status_modify(workflow_action='publish')
        self.psc.proj2.content_status_modify(workflow_action='publish')

        self.resetView()

    def resetView(self):
        self.view = self.psc.restrictedTraverse('@@category_view')

    def testViewLookup(self):
        self.failIf(self.view is None)
    
    def test_category_name(self):
        self.psc.setAvailableCategories([
          'cat1|Category 1|Projects of category 1',
          'cat2|Category 2|Projects of category 2',
          ])
        self.resetView()
        self.assertEqual(self.view.category_name('cat1'), 'Category 1' )
    
    def test_category_description(self):
        self.psc.setAvailableCategories([
          'cat1|Category 1|Projects of category 1',
          'cat2|Category 2|Projects of category 2',
          ])
        self.assertEqual(self.view.category_description('cat1'), 'Projects of category 1')

    def test_by_category(self):
        objs = [brain.getObject() for brain in self.view.by_category(
          'cat1')]
        objs.sort()
        for wanted in (self.psc.proj4, self.psc.proj3, self.psc.proj1):
            self.assert_(wanted in objs)

        objs = [brain.getObject() for brain in self.view.by_category(
          'cat1', states=['published',])]

        for wanted in (self.psc.proj4, self.psc.proj3):
            self.assert_(wanted in objs)
        
        objs = [brain.getObject() for brain in self.view.by_category(
          'cat1', limit=2)]
        objs.sort()
        for wanted in (self.psc.proj4, self.psc.proj3):
            self.assert_(wanted in objs)    
    
    def test_contained(self):

        objs = [brain.getObject() for brain in self.view._contained(
          category='cat1', portal_type='PSCProject', states=['published'], sort_on='sortable_title')]
        self.assertEqual([self.psc.proj3, self.psc.proj4], objs)

        objs = [brain.getObject() for brain in self.view._contained(
          category='cat1', portal_type='PSCProject', states=['published'])]
        
        for proj in (self.psc.proj4, self.psc.proj3):
            self.assert_(proj in objs)

        self.assertEqual([], self.view._contained(
          category='cat1', portal_type='DummyType', states=['published']))
        
        objs = [brain.getObject() for brain in self.view._contained(
          category='cat1', portal_type='PSCProject', states=['published'], limit=2)]
        self.assertEqual([self.psc.proj3, self.psc.proj4],
          objs)
        
        objs = [brain.getObject() for brain in self.view._contained(
          category='cat1', portal_type='PSCProject', states=['published'], sort_on='sortable_title', sort_order='reverse')]
        self.assertEqual([self.psc.proj3, self.psc.proj4], objs)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCategoryView))
    return suite

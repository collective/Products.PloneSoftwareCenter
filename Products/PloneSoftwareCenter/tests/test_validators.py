from base import PSCTestCase

from Products.PloneSoftwareCenter.validators import ProjectIdValidator

class TestValidators(PSCTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        
        self.psc = self.portal.psc
        self.proj = self.portal.psc.proj
        
    def testProjectIdValidator(self):
        # Archetypes validation machinery is unclear so it's not clear
        # whether the test should ensure that additional keywords like
        # errors and REQUEST should be passed in
        validator = ProjectIdValidator('foo')
        self.psc.setAvailableCategories([
          'cat1|Category 1|Projects of category 1',
          'cat2|Category 2|Projects of category 2',
          ])
        self.assertNotEqual(1, validator('cat1', instance = self.proj))
        self.assertEqual(1, validator('cat3', instance = self.proj))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestValidators))
    return suite

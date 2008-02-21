from base import PSCTestCase

from Products.CMFCore.utils import getToolByName

class TestDocFolder(PSCTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        self.portal.psc.proj.invokeFactory('PSCDocumentationFolder',
          'documentation')
        self.documentation = self.portal.psc.proj.documentation
    
    def allowDocumentContentType(self):
        typesTool = getToolByName(self.portal, 'portal_types')
        fti = typesTool['PSCDocumentationFolder']
        act = list(fti.allowed_content_types)
        if 'Document' not in act:
            act.append('Document')
        fti.allowed_content_types = act
    
    def testEditFields(self):
        self.documentation.setTitle('Custom Title')
        self.assertEqual('Custom Title', self.documentation.Title())
        
        self.documentation.setDescription('Custom description.')
        self.assertEqual('Custom description.',
          self.documentation.Description())
        
        self.documentation.setAudiencesVocab(['Users', 'Gurus'])
        self.assertEqual(('Users', 'Gurus'),
          self.documentation.getAudiencesVocab())
    
    def test_renameAfterCreation(self):
        proj = self.portal.psc.proj
        
        proj.manage_delObjects(['documentation'])
        proj.invokeFactory('PSCDocumentationFolder', 'foo')
        proj.foo._renameAfterCreation()
        self.failUnless('documentation' in proj.objectIds())
    
    def test_generateUniqueId(self):
        consideredTypes = {
            'HelpCenterFAQFolder': 'faq',
            'HelpCenterHowToFolder': 'how-to',
            'HelpCenterTutorialFolder': 'tutorial',
            'HelpCenterErrorReferenceFolder': 'error',
            'HelpCenterLinkFolder': 'link',
            'HelpCenterGlossary': 'glossary',
            'HelpCenterInstructionalVideoFolder': 'video',
            }
        
        for k, v in consideredTypes.items():
            self.assertEqual(v, self.documentation.generateUniqueId(k))
        
        self.allowDocumentContentType()
        
        self.documentation.invokeFactory('Document', 'faq')
        self.assertEqual('faq.0',
          self.documentation.generateUniqueId('HelpCenterFAQFolder'))
        
        self.documentation.invokeFactory('Document', 'faq.0')
        self.assertEqual('faq.1',
          self.documentation.generateUniqueId('HelpCenterFAQFolder'))
    
    def test_ensureUniqueId(self):
        self.allowDocumentContentType()
        
        self.documentation.invokeFactory('Document', 'foo')
        self.assertEqual('foo.0',
          self.documentation._ensureUniqueId('foo'))
        
        self.documentation.invokeFactory('Document', 'foo.0')
        self.assertEqual('foo.1',
          self.documentation._ensureUniqueId('foo'))
    
class TestDocFolderView(PSCTestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        self.portal.psc.proj.invokeFactory('PSCDocumentationFolder',
          'documentation')
        self.documentation = self.portal.psc.proj.documentation
        self.resetView()
    
    def resetView(self):
        self.view = self.documentation.restrictedTraverse('@@docfolder_view')
        
    def allowDocumentContentType(self):
        typesTool = getToolByName(self.portal, 'portal_types')
        fti = typesTool['PSCDocumentationFolder']
        act = list(fti.allowed_content_types)
        if 'Document' not in act:
            act.append('Document')
        fti.allowed_content_types = act
    
    def testViewLookup(self):
        self.failIf(self.view is None)
        
    def test_non_phc_contents(self):
        self.assertEqual(0, len(self.view.non_phc_contents()))
        
        self.allowDocumentContentType()
        
        self.documentation.invokeFactory('Document', 'opus')
        self.resetView()
        objs = [brain.getObject() for brain in self.view.non_phc_contents()]
        self.assertEqual([self.documentation.opus], objs)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDocFolder))
    suite.addTest(makeSuite(TestDocFolderView))
    return suite

from base import PSCTestCase
from base import developer_warning
from Testing import ZopeTestCase

from AccessControl.Permission import Permission

from Products.CMFCore.utils import getToolByName

from Products.PloneSoftwareCenter.permissions import AddSoftwareCenter

def allowMembersToAddCenter(obj):
    perms = [p for p in obj.ac_inherited_permissions(1) if p[0] == AddSoftwareCenter]
    p = perms[0]
    name, value = perms[0][:2]
    p = Permission(name, value, obj)
    roles = p.getRoles()
    if 'Member' not in roles:
        if type(roles) == type(()):
            roles = list(roles)
            roles.append('Member')
            roles = tuple(roles)
        else:
            roles.append('Member')
    p.setRoles(roles)

class TestCenterSecurity(PSCTestCase):

    def afterSetUp(self):
        # Definitions for convenience
        self.wf_tool = getToolByName(self.portal, 'portal_workflow')
        
        # Actual changes to portal
        allowMembersToAddCenter(self.portal)
        
        membership = getToolByName(self.portal, 'portal_membership')
        membership.addMember('user1', 'secret', ['Member'], [])
        membership.addMember('user2', 'secret', ['Member'], [])
        
        self.login('user1')
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
    
    def testProjectApproval(self):
        self.login('user2')
        self.portal.psc.invokeFactory('PSCProject', 'proj')
        proj = self.portal.psc.proj
        proj.content_status_modify(workflow_action='submit')
        
        self.assertEqual(self.wf_tool.getInfoFor(proj, 'review_state'), 'pending')
        
        self.login('user1')
        proj.content_status_modify(workflow_action='publish')
        self.assertEqual(self.wf_tool.getInfoFor(proj, 'review_state'), 'published')

class TestProjectSecurity(PSCTestCase):
    def afterSetUp(self):
        # Definitions for convenience
        self.wf_tool = getToolByName(self.portal, 'portal_workflow')
        
        # Actual changes to portal
        
        membership = getToolByName(self.portal, 'portal_membership')
        membership.addMember('user1', 'secret', ['Member'], [])
        membership.addMember('user2', 'secret', ['Member'], [])
        
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.psc = self.portal.psc
        
        self.login('user1')
        self.psc.invokeFactory('PSCProject', 'proj')
        self.proj = self.psc.proj
        self.proj.content_status_modify(workflow_action='submit')
        
        self.login('test_user_1_')
        self.proj.content_status_modify(workflow_action='publish')
    
    def testRoadmapCreation(self):
        self.login('user1')
        
        try:
            self.proj.invokeFactory('PSCImprovementProposalFolder', 'roadmap')
        except:
            self.fail('Project creator is unable to add a roadmap')
    
    def testProposalCreationAndApproval(self):
        self.login('user1')
        self.proj.invokeFactory('PSCImprovementProposalFolder', 'roadmap')
        
        try:
            self.proj.roadmap.invokeFactory('PSCImprovementProposal', '1')
        except:
            self.fail('Project creator is unable to add an improvement proposal.')
        ip = self.proj.roadmap['1']
        
        ip.content_status_modify(workflow_action = 'propose')
        self.assertEqual(self.wf_tool.getInfoFor(ip, 'review_state'), 'being-discussed')
        ip.content_status_modify(workflow_action = 'begin')
        self.assertEqual(self.wf_tool.getInfoFor(ip, 'review_state'), 'in-progress')
        ip.content_status_modify(workflow_action = 'complete')
        self.assertEqual(self.wf_tool.getInfoFor(ip, 'review_state'), 'ready-for-merge')
        ip.content_status_modify(workflow_action = 'merge')
        self.assertEqual(self.wf_tool.getInfoFor(ip, 'review_state'), 'completed')
        
        #When is a user supposed to be able to add improvement proposals?
    
    def testReleaseFolderDeletionAndCreation(self):
        self.login('user1')
        
        try:
            self.proj.manage_delObjects(['releases'])
        except:
            self.fail('Project creator is unable to delete Releases folder.')
        try:
            self.proj.invokeFactory('PSCReleaseFolder', 'releases')
        except:
            self.fail('Project creator is unable to create Releases folder.')
    
class TestPloneHelpCenterIntegration(PSCTestCase):
    def afterSetUp(self):
        # Definitions for convenience
        self.wf_tool = getToolByName(self.portal, 'portal_workflow')
        
        # Actual changes to portal
        
        membership = getToolByName(self.portal, 'portal_membership')
        membership.addMember('user1', 'secret', ['Member'], [])
        membership.addMember('user2', 'secret', ['Member'], [])
        
        self.setRoles(('Manager',))
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        self.psc = self.portal.psc
        
        self.login('user1')
        self.psc.invokeFactory('PSCProject', 'proj')
        self.proj = self.psc.proj
        self.proj.content_status_modify(workflow_action='submit')
        
        self.login('test_user_1_')
        self.proj.content_status_modify(workflow_action='publish')
        
        self.setRoles(('Manager',))
        qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
        try:
            qi_tool.installProduct('PloneHelpCenter')
        except AttributeError:
            self.fail('PloneHelpCenter integration tests cannot be run '
              'because the product is not installed.')
        # At least in Plone 3 an AttributeError while installing
        # PloneHelpCenter is swallowed.  So we have to do a better
        # check.
        self.failIf(qi_tool.PloneHelpCenter.error)

    def testDocumentationFolderCreation(self):
        self.login('user1')
        try:
            self.proj.invokeFactory('PSCDocumentationFolder', 'documentation')
        except:
            self.fail('Project creator unable to create documentation folder')
    
    def testFAQCreationByOwner(self):
        #Note: Rather than testing the creation and approval of every possible
        #PloneHelpCenter type within a PSCDocumentationFolder, we only test
        #FAQ creation and approval as a representative example.
        
        self.login('user1')
        self.proj.invokeFactory('PSCDocumentationFolder', 'documentation')
        
        documentation = self.proj.documentation
        
        try:
            documentation.invokeFactory('HelpCenterFAQFolder', 'faq')
        except:
            self.fail('Project creator unable to create FAQ Folder')
        faq = documentation.faq
        
        try:
            faq.invokeFactory('HelpCenterFAQ', 'question')
        except:
            self.fail('Project creator unable to create FAQ within FAQ Folder')
    
    def testFAQCreationByUser(self):
        #Note: Rather than testing the creation and approval of every possible
        #PloneHelpCenter type within a PSCDocumentationFolder, we only test
        #FAQ creation and approval as a representative example.
        
        self.login('user1')
        self.proj.invokeFactory('PSCDocumentationFolder', 'documentation')
        documentation = self.proj.documentation
        documentation.invokeFactory('HelpCenterFAQFolder', 'faq')
        faq = documentation.faq
        
        self.login('user2')
        try:
            faq.invokeFactory('HelpCenterFAQ', 'question')
        except:
            self.fail('Generic user unable to create FAQ within FAQ Folder')
    
    def testFAQApproval(self):
        #Note: Rather than testing the creation and approval of every possible
        #PloneHelpCenter type within a PSCDocumentationFolder, we only test
        #FAQ creation and approval as a representative example.
        
        self.login('user1')
        self.proj.invokeFactory('PSCDocumentationFolder', 'documentation')
        documentation = self.proj.documentation
        documentation.invokeFactory('HelpCenterFAQFolder', 'faq')
        faq = documentation.faq
        
        faq.invokeFactory('HelpCenterFAQ', 'q1')
        faq.q1.content_status_modify(workflow_action='publish')
        self.assertEqual(self.wf_tool.getInfoFor(faq.q1, 'review_state'),
          'published')
        
        self.login('user2')
        faq.invokeFactory('HelpCenterFAQ', 'q2')
        faq.q2.content_status_modify(workflow_action='submit')
        self.assertEqual(self.wf_tool.getInfoFor(faq.q2, 'review_state'),
          'pending')
        self.login('user1')
        faq.q2.content_status_modify(workflow_action='publish')
        self.assertEqual(self.wf_tool.getInfoFor(faq.q2, 'review_state'),
          'published')

    def testReleaseCreation(self):
        # a member can create a project and its releases 
        self.login('user2') 
        self.psc.invokeFactory('PSCProject', 'proj2') 
        try: 
            self.psc.proj2.releases.invokeFactory('PSCRelease', '0.1') 
        except:   
            self.fail('Project creator is unable to create its releases') 


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCenterSecurity))
    suite.addTest(makeSuite(TestProjectSecurity))
    if ZopeTestCase.hasProduct('PloneHelpCenter'):
        suite.addTest(makeSuite(TestPloneHelpCenterIntegration))
    else:
        developer_warning("PloneHelpCenter integration tests ignored.")
    return suite

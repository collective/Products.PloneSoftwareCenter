from base import PSCTestCase


class TestProductInstall(PSCTestCase):

    def afterSetUp(self):
        self.types = {
            'PloneSoftwareCenter'           : 'psc_area_workflow',
            'PSCProject'                    : 'psc_package_workflow',
            'PSCReleaseFolder'              : None,
            'PSCRelease'                    : 'psc_release_workflow',
            'PSCImprovementProposalFolder'  : None,
            'PSCImprovementProposal'        : 'psc_improvementproposal_workflow',
            'PSCDocumentationFolder'        : None,
            'PSCFile'                       : None,
            'PSCFileLink'                   : None,
        }

    def testTypesInstalled(self):
        for t in self.types.keys():
            self.failUnless(t in self.portal.portal_types.objectIds(),
                            '%s content type not installed' % t)
                            
    def testWorkflowsInstalled(self):
        for wf in self.types.values():
            if wf:
                self.failUnless(wf in self.portal.portal_workflow.objectIds())
    
    def testWorkflowsMapped(self):
        for fti, wf in self.types.items():
            chain = self.portal.portal_workflow.getChainForPortalType(fti)
            if wf is None:
                self.assertEqual(0, len(chain))
            else:
                self.assertEqual((wf,), tuple(chain))
    
    def testWorkflowScriptsInstalled(self):
        wf = self.portal.portal_workflow
        
        release_wf = wf['psc_release_workflow'].scripts
        package_wf = wf['psc_package_workflow'].scripts

        self.failUnless('release_new_state' in release_wf.objectIds())
        self.failUnless('re_release_state' in release_wf.objectIds())
        
        self.failUnless('give_reviewer_localrole' in package_wf.objectIds())
        self.failUnless('take_reviewer_localrole' in package_wf.objectIds())
        
    def testCatalogIndexesInstalled(self):
        catalog = self.portal.portal_catalog
        self.failUnless('releaseCount' in catalog.indexes())
        
    def testCatalogMetadataInstalled(self):
        catalog = self.portal.portal_catalog
        self.failUnless('UID' in catalog.schema())
        self.failUnless('getCategoryTitles' in catalog.schema())
        
    def testPortalFactoryConfigured(self):
        factory = self.portal.portal_factory
        for t in self.types.keys():
            self.failUnless(t in factory.getFactoryTypes())
        
    def testNavtreePropertiesConfigured(self):
        pmntq = self.portal.portal_properties.navtree_properties.parentMetaTypesNotToQuery
        for t in ('PloneSoftwareCenter', 'PSCReleaseFolder', 'PSCImprovementProposalFolder', 'PSCRelease'):
            self.failUnless(t in pmntq)
    
    # XXX I don't think this is a good test because
    # the dependencies are not automatically installed by PSC
    # at this time. They are just installed in the test fixture.
    # config.HARD_DEPS is defined but not used.
    #def testDependenciesInstalled(self):
    #    qi_tool = getToolByName(self.portal, 'portal_quickinstaller')
    #    for p in ['AddRemoveWidget', 'ArchAddOn', 'DataGridField']:
    #        self.failUnless(qi_tool.isProductInstalled(p))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite

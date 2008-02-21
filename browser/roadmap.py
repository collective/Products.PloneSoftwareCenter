from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

from Products.PloneSoftwareCenter.browser.project import _upcoming_releases

class RoadmapView(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

        self.membership = getToolByName(self.context, 'portal_membership')
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.portal_url = getToolByName(self.context, 'portal_url')()

        self.context_path = '/'.join(self.context.getPhysicalPath())

    def state_title(self, state):
        """Given the state name, look up its title in portal_workflow
        """
        wftool = getToolByName(self, 'portal_workflow')
        wf = wftool.psc_improvementproposal_workflow
        return wf.states[state].title
        
        return self.context.utranslate(
          msgid='workflow_state_title_%s' % state,
          domain='plonesoftwarecenter',
          default=wf.states[state].title)

    def improvement_proposals(self, review_state = []):
        """Get the improvement proposals in this folder, sorted on plip number,
        as a list of catalog brains.
        """
        catalog = getToolByName(self, 'portal_catalog')

        query = {}
        query['portal_type'] = 'PSCImprovementProposal'
        query['path'] = '/'.join(self.context.getPhysicalPath())

        if review_state:
            query['review_state'] = review_state

        proposals = catalog.portal_catalog(query)
                                
        def sortProposals(x, y):
            try: xval = int(x.getId)
            except ValueError: xval = 0
            try: yval = int(y.getId)
            except ValueError: yval = 0
            return cmp(xval, yval)
                                    
        proposals = [p for p in proposals]
        proposals.sort(sortProposals)
        return proposals
    
    def upcoming_releases(self):
        return _upcoming_releases(self.context.aq_inner.aq_parent)

    def getStateTitle(self, state):
        """Given the state name, look up its title in portal_workflow
        """
        wftool = getToolByName(self, 'portal_workflow')
        wf = wftool.psc_improvementproposal_workflow
        return wf.states[state].title

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

from Products.PloneSoftwareCenter.browser.project import _upcoming_releases

class ReleaseFolderView(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

        self.membership = getToolByName(self.context, 'portal_membership')
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.portal_url = getToolByName(self.context, 'portal_url')()

        self.context_path = '/'.join(self.context.getPhysicalPath())

    def upcoming_releases(self):
        """Get a list of upcoming releases, in reverse order of effective date.
        """
        return _upcoming_releases(self.context.aq_inner.aq_parent)

    def previous_releases(self):
        """Get a list of previously published releases, in reverse order of
        effective date.
        """
        catalog = getToolByName(self, 'portal_catalog')
        res = catalog.searchResults(portal_type = 'PSCRelease',
                                    review_state = ['final'],
                                    path = '/'.join(self.context.getPhysicalPath()),
                                    sort_on = 'effective',
                                    sort_order = 'reverse')
        return [r.getObject() for r in res]


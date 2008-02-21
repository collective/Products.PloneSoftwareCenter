from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

class DocFolderView(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

        self.membership = getToolByName(self.context, 'portal_membership')
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.portal_url = getToolByName(self.context, 'portal_url')()

        self.context_path = '/'.join(self.context.getPhysicalPath())

    def non_phc_contents(self):
        """Get a list of folder objects of types not defined by the help
        center product which have been placed in this help center.
        """

        phcTypes = self.context.allowed_content_types
        catalog = getToolByName(self, 'portal_catalog')
        allTypes = catalog.uniqueValuesFor('portal_type')

        nonPHCTypes = [t for t in allTypes if t not in phcTypes]

        # Need this, else we end up with all types, not no types :)
        if not nonPHCTypes:
            return []

        return self.context.getFolderContents(contentFilter = {'portal_type' : nonPHCTypes})

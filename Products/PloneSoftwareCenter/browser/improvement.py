from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

class ImprovementView(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

        self.membership = getToolByName(self.context, 'portal_membership')
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.portal_url = getToolByName(self.context, 'portal_url')()

        self.context_path = '/'.join(self.context.getPhysicalPath())

    def title(self):
        """Return the title as "#${id}: ${title}".

        The id is the proposal number, and we want it to be associated
        with the title when it's displayed.
        """
        return '#%s: %s' % (self.context.getId(), self.context.getField('title').get(self.context))
    
    def raw_title(self):
        """Get the raw title of the improvement proposal - no #${id} prefixing.
        """
        return self.context.getField('title').get(self.context)

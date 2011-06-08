from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.atapi import DisplayList
import re
from Products.PloneSoftwareCenter import PSCMessageFactory as _

class ReleaseView(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

        self.membership = getToolByName(self.context, 'portal_membership')
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.portal_url = getToolByName(self.context, 'portal_url')()

        self.context_path = '/'.join(self.context.getPhysicalPath())

    def start(self):
        """Provide a 'start' attribute so that the calendar can show the
        release as if it were an event.
        """
        return self.context.getExpectedReleaseDate()

    def end(self):
        """Provide ad 'end' attribute so that the calendar can show the
        release as if it were an event.
        """
        return self.context.getExpectedReleaseDate()

    def compatibility_vocab(self):
        """Get the available compatability versions from the parent project
           area via acqusition.
        """
        return self.context.getAvailableVersionsAsDisplayList()

    def license_vocab(self):
        """Get the available licenses from the parent project area via
         acqusition.
        """
        return self.context.getAvailableLicensesAsDisplayList()

    def related_features_vocab(self):
        """Get list of PLIPs possible to add to this release."""
        catalog = getToolByName(self, 'portal_catalog')
        projectPath = self.context.getPhysicalPath()[:-2]
        if len(projectPath) > 1 and projectPath[-1] == 'portal_factory':
            projectPath = projectPath[:-2]
            
        search = catalog.searchResults(portal_type = 'PSCImprovementProposal',
                                       path = '/'.join(projectPath))
        
        items = [s for s in search]
        items.sort(lambda x, y: cmp(int(x.getId), int(y.getId)))
        lst = DisplayList()
        for i in items:
            title = i.Title
            if len(title) > 40:
                title = title[:40] + '...'
                
            lst.add(i.UID, title)
        return lst

    def validate_id(self, value):
        """Validate the id field, ensuring a valid web address was
        entered.
        """
        if not value:
            return _(u"Please provide a version number")
        if re.search (r'[^\w.-]', value):
            return _(u'Please only use numbers, letters, underscores (_), '
                    'dashes (-) and periods (.) in the version string, no '
                    'other punctuation characters or whitespace')
        else:
            return None

    def is_outdated(self):
        """Return true if this release is no longer supported."""
        currentVersions = self.context.getCurrentVersions()
        if currentVersions and self.context.getId() not in currentVersions:
            return True
        else:
            return False
    
    def is_released(self):
        """Returns true if the release has already been released."""
        wtool = getToolByName(self.context, 'portal_workflow')
        return wtool.getInfoFor(self.context, 'review_state') != 'pre-release'
    
    def release_date(self):
        """Gets the release date."""
        if self.is_released():
            try:
                return self.context.toLocalizedTime(self.context.effective())
            except ValueError:
                # no release date set for some reason
                return ''
        elif self.context.getExpectedReleaseDate():
                return self.context.toLocalizedTime(
                  self.context.getExpectedReleaseDate())
        else:
            return None

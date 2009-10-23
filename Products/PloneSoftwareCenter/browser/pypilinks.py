"""
 View that provides a page of links compatible
 with easy_install.

$Id:$
"""
import itertools

from zope.deprecation import deprecation

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class PyPILinksView(BrowserView):
    """view used for the main index page"""

    def get_urls_and_titles(self, brain):
        """returns url and title"""
        for element in brain.getObject().objectValues():
            info = {'title': element.title or ''}
            if element.portal_type == 'PSCFileLink':
                info['url'] = element.externalURL
            else:
                info['url'] = element.absolute_url()
            yield info

    def _sort_releases(self, r1, r2):
        return cmp(r1['url'], r2['url'])

    def get_files(self):
        """provides the simple view over the projects
        with links to the published files"""
        sc = self.context
        catalog = getToolByName(self.context, 'portal_catalog')
        sc_path = '/'.join(sc.getPhysicalPath())
        query = {'path': sc_path, 'portal_type': 'PSCRelease',
                 'review_state': ('hidden', 'pre-release', 'alpha',
                                  'beta', 'release-candidate', 'final')}
        return sorted(itertools.chain(*[self.get_urls_and_titles(brain)
                                        for brain in catalog(**query)]), 
                      self._sort_releases)

class PyPILinksViewDeprecated(PyPILinksView):
    """view with deprecation warnings"""

    @deprecation.deprecate(("The 'simple' view is deprecated, "
                            "use the 'links' view instead"))
    def get_files(self):
        return PyPILinksView.get_files(self)


from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner


def _upcoming_releases(proj):
    """Get a list of upcoming releases for a project, in reverse order of
    effective date.
    """
    
    releaseFolder = proj.getReleaseFolder()
    catalog = getToolByName(proj, 'portal_catalog')
    res = catalog.searchResults(
      portal_type = 'PSCRelease',
      review_state = ['pre-release', 'alpha', 'beta', 'release-candidate'],
      path = '/'.join(releaseFolder.getPhysicalPath()),
      sort_on = 'effective',
      sort_order = 'reverse')
    return [r.getObject() for r in res]


class ProjectView(BrowserView):
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        
        self.membership = getToolByName(self.context, 'portal_membership')
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.portal_url = getToolByName(self.context, 'portal_url')()
        
        self.context_path = '/'.join(self.context.getPhysicalPath())
        
    def get_installation_instructions(self):
        psc = self.context.getParentNode()
        return psc.getInstallation_instructions()
    
    def latest_release(self):
        """Get the most recent final release or None if none can be found.
        """
        releaseFolder = self.context.getReleaseFolder()
        
        res = None
        
        if releaseFolder:
            catalog = getToolByName(self.context, 'portal_catalog')
            res = catalog.searchResults(
              path = '/'.join(releaseFolder.getPhysicalPath()),
              review_state = 'final',
              sort_on = 'Date',
              sort_order = 'reverse',
              portal_type = 'PSCRelease')
        
        if not res:
            return None
        else:
            return res[0].getObject()
    
    def latest_release_date(self):
        """Get the date of the latest release
        """
        
        latest_release = self.latest_release()


        if latest_release:
            return self.context.toLocalizedTime(latest_release.effective())
        else:
            return None
    
    def upcoming_releases(self):
        """Get a list of upcoming releases, in reverse order of effective date.
        """
        
        return _upcoming_releases(self.context)
    
    
    def all_releases(self):
        """Get a list of all releases, ordered by version, starting with the latest. 
        """
        proj = self.context
        releaseFolder = proj.getReleaseFolder()
        catalog = getToolByName(proj, 'portal_catalog')
        res = catalog.searchResults(
          portal_type = 'PSCRelease',
          path = '/'.join(releaseFolder.getPhysicalPath()),
          sort_on = 'id',
          sort_order = 'reverse')
        return [r.getObject() for r in res]
    
    def release_rss_url(self):
        """Get a link with the URL to an RSS feed for releases of this project
        """
        
        here_url = self.context.absolute_url()
        
        req_vars = [
          ['portal_type', 'PSCRelease'],
          ['sort_on', 'Date'],
          ['sort_order', 'reverse'],
          ['path', self.context_path],
          ]
        
        req_vars_str = '&'.join(
          ['%s=%s' % (pair[0], pair[1]) for pair in req_vars]
          )
        
        return '%s/search_rss?%s' % (here_url, req_vars_str)
        
    def display_categories(self):
        """Get a list of categories, separated by commas, for display
        """
        try:
            use_classifiers = self.context.getUseClassifiers()
        except:
            use_classifiers = False
        if use_classifiers:
            return ', '.join(self.context.getVocabularyTitlesFromCLassifiers())
        else:
            return ', '.join(self.context.getCategoryTitles())
        
    def similar_search_url(self):
        """Get a url to search for projects by the same author
        """
        
        req_vars = [
          ['portal_type%3Alist', 'PSCProject'],
          ['Creator', self.context.Creator()],
          ]
        
        req_vars_str = '&'.join(
          ['%s=%s' % (pair[0], pair[1]) for pair in req_vars]
          )
        
        return '%s/search?%s' % (self.portal_url, req_vars_str)
        
    def is_public(self):
        """Find out if this project is published
        """
        
        wtool = getToolByName(self.context, 'portal_workflow')
        return wtool.getInfoFor(self.context, 'review_state') == 'published'
        
    def release_folder_url(self):
        """Get the url to the release folder, or None if it does not exist
        """
        
        ids = self.context.contentIds(
          filter = {'portal_type': 'PSCReleaseFolder'})
        if ids:
            return '%s/%s' % (self.context.absolute_url(), ids[0])
        

    def roadmap_folder_url(self):
        """Get the url to the roadmap folder, or None if it does not exist
        """
        
        ids = self.context.contentIds(
          filter = {'portal_type': 'PSCImprovementProposalFolder'})
        if ids:
            return '%s/%s' % (self.context.absolute_url(), ids[0])
    
    def has_documentation_link(self):
        """Returns whether there is a documentation folder or link
        """
        
        return 'documentation' in self.context.objectIds() or self.context.getDocumentationLink()
    
    def documentation_url(self):
        """Get the url to the documentation folder or link, or None if it does not 
        exist
        """
        
        ids = self.context.contentIds(
          filter = {'portal_type': 'PSCDocumentationFolder'})
        if ids:
            return '%s/documentation' % self.context.absolute_url()
        elif self.context.getDocumentationLink():
            return self.context.getDocumentationLink()
        else:
            return None
    
    def documentation_link_class(self):
        """Get the class of the <a> element that links to the documentation
        """
        
        if 'documentation' in self.context.objectIds():
            return None
        elif self.context.getDocumentationLink():
            return 'link-plain'
        else:
            return None
    
    def additional_resources(self, ignore = ('PSCDocumentationFolder',)):
        """
        Get any contained resources (objects) not of the types in the list of
        ignored types passed in. This essentially allows access to contained
        help-center items, collectors etc.
        """
        return [o for o in self.context.folderlistingFolderContents() \
                    if o.portal_type not in ignore] 
    
    def criteria_info(self):
        """
        Get the list of self-certification criteria and whether the project
        meets each criterion.
        """
        
        res = []

        try: 
            for k, v in self.context.getSelfCertificationCriteriaVocab().items():
                if k in self.context.getSelfCertifiedCriteria():
                    res.append({'selected': True, 'text': v})
                else:
                    res.append({'selected': False, 'text': v})
            return res
        except:
            return res

    def has_criteria_info(self):
        """
        Check each key value for True/False, return False if all False, True otherwise.
        This is needed so we can *not* show the Self-Certification header when a
        project has none. XXX: Combine me with criteria_info.
        """
        critlist = []
        for ci in self.criteria_info():
            critlist.append(ci['selected'])
        if True in critlist:
            return True
        else:
            return False

    def has_review_comment(self):
        """
        Check for reviewComment field that is not empty.
        """
        try:
            if self.context.getReviewComment() is not "":
                return True
            else:
                return False
        except KeyError:
            return False


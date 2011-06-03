from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

class CategoryView(BrowserView):
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        
        self.membership = getToolByName(self.context, 'portal_membership')
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.portal_url = getToolByName(self.context, 'portal_url')()
        
        self.context_path = '/'.join(self.context.getPhysicalPath())
        
    
    def get_products(self, category, version, sort_on, SearchableText=None):
        featured = False
        # featured content should be filtered by state and then 
        # sorted by average rating
        if sort_on == 'featured':
            featured = True
            sort_on = 'positive_ratings'
        contentFilter = {'SearchableText': SearchableText,
			             'portal_type': 'PSCProject',
			             'sort_on' : sort_on,
			             'sort_order': 'reverse'}
        
        if version != 'any':
            contentFilter['getCompatibility'] = version
        if featured:
            contentFilter['review_state'] = 'featured'
        if category:
            contentFilter['getCategories'] = category
            
        return self.catalog(**contentFilter)
    
    def get_latest_plone_release(self):
        """Get the latest version from the vocabulary. This only 
        goes by string sorting so would need to be reworked if the 
        plone versions dramatically changed"""
        # getAvailableVersions is coming from root.py. ?
        versions = list(self.context.getAvailableVersions())
        versions.sort(reverse=True)
        return versions[0]
    
    
    def by_category(self, category, states=[], limit=None):
        """Get catalog brains for projects in category."""
        return self._contained(states, category, 'PSCProject', limit,
                                    sort_on='sortable_title', sort_order = 'asc')

    def _contained(self, states, category, portal_type, limit=None,
                        sort_on='Date', sort_order='reverse'):
        """Get contained objects of type portal_type
        that are in states and have category."""

        catalog = getToolByName(self, 'portal_catalog')
        my_path = '/'.join(self.context.getPhysicalPath())
        query = { 'path'         : my_path,
                  'portal_type'  : portal_type,
                }

        if states:
            query['review_state'] = states
        if category:
            if self.context.getUseClassifiers():
                query['getClassifiers'] = category 
            else:
                query['getCategories'] = category
        if limit:
            query['sort_limit'] = limit
        if sort_on:
            query['sort_on'] = sort_on
        if sort_order:
            query['sort_order'] = sort_order

        results = catalog.searchResults(query)
        if len(results) is not 0:
            if limit:
                return results[:int(limit)]
            else:
                return results
        else:
            return [] # return empty list, not catalog instance with no results.

    def category_name(self, category):
        """Get the long name of a category.
        """
        return self.context.getField('availableCategories').lookup(self.context, category, 1)

    def category_description(self, category):
        """Get the description of a category.
        """
        return self.context.getField('availableCategories').lookup(self.context, category, 2)

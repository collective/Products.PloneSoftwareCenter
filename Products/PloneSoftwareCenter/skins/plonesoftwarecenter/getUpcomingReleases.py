## Script (Python) "getUpcomingReleases"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=releasesFolder='../releases', states=['pre-release', 'alpha', 'beta', 'release-candidate']
##title=Get upcoming software releases

from Products.CMFCore.utils import getToolByName

wftool = getToolByName(context, 'portal_workflow')
folder = context.restrictedTraverse(releasesFolder)

typesFilter = {'portal_type' : ['PSCRelease']}

# Return a list of items sorted by expected release dates in reverse order;
# items with no expected date set are returned at the end, in folder-order.

datedReleases = []
undatedReleases = []

for r in folder.folderlistingFolderContents(contentFilter = typesFilter):
    if wftool.getInfoFor(r, 'review_state') in states:
        if r.getExpectedReleaseDate():
            datedReleases.append(r)
        else:
            undatedReleases.append(r)
            
datedReleases.sort(lambda x, y: \
                    cmp(x.getExpectedReleaseDate(), y.getExpectedReleaseDate()))

releases = datedReleases + undatedReleases

return releases
        
        

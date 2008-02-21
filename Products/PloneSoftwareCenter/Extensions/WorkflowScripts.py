# Contains external methods used as workflow scripts

from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

def reReleaseState(self, state_change):
   """Perform a re-release to the same state
   """
   obj = state_change.object
   number = obj.getReleaseNumber()
   if not number:
      number = 1
   obj.setReleaseNumber(number + 1)
   obj.setEffectiveDate(DateTime())
   obj.reindexObject()

def releaseNewState(self, state_change):
    """Make a new release before the final release
    """
    obj = state_change.object
    obj.setReleaseNumber(1)
    obj.setEffectiveDate(DateTime())
    obj.reindexObject()
    
    catalog = getToolByName(obj, 'portal_catalog')
    project = obj.aq_inner.aq_parent.aq_parent
    
    releases = catalog.searchResults(portal_type = 'PSCRelease',
                                     review_state = ('alpha', 'beta', 'release-candidate', 'final',),
                                     path = '/'.join(project.getPhysicalPath()))
    
    project.manage_changeProperties(releaseCount = len(releases))
    project.reindexObject(idxs=('releaseCount',))

def giveReviewerLocalrole(self, state_change):
    """Give the object's owner the 'Reviewer' localrole."""
    
    obj = state_change.object
    owner = obj.Creator()
    roles = list(obj.get_local_roles_for_userid(owner))
    roles = roles + ['Reviewer',]
    obj.manage_setLocalRoles(owner, roles)

def takeReviewerLocalrole(self, state_change):
    """Take away the 'Reviewer' localrole from the object's owner"""
    
    obj = state_change.object
    owner = obj.Creator()
    
    roles = list(obj.get_local_roles_for_userid(owner))
    
    if 'Reviewer' in roles:
        roles.remove('Reviewer')
        if not roles:
            obj.manage_delLocalRoles([owner])
        else:
            obj.manage_setLocalRoles(owner, roles)
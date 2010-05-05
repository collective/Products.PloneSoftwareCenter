import doctest
from App.Common import package_home
PACKAGE_HOME = package_home(globals())

from Products.CMFCore.utils import getToolByName

# Standard options for DocTests
optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)

def verifyURLWithRequestVars(url, base, request_list):
    request_list = tuple(request_list)
    
    if url.count('?') not in [0, 1]:
        return False
    
    if url.count('?') == 0 and request_list != []:
        return False
    
    if url.count('?'):
        url1, url2 = url.split('?')
    else:
        url1 = url
        url2 = ''
    
    actual_vars = url2.split('&')
    for item in request_list:
        count = actual_vars.count(item)
        if not count:
            return False
        for i in range(count):
            actual_vars.remove(item)
    
    return actual_vars == []

def setUpDefaultMembers(portal):
    portal_membership = getToolByName(portal, 'portal_membership')
    membership = getToolByName(portal, 'portal_membership')
    membership.addMember('member1', 'secret', ['Member'], [])
    membership.addMember('member2', 'secret', ['Member'], [])
    membership.addMember('member3', 'secret', ['Member'], [])

def setUpEvaluator(psc, id):
    roles = list(psc.get_local_roles_for_userid(id))
    if 'PSCEvaluator' not in roles:
        roles.append('PSCEvaluator')
    psc.manage_setLocalRoles(id, roles)

"""
$Id$
"""
from Products.CMFCore.permissions import setDefaultRoles

AddSoftwareCenter = "PloneSoftwareCenter: Add Software Center"
AddProject = 'PloneSoftwareCenter: Add Project'
AddReviewComment = 'PloneSoftware: Add Review Comment'
ApproveProject = 'PloneSoftwareCenter: Approve Project'

# Let members add new projects, but only manager add help centres
setDefaultRoles(AddSoftwareCenter, ('Manager',))

# Setting this by default and controlling with area workflow means factory
# works
setDefaultRoles(AddProject, ('Manager', 'Owner',))

setDefaultRoles(AddReviewComment, ('Manager', 'PSCEvaluator',))
setDefaultRoles(ApproveProject, ('Manager', 'PSCEvaluator',))

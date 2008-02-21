def initializeSoftwareCenterSecurity(ob, event):
    addProjectEvaluatorRole(ob)
    allowCreatorToReview(ob)

def addProjectEvaluatorRole(ob):
    """Add a PSCEvaluator role
    """
    
    if 'PSCEvaluator' not in ob.validRoles():
        # Note: API sucks :-(
        ob.manage_defined_roles(submit='Add Role',
                                REQUEST={'role': 'PSCEvaluator'})

def allowCreatorToReview(ob):
    """Assign the Reviewer and PSCEvaluator roles to a software center creator.
    """
    
    owner = ob.Creator()
    roles = list(ob.get_local_roles_for_userid(owner))
    roles = roles + ['PSCEvaluator', 'Reviewer']
    ob.manage_setLocalRoles(owner, roles)
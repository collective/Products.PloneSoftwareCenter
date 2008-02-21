from Products.validation.interfaces import ivalidator
import re


is_valid_contact = re.compile('[mailto:,http:]')


class ProjectIdValidator:
    """Ensure that we don't get a value for the id of a project that is the same 
    as the id of a category. This will break our nice acquisition-fuelled 
    listing templates and generally be bad.
    """
    
    __implements__= (ivalidator,)
    
    def __init__(self, name):
        self.name = name
        return None
    
    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        if value in instance.getAvailableCategoriesAsDisplayList().keys():
            return "Short name %s is invalid - " \
                   "it is the same as the name of a project category" % (value,)
        else:
            return 1

class ProjectContactValidator:
    """Check to see if field contains a valid URI (mailto: or http:)
       else check for email address else kick it back to the form."""

    __implements__ = (ivalidator,)

    def __init__(self, name):
        self.name = name
        return None


    def __call__(self, value, *args, **kwargs):
        # if not is_valid_contact(value):
        #     return """Not a valid contact."""
        #print value
        #print is_valid_contact(value)
        #return 1
        return """Not a valid contact."""

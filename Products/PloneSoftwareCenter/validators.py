# Old Style
 
from Products.validation.interfaces import ivalidator
import re

# New Style

try:
    # Plone 4 and higher
    import plone.app.upgrade
    USE_BBB_VALIDATORS = False
except ImportError:
    # BBB Plone 3
    USE_BBB_VALIDATORS = True
    

from zope.interface import implements
from Products.validation.interfaces.IValidator import IValidator
from zope.component import adapts
from Products.Archetypes.interfaces import IObjectPreValidation
from Products.PloneSoftwareCenter.interfaces import IProjectContent

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plonesoftwarecenter')

is_valid_contact = re.compile('[mailto:,http:]')


# Old style validators

class ProjectIdValidator:
    """Ensure that we don't get a value for the id of a project that is the same 
    as the id of a category. This will break our nice acquisition-fuelled 
    listing templates and generally be bad.
    """
    
    if USE_BBB_VALIDATORS:
        __implements__ = (ivalidator,)
    else:
        implements(IValidator)
    
    def __init__(self, name):
        self.name = name
        return None
    
    def __call__(self, value, *args, **kwargs):
        instance = kwargs['instance']
        if value in instance.getAvailableCategoriesAsDisplayList().keys():
            return _(u"Short name %s is invalid - it is the same as the name of a project category") % (value,)
        else:
            return 1

class ProjectContactValidator:
    """Check to see if field contains a valid URI (mailto: or http:)
       else check for email address else kick it back to the form."""

    if USE_BBB_VALIDATORS:
        __implements__ = (ivalidator,)
    else:
        implements(IValidator)

    def __init__(self, name):
        self.name = name
        return None


    def __call__(self, value, *args, **kwargs):
        # if not is_valid_contact(value):
        #     return """Not a valid contact."""
        #print value
        #print is_valid_contact(value)
        #return 1
        return _(u"""Not a valid contact.""")


# New style validators

class ValidateEggNameUnique(object):
    """ Ensure that an egg is not already registered under a different project. """
    
    implements(IObjectPreValidation)
    adapts(IProjectContent)
    
    def __init__(self, context):
        super(ValidateEggNameUnique, self).__init__()
        self.context = context
    
    def __call__(self, request):
        """ Validate that the fields for egg name registrations do not conflict with existing names """
        main = request.get("distutilsMainId", None)
        secondary = request.get("distutilsSecondaryIds", None)
        if (not main) and secondary:
            return {"distutilsMainId":_("You must set the primary package before you can select secondary packages.")}

        main = (main, )
        
        if isinstance(secondary, str):
            secondary = (secondary, )
        elif isinstance(secondary, list) or isinstance(secondary, tuple):
            secondary = tuple(secondary)
        else:
            return {"distutilsSecondaryIds":_("You must provide a list of package names")}
        
        errors = {}
        
        if not self.context._distUtilsNameAvailable(main):
            errors['distutilsMainId'] = _("This package is already claimed by another project.")
        if not self.context._distUtilsNameAvailable(secondary):
            errors['distutilsSecondaryIds'] = _("This contains packages already claimed by another project.")

        if not errors:
            return None
        else:
            return errors

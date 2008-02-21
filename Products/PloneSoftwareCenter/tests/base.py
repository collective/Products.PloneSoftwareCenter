"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ArchAddOn')
ZopeTestCase.installProduct('AddRemoveWidget')
ZopeTestCase.installProduct('ExternalStorage')
# If PloneHelpCenter is available, initialize it.
ZopeTestCase.installProduct('PloneHelpCenter')
ZopeTestCase.installProduct('PloneSoftwareCenter')

from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

setupPloneSite(products=('PloneSoftwareCenter',))

class PSCTestCase(PloneTestCase):
    """Base class for integration tests
    """
    
class PSCFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests
    """
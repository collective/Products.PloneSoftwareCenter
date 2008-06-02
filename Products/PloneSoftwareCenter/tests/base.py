"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""
import warnings
import os

from Testing import ZopeTestCase

ZopeTestCase.installProduct('ArchAddOn')
ZopeTestCase.installProduct('AddRemoveWidget')
ZopeTestCase.installProduct('DataGridField')
ZopeTestCase.installProduct('ExternalStorage')

from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

from Products.Five import fiveconfigure
from Products.Five import zcml

from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.layer import PloneSite

@onsetup
def install_psc():
    import Products.PloneSoftwareCenter
    fiveconfigure.debug_mode = True
    try:
        zcml.load_config('configure.zcml', Products.PloneSoftwareCenter)
        ZopeTestCase.installProduct('PloneHelpCenter')
        ZopeTestCase.installProduct('PloneSoftwareCenter')
        
        # try:
        #     # If PloneHelpCenter is available, initialize it.
        #     import Products.PloneHelpCenter
        # except ImportError:
        #     # Plone Help Center not available
        #     pass
    finally:
        fiveconfigure.debug_mode = False
        
@onsetup
def install_plugins():
    # TODO, move all externalstorage testing to collective.psc.externalstorage
    import collective.psc.externalstorage
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', collective.psc.externalstorage)
    ZopeTestCase.installPackage('collective.psc.externalstorage')
    fiveconfigure.debug_mode = False

    from zope.component import getGlobalSiteManager
    from collective.psc.externalstorage.config import ESConfiguration
    from collective.psc.externalstorage.interfaces import IESConfiguration
    gsm = getGlobalSiteManager()
    gsm.registerUtility(ESConfiguration, IESConfiguration)

install_psc()
# install_plugins()
setupPloneSite(products=('PloneSoftwareCenter',))

class DeveloperWarning(Warning):
    pass

def developer_warning(msg):
    warnings.warn(msg, DeveloperWarning)

class PSCTestCase(PloneTestCase):
    """Base class for integration tests
    """
    def warning(self, msg):
        developer_warning(msg)
        @classmethod
        def tearDown(cls):
            pass

class PSCFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests
    """


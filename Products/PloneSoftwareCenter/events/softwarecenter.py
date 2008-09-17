from Products.CMFCore.utils import getToolByName
import logging
import transaction

from zope.component import getAdapter
from zope.interface import implements
from zope.component.interfaces import ObjectEvent

from Products.PloneSoftwareCenter.events.interfaces import \
           IStorageStrategyChanging
from Products.PloneSoftwareCenter.storage.interfaces import IPSCFileStorage


def initializeSoftwareCenterSecurity(ob, event):
    addProjectEvaluatorRole(ob)
    allowCreatorToReview(ob)

def addProjectEvaluatorRole(ob):

    
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

class StorageStrategyChanging(ObjectEvent):
    """Event triggered by PSC when the storage strategy is
    changed"""
    implements(IStorageStrategyChanging)

    def __init__(self, object, old_storage, new_storage):
        self.object = object
        self.old_storage = old_storage
        self.new_storage = new_storage

def changeStorageStrategy(psc, event):
    """Triggered when the storage strategy changes"""
    # let's get all files held by this PSC instance
    psc_path =  '/'.join(psc.getPhysicalPath())
    catalog = getToolByName(psc, 'portal_catalog')
    files = catalog.searchResults(portal_type='PSCFile',
                                  path=psc_path)
    
    # at this stage the storage hasn't changed yet
    new_adapter = getAdapter(psc, IPSCFileStorage, event.new_storage)

    def _getStorage(*args):
        return new_adapter
    
    # now for each file we want to set the 
    # content using the new storage
    #
    try:
        for key, f in enumerate(files):
            if key != 0 and float(key) / 100. % 1 == 1:
                transaction.savepoint()
            logging.info('Changing strategy for %s' % key)
            f = f.getObject()
            field = f.getPrimaryField()
            content = f.getDownloadableFile()
            old_storage = field.getStorage
            field.getStorage = _getStorage
            try:
                f.setDownloadableFile(content)
            finally:
                field.getStorage = old_storage
    except Exception, e:
        transaction.abort()
        raise e


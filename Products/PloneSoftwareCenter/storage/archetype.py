from zope.interface import implements
from zope.component import adapts

from Products.Archetypes.atapi import AttributeStorage

from Products.PloneSoftwareCenter.storage.interfaces import IPSCFileStorage
from Products.Archetypes.interfaces.storage import IStorage

class ArchetypeStorage(AttributeStorage):
    """adapts a release folder as a dummy storage
    """ 
    name = 'archetype'
    implements(IPSCFileStorage)

    def __init__(self, context):
        self.context = context

    def getName(self):
        return self.name



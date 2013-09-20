from Products.Archetypes.atapi import AttributeStorage
from Products.PloneSoftwareCenter.storage.interfaces import IPSCFileStorage
from zope.interface import implements


class ArchetypeStorage(AttributeStorage):
    """adapts a release folder as a dummy storage
    """
    implements(IPSCFileStorage)

    title = u"Archetypes"
    description = u"stores releases via Archetype's AttributeStorage"

    def __init__(self, context):
        self.context = context

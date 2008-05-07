from zope.interface import Interface

class IPSCFileStorage(Interface):
    """adapter for storing file"""

    def get(name, instance, **kwargs):
        """returns the file `name` in an archetype instance"""

    def set(name, instance, value, **kwargs):
        """sets the file `name` in an archetype instance"""

    def unset(name, instance, **kwargs):
        """removes the file `name` in an archetype instance"""
    
    def getName(instance):
        """returns the storage name"""


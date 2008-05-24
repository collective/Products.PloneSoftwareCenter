from zope.interface import Interface
import zope.schema

class IPSCFileStorage(Interface):
    """adapter for storing file"""

    def get(name, instance, **kwargs):
        """returns the file `name` in an archetype instance"""

    def set(name, instance, value, **kwargs):
        """sets the file `name` in an archetype instance"""

    def unset(name, instance, **kwargs):
        """removes the file `name` in an archetype instance"""
    
    title = zope.schema.TextLine(
                title=u"Title",
                required=True)

    description = zope.schema.TextLine(
                title=u"Description",
                required=True)
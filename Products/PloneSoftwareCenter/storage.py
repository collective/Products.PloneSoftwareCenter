from zope.interface import implements
from zope.component import adapts
from zope.component import getAdapter
from zope.component import getAdapters
from zope.component import getGlobalSiteManager

from Products.PloneSoftwareCenter.interfaces import IReleaseContent
from Products.PloneSoftwareCenter.interfaces import IPSCFileStorage

class BaseStorage(object):
    """Base class for storage adapters""" 
    name = ''
    adapts(IReleaseContent)
    implements(IPSCFileStorage)

    def __init__(self, context):
        self.context = context

    def getName(self):
        return self.name

class ZODBStorage(BaseStorage):
    """adapts a release folder as a ZODB storage
    """ 
    name = 'zodb'
    
    def setFileContent(self, content, filename):
        context = self.context
        rf = context._getOb(filename, None) 
        if rf is None:
            context.invokeFactory('PSCFile', id=filename)
        rf = context._getOb(filename) 
        rf.setDownloadableFile(content, filename=filename)
        rf.setTitle(filename)
        return filename 
   
    def getFileContent(self, filename):
        """returns file content"""
        # XXX see how to stream efficiently
        file_ = self.context._getOb(filename, None)
        return file_.data

    def getFileNames(self):
        return self.context.objectIds()

def getFileStorageNames(context):
    """return registered class for IPSCFileStorage""" 
    sm = getGlobalSiteManager()
    return (name for name, adapter in 
            getAdapters((context,), IPSCFileStorage))

def getFileStorage(context, name):
    """return the adapter, given the name"""
    return getAdapter(context, IPSCFileStorage, name)

def getStorageName(context):
    """returns the storage name, which is stored at PSC level"""
    # XXX crawl back up - what if the node in not in a PSC instance ?
    psc = content
    while not isinstance(psc, PloneSoftwareCenter):
        psc = psc.getParentNode()
    return psc.getStorageStrategy()


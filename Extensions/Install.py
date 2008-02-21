from StringIO import StringIO
from Products.CMFCore.utils import getToolByName

from Products.PloneSoftwareCenter import config

EXTENSION_PROFILES = ('Products.PloneSoftwareCenter:default',)

def install(self):
    out = StringIO()

    tool=getToolByName(self, "portal_setup")

    try:
        tool.runAllImportStepsFromProfile(
            'profile-%s' % EXTENSION_PROFILES[0],
            purge_old=False)
    except AttributeError:   # before plone 3
        tool.setImportContext('profile-%s' % EXTENSION_PROFILES[0])
        tool.runAllImportSteps(purge_old=False)

    print >> out, "Successfully installed %s" % config.PROJECTNAME

    return out.getvalue()

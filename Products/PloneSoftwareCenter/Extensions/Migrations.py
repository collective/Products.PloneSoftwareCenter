try:
    from Products.contentmigration.migrator import InlineFieldActionMigrator, BaseInlineMigrator
    from Products.contentmigration.walker import CustomQueryWalker
    haveContentMigrations = True
except ImportError:
    haveContentMigrations = False
    
import types

from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.Archetypes import transaction
from Products.CMFPlone.utils import safe_hasattr

from Acquisition import aq_base
from DateTime import DateTime

def v1beta7_v1beta8(self, out):
    """Migrate from beta 7 to beta 8
    """
    
    if not haveContentMigrations:
        print >> out, "WARNING: Install contentmigrations to be able to migrate from v1 beta 7 to beta 8"
        return

    class ReleaseStateMigrator(BaseInlineMigrator):
        src_portal_type = src_meta_type = 'PSCRelease'
        
        stateMap = {'final' : 'final',
                    'rc'    : 'release-candidate',
                    'beta'  : 'beta',
                    'alpha' : 'alpha',
                    'in progress' : 'pre-release',
                    'in-progress' : 'pre-release'}
        
        def migrate_releaseState(self):
            maturity = getattr(aq_base(self.obj), 'maturity', None)
            wftool = getToolByName(self.obj, 'portal_workflow')
            wfdef = getattr(aq_base(wftool), 'psc_release_workflow', None)
            if maturity is not None and wfdef is not None:
                maturity = str(maturity)
                state = self.stateMap.get(maturity.lower(), 'pre-release')
                wfstate = {'action'       : None, 
                           'actor'        : None, 
                           'comments'     : 'Updated by migration; maturity was ' + maturity,
                           'review_state' : state,
                           'time'         : DateTime()}
                wftool.setStatusOf('psc_release_workflow', self.obj, wfstate)
                wfdef.updateRoleMappingsFor(self.obj)
                self.obj.reindexObject()
                
    class ReleaseCountMigrator(BaseInlineMigrator): 
        src_portal_type = src_meta_type = 'PSCProject'
        
        def migrate_releaseCount(self):
            releaseCount = getattr(aq_base(self.obj), 'releaseCount', None)
            catalog = getToolByName(self.obj, 'portal_catalog')
            releases = catalog.searchResults(portal_type = 'PSCRelease',
                                             review_state = ('alpha', 'beta', 'release-candidate', 'final',),
                                             path = '/'.join(self.obj.getPhysicalPath()))
            if releaseCount is None:
                self.obj.manage_addProperty('releaseCount', len(releases), 'int')
            else:
                self.obj.manage_changeProperties(releaseCount = len(releases))
            self.obj.reindexObject()
    
    portal = getToolByName(self, 'portal_url').getPortalObject()
    
    # Migrate release state
    walker = CustomQueryWalker(portal, ReleaseStateMigrator, query = {})
    transaction.savepoint(optimistic=True)
    print >> out, "Migrating from field-based maturity to workflow-based maturity"
    walker.go()
    
    # Migrate release count variable
    walker = CustomQueryWalker(portal, ReleaseCountMigrator, query = {})
    transaction.savepoint(optimistic=True)
    print >> out, "Adding release count property"
    walker.go()
    
def migrate(self):
    """Run migrations
    """
    out = StringIO()
    print >> out, "Starting PloneSoftwareCenter migration"
    v1beta7_v1beta8(self, out)
    print >> out, "PloneSoftwareCenter migrations finished"
    return out.getvalue()
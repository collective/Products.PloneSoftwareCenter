try:
    from Products.contentmigration.archetypes import ATItemMigrator
    from Products.contentmigration.walker import CustomQueryWalker
    haveContentMigrations = True
except ImportError:
    ATItemMigrator = object
    haveContentMigrations = False

from Products.CMFCore.utils import getToolByName
from transaction import savepoint

class blobMigrator(ATItemMigrator):
    src_portal_type = 'Downloadable File'
    src_meta_type = 'PSCFile'
    dst_portal_type = 'Blob'
    dst_meta_type = 'ATBlob'

    # migrate all fields except 'file', which needs special handling...
    fields_map = {
        'downloadableFile': None,
    }

    def migrate_data(self):
        self.new.getField('downloadadbleFile').getMutator(self.new)(self.old)

    def last_migrate_reindex(self):
        self.new.reindexObject()


def migrationWalker(self):
    """ set up walker for migrating instances """
    portal = getToolByName(self, 'portal_url').getPortalObject()
    return CustomQueryWalker(portal, blobMigrator, query = {})

def migrateFiles(self):
    """ migrate instances """
    walker = migrationWalker(self)
    savepoint(optimistic=True)
    walker.go()
    return walker.getOutput()


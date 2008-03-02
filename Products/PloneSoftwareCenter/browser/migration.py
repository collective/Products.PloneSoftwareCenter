from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.blob.migrations import haveContentMigrations
from plone.app.blob.migrations import migrateATFiles
from plone.app.blob.migrations import getATFilesMigrationWalker

class MigrationView(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        options = {}
        clicked = request.form.has_key
        if not haveContentMigrations:
            msg = _(u'Please install contentmigrations to be able to migrate to blobs.')
            IStatusMessage(request).addStatusMessage(msg, type='warning')
            options = { 'notinstalled': 42 }
        elif clicked('migrate'):
            output = migrateATFiles(self)
            count = len(output.split('\n')) - 1
            msg = _(u'blob_migration_info',
                default=u'Blob migration performed for ${count} item(s).',
                mapping={'count': count})
            IStatusMessage(request).addStatusMessage(msg, type='info')
            options = { 'count': count, 'output': output }
        elif clicked('cancel'):
            msg = _(u'Blob migration cancelled.')
            IStatusMessage(request).addStatusMessage(msg, type='info')
            request.RESPONSE.redirect(getToolByName(context, 'portal_url')())
        else:
            walker = getATFilesMigrationWalker(self)
            options = { 'available': len(list(walker.walk())) }
        return self.index(**options)


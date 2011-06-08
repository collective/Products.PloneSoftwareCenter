"""
$Id: PSCDocumentationFolder.py 24410 2006-06-05 01:40:27Z optilude $
"""

from zope.interface import implements

from Products.PloneSoftwareCenter.interfaces import IDocumentationFolderContent

from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.atapi import *
try:
    import transaction
except ImportError:  # BBB
    from Products.Archetypes import transaction

from Products.ATContentTypes.content.base import ATCTMixin

from Products.PloneSoftwareCenter import PSCMessageFactory as _
from Products.PloneSoftwareCenter.config import PROJECTNAME, DOCUMENTATION_ID
try:
    from Products.PloneHelpCenter.interfaces import IHelpCenterContent
except ImportError:
    IHelpCenterContent = None

PSCDocumentationFolderSchema = OrderedBaseFolderSchema.copy() + Schema((

    StringField(
        name='id',
        required=0,
        searchable=1,
        mode='r', # Leave the custom auto-generated ID
        widget=StringWidget (
            label=_(u"label_doc_short_name", default=u"Short name"),
            description=_(u"help_doc_short_name", default=u"Short name of the container - this should be 'documentation' to comply with the standards."),
            i18n_domain="plonesoftwarecenter",
        ),
    ),

    StringField(
        name='title',
        default='Documentation',
        searchable=1,
        accessor="Title",
        widget=StringWidget(
            label=_(u"label_doc_title", default=u"Title"),
            description=_(u"help_doc_title", default=u"Enter a title for the container"),
            i18n_domain="plonesoftwarecenter",
        ),
    ),

    StringField(
        name='description',
        default='Documentation for this project.',
        searchable=1,
        accessor="Description",
        widget=TextAreaWidget(
            label=_(u"label_doc_description", default=u"Description"),
            description=_(u"help_doc_description", default=u"Enter a description of the container"),
            i18n_domain="plonesoftwarecenter",
        ),
    ),
    
    LinesField(
        'audiencesVocab',
        accessor='getAudiencesVocab',
        edit_accessor='getRawAudiencesVocab',
        mutator='setAudiencesVocab',
        required=0,
        languageIndependent=1,
        widget=LinesWidget(
            label=_(u"phc_label_audience_helpcenter", default=u"Documentation audiences"),
            description=_(u"psc_audience_helpcenter", default=u"Audiences are optional. One type of audience on each line. If you leave this blank, audience information will not be used. Audience is typically 'End user', 'Developer' and similar."),
            i18n_domain = "plonehelpcenter",
        ),
    ),

))

class PSCDocumentationFolder(ATCTMixin, OrderedBaseFolder):
    """Folder type for holding documentation."""

    if IHelpCenterContent is not None:
        implements(IDocumentationFolderContent, IHelpCenterContent)
    else:
        implements(IDocumentationFolderContent)
    

    archetype_name = 'Documentation Section'
    immediate_view = 'base_edit'
    default_view = 'helpcenter_view'
    content_icon = 'documentation_icon.gif'
    schema = PSCDocumentationFolderSchema
    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    global_allow = False
    filter_content_types = True
    allowed_content_types = ('HelpCenterFAQFolder',
                             'HelpCenterHowToFolder',
                             'HelpCenterTutorialFolder',
                             'HelpCenterErrorReferenceFolder',
                             'HelpCenterLinkFolder',
                             'HelpCenterGlossary',
                             'HelpCenterInstructionalVideoFolder',
                             'HelpCenterReferenceManualFolder',)

    typeDescMsgId = 'description_edit_documentationfolder'
    typeDescription = ('A Documentation Section is used to hold software '
                       'documentation. It is given a default short name and '
                       'title to ensure that projects are consistent. '
                       'Please do not rename it.')

    def _renameAfterCreation(self, check_auto_id=False):
        parent = self.aq_inner.aq_parent
        if DOCUMENTATION_ID not in parent.objectIds():            
            # Can't rename without a subtransaction commit when using
            # portal_factory!
            transaction.savepoint(optimistic=True)
            self.setId(DOCUMENTATION_ID)
        

    security.declareProtected(permissions.View, 'generateUniqueId')
    def generateUniqueId(self, type_name):
        """Override for the .py script in portal_scripts with the same name.

        Gives some default names for contained content types.
        """

        consideredTypes = {
            'HelpCenterFAQFolder': 'faq',
            'HelpCenterHowToFolder': 'how-to',
            'HelpCenterTutorialFolder': 'tutorial',
            'HelpCenterErrorReferenceFolder': 'error',
            'HelpCenterLinkFolder': 'link',
            'HelpCenterGlossary': 'glossary',
            'HelpCenterInstructionalVideoFolder': 'video',
            }

        # Use aq parent if we don't know what to do with the type
        if type_name not in consideredTypes:
            return self.aq_inner.aq_parent.generateUniqueId(type_name)
        else:
            return self._ensureUniqueId(consideredTypes[type_name])
    
    security.declarePrivate('_ensureUniqueId')
    def _ensureUniqueId(self, id):
        """Test the given id. If it's not unique, append .<n> where n is a
        number to make it unique.
        """
        if id in self.objectIds():
            idx = 0
            while '%s.%d' % (id, idx) in self.objectIds():
                idx += 1
            return '%s.%d' % (id, idx)
        else:
            return id
    
registerType(PSCDocumentationFolder, PROJECTNAME)

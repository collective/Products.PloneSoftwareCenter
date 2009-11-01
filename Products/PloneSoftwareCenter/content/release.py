"""
$Id: PSCRelease.py 24703 2006-06-11 01:44:04Z optilude $
"""

from zope.interface import implements

from Products.PloneSoftwareCenter.interfaces import IReleaseContent

import re

from random import random
from DateTime import DateTime

from Acquisition import aq_inner
from Acquisition import aq_parent

from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.base import ATCTMixin

from Products.AddRemoveWidget import AddRemoveWidget

from Products.PloneSoftwareCenter import config

from zope.annotation.interfaces import IAnnotations


PSCReleaseSchema = OrderedBaseFolderSchema.copy() + Schema((

    StringField('id',
        required=1,
        searchable=1,
        mode="rw",
        accessor="getId",
        mutator="setId",
        default=None,
        widget=StringWidget(
            label='Version',
            label_msgid='label_release_version',
            description="This field is also used in the URL "
                        "of the item, so please don't use spaces and special "
                        "characters. Also, please do NOT include the alpha, beta, or release candidate "
                        "state as this is handled by the "
                        "workflow. Example: '0.1'.",
            description_msgid='help_release_version',
            i18n_domain='plonesoftwarecenter',
        ),
    ),

    ComputedField('title',
        accessor='Title',
        expression="context.generateTitle()",
        mode='r',
        widget=ComputedWidget(
            label='Release title',
            label_msgid="label_release_title",
            description="The title of the release, computed from the title of the project and the version number.",
            description_msgid="help_release_title",
            i18n_domain='plonesoftwarecenter',
            modes=('view',),
            visible={
                'edit': 'invisible',
                'view': 'visible',
            },
        ),
    ),

    IntegerField('releaseNumber',
        required=0,
        searchable=0,
        default=1,
        widget=StringWidget(
            condition="object/showReleaseNumber",
            label='Release number',
            label_msgid='label_release_number',
            description='The release number. You do normally NOT need to adjust this manually. '
                        'For example, if this is a beta and the release number is 2, ' 
                        'the release will be titled "beta 2". Note that this does not apply to final '
                        'releases, nor to the first release (so beta 1 is just called "beta"). '
                        'Also note that this number ' 
                        'will be automatically adjusted if you re-release using the "state" menu.',
            description_msgid='help_release_number',
            i18n_domain='plonesoftwarecenter',
        ),
    ),

    StringField('codename',
        required=0,
        searchable=1,
        widget=StringWidget(
            label='Codename',
            label_msgid='label_release_codename',
            description='Codename for this release, if you have one.',
            description_msgid='help_release_codename',
            i18n_domain='plonesoftwarecenter',
        ),
    ),

    TextField('description',
        default='',
        searchable=1,
        required=1,
        accessor='Description',
        storage=MetadataStorage(),
        widget=TextAreaWidget(
            label='Release Summary',
            label_msgid='label_release_summary',
            description='A short description of the most important '
                        'focus of this release. Not a version history, '
                        'but in plain text what the main benefit of '
                        'this release is.',
            description_msgid='help_release_summary',
            i18n_domain='plonesoftwarecenter',
            rows=5,
        ),
    ),

    TextField('text',
        searchable=1,
        primary=1,
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=config.TEXT_TYPES,
        widget=RichWidget(
            label='Full Release Description',
            label_msgid='label_release_body_text',
            description='The complete release text.',
            description_msgid='help_release_body_text',
            i18n_domain='plonesoftwarecenter',
            rows=15,
        ),
    ),

    TextField('changelog',
        required=0,
        searchable=1,
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=config.TEXT_TYPES,
        widget=RichWidget(
            label='Changelog',
            label_msgid='label_release_changelog',
            description='A detailed log of what has changed since the previous release.',
            description_msgid='help_release_changelog',
            i18n_domain='plonesoftwarecenter',
            rows=10,
        ),
    ),

    StringField('releaseManager',
        required=0,
        searchable=1,
        widget=StringWidget(
            label='Release Manager',
            label_msgid='label_release_relmgr',
            description='Release manager for this release.',
            description_msgid='help_release_relmgr',
            i18n_domain='plonesoftwarecenter',
        ),
    ),

    StringField('releaseManagerContact',
        required=0,
        searchable=0,
        widget=StringWidget(
            label='Release Manager Contact E-mail',
            label_msgid='label_release_relmgr_email',
            description='Contact e-mail for Release Manager.',
            description_msgid='help_release_relmgr_email',
            i18n_domain='plonesoftwarecenter',
        ),
    ),

    DateTimeField('improvementProposalFreezeDate',
        required=0,
        searchable=0,
        widget=CalendarWidget(
            label='Proposals freeze date',
            label_msgid='label_release_improvement_proposal_freeze_date',
            description='Date after which no more Improvement Proposals will be associated with the release',
            description_msgid='help_release_improvement_proposal_freeze_date',
            i18n_domain='plonesoftwarecenter',
            show_hm = False,
        ),
    ),
    
    DateTimeField('featureFreezeDate',
        required=0,
        searchable=0,
        widget=CalendarWidget(
            label='Feature freeze date',
            label_msgid='label_release_feature_freeze_date',
            description='Date after which no new features will added to the release',
            description_msgid='help_release_feature_freeze_date',
            i18n_domain='plonesoftwarecenter',
            show_hm = False,
        ),
    ),

    DateTimeField('expectedReleaseDate',
        required=0,
        searchable=0,
        widget=CalendarWidget(
            label='(Expected) Release Date',
            label_msgid='label_release_expected_date',
            description='Date on which a final release is expected to be made or was made',
            description_msgid='help_release_expected_date',
            i18n_domain='plonesoftwarecenter',
            show_hm = False,
        ),
    ),

    StringField(
        name='license',
        required=1,
        vocabulary='getLicenseVocab',
        widget=SelectionWidget(
            label='License',
            label_msgid='label_release_license',
            description='Release License',
            description_msgid='help_release_license',
            i18n_domain='plonesoftwarecenter',
        ),
    ),

    LinesField(
        name='compatibility',
        required=1,
        searchable=1,
        index='KeywordIndex:schema',
        vocabulary='getCompatibilityVocab',
        widget=MultiSelectionWidget(
            label='Compatibility',
            label_msgid='label_release_compatibility',
            description='Tested and working with the following versions:',
            description_msgid='help_release_compatibility',
            i18n_domain='plonesoftwarecenter',
        ),
    ),

    ReferenceField('relatedFeatures',
        allowed_types=('PSCImprovementProposal',),
        multiValued=1,
        enforceVocabulary=1,
        relationship='RelatedFeatures',
        widget=AddRemoveWidget(
            label='Associated feature proposals',
            label_msgid="label_release_associated_feature_proposals",
            description="Please select related improvement proposals for features going into this release.",
            description_msgid="help_release_associated_feature_proposals",
            i18n_domain='plonesoftwarecenter',
        ),
        vocabulary='getRelatedFeaturesVocab',
    ),

    StringField('repository',
        searchable=1,
        required=0,
        validators=('isURL',),
        mutator='setRepository',
        widget=StringWidget(
            label="Repository branch",
            label_msgid="label_release_repository",
            description="URL of version control repository branch for this release.",
            description_msgid="help_release_repository",
            i18n_domain="plonesoftwarecenter",
        ),
    ),

))

PSCReleaseSchema.moveField('releaseNumber', before='description')

class PSCRelease(ATCTMixin, OrderedBaseFolder):
    """A release of a software project, either final or in progress"""

    implements(IReleaseContent)

    archetype_name = 'Software Release'
    immediate_view = default_view = 'psc_release_view'
    suppls_views = ()
    content_icon = 'download_icon.gif'
    schema = PSCReleaseSchema
    _at_rename_after_creation = False
    global_allow = False

    allowed_content_types = ('PSCFile', 'PSCFileLink',)

    security = ClassSecurityInfo()

    typeDescMsgId = 'description_edit_release'
    typeDescription = ('Contains details about a planned '
                       'or completed release of the project. Releases '
                       'may be related to specific Improvement Proposals, '
                       'to generate a roadmap. You the downloadable '
                       'files or external download locations inside a '
                       'release.')

    security.declareProtected(permissions.ModifyPortalContent, 'setRepository')
    def setRepository(self, value):
        """Set the repository branch, stripping off whitespace and any trailing
        slashes
        """
        value = value.strip()
        while value.endswith('/'):
            value = value[:-1]
        self.getField('repository').set(self, value)

    security.declarePublic('generateTitle')
    def generateTitle(self):
        """Generate the title of the release from the project name +
        the version 
        """ 
        # The first time this is called (it's called like two dozen times
        # when a release is created...) we don't seem to have an acquisition
        # context, so the call to aq_inner fails. Thus, we fall back on a
        # hardcoded string if the parent title lookup fails.

        portal_workflow = None
        try:
            version = self.getId()
            parentTitle = None
            try:
                parentTitle = IAnnotations(self)['title_hint']
            except KeyError:
                parentTitle = self.aq_inner.aq_parent.aq_parent.Title()
            portal_workflow = getToolByName(self, 'portal_workflow')
        except AttributeError:
            version = '?'
            parentTitle = '?'

        maturity = self.getMaturity()
        number = self.getReleaseNumber()

        if portal_workflow is None or maturity is None or maturity == 'final':
            return "%s %s" % (parentTitle, version,)
        else:
            maturityTitle = portal_workflow.getTitleForStateOnType(maturity, self.portal_type)
            if number is None or number <= 1:
                return "%s %s (%s)" % (parentTitle, version, maturityTitle,)
            else:
                return "%s %s (%s %d)" % (parentTitle, version, maturityTitle, number,)

    security.declareProtected(permissions.View, 'getRelatedFeatures')
    def getRelatedFeatures(self, review_state=None):
        """Get list of PLIPs associated with this release. Give a review state
        to return only features in this state.
        """
        items = self.getField('relatedFeatures').get(self)
        if review_state:
            wftool = getToolByName(self, 'portal_workflow')
            items = [i for i in items if wftool.getInfoFor(i, 'review_state') == review_state]
        items.sort(lambda x, y: cmp(int(x.getId()), int(y.getId())))
        return items

    security.declareProtected(permissions.View, 'getMaturity')
    def getMaturity(self):
        """Return the maturity (state) of this release"""
        try:
            portal_workflow = getToolByName(self, 'portal_workflow')
        except AttributeError:
            return ''
        return portal_workflow.getInfoFor(self, 'review_state')
    
    security.declareProtected(permissions.View, 'getLicenseVocab')
    def getLicenseVocab(self):
        """Get the available licenses from the parent project area via
         acqusition.
        """
        return self.getAvailableLicensesAsDisplayList()
    
    security.declareProtected(permissions.View, 'getCompatibilityVocab')
    def getCompatibilityVocab(self):
        """Get the available compatability versions from the parent project
           area via acqusition.
        """
        return self.getAvailableVersionsAsDisplayList()
    
    security.declareProtected(permissions.View, 'getRelatedFeaturesVocab')
    def getRelatedFeaturesVocab(self):
        """Get list of Improvement Proposals possible to add to this release
           from the parent project area via acquisition"""
        return self.getAvailableFeaturesAsDisplayList()
    
    security.declareProtected(permissions.View, 'showReleaseNumber')
    def showReleaseNumber(self):
        """Determine if the 'release number' field should be visible.
        """
        
        # Note: This is view code which ideally should not be on the
        # content itself, but because Archetypes is not componentized
        # yet this is not possible.
        wftool = getToolByName(self, 'portal_workflow')
        review_state = wftool.getInfoFor(self, 'review_state')
        return review_state not in ('final', 'pre-release',)

registerType(PSCRelease, config.PROJECTNAME)

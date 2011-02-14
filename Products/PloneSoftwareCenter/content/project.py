"""
$Id: PSCProject.py 24623 2006-06-09 08:13:43Z optilude $
"""
from zope.interface import implements
from zope.component import getMultiAdapter

from Products.PloneSoftwareCenter.interfaces import IProjectContent

from AccessControl import ClassSecurityInfo

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.atapi import *
from Products.validation import V_SUFFICIENT, V_REQUIRED
from Products.ATContentTypes.content.base import ATCTMixin
try:
    from Products.ATContentTypes.content.base import updateActions
    NEEDS_UPDATE = True
except ImportError:
    NEEDS_UPDATE = False
    
from Products.PloneSoftwareCenter import config
from Products.PloneSoftwareCenter.permissions import ApproveProject, \
  AddReviewComment
from Products.PloneSoftwareCenter.utils import get_projects_by_distutils_ids

from zExceptions import Unauthorized
import DateTime


PSCProjectSchema = OrderedBaseFolder.schema.copy() + Schema((

    StringField('id',
        required=0,
        searchable=1,
        validators=('isNonConflictingProjectId',),
        widget=IdWidget (
            label="Short name",
            label_msgid="label_project_short_name",
            description="Should not contain spaces, underscores or mixed case. Short Name is part of the item's web address.",
            description_msgid="help_project_short_name",
            i18n_domain="plonesoftwarecenter",
        ),
    ),
    
    TextField('description',
        default='',
        required=1,
        searchable=1,
        accessor="Description",
        storage=MetadataStorage(),
        widget=TextAreaWidget(
            label="Project Summary",
            label_msgid="label_project_description",
            description="A short summary of the project.",
            description_msgid="help_description",
            i18n_domain="plonesoftwarecenter",
            rows=5,
        ),
    ),

    TextField('text',
        default='',
        required=1,
        searchable=1,
        primary=1,
        default_content_type='text/plain',
        default_output_type='text/html',
        allowable_content_types=config.TEXT_TYPES,
        widget=RichWidget(
            label="Full Project Description",
            label_msgid="label_package_body_text",
            description="The complete project description.",
            description_msgid="help_package_body_text",
            i18n_domain="plonesoftwarecenter",
            rows=25,
        ),
    ),
    
    LinesField('classifiers',
        multiValued=1,
        required=0,
        vocabulary='getClassifiersVocab',
        enforceVocabulary=1,
        schemata="metadata",
        index='KeywordIndex:schema',
        widget=MultiSelectionWidget(
            label='Classifiers',
            label_msgid='label_classifiers',
            description='Trove classifiers for this item.',
            description_msgid='help_classifiers',
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),

    LinesField('categories',
        multiValued=1,
        required=1,
        vocabulary='getCategoriesVocab',
        enforceVocabulary=1,
        index='KeywordIndex:schema',
        widget=MultiSelectionWidget(
            label='Categories',
            label_msgid="label_categories",
            description='Categories that this item should appear in.',
            description_msgid="help_categories",
            i18n_domain="plonesoftwarecenter",
        ),
    ),
    
    StringField('distutilsMainId',
        required=0,
        schemata="distutils",
        index='KeywordIndex:schema',
        widget=StringWidget(
            label="Distutils id",
            label_msgid="label_project_distutils_main_id",
            description=("When the package that has this id is uploaded"
                         " or registered, the project description is "
                         " updated consequently"),
            description_msgid="help_project_distutils_main_id",
            i18n_domain="plonesoftwarecenter",
        ),
    ),
    
    LinesField('distutilsSecondaryIds',
        multiValued=1,
        required=0,
        schemata="distutils",
        index='KeywordIndex:schema',
        widget=LinesWidget(
            label='Distutils secondary Ids',
            label_msgid="label_project_distutils_secondary_ids",
            description='Other Distutils names managed by this project.',
            description_msgid="help_project_distutils_secondary_id",
            i18n_domain="plonesoftwarecenter",
        ),
    ),
    
    IntegerField('downloadCount',
        required = 0,
        schemata = 'distutils',
        widget = IntegerWidget(
            label = 'Download Count',
            label_msgid = 'label_project_download_count',
            description = 'Download count retrieved from pypi. Set to -1 to deprioritize and exclude from updates.',
            description_msgid = 'help_project_download_count',
            i18n_domain = 'plonesoftwarecenter',
            ),
        write_permission = 'Manage portal',
        ),
    
    LinesField('selfCertifiedCriteria',
        multiValued=1,
        required=0,
        vocabulary='getSelfCertificationCriteriaVocab',
        enforceVocabulary=1,
        index='KeywordIndex:schema',
        schemata="review",
        widget=MultiSelectionWidget(
            label="Self-Certification Checklist",
            label_msgid="label_self_certification_checklist",
            description='Check which criteria this project fulfills.',
            description_msgid="help_self_certification_checklist",
            i18n_domain="plonesoftwarecenter",
            format="checkbox",
        ),
    ),
    
    BooleanField('isApproved',
        required=0,
        write_permission=ApproveProject,
        schemata="review",
        widget=BooleanWidget(
            label="Approved",
            label_msgid="label_approved",
            description_msgid="description_approved",
            description="Indicate whether this project is approved by product reviewers.",
            i18n_domain="plonesoftwarecenter",
        ),
    ),
    
    TextField('reviewComment',
        searchable=1,
        required=0,
        schemata="review",
        write_permission=AddReviewComment,
        widget=TextAreaWidget(
            label="Review Comment",
            label_msgid="label_review_comment",
            description="Additional notes by reviewers of this project.",
            description_msgid="help_review_comment",
            i18n_domain="plonesoftwarecenter",
        ),
    ),

    LinesField('unsupportedVersions',
        required=0,
        multiValued=1,
        schemata="metadata",
        vocabulary='getVersionsVocab',
        widget=InAndOutWidget(
            label="Unsupported versions",
            label_msgid="label_unsupported_versions",
            description_msgid="description_unsupported_versions",
            description="For documentation items and releases, users will be warned if the relevant version is in the list on the right.",
            i18n_domain="plonesoftwarecenter",
        ),
    ),

    StringField('contactAddress',
        required=1,
        validators = (('isMailto', V_SUFFICIENT), ('isURL', V_REQUIRED),),
        widget=StringWidget(
            label="Contact address",
            label_msgid="label_package_contact_address",
            description="Contact address for the project. Use mailto: or http:// prefix depending on what contact method you prefer.",
            description_msgid="help_package_contact_address",
            i18n_domain="plonesoftwarecenter",
        ),
    ),

    StringField('homepage',
        searchable=1,
        required=0,
        validators=('isURL',),
        widget=StringWidget(
            label="Home page ",
            label_msgid="label_package_homepage",
            description="If the project has an external home page, enter its URL.",
            description_msgid="help_package_homepage",
            i18n_domain="plonesoftwarecenter",
        ),
    ),

    StringField('documentationLink',
        searchable=1,
        required=0,
        validators=('isURL',),
        widget=StringWidget(
            label="URL of documentation repository",
            label_msgid="label_package_documentation",
            description="If the project has externally hosted documentation, enter its URL.",
            description_msgid="help_package_documentation",
            i18n_domain="plonesoftwarecenter",
        ),
    ),

    StringField('repository',
        searchable=1,
        required=0,
        validators=('isURL',),
        widget=StringWidget(
            label="URL of version control repository",
            label_msgid="label_package_repository",
            description="If the project has a code repository, enter its URL.",
            description_msgid="help_package_repository",
            i18n_domain="plonesoftwarecenter",
        ),
    ),

    StringField('tracker',
        searchable=1,
        required=0,
        validators=('isURL',),
        widget=StringWidget(
            label="Issue tracker URL",
            label_msgid="label_package_tracker",
            description="If the project has an external issue tracker, enter its URL.",
            description_msgid="help_package_tracker",
            i18n_domain="plonesoftwarecenter",
        ),
    ),

    StringField('mailingList',
        searchable=1,
        required=0,
        validators=('isURL',),
        widget=StringWidget(
            label="Support mailing list or forum URL",
            label_msgid="label_package_mailinglist",
            description="URL of mailing list information page/archives or support forum, if the project has one.",
            description_msgid="help_package_mailinglist",
            i18n_domain="plonesoftwarecenter",
        ),
    ),

    ImageField('logo',
        required=0,
        original_size=(150,75),
        sizes=config.IMAGE_SIZES,
        widget=ImageWidget(
            label="Logo",
            label_msgid="label_package_logo",
            description="Add a logo for the project (or organization/company) by clicking the 'Browse' button. Max 150x75 pixels (will be resized if bigger).",
            description_msgid="help_package_logo",
            i18n_domain="plonesoftwarecenter",
        ),
    ),

    StringField('logoURL',
        searchable=1,
        required=0,
        validators=('isURL',),
        widget=StringWidget(
            label="Logo link",
            label_msgid="label_package_logo_link",
            description="The URL the logo should link to, if applicable.",
            description_msgid="help_package_logo_link",
            i18n_domain="plonesoftwarecenter",
        ),
    ),

    ImageField('screenshot',
        required=0,
        original_size=(800,600),
        sizes=config.IMAGE_SIZES,
        widget=ImageWidget(
            label="Screenshot",
            label_msgid="label_package_screenshot",
            description="Add a screenshot by clicking the 'Browse' button. Max 800x600 (will be resized if bigger).",
            description_msgid="help_package_screenshot",
            i18n_domain="plonesoftwarecenter",
        ),
    ),

))



PSCProjectSchema['subject'].widget.visible={"view":False,"edit":False}
PSCProjectSchema.moveField("categories",before="allowDiscussion")
PSCProjectSchema.moveField("classifiers",after="categories")
PSCProjectSchema.moveField("unsupportedVersions",after="classifiers")

class PSCProject(ATCTMixin, OrderedBaseFolder):
    """Project class that holds the information about the Software Project.
    """

    implements(IProjectContent)

    archetype_name = 'Software Project'
    immediate_view = default_view = 'psc_project_view'
    suppl_views = ()
    content_icon = 'product_icon.gif'
    schema = PSCProjectSchema
    _at_rename_after_creation = True

    global_allow = False
    allowed_content_types = ('PSCReleaseFolder',
                            'PSCImprovementProposalFolder',
                            'PSCDocumentationFolder',)

    security = ClassSecurityInfo()

    typeDescMsgId = 'description_edit_package'
    typeDescription = ('A Software Project contains details about a '
                       'particular software package. It can keep track '
                       'of meta-data about the project, as well as '
                       'releases and improvement proposals.')
    if NEEDS_UPDATE:                   
        actions = updateActions(ATCTMixin,
            ({
            'id'          : 'local_roles',
            'name'        : 'Sharing',
            'action'      : 'string:${object_url}/sharing',
            'permissions' : (permissions.ManageProperties,),
             },
            {
            'id'          : 'view',
            'name'        : 'View',
            'action'      : 'string:${folder_url}/',
            'permissions' : (permissions.View,),
             },
            )
        )
    
    
    def canSelectDefaultPage(self):
        return False

    security.declarePrivate('initializeArchetype')
    def initializeArchetype(self, **kwargs):
        """Initialize package.

        Projects are initialized with a release folder.
        """
        OrderedBaseFolder.initializeArchetype(self,**kwargs)
        
        # if self.haveHelpCenter() and \
        #        not self.objectIds('PSCDocumentationFolder'):
        #    self.invokeFactory('PSCDocumentationFolder',
        #                       config.DOCUMENTATION_ID)
        
        if not self.objectIds('PSCReleaseFolder'):
            self.invokeFactory('PSCReleaseFolder', config.RELEASES_ID)
        
        # if not self.objectIds('PSCImprovementProposalFolder'):
        #     self.invokeFactory('PSCImprovementProposalFolder',
        #                        config.IMPROVEMENTS_ID)
        
        if not self.hasProperty('releaseCount'):
            self.manage_addProperty('releaseCount', 0, 'int')

    def _setAndIndexField(self, field_name, index_name, value):
        self.getField(field_name).set(self, value)
        self.reindexObject(idxs=[index_name])
        catalog = getToolByName(self, 'portal_catalog')
        res = catalog.searchResults(
                          portal_type=['PSCRelease',
                                       'PSCFile',
                                       'PSCFileLink',
                                       'PSCImprovementProposal'],
                          path='/'.join(self.getPhysicalPath()))
        for r in res:
            o = r.getObject()
            o.reindexObject(idxs=[index_name])


    security.declareProtected(permissions.View, 'getView')
    def getView(self):
        """returns the view object"""
        return getMultiAdapter((self, self.REQUEST), name='project_view')
   
    security.declareProtected(permissions.ModifyPortalContent,
                              'setClassifiers')
    def setClassifiers(self, value):
        """Overrides classifiers mutator so we can reindex internal content.
        """
        self._setAndIndexField('classifiers', 'getClassifiers', value)

    security.declareProtected(permissions.ModifyPortalContent,
                              'setCategories')
    def setCategories(self, value):
        """Overrides categories mutator so we can reindex internal content.
        """
        self._setAndIndexField('categories', 'getCategories', value)

    security.declareProtected(permissions.View, 'getCategoryTitles')
    def getCategoryTitles(self):
        """Return selected categories as a list of category long names,
        for the user interface.
        """
        vocab = self.getCategoriesVocab()
        values = [vocab.getValue(c) or c for c in self.getCategories()]
        values.sort()
        return values
    
    security.declareProtected(permissions.View,
                              'getVocabularyTitlesFromCLassifiers')
    def getVocabularyTitlesFromCLassifiers(self):
        """Return selected categories as a list of category long names,
        for the user interface. Uses the classifiers.
        """
        vocab = self.getClassifiersVocab()
        values = [vocab.getValue(c) or c for c in self.getClassifiers()]
        values.sort()
        return values

    security.declareProtected(permissions.View, 'getClassifiersVocab')
    def getClassifiersVocab(self):
        """Get classifiers vocabulary from parent project area via acquisition.
        """
        return self.getAvailableClassifiersAsDisplayList()
    

    security.declareProtected(permissions.View, 'getCategoriesVocab')
    def getCategoriesVocab(self):
        """Get categories vocabulary from parent project area via acquisition.
        """
        return self.getAvailableCategoriesAsDisplayList()
    
    security.declareProtected(permissions.View, 'getSelfCertificationCriteriaVocab')
    def getSelfCertificationCriteriaVocab(self):
        """Get self-certification criteria vocabulary from parent project area
        via acquisition.
        """
        return self.getAvailableSelfCertificationCriteriaAsDisplayList()
    
    security.declareProtected(permissions.View, 'getReleaseFolder')
    def getReleaseFolder(self):
        """Get the release folder.

        We only should have one, so only deal with case of single
        folder. May return None if no roadmap folder exists.
        """
        type_filter = {'portal_type' : 'PSCReleaseFolder' }
        folders = self.contentValues(filter = type_filter)
        if folders:
            return folders[0]
        else:
            return None

    security.declareProtected(permissions.View, 'getRoadmapFolder')
    def getRoadmapFolder(self):
        """Get the roadmap folder.

        We only should have one, so only deal with case of single
        folder. May return None if no roadmap folder exists.
        """
        type_filter = {'portal_type' : 'PSCImprovementProposalFolder'}
        folders = self.contentValues(filter = type_filter)
        if folders:
            return folders[0]
        else:
            return None

    security.declareProtected(permissions.View, 'getNotAddableTypes')
    def getNotAddableTypes(self):
        """Hide the release container types if it already exists.
        """
        ignored = []
        objectIds = self.objectIds()
        if config.RELEASES_ID in objectIds:
            ignored.append('PSCReleaseFolder')
        if config.IMPROVEMENTS_ID in  objectIds:
            ignored.append('PSCImprovementProposalFolder')
        if not self.haveHelpCenter() or \
            config.DOCUMENTATION_ID in objectIds:
            ignored.append('PSCDocumentationFolder')
        if config.TRACKER_ID in  objectIds:
            ignored.append('PoiPscTracker')
        return ignored

    security.declareProtected(permissions.View, 'getVersionsVocab')
    def getVersionsVocab(self):
        """To ensure PloneHelpCenter integration works, return the versions
        defined, by looking at the versions found in the releases.
        """
        catalog = getToolByName(self, 'portal_catalog')
        releases = catalog.searchResults(portal_type = 'PSCRelease',
                                         path = '/'.join(self.getPhysicalPath()))
        return [r.getId for r in releases if r]

    security.declareProtected(permissions.View, 'getCurrentVersions')
    def getCurrentVersions(self):
        """To ensure PloneHelpCenter integration works, return the versions
        which are supported, by looking at the versions found in the releases
        and subtracting the ones listed in unsupportedVersions.
        """
        allVersions = self.getVersionsVocab()
        unsupported = self.getUnsupportedVersions()
        return [v for v in allVersions if v not in unsupported]
        
    security.declareProtected(permissions.View, 'haveHelpCenter')
    def haveHelpCenter(self):    
        """Test to see if PloneHelpCenter is installed
        """
        ttool = getToolByName(self, 'portal_types')
        if 'HelpCenter' in ttool.objectIds():
            return True
        else:
            return False
    
    security.declareProtected(permissions.View, 'getAvailableFeaturesAsDisplayList')
    def getAvailableFeaturesAsDisplayList(self):
        """Get list of Improvement Proposals in DisplayList form."""
        catalog = getToolByName(self, 'portal_catalog')
        projectPath = self.getPhysicalPath()
        if len(projectPath) > 1 and projectPath[-1] == 'portal_factory':
            projectPath = projectPath[:-2]

        search = catalog.searchResults(portal_type = 'PSCImprovementProposal',
                                       path = '/'.join(projectPath))
        lst = DisplayList()
        for i in search:
            title = i.Title
            if len(title) > 40:
                title = title[:40] + '...'

            lst.add(i.UID, title)
        return lst
   
    def _distUtilsNameAvailable(self, ids):
        current_id = self.getId() 
        sc = self.getParentNode()
        existing_projects = get_projects_by_distutils_ids(sc, ids)

        # make sure the names are not in another project already
        for project_id in existing_projects:
            if project_id != current_id:
                return False
        return True

    def getCompatibility(self):
        '''Get the compatibility of the product by getting  
        the compatabilities of the LATEST release. This is 
        used primarily by the index.
        '''
        compatabilities = []
        release = self.getLatestRelease()
        if release:
            for release_compatability in release.getCompatibility:
                compatabilities.append(release_compatability)
        compatabilities.sort(reverse=True)
        return set(compatabilities)
            
    def getLatestRelease(self):
        """Get the most recent final release brain or None if none 
        can be found.
        """
        releaseFolder = self.getReleaseFolder()
        
        res = None
        
        if releaseFolder:
            catalog = getToolByName(self, 'portal_catalog')
            res = catalog.searchResults(
              path = '/'.join(releaseFolder.getPhysicalPath()),
              review_state = 'final',
              sort_on = 'Date',
              sort_order = 'reverse',
              portal_type = 'PSCRelease')
        
        if not res:
            return None
        else:
            return res[0]
            
    def mayBeUnmaintained(self):
        """Return True if there hasn't been a release in over a year"""
        lastRelease = self.getLatestReleaseDate()
        if not lastRelease:
            return False
            
        if DateTime.DateTime() - lastRelease > 360:
            return True
            
        return False
        
            
    def getLatestReleaseDate(self):
        """
        Return the effective date of the last release. This is currently used for index 
        and catalog data.
        """
        latest = self.getLatestRelease()
        if latest:
            return latest.effective
        return None
    

    security.declareProtected(permissions.ModifyPortalContent,  
                              'setDistutilsSecondaryIds')
    def setDistutilsSecondaryIds(self, names):
        if not self._distUtilsNameAvailable(names):
            raise Unauthorized
        self.getField('distutilsSecondaryIds').set(self, names) 
        self.reindexObject()

    security.declareProtected(permissions.ModifyPortalContent,  
                              'setDistutilsMainId')
    def setDistutilsMainId(self, name):
        if not self._distUtilsNameAvailable([name]):
            raise Unauthorized
        self.getField('distutilsMainId').set(self, name) 
        self.reindexObject()

registerType(PSCProject, config.PROJECTNAME)


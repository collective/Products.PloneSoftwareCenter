"""
$Id: PloneSoftwareCenter.py 24613 2006-06-08 23:40:22Z optilude $
"""

from zope.interface import implements
from zope import event

from Products.PloneSoftwareCenter.interfaces import ISoftwareCenterContent
from Products.PloneSoftwareCenter.storage import getFileStorageVocab
from Products.PloneSoftwareCenter.events.softwarecenter import \
        StorageStrategyChanging

from AccessControl import ClassSecurityInfo

from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName

from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.base import ATCTMixin
try:
    from Products.ATContentTypes.content.base import updateActions
    NEEDS_UPDATE = True
except ImportError:
    NEEDS_UPDATE = False
    
from Products.ArchAddOn.Fields import SimpleDataGridField
from Products.ArchAddOn.Widgets import SimpleDataGridWidget
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget

from Products.PloneSoftwareCenter.config import PROJECTNAME
from Products.PloneSoftwareCenter.config import trove

from Products.PloneSoftwareCenter import PSCMessageFactory as _

PloneSoftwareCenterSchema = OrderedBaseFolder.schema.copy() + Schema((

    TextField('description',
        searchable=1,
        accessor='Description',
        storage=MetadataStorage(),
        widget=TextAreaWidget(
            label=_(u"label_package_area", default=u"Description"),
            description=_(u"help_package_area", default=u"Description for the software center."),
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),

    SimpleDataGridField('availableClassifiers',
            columns=3,
        column_names=('id', 'title', 'trove-id'),
        default=trove.get_datagrid(),
        widget=SimpleDataGridWidget(
            label=_(u"label_classifiers", default=u"Classifiers"),
            description=_(u"help_classifiers_vocab", default=u"Define the Trove classifiers. The format is 'Id | Title | Trove id'. The Id must be unique, and Trove id corresponds to the Trove value"),
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),

    BooleanField('useClassifiers',
        required=0,
        widget=BooleanWidget(
            label=_(u"label_use_classifier", default=u"Use Classifiers to display Categories (with Topic :: *)."),
            description=_(u"description_use_classifier", default=u"Indicate whether the Software Center uses the Classifiers field to display projects. In that case it gets all lines starting with 'Topic' and builds the category list with them."),
            i18n_domain="plonesoftwarecenter",
        ),
    ),


    SimpleDataGridField('availableCategories',
            columns=3,
        column_names=('id', 'title', 'description'),
        default=[
            'standalone|Stand-alone products|Projects that are self-contained.', 
            'add-on|Add-on components|Projects that provide additional functionality.', 
            'infrastructure|Infrastructure|Projects that provide services.',
        ],
        widget=SimpleDataGridWidget(
            label=_(u"label_categories_vocab", default=u"Categories"),
            description=_(u"help_categories_vocab", default=u"Define the available categories for classifying the projects. The format is Short Name | Long name | Description. The id must be unique."),
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),

    SimpleDataGridField('availableLicenses',
        column_names=('id', 'title', 'url'),
        columns=3,
        default=[
            'GPL|GPL - GNU General Public License|http://creativecommons.org/licenses/GPL/2.0/',
            'LGPL|LGPL - GNU Lesser General Public License|http://creativecommons.org/licenses/LGPL/2.1/',
            'BSD|BSD License (revised)|http://opensource.org/licenses/bsd-license',
            'Freeware|Freeware|http://wikipedia.org/Freeware',
            'Public Domain|Public Domain|http://creativecommons.org/licenses/publicdomain',
            'OSI|Other OSI Approved|http://opensource.org/licenses',
            'ZPL|Zope Public License (ZPL)|http://opensource.org/licenses/zpl',
            'Commercial|Commercial License|http://plone.org/documentation/faq/plone-license',
        ],
        widget=SimpleDataGridWidget(
            label=_(u"label_licenses_vocab", default=u"Available licenses"),
            description=_(u"help_licenses_vocab", default=u"Define the available licenses for software releases. The format is Short Name | Title | URL."),
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),

    LinesField('availableVersions',
        default=[
            'Plone 4.3',
            'Plone 4.2',
            'Plone 4.1',
            'Plone 4',
            'Plone 3',
            'Plone 2.5',
            'Plone 2.1',
        ],
        widget=LinesWidget(
            label=_(u"label_versions_vocab", default=u"Versions"),
            description=_(u"help_versions_vocab", default=u"Define the vocabulary for versions that software releases can be listed as being compatible with. The first item will be the default selection."),
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),

    LinesField('availablePlatforms',
        default=[
            'All platforms',
            'Linux',
            'Linux-x64',
            'Mac OS X',
            'Windows',
            'BSD',
            'UNIX (other)'
        ],
        widget=LinesWidget(
            label=_(u"label_platforms_vocab", default=u"Platforms"),
            description=_(u"help_platforms_vocab", default=u"Define the available platforms for software files. The first line is reserved for All platforms or any equivalent labeling."),
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),
    
    LinesField('projectEvaluators',
        languageIndependent=1,
        widget=LinesWidget(
            label=_(u"label_project_evaluators", default=u"Project Evaluators"),
            description=_(u"help_project_evaluators", default=u"Enter additional names (no need to include the current owner) for those who can make official reviews of projects."),
            i18n_domain="plonesoftwarecenter",
        ),
    ),
    
    LinesField('availableSelfCertificationCriteria',
        default=[
            'Internationalized',
            'Unit tests',
            'End-user documentation',
            'Internal documentation (documentation, interfaces, etc.)',
            'Existed and maintained for at least 6 months',
            'Installs and uninstalls cleanly',
            'Code structure follows best practice',
        ],
        widget=LinesWidget(
            label=_(u"label_self_certification_criteria_vocab", default=u"Self-Certification Checklist"),
            description=_(u"help_self_certification_criteria_vocab", default=u"Define the available criteria for developers to self-certify their projects."),
            i18n_domain='plonesoftwarecenter',
            rows=10,
        ),
    ),
    
    StringField('product_title',
        default='Add-on Product',
        widget=StringWidget(
            label=_(u"label_product_title", default=u"Product Title"),
            description=_(u"help_product_title", default=u"Title of products when using the project view. For example, 'Add-on Product', 'Extension', or 'Template'."),
            i18n_domain='plonesoftwarecenter',
        ),
    ),
    
    TextField('addon_description',
        default='Add-ons extend your Plone site with additional functionality.',
        widget=TextAreaWidget(
            label=_(u"label_addon_description", default=u"Product Description"),
            description=_(u"help_addon_description", default=u"When using project view, please provide some text to introduce the products."),
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),
    
    TextField('installation_instructions',
        default='If you are using Plone 3.2 or higher, you probably want to install '
                'this product with buildout. See <a href="http://plone.org/'
                'documentation/kb/installing-add-ons-quick-how-to">our tutorial on '
                'installing add-on products with buildout</a> for more information.',
        default_content_type='text/html',
        default_output_type='text/html',
        widget=TextAreaWidget(
            label=_(u"label_installation_instructions", default=u"Product Installation Instructions"),
            description=_(u"help_installation_instructions", default=u"Enter any installation instructions that should appear on each product page."),
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),

    ReferenceField('featuredProject',
        multiValued=0,
        allowed_types=('PSCProject',),
        relationship='featuredProject',
        widget=ReferenceBrowserWidget(
            label=_(u"label_featured_project", default=u"Featured Project"),
            description=_(u"help_featured_project", default=u"Featured project for the software center (for use with the plonesoftwarecenter_ploneorg template)."),
            i18n_domain='plonesoftwarecenter',
        ),
    ),

    ReferenceField('featuredProjectRelease',
        multiValued=0,
        allowed_types=('PSCRelease',),
        relationship='featuredProjectRelease',
        widget=ReferenceBrowserWidget(
            label=_(u"label_featured_project_release", default=u"Featured Project Release"),
            description=_(u"help_featured_project_release", default=u"Featured project release for the featured project of the software center (for use with the plonesoftwarecenter_ploneorg template)."),
            i18n_domain='plonesoftwarecenter',
        ),
    ),

    StringField('storageStrategy',
        default='archetype',
        vocabulary='getFileStorageStrategyVocab',
        widget=SelectionWidget(
            label=_(u"label_storage_strategy", default=u"Storage strategy"),
            description=_(u"help_storage_strategy", default=u"Defines the storage strategies for files"),
            i18n_domain="plonesoftwarecenter",
        ),
),             

))

class PloneSoftwareCenter(ATCTMixin, BaseBTreeFolder):
    """A simple folderish archetype for the Software Center."""

    implements(ISoftwareCenterContent)

    content_icon = 'product_icon.gif'

    archetype_name = 'Software Center'
    metatype = 'PloneSoftwareCenter'
    immediate_view = default_view = 'plonesoftwarecenter_view'
    suppl_views = ()

    global_allow = 1
    filter_content_types = 1
    allowed_content_types = ('PSCProject',)
    schema = PloneSoftwareCenterSchema
    _at_rename_after_creation = True

    security = ClassSecurityInfo()
    
    typeDescription = "A container for software projects"

    if NEEDS_UPDATE: # pre Plone3/GS-based install
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

    # Validator

    security.declarePrivate('validate_availableCategories')
    def validate_availableCategories(self, value):
        """Ensure that when setting available categories, we don't accidentally
        set the same category id as an existing project.
        """
        catalog = getToolByName(self, 'portal_catalog')
        projects = catalog.searchResults(
                            portal_type = 'PSCProject',
                            path = '/'.join(self.getPhysicalPath()))
        
        categoryIds = [v.split('|')[0].strip() for v in value]
        projectIds = [p.getId for p in projects]

        empty = []
        invalid = []
        for cat in categoryIds:
            if not cat:
                empty.append(cat)
            elif cat in projectIds or categoryIds.count(cat) > 1:
                invalid.append(cat)
    
        if empty:
            return "Please enter categories as Short Name | Long name | Description."
        if invalid:
            return "The following short category names are in use, either " \
                   "by another category, or by a project in the software " \
                   "center: %s." % (','.join(invalid))
        else:
            return None

    # Vocabulary methods
    security.declareProtected(permissions.View, 
                              'getAvailableTopicsFromClassifiers')
    def getAvailableTopicsFromClassifiers(self):
        """Get categories in DisplayList form, extracted from
        all classifiers that starts with 'Topic'"""
        field = self.getField('availableClassifiers')
        classifiers = field.getAsGrid(field)
        vocab = {}
        for id, title, trove_id in classifiers:
            if trove_id.startswith('Topic'):
                vocab[id] = (title, trove_id)
        return vocab

    security.declareProtected(permissions.View, 
                              'getAvailableCategoriesAsDisplayList')
    def getAvailableCategoriesAsDisplayList(self):
        """Get categories in DisplayList form."""
        return self.getField('availableCategories').getAsDisplayList(self)

    security.declareProtected(permissions.View, 'getAvailableClassifiersAsDisplayList')
    def getAvailableClassifiersAsDisplayList(self):
        return self.getField('availableClassifiers').getAsDisplayList(self)


    security.declareProtected(permissions.View, 'getAvailableLicensesAsDisplayList')
    def getAvailableLicensesAsDisplayList(self):
        """Get licenses in DisplayList form."""
        return self.getField('availableLicenses').getAsDisplayList(self)

    security.declareProtected(permissions.View, 'getAvailableVersionsAsDisplayList')
    def getAvailableVersionsAsDisplayList(self):
        """Get versions in DisplayList form."""
        return DisplayList([(item, item) for item in self.getAvailableVersions()])
    
    security.declareProtected(permissions.View, 'getAvailableVersionsAsDisplayList')
    def getAvailableSelfCertificationCriteriaAsDisplayList(self):
        """Get self-certification criteria in DisplayList form."""
        try: 
            return DisplayList([(item, item) for item in self.getAvailableSelfCertificationCriteria()])
        except:
            return DisplayList([('no','criteria')])
    
    # Mutator methods
    security.declareProtected(permissions.ModifyPortalContent, 'setProjectEvaluators')
    def setProjectEvaluators(self, value, **kw):
        orig = self.getProjectEvaluators()
        self.getField('projectEvaluators').set(self, value, **kw)
        
        usersToDemote = [id for id in orig if id not in value]
        usersToPromote = [id for id in value if id not in orig]
        
        for id in usersToDemote:
            roles = list(self.get_local_roles_for_userid(id))
            while 'PSCEvaluator' in roles:
                roles.remove('PSCEvaluator')
            if not roles:
                self.manage_delLocalRoles([id])
            else:
                self.manage_setLocalRoles(id, roles)
        for id in usersToPromote:
            roles = list(self.get_local_roles_for_userid(id))
            if 'PSCEvaluator' not in roles:
                roles.append('PSCEvaluator')
            self.manage_setLocalRoles(id, roles)

    security.declareProtected(permissions.View, 
                              'getFileStorageStrategyVocab')
    def getFileStorageStrategyVocab(self):
        """returns registered storage strategies"""
        return getFileStorageVocab(self)

    security.declareProtected(permissions.ModifyPortalContent, 'setStorageStrategy')
    def setStorageStrategy(self, value, **kw):
        """triggers an event before changing the field"""
        # the event will raise an error if any
        # project failed to migrate from one storage
        # to another
        old = self.getStorageStrategy()
        if old != value:
            event.notify(StorageStrategyChanging(self, old, value))
        self.getField('storageStrategy').set(self, value, **kw)

registerType(PloneSoftwareCenter, PROJECTNAME)

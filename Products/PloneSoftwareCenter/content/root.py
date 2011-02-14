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

PloneSoftwareCenterSchema = OrderedBaseFolder.schema.copy() + Schema((

    TextField('description',
        searchable=1,
        accessor='Description',
        storage=MetadataStorage(),
        widget=TextAreaWidget(
            label_msgid='label_package_area',
            label='Description',
            description_msgid='help_package_area',
            description='Description for the software center.',
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),

    SimpleDataGridField('availableClassifiers',
            columns=3,
        column_names=('id', 'title', 'trove-id'),
        default=trove.get_datagrid(),
        widget=SimpleDataGridWidget(
            label='Classifiers',
            label_msgid='label_classifiers',
            description=('Define the Trove classifiers. '
                         'The format is "Id | Title | Trove id". '
                         'The Id must be unique, and Trove id corresponds '
                         'to the Trove value'),
            description_msgid='help_classifiers_vocab',
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),

    BooleanField('useClassifiers',
        required=0,
        widget=BooleanWidget(
            label="Use Classifiers to display Categories (with Topic :: *).",
            label_msgid="label_use_classifier",
            description_msgid="description_use_classifier",
            description=("Indicate whether the Software Center uses the "
                         "Classifiers field to display projects. " 
                         "In that case it gets all lines starting with "
                         "'Topic' and builds the category list with them." 
                         ),
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
            label='Categories',
            label_msgid='label_categories_vocab',
            description='Define the available categories for classifying the projects. The format is Short Name | Long name | Description. The id must be unique.',
            description_msgid='help_categories_vocab',
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
            label='Available licenses',
            label_msgid='label_licenses_vocab',
            description='Define the available licenses for software releases. The format is Short Name | Title | URL.',
            description_msgid='help_licenses_vocab',
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),

    LinesField('availableVersions',
        default=[
            'Plone 4',
            'Plone 3',
            'Plone 2.5',
            'Plone 2.1',
        ],
        widget=LinesWidget(
            label='Versions',
            label_msgid='label_versions_vocab',
            description='Define the vocabulary for versions that software releases can be listed as being compatible with. The first item will be the default selection.',
            description_msgid='help_versions_vocab',
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),

    LinesField('availablePlatforms',
        default=[
            'All platforms',
            'Linux',
            'Mac OS X',
            'Windows',
            'BSD',
            'UNIX (other)'
        ],
        widget=LinesWidget(
            label='Platforms',
            label_msgid='label_platforms_vocab',
            description='Define the available platforms for software files. The first line is reserved for All platforms or any equivalent labeling.',
            description_msgid='help_platforms_vocab',
            i18n_domain='plonesoftwarecenter',
            rows=6,
        ),
    ),
    
    LinesField('projectEvaluators',
        languageIndependent=1,
        widget=LinesWidget(
                label='Project Evaluators',
                label_msgid="label_project_evaluators",
                description="Enter additional names (no need to include the current owner) for those who can make official reviews of projects.",
                description_msgid="help_project_evaluators",
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
            label='Self-Certification Checklist',
            label_msgid='label_self_certification_criteria_vocab',
            description='Define the available criteria for developers to '
              'self-certify their projects.',
            description_msgid='help_self_certification_criteria_vocab',
            i18n_domain='plonesoftwarecenter',
            rows=10,
        ),
    ),

    ReferenceField('featuredProject',
        multiValued=0,
        allowed_types=('PSCProject',),
        relationship='featuredProject',
        widget=ReferenceBrowserWidget(
            label='Featured Project',
            label_msgid='label_featured_project',
            description='Featured project for the software center '
                        '(for use with the plonesoftwarecenter_ploneorg template).',
            description_msgid='help_featured_project',
            i18n_domain='plonesoftwarecenter',
        ),
    ),

    ReferenceField('featuredProjectRelease',
        multiValued=0,
        allowed_types=('PSCRelease',),
        relationship='featuredProjectRelease',
        widget=ReferenceBrowserWidget(
            label='Featured Project Release',
            label_msgid='label_featured_project_release',
            description='Featured project release for the featured project of the software center '
                        '(for use with the plonesoftwarecenter_ploneorg template).',
            description_msgid='help_featured_project',
            i18n_domain='plonesoftwarecenter',
        ),
    ),

    StringField('storageStrategy',
        default='archetype',
        vocabulary='getFileStorageStrategyVocab',
        widget=SelectionWidget(   
            label="Storage strategy",
            label_msgid="label_storage_strategy",
            description="Defines the storage strategies for files",
            description_msgid="help_storage_strategy",
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

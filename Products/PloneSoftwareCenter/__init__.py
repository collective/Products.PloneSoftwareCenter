"""
$Id$
"""

from Products.CMFCore.utils import ContentInit
from Products.CMFCore.DirectoryView import registerDirectory

from Products.Archetypes.atapi import listTypes, process_types

from Products.PloneSoftwareCenter import config
from Products.PloneSoftwareCenter import permissions as psc_permissions
from Products.CMFCore import permissions

from Products.validation import validation
from Products.PloneSoftwareCenter import validators

from zope.i18nmessageid import MessageFactory
PSCMessageFactory = MessageFactory('plonesoftwarecenter')

validation.register(validators.ProjectIdValidator('isNonConflictingProjectId'))
validation.register(validators.ProjectContactValidator('isValidContact'))

registerDirectory(config.SKINS_DIR, config.GLOBALS)


def initialize(context):
    # Kick content registration and sys.modules mangling
    from Products.PloneSoftwareCenter import content

    allTypes = listTypes(config.PROJECTNAME)

    # Register Archetypes content with the machinery
    content_types, constructors, ftis = process_types(
        allTypes, config.PROJECTNAME)

    center_content_types = []
    center_constructors = []

    project_content_types = []
    project_constructors = []

    member_content_types = []
    member_constructors = []

    for i in range(len(allTypes)):
        aType = allTypes[i]
        if aType['klass'].meta_type in ('PloneSoftwareCenter',):
            center_content_types.append(content_types[i])
            center_constructors.append(constructors[i])
        elif aType['klass'].meta_type in ('PSCProject',):
            project_content_types.append(content_types[i])
            project_constructors.append(constructors[i])
        else:
            member_content_types.append(content_types[i])
            member_constructors.append(constructors[i])

    # software center itself
    ContentInit(
        config.PROJECTNAME + ' Center',
        content_types=tuple(center_content_types),
        permission=psc_permissions.AddSoftwareCenter,
        extra_constructors=tuple(center_constructors),
        fti=ftis,
        ).initialize(context)

    # projects
    ContentInit(
        config.PROJECTNAME + ' Project',
        content_types=tuple(project_content_types),
        permission=psc_permissions.AddProject,
        extra_constructors=tuple(project_constructors),
        fti=ftis,
        ).initialize(context)

    # regular content
    ContentInit(
        config.PROJECTNAME + ' Project Content',
        content_types=tuple(member_content_types),
        permission=permissions.AddPortalContent,
        extra_constructors=tuple(member_constructors),
        fti=ftis,
        ).initialize(context)

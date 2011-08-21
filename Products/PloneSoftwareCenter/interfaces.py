from zope.interface import Interface


class ISoftwareCenterContent(Interface):
    """The root software center
    """


class IProjectContent(Interface):
    """A project in the software center
    """


class IDocumentationFolderContent(Interface):
    """A folder for documentation
    """


class IImprovementProposalFolderContent(Interface):
    """A folder for improvement proposals
    """


class IImprovementProposalContent(Interface):
    """An improvement proposal
    """


class IReleaseFolderContent(Interface):
    """A folder for releases
    """


class IReleaseContent(Interface):
    """A release in a project
    """


class IFileContent(Interface):
    """A downloadable file
    """


class IFileLinkContent(Interface):
    """A link to a downloadable file
    """

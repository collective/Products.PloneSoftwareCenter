Overview

  Plone Software Center is a tool to keep track of software projects and
  software releases, and is used to power the Products download area on
  plone.org.

  It was formerly called ArchPackage.

Installation

  Install as a usual Plone Product. If you have Plone Help Center
  installed, you get the ability to add documentation objects inside
  the Software Projects.

  - Requires Plone (3.0 or higher).

  - Requires DataGridField (1.6.0-beta2 or higher).
  
  - Requires AddRemoveWidget (1.0-beta3 or higher).

  - Requires ArchAddOn (1.0-beta2 or higher).

  - (Optionally requires) contentratings
    (https://svn.plone.org/svn/collective/contentratings/trunk/)
    This makes PSCProject ratable.

  - (Optionally requires) ExternalStorage (svn trunk) if you want files stored on FS 
    instead of in the ZODB.

  - (Optionally requires) PloneHelpCenter (1-5-beta3 or higher) to provide project-specific help
    containers.

Note for pre-1.0 users

  - Plone Software Center 1.0 switched to BTree-based containers for the projects
    and Improvement Proposals. This means that any 0.9-based instance (or earlier)
    have to reinstall and create a new instance of the project area, since the
    storages are incompatible. Sorry about the inconvenience.



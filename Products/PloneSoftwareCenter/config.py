"""
$Id$
"""
from zLOG import LOG, PROBLEM

# Use ExternalStorage for PSCFile?
USE_EXTERNAL_STORAGE = True

# Change to point to where content should be stored, it can be an
# absolute or a relative path.
# A relative path is based on '$INSTANCE_HOME/var' directory (the
# Data.fs dir) or, if present, on ENVIRONMENT_VARIABLE defined by
# the ExternalStorage config (default: EXTERNAL_STORAGE_BASE_PATH)
EXTERNAL_STORAGE_PATH = 'files'

PROJECTNAME = 'PloneSoftwareCenter'
SKINS_DIR = 'skins'

HARD_DEPS = ('AddRemoveWidget', 'ArchAddOn', 'DataGridField',)
SOFT_DEPS = 'ATReferenceBrowserWidget',

RELEASES_ID = 'releases'
IMPROVEMENTS_ID = 'roadmap'
DOCUMENTATION_ID = 'documentation'
TRACKER_ID = 'issues'

TEXT_TYPES = (
    'text/structured',
    'text/x-rst',
    'text/html',
    'text/plain',
)

IMAGE_SIZES = {
    'preview': (400, 400),
    'thumb': (128, 128),
    'tile': (64, 64),
    'icon': (32, 32),
    'listing': (16, 16),
}

GLOBALS = globals()

if USE_EXTERNAL_STORAGE:
    try:
        import Products.ExternalStorage
    except ImportError:
        LOG('PloneSoftwareCenter',
            PROBLEM, 'ExternalStorage N/A, falling back to AttributeStorage')
        USE_EXTERNAL_STORAGE = False

import os
from Globals import package_home
from trove import TroveClassifier 

trove_default = os.path.join(package_home(GLOBALS), 'TROVE.txt')
trove = TroveClassifier(trove_default)


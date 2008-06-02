"""
$Id$
"""
from zLOG import LOG, PROBLEM
import os
from Globals import package_home
from trove import TroveClassifier 

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

trove_default = os.path.join(package_home(GLOBALS), 'TROVE.txt')
trove = TroveClassifier(trove_default)


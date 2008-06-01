"""
$Id: test_functional.py 18604 2006-01-28 03:39:52Z dreamcatcher $
"""
import doctest
import os

from ZPublisher.HTTPRequest import FileUpload

from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from Products.PloneSoftwareCenter.tests.base import PSCFunctionalTestCase


OPTIONFLAGS = (doctest.REPORT_NDIFF |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def addMember(self, username, fullname="", email="", roles=('Member',)):
    self.portal.portal_membership.addMember(username, 'secret', roles, [])
    member = self.portal.portal_membership.getMemberById(username)
    member.setMemberProperties({'fullname': fullname, 'email': email})

def setUp(context):
    """creates a software center"""
    context.setRoles(['Manager'])
    context.portal.invokeFactory('PloneSoftwareCenter', id='psc')
    addMember(context, 'member1', 'Member one')

class FileHolder(object):
    def __init__(self, path):
        self.path = path
        self.file = open(path)
        self.headers = {}
        self.filename = os.path.basename(path)

datadir = os.path.dirname(__file__)

def test_suite():
    tarball = FileUpload(FileHolder(os.path.join(datadir, 'project-macosx-10.3-fat.tar.gz')))
    egg = FileUpload(FileHolder(os.path.join(datadir, 'project.egg')))
 
    globs = globals()
    globs['tarball'] = tarball
    globs['egg'] = egg

    return Suite(os.path.basename('pypi.txt'),
                 os.path.basename('permissions.txt'),
                 optionflags=OPTIONFLAGS,
                 package='Products.PloneSoftwareCenter.tests',
                 test_class=PSCFunctionalTestCase,
                 setUp=setUp, globs=globs)


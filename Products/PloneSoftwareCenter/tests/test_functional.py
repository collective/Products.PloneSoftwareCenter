"""
$Id: test_functional.py 18604 2006-01-28 03:39:52Z dreamcatcher $
"""
import unittest
import doctest
import os, sys

from ZPublisher.HTTPRequest import FileUpload

from Testing import ZopeTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from Products.PloneSoftwareCenter.tests.base import PSCFunctionalTestCase


OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def setUp(context):
    """creates a software center"""
    from Testing.ZopeTestCase import user_name, user_password
    context.setRoles(['Manager'])
    context.portal.invokeFactory('PloneSoftwareCenter', id='psc')

class FileHolder(object):
    def __init__(self, path):
        self.path = path
        self.file = open(path)
        self.headers = {}
        self.filename = os.path.basename(path)

datadir = os.path.dirname(__file__)

def test_suite():
    tarball = FileUpload(FileHolder(os.path.join(datadir, 'project.tgz')))
    egg = FileUpload(FileHolder(os.path.join(datadir, 'project.egg')))
 
    globs = globals()
    globs['tarball'] = tarball
    globs['egg'] = egg

    return Suite(os.path.basename('pypi.txt'),
                 optionflags=OPTIONFLAGS,
                 package='Products.PloneSoftwareCenter.tests',
                 test_class=PSCFunctionalTestCase,
                 setUp=setUp, globs=globs)


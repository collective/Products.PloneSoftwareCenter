"""
Contains utility functions

$Id$
"""
import os
import re
import zipfile
import StringIO
import operator
import distutils.version
from itertools import chain

from Products.CMFCore.utils import getToolByName

re_validPackage = re.compile(r"(?i)^\s*([a-z_]\w*(?:\.[a-z_]\w*)*)(.*)")
# (package) (rest)

re_paren = re.compile(r"^\s*\((.*)\)\s*$") # (list) inside of parentheses
re_splitComparison = re.compile(r"^\s*(<=|>=|<|>|!=|==)\s*([^\s,]+)\s*$")
# (comp) (version)


safe_zipnames = re.compile(r'(purelib|platlib|headers|scripts|data).+', re.I)

def plat(name):
    generic = r'^[\w\-\.]+\.%s\-[\w\-\.]+\.tar\.gz$'
    return re.compile(generic % name, re.I)

platform_catchers = ((plat('macosx'), 'Mac OS X'), 
                     (plat('linux'), 'Linux'),
                     (plat('linux-x64'), 'Linux-x64'),
                     (plat('win32'), 'Windows'))

def which_platform(filename_or_url):
    """Get the platform with the filename.
    
    - an egg will be considered as non-specific to a platform
      even if it contains a specific compilation
    - a tar.gz name will be scanned 
    """
    if '/' in filename_or_url:
        filename = filename_or_url.split('/')[-1]
    else:
        filename = filename_or_url

    for catcher, platform in platform_catchers:
        if catcher.search(filename) is not None:
            return platform
    return 'All platforms'

def is_distutils_file(content, filename, filetype):
    """Perform some basic checks to see whether the indicated file could be
    a valid distutils file.
    """
    if filename.endswith('.exe'):
        # check for valid exe
        if filetype != 'bdist_wininst':
            return False

        try:
            t = StringIO.StringIO(content)
            t.filename = filename
            z = zipfile.ZipFile(t)
            l = z.namelist()
        except zipfile.error:
            return False

        for zipname in l:
            if not safe_zipnames.match(zipname):
                return False

    elif filename.endswith('.zip'):
        # check for valid zip
        try:
            t = StringIO.StringIO(content)
            t.filename = filename
            z = zipfile.ZipFile(t)
            l = z.namelist()
        except zipfile.error:
            return False
        for entry in l:
            parts = os.path.split(entry)
            if len(parts) == 2 and parts[1] == 'PKG-INFO':
                # eg. "roundup-0.8.2/PKG-INFO"
                break
        else:
            return False

    return True

def splitUp(pred):
   """Parse a single version comparison.
   Return (comparison string, StrictVersion)
   """
   res = re_splitComparison.match(pred)
   if not res:
       raise ValueError, "Bad package restriction syntax:  " + pred
   comp, verStr = res.groups()
   return (comp, distutils.version.StrictVersion(verStr))

compmap = {"<": operator.lt, "<=": operator.le, "==": operator.eq,
           ">": operator.gt, ">=": operator.ge, "!=": operator.ne}

class VersionPredicate:
   """Parse and test package version predicates.

   >>> v = VersionPredicate("pyepat.abc (>1.0, <3333.3a1, !=1555.1b3, !=1.2.3)")
   >>> print v
   pyepat.abc (> 1.0, < 3333.3a1, != 1555.1b3, != 1.2.3)
   >>> v.satisfied_by("1.1")
   True
   >>> v.satisfied_by("1.4")
   True
   >>> v.satisfied_by("1.0")
   False
   >>> v.satisfied_by("4444.4")
   False
   >>> v.satisfied_by("1555.1b3")
   False
   >>> v = VersionPredicate("pat( ==  0.1  )  ")
   >>> v.satisfied_by("0.1")
   True
   >>> v.satisfied_by("0.2")
   False
   >>> v = VersionPredicate("p1.p2.p3.p4(>=1.0, <=1.3a1, !=1.2zb3)")
   Traceback (most recent call last):
   ...
   ValueError: invalid version number '1.2zb3'

   """

   def __init__(self, versionPredicateStr):
       """Parse a version predicate string.
       """
       # Fields:
       #    name:  package name
       #    pred:  list of (comparison string, StrictVersion)

       versionPredicateStr = versionPredicateStr.strip()
       if not versionPredicateStr:
           raise ValueError, "Empty package restriction"
       match = re_validPackage.match(versionPredicateStr)
       if not match:
           raise ValueError, "Bad package name in " + versionPredicateStr
       self.name, paren = match.groups()
       paren = paren.strip()
       if paren:
           match = re_paren.match(paren)
           if not match:
               raise ValueError, "Expected parenthesized list: " + paren
           str = match.groups()[0]
           self.pred = [splitUp(aPred) for aPred in str.split(",")]
           if not self.pred:
               raise ValueError("Empty Parenthesized list in %r" 
                                % versionPredicateStr )
       else:
           self.pred=[]

   def __str__(self):
       if self.pred:
           seq = [cond + " " + str(ver) for cond, ver in self.pred]
           return self.name + " (" + ", ".join(seq) + ")"
       else:
           return self.name

   def satisfied_by(self, version):
       """True if version is compatible with all the predicates in self.
          The parameter version must be acceptable to the StrictVersion
          constructor.  It may be either a string or StrictVersion.
       """
       for cond, ver in self.pred:
           if not compmap[cond](version, ver):
               return False
       return True


def check_provision(value):
    m = re.match("[a-zA-Z_]\w*(\.[a-zA-Z_]\w*)*(\s*\([^)]+\))?$", value)
    if not m:
        raise ValueError("illegal provides specification: %r" % value)
    return m.group(2)

def search_projects_by_field(center, field, value):
    value = [v for v in value if v]
    if not value:
        # If there is no search to be done there's no point checking 
        # the catalogue
        raise StopIteration     
    catalog = getToolByName(center, 'portal_catalog')
    sc_path = '/'.join(center.getPhysicalPath())
    query = {'path'         : sc_path,
             'portal_type'  : 'PSCProject'}
    if isinstance(value, tuple) or isinstance(value, list):
        for name in value:
            query[field] = name
            projects = catalog(**query)
            for brain in projects:
                yield brain.getId
    else:
        query[field] = value
        projects = catalog(**query)
        for brain in projects:
            yield brain.getId

def get_projects_by_distutils_ids(sc, ids):
    primary = search_projects_by_field(sc, 'getDistutilsMainId', ids)
    secondary = search_projects_by_field(sc, 'getDistutilsSecondaryIds', ids) 
    return chain(primary, secondary)


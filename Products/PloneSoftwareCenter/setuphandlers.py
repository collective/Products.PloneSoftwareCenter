"""
contains handlers for GS
"""
import xmlrpclib
import tempfile
import os
import shutil
import logging
import tarfile
import zipfile
import re
import sys
import subprocess
import urllib2
import socket

from StringIO import StringIO
from OFS.Image import File

from zExceptions import Unauthorized
from Products.Archetypes.atapi import *
from Products.CMFCore.utils import getToolByName
from Products.PloneSoftwareCenter.content.downloadablefile import PSCFileSchema

NAME = re.compile('Name: (.*)')

# if your previous instance had
WAS_EXTERNAL_STORAGE = True
EXTERNAL_STORAGE_PATHS = ('/srv/plone.org/zope/files/',
    '/srv/plone.org/buildout/parts/instance01/var/files/',
    '/srv/plone.org/buildout/parts/instance02/var/files/',
    '/srv/plone.org/buildout/parts/instance03/var/files/',
    '/srv/plone.org/buildout/parts/instance04/var/files/')


def temp(function):
    def _temp(*args, **kw):
        working_dir = tempfile.mkdtemp()
        old_location = os.getcwd()
        os.chdir(working_dir)
        try:
            return function(*args, **kw)
        finally:
            os.chdir(old_location)
            shutil.rmtree(working_dir, ignore_errors=True)
    return _temp


def timeout(function):
    def _timeout(*args, **kw):
        old = socket.getdefaulttimeout()
        socket.setdefaulttimeout(4)
        try:
            return function(*args, **kw)
        finally:
            socket.setdefaulttimeout(old)
    return _timeout


class DistantFile(object):
    def __init__(self, url):
        try:
            self.handle = urllib2.urlopen(url)
        except (urllib2.HTTPError, urllib2.URLError):
            self.handle = None
        self.url = url
        self.on_pypi = url.startswith('http://pypi.python.org')

    def getDownloadableFile(self):
        return self

    def getId(self):
        url = self.url.split('#md5=')
        url = url[0]
        return url.split()[-1]

    def get_data(self):
        if self.handle is None:
            return ""
        return self.handle.read()


@timeout
def before_1_5(portal_setup):
    """runs a migration on a previous version of PSC
    before the product switched to migration.xml
    """
    def _upgrade_project(project):
        #main = StringField('distutilsMainId',
        #  required=0,
        #  schemata="distutils",
        #  index='KeywordIndex:schema',
        #  )
        #project.schema['distutilsMainId'] = main

        #sec = LinesField('distutilsSecondaryIds',
        #      multiValued=1,
        #      required=0,
        #      schemata="distutils",
        #      index='KeywordIndex:schema')
        #project.schema['distutilsSecondaryIds'] = sec
        pass

    def _upgrade_psc(psc):
        logging.info('Upgrading %s' % psc.title_or_id())
        # we might want to do something else here
        #strategy = StringField('storageStrategy',
        #       default='archetype',
        #       vocabulary='getFileStorageStrategyVocab',
        #)

        #psc.schema['storageStrategy'] = strategy

    def _discovering_dist_ids(project):
        # for each file in the project we
        # extract the distutils name
        project_path = '/'.join(project.getPhysicalPath())
        files = cat(**{'portal_type': ['PSCFile', 'PSCFileLink'],
                       'path': project_path})
        ids = []
        for file_ in files:
            portal_type = file_.portal_type
            if portal_type == 'PSCFileLink':
                # the file is somewhere else, let's scan it
                file_ = file_.getObject()
                file_ = DistantFile(file_.getExternalURL())
            else:
                file_ = file_.getObject()
            # trying to get back from old
            # storage
            # ExternalStorage here
            #
            if WAS_EXTERNAL_STORAGE and portal_type != 'PSCFileLink':
                from Products.ExternalStorage.ExternalStorage import\
                     ExternalStorage
                storage = ExternalStorage(
                  prefix=EXTERNAL_STORAGE_PATHS[0],
                  archive=False,
                  rename=False,
                  )
                # transferring old data to new AT container
                fs = file_.schema['downloadableFile']
                old = fs.storage
                fs.storage = storage
                portal_url = getToolByName(file_, 'portal_url')

                real_file = os.path.join(
                    *portal_url.getRelativeContentPath(file_))
                for path in EXTERNAL_STORAGE_PATHS:
                    final_file = os.path.join(path, real_file)
                    if os.path.exists(final_file):
                        break
                if not os.path.exists(final_file):
                    logging.info(
                        '******** could not get %s on the file system !!'
                        % real_file)
                    continue
                    #raise ValueError('File not found %s' % final_file)
                fs.storage = old
                dfile = file_.getDownloadableFile()
                filename = dfile.filename
                data = open(final_file).read()
                if data == '':
                    logging.info('empty file ! %s' % final_file)
                #f = File(filename, filename, open(final_file))
            elif portal_type != 'PSCFileLink':
                storage = AttributeStorage()
                fs = file_.schema['downloadableFile']
                old = fs.storage
                fs.storage = storage
                dfile = file_.getDownloadableFile()
                data = dfile.get_data()
                filename = dfile.filename
                fs.storage = old
                #file_.getDownloadableFile().data = data
                #f = File(filename, filename, StringIO(data))
            if portal_type != 'PSCFileLink':
                #file_.setDownloadableFile(f)
                file_.schema = PSCFileSchema
                if filename == '' and data == '':
                    logging.info('file empty for %s' % file_)
                else:
                    if filename is None:
                        filename = file_.getId()
                    file_.setDownloadableFile(File(filename,
                        filename, StringIO(data)))
            id_ = extract_distutils_id(file_)
            if id_ is not None and id_ not in ids:
                ids.append(id_)
        return ids

    # XXX see what to do with earlier versions than
    # < 1.5
    cat = getToolByName(portal_setup, 'portal_catalog')
    # getting all PSC instances
    pscs = cat(**{'portal_type': 'PloneSoftwareCenter'})

    # checking all PloneSoftwareCenter instances
    for psc in pscs:
        psc = psc.getObject()

        _upgrade_psc(psc)
        # for each instance we want to
        # synchronize distutils ids
        distutils_ids = {}
        for project in psc.objectValues():
            if project.getId() in ('plone',):
                logging.info('Skipping %s' % project.getId())
                continue
            logging.info('Working on %s' % project.getId())
            _upgrade_project(project)
            # trying to find distutils ids
            ids = _discovering_dist_ids(project)
            for id_ in ids:
                old = distutils_ids.get(id_, ())
                if project in old:
                    continue
                distutils_ids[id_] = old + (project,)
        # synchronize with the Cheeseshop
        logging.info('Starting synchro')
        pypi_synchro(distutils_ids)


@temp
def extract_distutils_id(egg_or_tarball):
    """gives the disutils id"""
    file_ = egg_or_tarball.getDownloadableFile()
    filename = egg_or_tarball.getId()
    try:
        data = file_.get_data()
    except socket.timeout:
        data = ''
    if data == '':
        logging.info('Could not get the file for %s' % filename)
        return None

    fileobj = StringIO(data)
    # is it a tarfile (let's trust the extension)
    if (filename.split('.')[-2:] == ['tar', 'gz'] or
        filename.split('.')[-1] == 'tgz'):
        # Python 2.4's tarfile should be too buggy
        # to extract setup.py
        try:
            tar = tarfile.TarFile.open(filename, fileobj=fileobj, mode='r:gz')
        except tarfile.ReadError:
            return None
        first_member = tar.getnames()[0]
        folder = os.path.split(first_member)[0]
        for tarinfo in tar:
            try:
                tar.extract(tarinfo)
            except TypeError:
                pass
        tar.close()
        # let's get into the extracted package
        old = os.getcwd()
        folder = os.path.join(old, folder)
        if 'setup.py' not in os.listdir(folder):
            # we are probably one level too high
            folder = os.path.join(folder, first_member)
        try:
            os.chdir(folder)
        except TypeError:
            return None
        # if the file does not have a setup.py, let's quit
        if 'setup.py' not in os.listdir(folder):
            return None
        try:
            name = subprocess.Popen([sys.executable, 'setup.py', '--name'],
                                    stdout=subprocess.PIPE).communicate()[0]
        finally:
            os.chdir(old)

        logging.info('Found a distutils name : %s' % str(name))
        return name.strip()
    # its an egg (a zip)
    elif os.path.splitext(filename)[-1] == '.egg':
        zip = zipfile.ZipFile(fileobj, 'r')
        try:
            for info in zip.infolist():
                if info.filename != 'EGG-INFO/PKG-INFO':
                    continue
                res = NAME.search(zip.read(info.filename))
                if res is not None and len(res.groups()) == 1:
                    logging.info('Found a distutils name : %s' % str(
                        res.groups()[0]))
                    return res.groups()[0]
        finally:
            zip.close()

    # its something we don't want to deal with
    return None


def _attribute_distid(project, distid):
    try:
        if not project.getDistutilsMainId():
            logging.info('%s owns %s (main id)' % (project.getId(), distid))
            project.setDistutilsMainId(distid)
        else:
            logging.info('%s owns %s (secondary id)' % (
                project.getId(), distid))
            project.setDistutilsSecondaryIds(distid)
        project.reindexObject()
        logging.info('%s owns %s' % (project.getId(), distid))
    except Unauthorized:
        logging.info('%s is already owned, cannot give it to %s' % \
                       (project.getId(), distid))

tiny_cache = {}


def _pypi_certified_owner(distid):
    if distid in tiny_cache:
        return tiny_cache[distid]
    logging.info('asking PyPI for contact for %s' % distid)
    pypi = xmlrpclib.ServerProxy('http://python.org/pypi')
    versions = pypi.package_releases(distid)
    if versions == []:
        return None, None
    version = versions[-1]
    data = pypi.release_data(distid, version)
    maintainer = data['maintainer_email']
    author = data['author_email']
    return maintainer, author


def pypi_synchro(distutils_ids):
    """for each id, we want to check a few infos
    one PyPI to try to match the package"""
    # let's check on PyPI for the given id, who is the email contact
    for distid, projects in distutils_ids.items():
        pypi_owners = _pypi_certified_owner(distid)
        if pypi_owners is (None, None):
            # there are no such package at PypI.
            # we can use that id here
            # we give it to the first one
            #
            # XXX what happens if someone else
            # registers at PyPI later ?
            # we get out of sync, but this is quite
            # unavoidable: PSC doesn't act as a pypi mirror
            p = projects[0]
            _attribute_distid(p, distid)
            for p2 in projects[1:]:
                logging.warning('%s conflicts with %s' % \
                                  (p2.getId(), p.getId()))
        # (author_email, id) is unique at PyPI
        for i, project in enumerate(projects):
            author_email = project.getContactAddress()
            if author_email.startswith('mailto:'):
                # get ridd of that crappy header
                author_email = author_email[len('mailto:'):]
            if author_email in pypi_owners:
                # found !
                _attribute_distid(project, distid)
                for p in projects[i + 1:]:
                    logging.warning('%s conflicts with %s' % \
                            (p2.getId(), project.getId()))
                break

# XXX I'm not really sure what is going on here (above ^^^), does all this
# get run every time the profile is imported?


# Rip off SteveM's PHC catalog index import stuff
def install(self):
    out = StringIO()

    # Add catalog metadata columns and indexes
    catalog = getToolByName(self, 'portal_catalog')
    addCatalogIndex(self, out, catalog, 'getCategories', 'KeywordIndex')
    addCatalogMetadata(self, out, catalog, 'getCategories')
    addCatalogIndex(self, out, catalog, 'getClassifiers', 'KeywordIndex')
    addCatalogMetadata(self, out, catalog, 'getClassifiers')
    addCatalogIndex(self, out, catalog, 'getCategoryTitles', 'KeywordIndex')
    addCatalogMetadata(self, out, catalog, 'getCategoryTitles')
    addCatalogIndex(self, out, catalog, 'getCompatibility', 'KeywordIndex')
    addCatalogMetadata(self, out, catalog, 'getCompatibility')
    addCatalogIndex(self, out, catalog, 'getProposalTypes', 'KeywordIndex')
    addCatalogMetadata(self, out, catalog, 'getProposalTypes')
    addCatalogIndex(self, out, catalog, 'getProposer', 'KeywordIndex')
    addCatalogMetadata(self, out, catalog, 'getProposer')
    addCatalogIndex(self, out, catalog, 'getRelatedReleases', 'KeywordIndex')
    addCatalogMetadata(self, out, catalog, 'getRelatedReleases')
    addCatalogIndex(self, out, catalog, 'getSeconder', 'KeywordIndex')
    addCatalogMetadata(self, out, catalog, 'getSeconder')
    addCatalogIndex(self, out, catalog, 'getSelfCertifiedCriteria',
        'KeywordIndex')
    addCatalogMetadata(self, out, catalog, 'getSelfCertifiedCriteria')
    addCatalogIndex(self, out, catalog, 'releaseCount', 'FieldIndex')
    addCatalogMetadata(self, out, catalog, 'releaseCount')
    addCatalogIndex(self, out, catalog, 'getDistutilsMainId', 'KeywordIndex')
    addCatalogMetadata(self, out, catalog, 'getDistutilsMainId')
    addCatalogIndex(self, out, catalog, 'getDistutilsSecondaryIds',
        'KeywordIndex')
    addCatalogMetadata(self, out, catalog, 'getDistutilsSecondaryIds')
    addCatalogIndex(self, out, catalog, 'getDownloadCount', 'FieldIndex')
    addCatalogIndex(self, out, catalog, 'getLatestReleaseDate', 'DateIndex')
    addCatalogMetadata(self, out, catalog, 'getLatestReleaseDate')
    print >> out, "Added PSC items to catalog indexes and metadata"
    setupCioppinoTwoThumbs(self, out)


def addCatalogIndex(self, out, catalog, index, type, extra=None):
    """Add the given index name, of the given type, to the catalog."""

    if index not in catalog.indexes():
        catalog.addIndex(index, type, extra)
        print >> out, "Added index", index, "to catalog"
    else:
        print >> out, "Index", index, "already in catalog"


def addCatalogMetadata(self, out, catalog, column):
    """Add the given column to the catalog's metadata schema"""

    if column not in catalog.schema():
        catalog.addColumn(column)
        print >> out, "Added", column, "to catalog metadata"
    else:
        print >> out, column, "already in catalog metadata"


def setupCioppinoTwoThumbs(self, out):
    """
    Install the twothumbs product and reindex its indexes
    """
    # I am getting weird errors putting this in metadata.xml
    # I think it has something to do with custome profile stuff
    # in extensions/install.py
    qi = getToolByName(self, 'portal_quickinstaller')
    if not qi.isProductInstalled('cioppino.twothumbs'):
        qi.installProduct('cioppino.twothumbs',)
        print >> out, "Installed cioppino.twothumbs"


def importVarious(context):
    """
    Final plonesoftwarecenter import steps.
    """

    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('plonesoftwarecenter-various.txt') is None:
        return

    site = context.getSite()
    print install(site)

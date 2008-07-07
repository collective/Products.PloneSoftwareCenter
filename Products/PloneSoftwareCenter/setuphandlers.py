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

from StringIO import StringIO

from Products.CMFCore.utils import getToolByName

NAME = re.compile('Name: (.*)')

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


def before_1_5(portal_setup):
    """runs a migration on a previous version of PSC
    
    before the product switched to migration.xml
    """
    def _upgrade_psc(psc):
        logging.info('Upgrading %s' % psc.title_or_id())
        # we might want to do something else here

    def _discovering_dist_ids(project):
        # for each file in the project we 
        # extract the distutils name
        project_path = '/'.join(project.getPhysicalPath())
        files = cat(**{'portal_type': 'PSCFile',
                       'path': project_path})
        ids = []
        for file_ in files:
            file_ = file_.getObject()
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
            logging.info('Working on %s' % project.getId())

            # trying to find distutils ids
            ids = _discovering_dist_ids(project)
        
            for id_ in ids:
                old = distutils_ids.get(id_, ())
                if project in old:
                    continue
                distutils_ids[id_] = old + (project,) 
        
        # synchronize with the Cheeseshop
        pypi_synchro(distutils_ids)

@temp
def extract_distutils_id(egg_or_tarball):
    """gives the disutils id"""
    file_ = egg_or_tarball.getDownloadableFile()
    filename = egg_or_tarball.getId()
    data = file_.get_data()
    if data == '':
        return None

    fileobj = StringIO(data)
    # is it a tarfile (let's trust the extension)
    if filename.split('.')[-2:] == ['tar', 'gz']:
        # Python 2.4's tarfile should be too buggy
        # to extract setup.py
        tar = tarfile.TarFile.open(filename, fileobj=fileobj, mode='r:gz')
        first_member = tar.getnames()[0]
        folder = os.path.split(first_member)[0]
        for tarinfo in tar:
            tar.extract(tarinfo)
        tar.close()
        # let's get into the extracted package
        old = os.getcwd()
        os.chdir(folder)
        try:
            name = subprocess.Popen([sys.executable, 'setup.py', '--name'], 
                                    stdout=subprocess.PIPE).communicate()[0]
        finally:
            os.chdir(old)
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
                    return res.groups()[0]
        finally:       
            zip.close()

    # its something we don't want to deal with
    return None

def _attribute_distid(project, distid):
    if not project.getDistutilsMainId():
        project.setDistutilsMainId(distid)
    else:
        project.setDistutilsSecondaryIds(distid)
    project.reindexObject()
    logging.info('%s owns %s' % (project.getId(), distid))

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
    maintainer = pypi.release_data(distid, version)['maintainer_email']
    author = pypi.release_data(distid, version)['author_email']
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
            logging.info('%s owns %s' % (p.getId(), distid))
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
                for p in projects[i+1:]:
                    logging.warning('%s conflicts with %s' % \
                            (p2.getId(), project.getId()))
                break


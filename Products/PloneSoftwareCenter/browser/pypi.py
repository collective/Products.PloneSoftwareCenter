"""
$Id: PyPI.py 18612 2006-01-28 14:46:00Z dreamcatcher $
"""
import re
import hashlib

from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from AccessControl.SpecialUsers import nobody
import transaction

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import SimpleItemWithProperties, UniqueObject
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five import BrowserView
from Products.Archetypes.event import ObjectEditedEvent

from Products.PloneSoftwareCenter.utils import VersionPredicate
from Products.PloneSoftwareCenter.utils import which_platform
from Products.PloneSoftwareCenter.utils import is_distutils_file
from Products.PloneSoftwareCenter.utils import get_projects_by_distutils_ids

from plone.i18n.normalizer.interfaces import IFileNameNormalizer

from zope.annotation.interfaces import IAnnotations
from zope.component import queryUtility
from zope.event import notify

safe_filenames = re.compile(r'.+?\.(exe|tar\.gz|bz2|egg|rpm|deb|zip|tgz)$', re.I)

PROJECT_MAP = {
    #'title': 'name',
    'description': 'summary',
    'text': 'description',
    'classifiers': 'classifiers',
    'contactAddress': 'author_email',
    'homepage': 'home_page',
    }

RELEASE_MAP = {
    'license': 'license',
    # 'maturity': 'classifiers',
    'description': 'release_summary', # Not yet
    'text': 'release_description', # Not yet
    'changelog': 'changelog', # Not yet
    }

RELEASE_LINK_MAP = {
    'platform': 'platform',
    'externalURL': 'download_url',
    }

devVersion = re.compile("([0-9]+(-)?dev)|(-[Rr]([0-9]+)$)")

def isDevelopmentVersion(version):
    return bool(devVersion.search(version))

class PyPIView(BrowserView):
    """view that implements the PyPI API
    """
    def _get_portal_workflow(self):
        return getToolByName(self.context, 'portal_workflow', None)

    def _maybe_submit(self, project):
        wf = self._get_portal_workflow()
        if wf is None:
            return
        state = wf.getInfoFor(project, 'review_state', None)
        if state == 'unapproved':
            try:
                wf.doActionFor(project, 'submit')
            except WorkflowException:
                pass
        state = wf.getInfoFor(project, 'review_state', None)
        if state == 'pending':
            try:
                wf.doActionFor(project, 'publish')
            except WorkflowException:
                pass

    def _maybe_release(self, project, release):
        """Publishing the release, only of the project is published."""
        if not self._is_published(project):
            return
        wf = self._get_portal_workflow()
        if wf is None:
            return
        state = wf.getInfoFor(release, 'review_state', None)
        if state in ('pre-release',):
            try:
                if isDevelopmentVersion(self.data['version']):
                    wf.doActionFor(release, 'release-alpha')
                elif bool(re.compile("([0-9]+(-)?a([0-9]*))").search(self.data['version'])):
                    wf.doActionFor(release, 'release-alpha')
                elif bool(re.compile("([0-9]+(-)?b([0-9]*))").search(self.data['version'])):
                    wf.doActionFor(release, 'release-beta')
                elif bool(re.compile("([0-9]+(-)?rc([0-9]*))").search(self.data['version'])):
                    wf.doActionFor(release, 'release-candidate')
                else:
                    wf.doActionFor(release, 'release-final')
            except WorkflowException:
                pass

    def _validate_metadata(self, data):
        """ Validate the contents of the metadata.
        """
        for field in ('name', 'version'):
            if not data.has_key(field):
                raise ValueError, 'Missing required field "%s"' % field
        if data.has_key('metadata_version'):
            del data['metadata_version']

        # make sure relationships are lists
        for name in ('requires', 'provides', 'obsoletes'):
            if data.has_key(name) and not isinstance(data[name], list):
                data[name] = [data[name]]

        # make sure classifiers is a list
        if data.has_key('classifiers'):
            classifiers = data['classifiers']
            if not isinstance(classifiers, list):
                classifiers = [classifiers]
            data['classifiers'] = classifiers

        # check requires and obsoletes
        def validate_version_predicates(col, sequence):
            try:
                map(VersionPredicate, sequence)
            except ValueError, message:
                raise ValueError, 'Bad "%s" syntax: %s' % (col, message)
        for col in ('requires', 'obsoletes'):
            if data.has_key(col) and data[col]:
                validate_version_predicates(col, data[col])

        # check provides
        if data.has_key('provides') and data['provides']:
            try:
                map(versionpredicate.check_provision, data['provides'])
            except ValueError, message:
                raise ValueError, 'Bad "provides" syntax: %s' % message

        # check classifiers (filter them out)
        cats = [cols.split('|')[-1] for cols in self._get_classifiers()]
        filter_ = lambda key: key in cats

        if data.has_key('classifiers'):
            data['classifiers'] = filter(filter_, data['classifiers'])

    def _is_published(self, project):
        """returns true if not publised"""
        wf = self._get_portal_workflow()
        if wf is not None:
            state = wf.getInfoFor(project, 'review_state', None)
            return state not in ('unapproved', 'pending')
        return False

    def _store_package(self, name, version, data):
        msg = []
        user = getSecurityManager().getUser()
        sc = self.context
        normalized_name = self.normalizeName(name)

        # getting project and release packages.
        try:
            project, release = self._get_package(normalized_name,
                                                 name, version, msg)
        except Unauthorized, e:
            return self.fail(str(e), 401)

        # Now, edit info
        self._edit_project(project, distutils_name=name, data=data,
                           msg=msg)

        # Submit project if not submitted yet.
        self._maybe_submit(project)

        release_data = {}
        for k, v in RELEASE_MAP.items():
            value = data.get(v)
            if not value:
                continue
            if v in ('author_email',) and not value.startswith('mailto:'):
                value = 'mailto:%s' % value
            release_data[k] = value

        if not user.allowed(release.update):
            return self.fail('Unauthorized', 401)

        msg.append('Updated Release: %s' % version)
        release.update(**release_data)


        # Now, check if there's a 'download_url', then create a file
        # link
        url = data.get('download_url')
        if not url in ('', 'UNKNOWN', None):
            rl_data = {}
            for k, v in RELEASE_LINK_MAP.items():
                value = data.get(v)
                if not value:
                    continue
                rl_data[k] = value
            # we don't have a file title for links, so let's use the url
            rl_data['title'] = url

            rl = release._getOb('download', None)
            if rl is None:
                msg.append('Created Download Link')
                try:
                    release.invokeFactory('PSCFileLink', id='download')
                except Unauthorized:
                    return self.fail('Unauthorized', 401)
                rl = release._getOb('download')

            if not user.allowed(rl.update):
                return self.fail('Unauthorized', 401)

            msg.append('Updated Download Link')
            rl.update(**rl_data)
            self._setPlatform(rl, url)

            # notify we did add a file
            notify(ObjectEditedEvent(rl))

        # Make a release if not released yet.
        self._maybe_release(project, release)

        return '\n'.join(msg)

    def _edit_project(self, project, distutils_name=None,
                      data=None, msg=None):
        """edit project infos"""
        user = getSecurityManager().getUser()
        if not user.allowed(project.update):
            return self.fail('Unauthorized', 401)

        if data is None:
            data = self.data
        project_data = {}
        for k, v in PROJECT_MAP.items():
            value = data.get(v)
            if not value:
                continue
            # XXX finding the classifier id
            if k == 'classifiers':
                classifiers = self.context.getField('availableClassifiers')
                value = [classifiers.getRow(self.context, val, 2)
                         for val in value]
                value = [val['id'] for val in value if val is not None]

            if v == 'author_email':
                value  = 'mailto:%s' % value

            project_data[k] = value

        priority = None
        # setting up the distutils name
        # XXX this could be put in the update() call
        if distutils_name is not None:
            if project.getDistutilsMainId() == '':
                project.setDistutilsMainId(distutils_name)
                priority = 'm'
            elif not (distutils_name == project.getDistutilsMainId()):
                secondary_ids = project.getDistutilsSecondaryIds()
                if distutils_name not in secondary_ids:
                    secondary_ids = secondary_ids + (distutils_name,)
                    project.setDistutilsSecondaryIds(secondary_ids)
            else:
                priority='m'

            # setting the title in case it is empty
            if project.Title() == '':
                project_data['title'] = distutils_name

        if priority == 'm':
            project.update(**project_data)

        if msg is not None:
            msg.append('Updated Project: %s' % project.title_or_id())

        # XXX see how to pass this to update()
        # making description a x-rst
        description = data.get('description')
        if priority == 'm' and description is not None:
            project.setText(description,
                            mimetype='text/x-rst')

    def _get_package(self, normalized_name, name, version, msg=None):
        sc = self.context
        existing_projects = list(get_projects_by_distutils_ids(sc, [name]))

        if existing_projects == []:
            # checking if the project already exists
            if normalized_name in sc.objectIds():
                project = sc[normalized_name]
                existing_projects = [normalized_name]
                # empty distutils id ? let's take it !
                if project.getDistutilsMainId() == '':
                    project.setDistutilsMainId(normalized_name)
                else:
                    # main id is taken, let's add it
                    # as a secondary id
                    secondids = project.getDistutilsSecondaryIds()
                    secondids = secondids + (normalized_name,)
                    project.setDistutilsSecondaryIds(secondids)

        if existing_projects == []:
            # let's create the project
            if msg is not None:
                msg.append('Created Project: %s' % name)
            sc.invokeFactory('PSCProject', normalized_name)
            project = sc._getOb(normalized_name)
            project.setTitle(name)
            project.setDistutilsMainId(name)
        else:
            project_id = existing_projects[0]
            project = sc[project_id]

        self._edit_project(project, msg=msg, distutils_name=name)
        versions = project.getVersionsVocab()
        releases = project.getReleaseFolder()
        if releases is None:
            # let's create the release folder
            root_id = cid = 'releases'
            i = 1
            while cid in project.objectIds():
                i += 1
                cid = '%s-%d' (root_id, i)

            releases = project.injectFolder('PSCReleaseFolder',
                                            id=cid)

        is_secondary = name != project.distutilsMainId

        if is_secondary:
            version = '%s-%s' % (normalized_name, version)

        if not version in versions:
            # we need to create it
            releases.invokeFactory('PSCRelease', id=version)
            try:
                IAnnotations(releases[version])['title_hint'] = name
            except TypeError, KeyError:
                pass
            if msg is not None:
                msg.append('Created Release %s in Project %s' % \
                            (version, name))

        release = releases._getOb(version)
        return project, release

    def _get_classifiers(self):
        """returns current classifiers"""
        sc = self.context
        return sc.getField('availableClassifiers').get(sc)

    #
    # public API
    #
    def fail(self, msg, status=400):
        if self.request is None:
            raise ValueError, msg
        # Abort the transaction explicitly, as we won't raise an
        # exception here.
        transaction.abort()
        response = self.request.response
        response.setStatus(status)
        if status == 401:
            # Fake ourselves as PyPI.
            response.setHeader('WWW-Authenticate',
                               'basic realm="%s"' % 'pypi', 1)
        return msg

    def submit(self, data=None):
        """Submit a new Project
        """
        if getSecurityManager().getUser() in (nobody,):
            return self.fail('Unauthorized', 401)

        if data is None:
            data = self.request.form
        self.data = data
        try:
            self.verify(data=data)
        except ValueError, message:
            err = 'Error processing form: %s' % message
            return self.fail(err)

        name = data['name']
        version = data['version']
        return self._store_package(name, version, data)

    def verify(self, data=None):
        """Verify package metadata
        """
        if getSecurityManager().getUser() in (nobody,):
            return self.fail('Unauthorized', 401)

        if data is None:
            data = self.request.form

        try:
            self._validate_metadata(data)
        except ValueError, message:
            err = 'Error processing form: %s' % message
            return self.fail(err)

        return 'OK'

    def file_upload(self, data=None):
        """Upload a new Project File
        """
        user = getSecurityManager().getUser()
        if user in (nobody,):
            return self.fail('Unauthorized', 401)
        if data is None:
            data = self.request.form
        self.data = data

        # figure the package name and version
        name = data.get('name')
        version = data.get('version')
        if not name or not version:
            err = 'Name and version are required'
            return self.fail(err)

        name = data['name']
        version = data['version']
        normalized_name = self.normalizeName(name)

        try:
            project, release = self._get_package(normalized_name,
                                                 name, version)
        except Unauthorized, e:
            return self.fail(str(e), 401)

        # Submit project if not submitted yet.
        self._maybe_submit(project)

        content = data.get('content')
        filetype = data.get('filetype')
        if not content or not filetype:
            err = 'Both content and filetype are required'
            return self.fail(err)

        md5_digest = data.get('md5_digest')
        comment = data.get('comment')

        # check for valid filenames
        filename = content.filename
        if not safe_filenames.match(filename):
            err = 'Invalid distribution file: %s' % filename
            return self.fail(err)

        # check for dodgy filenames
        if '/' in filename or '\\' in filename:
            err = 'Invalid distribution file: %s' % filename
            return self.fail(err)

        # grab content
        # XXX optimize for memory
        content = content.read()

        # nothing over 100M please
        size = len(content)
        if size > 100*1024*1024:
            err = 'Invalid file size: %s' % size
            return self.fail(err)

        # check the file for valid contents based on the type
        if not is_distutils_file(content, filename, filetype):
            err = 'Not a distutils distribution file: %s (%s)' % (
                filename, filetype)
            return self.fail(err)

        # digest content
        if md5_digest:
            m = hashlib.md5()
            m.update(content)
            calc_digest = m.hexdigest()
            if md5_digest != calc_digest:
                err = 'MD5 digest supplied does not match uploaded file'
                return self.fail(err)

        msg = []
        rf = release._getOb(filename, None)
        if rf is None:
            msg.append('Created Release File: %s' % filename)
            try:
                release.invokeFactory('PSCFile', id=filename)

            except Unauthorized:
                return self.fail('Unauthorized', 401)
            rf = release._getOb(filename)

        if not user.allowed(rf.setDownloadableFile):
            return self.fail('Unauthorized', 401)

        msg.append('Updated Release File: %s' % filename)
        rf.setDownloadableFile(content, filename=filename)
        rf.setTitle(filename)
        self._setPlatform(rf, filename)
        # notify
        notify(ObjectEditedEvent(rf))

        # Make a release if not released yet.
        self._maybe_release(project, release)


        return '\n'.join(msg)

    def _setPlatform(self, release_file, filename):
        platforms = release_file.getPlatformVocab()
        founded = which_platform(filename)
        if founded in platforms:
            release_file.setPlatform(founded)
        return release_file.setPlatform(platforms[0])

    def list_classifiers(self):
        """returns classifiers titles"""
        field = self.context.getField('availableClassifiers')
        return '\n'.join(field.getColumn(field, 2))

    def normalizeName(self, text):
        """ Generate an id that
            1) is url-valid
            2) is lowercase
            3) ignores "products." in a Products.* namespace
        """
        # Remove Products, as applicable
        if text.startswith('Products.'):
            text = text[9:]

        # Convert to lowercase
        text = text.lower()

        return queryUtility(IFileNameNormalizer).normalize(text)

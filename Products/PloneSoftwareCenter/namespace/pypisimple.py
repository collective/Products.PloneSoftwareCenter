"""
 View that provides the package index API
 for easy_install.

$Id$
"""
import itertools
import os

from zope.interface import implements

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from Products.PloneSoftwareCenter.utils import get_projects_by_distutils_ids

from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.browser import IPublishTraverse
from zope.traversing.namespace import SimpleHandler
from zope.traversing.interfaces import TraversalError
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

class PyPISimpleTraverser(SimpleHandler):
    """ Custom traverser for the Simple Index
    """
    implements(IBrowserView, IPublishTraverse)

    def __init__(self, context, request):
        self.context = context
        self.request = request
	
    def __of__(self, context):
        return self

    def publishTraverse(self, request, name):
        """publish a project"""
        return PyPIProjectView(self.context, request, name)
        
    def traverse(self, name, ignored):
        if name == '':
            return PyPISimpleTraverser(self.context, self.request)

        path = name.split('/')
        if len(path) == 1:
            return PyPIProjectView(self.context, self.request, path[0])
        raise TraversalError(self.context, name)

    def __call__(self):
        return PyPISimpleView(self.context, self.request)()

SIMPLE = os.path.join(os.path.dirname(__file__), 'pypisimple.pt')
PROJECT = os.path.join(os.path.dirname(__file__), 'pypiproject.pt')
    
class PyPISimpleView(object):
    """view used for the main package index page"""
    implements(IBrowserPublisher)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.sc = self.context
        self.catalog = getToolByName(self.context, 'portal_catalog')
        self.sc_path = '/'.join(self.sc.getPhysicalPath())
        self.index_root = '%s/++simple++' % self.sc.absolute_url()

    def browserDefault(self, request):
        return self, ()

    def __of__(self, context):
        return self

    def __call__(self):
        template = ViewPageTemplateFile(SIMPLE)
        return template(self)

    def get_url_and_distutils_ids(self, project):
        """returns url and title"""

        yield {'distutilsMainId': project.distutilsMainId,
               'url': '%s/%s' % (self.index_root,
                                 project['distutilsMainId'])}

    def get_projects(self):
        """provides the simple view over the projects
        with links to the published files"""
        
        query = {'path': self.sc_path, 
                 'portal_type': 'PSCProject',
                 'review_state': 'published', 
                 'sortOn': 'getId'}

        def _filter_id(brain):
            element = brain.getObject()
            if element.distutilsMainId == '':
                return None
            return element

        projects = (_filter_id(brain) for brain 
                    in self.catalog(**query))

        return itertools.chain(*[self.get_url_and_distutils_ids(p)
                                 for p in projects if p is not None])

class PyPIProjectView(PyPISimpleView):

    def __init__(self, context, request, name):
        PyPISimpleView.__init__(self,  context, request)
        self.context = context
        self.request = request
        self.project_name = name
        self.projects = self._get_projects(name) 
        if self.projects == []:
            raise TraversalError(self.context, name)

    def _sort_files(self, f1, f2):
        return cmp(f1['url'], f2['url'])

    def _get_released_files(self, project):
        project_path = '/'.join(project.getPhysicalPath()) 
        query = {'path': project_path, 'portal_type': 'PSCRelease',
                 'review_state': ('alpha', 'beta', 'pre-release', 'final', 
                                  'hidden')}
        for brain in self.catalog(**query):
            for id_, file_ in brain.getObject().objectItems():
                yield {'url': file_.absolute_url(), 
                       'title': id_}

    def _get_projects(self, name):
        return get_projects_by_distutils_ids(self.context, [name])
       
    def __call__(self): 
        template = ViewPageTemplateFile(PROJECT)
        return template(self) 

    def get_name(self):
        return self.project_name

    def get_links(self):
        # let's browse the projects to get the releases
        # and the homepages
        links = []
        for project_name in self.projects:
            project = self.context[project_name]
            
            # archives first
            for archive in sorted(self._get_released_files(project),
                                  self._sort_files):
                links.append(archive)           
            
            # then url links 
            fields = ('homepage', 'repository')
            for field in fields:
                value = getattr(project, field, u'')
                title = '%s %s' % (project_name, field)
                if value != u'':
                    links.append({'url': value, 'title': title,
                                  'rel': field})
            
        return links


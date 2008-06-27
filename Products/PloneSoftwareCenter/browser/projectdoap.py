from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.PloneSoftwareCenter.interfaces import ISoftwareCenterContent
from Acquisition import aq_inner, aq_parent, aq_self
from DateTime import DateTime

from project import ProjectView

from xml.dom import *

class ProjectDOAPView(ProjectView):
    
    def categories_url(self):
        """Get a list of categories url in a list, to be used for displaying the
        categories
        """
        categories_url = []
        
        keys = [k for k in self.context.getCategories()]
        keys.sort()
        
        for cat in keys: 
            categories_url.append("%s/by-category/%s" % ('/'.join(self.context.absolute_url().split('/')[:-1]), cat))
    
        return categories_url
    
    def naked_description(self):
        """Returns the description in plaintext format
        """
        return self.context.getField('text').get(self.context, mimetype="text/plain")
    
    def get_tracker(self):
        """Returns the tracker url inserted if there is no tracker issue in the
           folder
        """
        query = {}
        query['path'] = {'query' : self.context_path}
        query['portal_type'] = 'PoiPscTracker'
        
        relresult = self.catalog.searchResults(query)
        if relresult:
            result = relresult[0].getURL()
        else:
            result = self.context.getTracker()
        
        return result
    
    def get_subcontent(self, field, portal_type):
        """Gets the subcontent contained in the field by parsing the catalog,
           getting the portal_type subcontent and drafting the array
        """
        query = {}
        query['path'] = {'query' : self.context_path}
        query['portal_type'] = portal_type
        
        relresult = self.catalog.searchResults(query)
        rawresult = []
        for item in relresult:
            itemObj = item.getObject()
            rawresult.append(itemObj.getField(field).get(itemObj))
        
        filteredresult = []
        for rawitem in rawresult:
            if rawitem not in filteredresult:
                filteredresult.append(rawitem)
        
        return filteredresult
    
    def all_licenses(self):
        """Returns all the licenses we have in all the releases, we parse the
        folder, get the licenses, and so on
        """
        parent = self.context.aq_inner.aq_parent.aq_self
        # TODO: maybe use adapters here?
        result = []
        if ISoftwareCenterContent.providedBy(parent):
            available = parent.getField('availableLicenses').getAsGrid(parent)
            
            filteredresult = self.get_subcontent('license', 'PSCRelease')
            
            for item in filteredresult:
                for available_item in available:
                    if item == available_item[0]:
                        result.append(available_item[2])
        else:
            result = False
                
        return result
    
    def get_oses(self):
        """Returns all the oses we have in all the releases, we parse the
        folders, get the oses, and so on
        """
        available = self.context.getAvailablePlatforms()
        result = []
        
        filteredresult = self.get_subcontent('platform', ['PSCFile', 'PSCFileLink'])
        for item in filteredresult:
            if item in available:
                result.append(item)
            if item == available[0]:
                result = []
                break
        
        return result
    
    def get_releases(self):
        """Returns all the releases in the form of a dict, making it easy for
        the template to get it
        """
        query = {}
        query['path'] = {'query' : self.context_path}
        query['portal_type'] = 'PSCRelease'
        
        result = []
        relresult = self.catalog.searchResults(query)
        for release in relresult:
            thisRelease = {}
            releaseObj = release.getObject()
            releasePath = releaseObj.getPhysicalPath()
            releasePath = '/'.join(releasePath)
            thisRelease['revision'] = releaseObj.getId()
            thisRelease['name'] = releaseObj.getCodename()
            releaseDate = releaseObj.getExpectedReleaseDate()
            if releaseDate:
                # removed the conversion: releaseDate is already a DateTime
                # and depending on your location.
                #
                # For instance this code:
                #   >>> DateTime(DateTime('1/12/2007'))
                #
                # will lead to a date that is at 1/11/2007 23:00
                #
                # releaseDate = DateTime(releaseDate)
                thisRelease['date'] = '%s-%s-%s' % (releaseDate.year(), releaseDate.mm(), releaseDate.dd())
            else:
                thisRelease['date'] = ''
            
            thisRelease['files'] = []
            query = {}
            query['path'] = {'query' : releasePath}
            query['portal_type'] = ['PSCFile']
            fileresults = self.catalog.searchResults(query)
            for fileresult in fileresults:
                thisRelease['files'].append(fileresult.getObject().absolute_url())
            
            query = {}
            query['path'] = {'query' : releasePath}
            query['portal_type'] = ['PSCFileLink']
            fileresults = self.catalog.searchResults(query)
            for fileresult in fileresults:
                thisRelease['files'].append(fileresult.getObject().getExternalURL())
            
            result.append(thisRelease)
        
        return result
            
class ProjectDOAPDocument(ProjectDOAPView):
    
    def __call__(self):
        implementation = getDOMImplementation()
        rdf = implementation.createDocument('http://usefulinc.com/ns/doap#','rdf:RDF',None)
        rdf.documentElement.setAttribute('xmlns','http://usefulinc.com/ns/doap#')
        rdf.documentElement.setAttribute('xmlns:rdf','http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        rdf.documentElement.setAttribute('xmlns:foaf','http://xmlns.com/foaf/0.1/')
        
        project = rdf.createElement('Project')
        project.setAttribute('rdf:about', self.context.getHomepage())
        
        name = rdf.createElement('name')
        name.appendChild(rdf.createTextNode(self.context.title_or_id()))
        project.appendChild(name)
        
        homepage = rdf.createElement('homepage')
        homepage.setAttribute('rdf:resource',self.context.getHomepage())
        project.appendChild(homepage)
        
        shortdesc = rdf.createElement('shortdesc')
        shortdesc.appendChild(rdf.createTextNode(self.context.Description()))
        project.appendChild(shortdesc)
        
        description = rdf.createElement('description')
        description.appendChild(rdf.createTextNode(self.naked_description()))
        project.appendChild(description)
        
        for categoryURL in self.categories_url():
            category = rdf.createElement('category')
            category.setAttribute('rdf:resource', str(categoryURL))
            project.appendChild(category)
        
        if self.has_documentation_link():
            wiki = rdf.createElement('wiki')
            wiki.setAttribute('rdf:resource', str(self.documentation_url()))
            project.appendChild(wiki)
        
        if self.get_tracker():
            tracker = rdf.createElement('bug-database')
            tracker.setAttribute('rdf:resource', str(self.get_tracker()))
            project.appendChild(tracker)
        
        if self.context.getScreenshot():
            screenshots = rdf.createElement('screenshots')
            screenshots.setAttribute('rdf:resource', '/'.join([self.context_path,'screenshot','image_view_fullscreen']))
            project.appendChild(screenshots)
        
        if self.context.getMailingList():
            mailingList = rdf.createElement('mailing-list')
            mailingList.setAttribute('rdf:resource', str(self.context.getMailingList()))
            project.appendChild(mailingList)
        
        for operatingSystem in self.get_oses():
            os = rdf.createElement('os')
            os.appendChild(rdf.createTextNode(operatingSystem))
            project.appendChild(os)
        
        for licenseURL in self.all_licenses():
            license = rdf.createElement('license')
            license.setAttribute('rdf:resource', str(licenseURL))
            project.appendChild(license)
        
        if self.release_folder_url():
            downloadPage = rdf.createElement('download-page')
            downloadPage.setAttribute('rdf:resource', str(self.release_folder_url()))
            project.appendChild(downloadPage)
        
        # TODO: Does not add repo for now, we will check this later with an extension
        #if self.context.getRepository():
        #    repository = rdf.createElement('Repository')
        #    location = rdf.createElement('location')
        #    location.setAttribute('rdf:resource',str(self.context.getRepository()))
        #    repository.appendChild(location)
        #    project.appendChild(repository)
        
        for release in self.get_releases():
            version = rdf.createElement('Version')
            if release['name']:
                name = rdf.createElement('name')
                name.appendChild(rdf.createTextNode(release['name']))
                version.appendChild(name)
            if release['revision']:
                revision = rdf.createElement('revision')
                revision.appendChild(rdf.createTextNode(release['revision']))
                version.appendChild(revision)
            if release['date']:
                created = rdf.createElement('created')
                created.appendChild(rdf.createTextNode(release['date']))
                version.appendChild(created)
            for releaseFile in release['files']:
                fileRelease = rdf.createElement('file-release')
                fileRelease.setAttribute('rdf:resource', releaseFile)
                version.appendChild(fileRelease)
            
            project.appendChild(version)
        
        rdf.documentElement.appendChild(project)
        
        self.context.REQUEST.response.setHeader('Content-Type', 'application/rdf+xml')
        return rdf.toprettyxml()

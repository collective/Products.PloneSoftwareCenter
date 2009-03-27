from base import PSCTestCase

from AccessControl.Permission import Permission
from AccessControl import Unauthorized

from Products.CMFCore.utils import getToolByName

from Products.PloneSoftwareCenter.permissions import AddSoftwareCenter
from Products.PloneSoftwareCenter.browser.pypi import PyPIView

def allowMembersToAddCenter(obj):
    perms = [p for p in obj.ac_inherited_permissions(1) if p[0] == AddSoftwareCenter]
    p = perms[0]
    name, value = perms[0][:2]
    p = Permission(name, value, obj)
    roles = p.getRoles()
    if 'Member' not in roles:
        if type(roles) == type(()):
            roles = list(roles)
            roles.append('Member')
            roles = tuple(roles)
        else:
            roles.append('Member')
    p.setRoles(roles)

class Resp:
    def setStatus(self, status):
        pass
    def setHeader(self, header, value, ext):
        if header.lower() == 'www-authenticate':
            raise Unauthorized()

class Req:
    def __init__(self, form):
        self.form = form
        self.response = Resp()


class TestPyPI(PSCTestCase):

    def afterSetUp(self):
        # Actual changes to portal
        allowMembersToAddCenter(self.portal)
        membership = getToolByName(self.portal, 'portal_membership')
        membership.addMember('user1', 'secret', ['Member'], [])
        membership.addMember('user2', 'secret', ['Member'], [])
        
    def testSubmit(self):
        self.login('user1')
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        psc = self.portal.psc

        # a user can submit a package
        # that creates a project and a release folder, to hold
        # release infos.
        # no links or file links are created
        # until the project is published by the PSC owner
        self.login('user2')
        form = {'': 'submit', 'license': 'GPL', 'name': 'iw.dist', 
                'metadata_version': '1.0', 'author': 'Ingeniweb', 
                'home_page': 'UNKNOWN', 'download_url': 'UNKNOWN', 
                'summary': 'xxx', 'author_email': 'support@ingeniweb.com',
                'version': '0.1.0dev-r6983', 'platform': 'UNKNOWN',
                'keywords': '', 
                'classifiers': ['Programming Language :: Python',
                                'Topic :: Utilities', 'Rated :: PG13'], 
                'description': 'xxx'}
        view = PyPIView(psc, Req(form))
        view.submit()
        # check what has been created
        iw_dist = psc['iw.dist']
        rel = iw_dist.releases['0.1.0dev-r6983']
        # we don't want any file or file link
        self.assertEquals(rel.objectIds(), [])

        view.submit()
        # check what has been created
        iw_dist = psc['iw.dist']
        rel = iw_dist.releases['0.1.0dev-r6983']
        # we don't want any file or file link 
        self.assertEquals(rel.objectIds(), [])

        # now let's provide an url
        form['download_url'] = 'the_url'
        form['platform'] = 'win32'
        view = PyPIView(psc, Req(form))  
        view.submit()
        self.assertEquals(rel.objectIds(), ['download'])
        
        # now let the user 1 publish the project
        self.login('user1')
        wf = self.portal.portal_workflow
        wf.doActionFor(iw_dist, 'publish')

    def test_edit_project(self):
        self.login('user1')
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        psc = self.portal.psc

        # making sure the project is correctly set
        self.login('user2')
        form = {'': 'submit', 'license': 'GPL', 'name': 'iw.dist', 
                'metadata_version': '1.0', 'author': 'Ingeniweb', 
                'home_page': 'UNKNOWN', 'download_url': 'UNKNOWN', 
                'summary': 'The summary', 
                'author_email': 'support@ingeniweb.com',
                'version': '0.1.0dev-r6983', 'platform': 'UNKNOWN',
                'keywords': '', 
                'classifiers': ['Programming Language :: Python',
                                'Topic :: Utilities', 'Rated :: PG13'], 
                'description': 'xxx'}
        view = PyPIView(psc, Req(form))

        view.submit()
        iw_dist = psc['iw.dist']
        self.assertEquals(iw_dist.getText(),  '<p>xxx</p>\n')

        form = {'': 'submit', 'license': 'GPL', 'name': 'iw.dist', 
                'metadata_version': '1.0', 'author': 'Ingeniweb',
                'version': '0.1.0dev-r6983'} 
       
        view = PyPIView(psc, Req(form))
        view.submit()
        self.assertEquals(iw_dist.getText(),  '<p>xxx</p>\n')

    def test_unexisting_classifier(self):
        # make sure the server doesn't fail on unexisting
        # classifiers
        self.login('user1')
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        psc = self.portal.psc

        # making sure the project is correctly set
        self.login('user2')
        form = {'': 'submit', 'license': 'GPL', 'name': 'iw.dist', 
                'metadata_version': '1.0', 'author': 'Ingeniweb', 
                'home_page': 'UNKNOWN', 'download_url': 'UNKNOWN', 
                'summary': 'The summary', 
                'author_email': 'support@ingeniweb.com',
                'version': '0.1.0dev-r6983', 'platform': 'UNKNOWN',
                'keywords': '', 
                'classifiers': ['Programming Language :: Python',
                                'Topic :: Utilities', 'Rated :: PG13',
                                'XXXXXXXXXXXXXXXXXXXXXXXXXXXX'], 
                'description': 'xxx'}
        view = PyPIView(psc, Req(form))

        # adding a field
        psc = self.portal.psc
        pg = 'rated-pg13|Rated PG13|Rated :: PG13'
        classifiers = psc.getField('availableClassifiers')
        values = classifiers.get(classifiers) 
        classifiers.set(psc, values + (pg,))  
        
        view.submit()
        iw_dist = psc['iw.dist']
        wanted = ('python', 'utilities', 'rated-pg13') 
        self.assertEquals(iw_dist.getClassifiers(),  wanted)

    def test_list_classifiers(self):
        # everyone can get the classifier list
        self.login('user1')
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        psc = self.portal.psc

        self.login('user2')
        view = PyPIView(psc, Req({})) 
        res = view.list_classifiers()
        res = res.split('\n')
        self.assertEquals(res[0], 'Development Status :: 1 - Planning')
        self.assertEquals(res[-1], 'Topic :: Utilities')

    def test_distutils_id_missing(self):

        # let's create a PSC with a project that 
        # has the same name but no distutils fixed 
        self.login('user1')
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        psc = self.portal.psc
        psc.invokeFactory('PSCProject', 'iw.dist')
        self.assertEquals(['iw.dist'], list(psc.objectIds()))

        # making sure the project is correctly set
        form = {'': 'submit', 'license': 'GPL', 'name': 'iw.dist', 
                'metadata_version': '1.0', 'author': 'Ingeniweb', 
                'home_page': 'UNKNOWN', 'download_url': 'UNKNOWN', 
                'summary': 'The summary', 
                'author_email': 'support@ingeniweb.com',
                'version': '0.1.0dev-r6983', 'platform': 'UNKNOWN',
                'keywords': '', 
                'classifiers': ['Programming Language :: Python',
                                'Topic :: Utilities', 'Rated :: PG13'], 
                'description': 'xxx'}
        view = PyPIView(psc, Req(form))

        view.submit()
        iw_dist = psc['iw.dist']
        self.assertEquals(iw_dist.getDistutilsMainId(),  'iw.dist')

    def test_distutils_id_missing2(self):

        # let's create a PSC with a project that 
        # has the same name but no distutils fixed 
        self.login('user1')
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        psc = self.portal.psc
        psc.invokeFactory('PSCProject', 'iw.dist')
        self.assertEquals(['iw.dist'], list(psc.objectIds()))
        
        psc['iw.dist'].setDistutilsMainId('another.one')

        # making sure the project is correctly set
        form = {'': 'submit', 'license': 'GPL', 'name': 'iw.dist', 
                'metadata_version': '1.0', 'author': 'Ingeniweb', 
                'home_page': 'UNKNOWN', 'download_url': 'UNKNOWN', 
                'summary': 'The summary', 
                'author_email': 'support@ingeniweb.com',
                'version': '0.1.0dev-r6983', 'platform': 'UNKNOWN',
                'keywords': '', 
                'classifiers': ['Programming Language :: Python',
                                'Topic :: Utilities', 'Rated :: PG13'], 
                'description': 'xxx'}
        view = PyPIView(psc, Req(form))

        view.submit()
        iw_dist = psc['iw.dist']
        self.assertEquals(iw_dist.getDistutilsSecondaryIds(),  ('iw.dist',))

    def test_filename_normalization(self):
        """ Make sure product ids are following our conventions. 
            http://plone.org/products/plonesoftwarecenter/issues/81
        """
        
        self.login('user1')
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        psc = self.portal.psc
        
        def createProductWithName(name):
            view = PyPIView(psc, Req({'': 'submit', 'name': name, 'version': '1.0'}))
            view.submit()
        
        # Use dotted product names when creating ids
        createProductWithName('collective.something')
        self.failUnless('collective.something' in psc.objectIds(), 'Product "collective.something" should be created as "collective.something". Existing ids are %s' % [a for a in psc.objectIds()])

        # Use lowercase
        createProductWithName('collective.BargainingAgreement')
        self.failUnless('collective.bargainingagreement' in psc.objectIds(), 'Product "collective.BargainingAgreement" should be created as "collective.bargainingagreement", using lowercase. Existing ids are %s' % [a for a in psc.objectIds()])
        
        # Don't repeat "products" for the Products.* namespace
        createProductWithName('Products.ImageRepository')
        self.failUnless('imagerepository' in  psc.objectIds(), 'Product "Products.ImageRepository" should be created as "imagerepository". Existing ids are %s' % [a for a in psc.objectIds()])

    def test_workflow_by_version(self):
        """ Make sure that release workflow state is being properly set using the upload's version as a guide. """

        self.login('user1')
        self.portal.invokeFactory('PloneSoftwareCenter', 'psc')
        psc = self.portal.psc
        wf = self.portal.portal_workflow

        def createProductWithNameAndVersion(name, version):
            view = PyPIView(psc, Req({'': 'submit', 'name': name, 'version': version}))
            view.submit()
            return psc[name].releases[version]

        rel = createProductWithNameAndVersion('collective.something', '1.0dev')
        self.assertEquals(wf.getInfoFor(rel, 'review_state'), 'alpha')

        rel = createProductWithNameAndVersion('collective.something', '1.0a1')
        self.assertEquals(wf.getInfoFor(rel, 'review_state'), 'alpha')

        rel = createProductWithNameAndVersion('collective.something', '1.0alpha1')
        self.assertEquals(wf.getInfoFor(rel, 'review_state'), 'alpha')
        
        rel = createProductWithNameAndVersion('collective.something', '1.0b1')
        self.assertEquals(wf.getInfoFor(rel, 'review_state'), 'beta')
        
        rel = createProductWithNameAndVersion('collective.something', '1.0beta')
        self.assertEquals(wf.getInfoFor(rel, 'review_state'), 'beta')

        rel = createProductWithNameAndVersion('collective.something', '1.0rc5')
        self.assertEquals(wf.getInfoFor(rel, 'review_state'), 'release-candidate')
        
        rel = createProductWithNameAndVersion('collective.something', '1.0')
        self.assertEquals(wf.getInfoFor(rel, 'review_state'), 'final')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPyPI))
    return suite


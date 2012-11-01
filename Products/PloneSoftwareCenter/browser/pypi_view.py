from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserPage


class PackageIndexView(BrowserPage):
    """
    Display Plone releases from PyPI
    """

    template = ViewPageTemplateFile('pypi_view.pt')

    def __call__(self):
        return self.template()

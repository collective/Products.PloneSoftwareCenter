"""utils to fetch download counts from PyPI"""

import logging
import transaction
import xmlrpclib

from Products.CMFCore.utils import getToolByName
from collections import deque, defaultdict

client = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')
logger = logging.getLogger('Products.PloneSoftwareCenter')


def by_two(source):
    out = []
    for x in source:
        out.append(x)
        if len(out) == 2:
            yield out
            out = []


def package_releases(packages):
    mcall = xmlrpclib.MultiCall(client)
    called_packages = deque()
    for package in packages:
        mcall.package_releases(package, True)
        called_packages.append(package)
        if len(called_packages) == 100:
            result = mcall()
            mcall = xmlrpclib.MultiCall(client)
            for releases in result:
                yield called_packages.popleft(), releases
    result = mcall()
    for releases in result:
        yield called_packages.popleft(), releases


def release_data(packages):
    mcall = xmlrpclib.MultiCall(client)
    i = 0
    for package, releases in package_releases(packages):
        for version in releases:
            mcall.release_urls(package, version)
            mcall.release_data(package, version)
            i += 1
            if i % 50 == 49:
                result = mcall()
                mcall = xmlrpclib.MultiCall(client)
                for urls, data in by_two(result):
                    yield urls, data
    result = mcall()
    for urls, data in by_two(result):
        yield urls, data


def update_package_download_counts(context):
    logger.info('Updating download counts from PyPI')

    app = context.getPhysicalRoot()
    catalog = getToolByName(context, 'portal_catalog')
    package_ids = catalog.uniqueValuesFor('getDistutilsMainId')
    counts = defaultdict(lambda: 0)
    for urls, data in release_data(package_ids):
        downloads = 0
        for url in urls:
            downloads += url['downloads']
        counts[data.get('name')] += downloads

    for package_id, downloads in counts.items():
        brain = catalog.unrestrictedSearchResults(
            getDistutilsMainId=package_id)[0]
        package = app.unrestrictedTraverse(brain.getPath())
        if package.getDownloadCount() != -1:
            package.setDownloadCount(downloads)
        transaction.commit()

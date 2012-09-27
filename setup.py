import os
from setuptools import setup, find_packages

version = '1.6.4'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__),
        *rnames)).read() + '\n\n'

long_description = (
    """
===================
PloneSoftwareCenter
===================

""" + read('README.rst') + read('docs', 'HISTORY.txt'))

description = """\
PloneSoftwareCenter is a tool that keeps track of software projects
"""

setup(name='Products.PloneSoftwareCenter',
      version=version,
      description=description,
      long_description=long_description,
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Plone Website Team',
      author_email='plone-website@lists.sourceforge.net',
      maintainer='Alex Clark',
      maintainer_email='aclark@aclark.net',
      url='https://github.com/collective/Products.PloneSoftwareCenter',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.ArchAddOn',
          'Products.AddRemoveWidget',
          'Products.DataGridField',
          'cioppino.twothumbs',
          # this is temporary until we get the ratings migrated
          'plone.contentratings',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

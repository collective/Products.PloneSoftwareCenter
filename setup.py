import os
from setuptools import setup, find_packages

version = '1.5'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    'Change history\n'
    '**************\n'
    + '\n' +
    open(os.path.join('docs','HISTORY.txt')).read()
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    open(os.path.join('Products','PloneSoftwareCenter','README.txt')).read()
    + '\n'
    )

description =  """\
Plone Software Center is a tool to keep track of software projects and 
software releases, and is used to power the Products download 
area on plone.org. It was formerly called ArchPackage.
"""

setup(name='Products.PloneSoftwareCenter',
      version=version,
      description=description,
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/collective/Products.PloneSoftwareCenter',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )


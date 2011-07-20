
Introduction
============

``Products.PloneSoftwareCenter`` is a **Plone add-on** that keeps track of software projects,
software releases, and other related information in Plone as Plone content.
It was originally created to power the `downloads section of plone.org`_. 

Features
--------

As of version 1.5, ``Products.PloneSoftwareCenter`` supports the `Python Package Index API`_.

.. _`Python Package Index API`: http://peak.telecommunity.com/DevCenter/EasyInstall#package-index-api

.. _`downloads section of plone.org`: http://plone.org/products

Installation
============

* Add ``Products.PloneSoftwareCenter`` to the eggs parameter of your instance section::

    [instance]
    recipe = plone.recipe.zope2instance
    eggs =
        Plone
        …
        Products.PloneSoftwareCenter

* Run ``bin/buildout``.
* Restart Plone.
* Install the add-on in Site Setup -> Add-ons.


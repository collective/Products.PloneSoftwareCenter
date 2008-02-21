## Script (Python) "findParentProjectURL"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=releaseUrl
##title=Calculate the parent project URL for the given release URL

parts = releaseUrl.split('/')
return '/'.join(parts[:-2])
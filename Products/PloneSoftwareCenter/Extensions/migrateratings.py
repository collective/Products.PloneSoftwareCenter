from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from Products.contentmigration.walker import CustomQueryWalker
from Products.contentmigration.migrator import BaseInlineMigrator
from zope.annotation.interfaces import IAnnotations
import transaction


class RatingsMigrator(BaseInlineMigrator):
  """
  Migrate PSC Projects from the content ratings product to the twothumbs product
  """
  
  src_portal_type = src_meta_type = 'PSCProject'

  def migrate_ratings(self):
      
      """
      contentratings and twothumbs both use annotations. Just want to move 
      one to another. Here we say anything >= 3 rating is a thumbs up
      """
      
      from cioppino.twothumbs import rate as thumbrate
      
      transaction.begin()
      item = self.obj 
      annotations = IAnnotations(item)
      if annotations:
        if annotations.has_key('contentratings.userrating.psc_stars'):
            ratings = annotations['contentratings.userrating.psc_stars'].all_user_ratings()
            annotations = thumbrate.setupAnnotations(item)
            for rating in ratings:
                userid = rating.userid
                value = rating._rating
                
                if rating >= 3.0:
                    thumbrate.loveIt(item, rating.userid)
                else:
                    thumbrate.hateIt(item,rating.userid)
            
      # we need to reindex th object anyways
      item.reindexObject()
      transaction.commit()

def migrate(self):
    out = StringIO()
    print >> out, "Starting ratings migration"
    
    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()
    
    
    # Migrate release count variable
    walker = CustomQueryWalker(portal, RatingsMigrator, query = {'portal_type':'PSCProject'})
    transaction.savepoint(optimistic=True)
    print >> out, "Switching from contentratings to twothumbs.."
    walker.go(out=out)
    print >> out, walker.getOutput()
    
    print >> out, "Migration finished"

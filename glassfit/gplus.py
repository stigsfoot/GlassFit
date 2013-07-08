import logging
import util
from pprint import pformat
import webapp2

def share_workout_gplus(handler, finished_card):
    """Share a completed workout with g+ but not its stats"""
    logging.info("Supposed to be sharing with g+")

    moment = {
        "type":"http://schemas.google.com/AddActivity",
        "target": {
            "id": "target-id-1",
            "type":"http://schemas.google.com/AddActivity",
            "name": "The Google+ Platform",
            "description": "A page that describes just how awesome Google+ is!",
            "image": "https://developers.google.com/+/plugins/snippet/examples/thing.png"
        }
    }
        
    handler.gplus_service.moments().insert(
        userId='me',
        collection='vault',
        body=moment
    ).execute()

class TestGplus(webapp2.RequestHandler):
    """Test g+ service using this endpoint"""
    @util.auth_required
    def get(self):
        if hasattr(self, 'gplus_service') and \
        self.gplus_service is not None:
            self.response.write("gplus is working")
        else:
            self.response.write("gplus isn't working")
            return
        user = self.gplus_service.people().get(userId='me').execute()
        self.response.write('<pre>%s</pre>' % pformat(user))

GPLUS_PATH = [ ('/d/gplus', TestGplus) ]

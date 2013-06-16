import logging
import webapp2
from datetime import datetime
from os import path
import util
import time
from oauth2client.anyjson import simplejson
# need this module to format datetime's per google's wishes
from feed.date import rfc3339

# A workout card is intended to
# 1. display a workout animated gif
# 2. display instructions
# 3. display a timer
# 4. schedule another card

# Right now we just hard code stuff
workouts_base = path.join(path.dirname(__file__), '../', 'templates/workouts/')


def workout_template(workout):
    return path.join(workouts_base, workout)


def body(workout):
    return {'text': 'Working out: doing {w}'.format(w=workout)}


class Card(webapp2.RequestHandler):
    @util.auth_required
    def get(self, workout_name, duration):
        """Render a workout card from a workout_name and a duration"""
        logging.info("Attempting to workout: {w} for {d}".format(w=workout_name, d=duration))
        template_path = workout_template(workout_name)
        logging.info("Rendering: {path}".format(path=template_path))
        self.mirror_service.timeline().insert(body=body(workout_name)).execute()

        timestamp_after_duration = int(time.mktime(time.gmtime())) + int(duration)

        logging.info("Notification will occur in {time}".format(time=timestamp_after_duration))

        self.mirror_service.timeline().insert(
            body={
                'text': 'Finished exercise. Should have waited {s} seconds'.format(s=duration),
                'notification': {
                    # TODO - ask on stackoverflow or something
                    # 'deliveryTime': rfc3339.timestamp_from_tf(timestamp_after_duration),
                    'level': 'DEFAULT'
                },
            }
        ).execute()


WORKOUT_PATHS = [
    ('/workout/(.+)/(\d+)', Card)
]
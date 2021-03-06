from os import path
import json
import logging
import jinja2
import random

workouts_base = path.join(path.dirname(__file__), '../', 'templates/workouts/')

def imgur(k): return 'http://i.imgur.com/%s' % k

image_maps = {
    5          : imgur('HyYB3K6.gif'),
    10         : imgur('e6UfFof.gif'),
    15         : imgur('lYSIymH.gif'),
    20         : imgur('fQ65krp.gif'),
    30         : imgur('9zqBGzy.gif'),
    'Warmup'   : imgur('oHhUWci.gif'),
    'Squats'   : imgur('2JyIEk7.gif'),
    'Pushups'  : imgur('I8oiUok.gif'),
    'Situps'   : imgur('GmkXqa1.gif'),
    'Abcrunch' : imgur('qNa4FmB.gif'),
    'Plank'    : imgur('0jflG6G.gif'),
    'SidePlank': imgur('ysDRSXj.gif'),
    'Curls'    : imgur('9m2NNgz.gif'),
    'Extention': imgur('ONgKutU.gif'),
    'Wallsit'  : imgur('UISoCjR.gif'),
}

backgrounds = [imgur('aSWkGtm.png')]

jinja = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path.dirname(workouts_base)))

class Exercise(object):
    def __init__(self, name): self.name = name
    def animation_path(self): return image_maps[self.name]

def timer_path(duration): return image_maps[duration]

warmup    = Exercise(name='Warmup')
squats    = Exercise(name='Squats')
pushups   = Exercise(name='Pushups')
situps    = Exercise(name='Situps')
ab_crunch = Exercise(name='Abcrunch')
plank     = Exercise(name='Plank')
sideplank = Exercise(name='SidePlank') 
curls     = Exercise(name='Curls') 
extention = Exercise(name='Extention')
wallsit   = Exercise(name='Wallsit') 

class WorkoutSet(object):
    def __init__(self, reps, time, exercise):
        self.reps = reps
        self.time = time
        self.exercise = exercise

    def template_vars(self):
        return {
                'workout_name': self.exercise.name,
                'duration': self.time,
                'num_reps': self.reps,
                'time_path': timer_path(self.time),
                'image_path': self.exercise.animation_path(),
                'background_path': random.choice(backgrounds)
                }
    @property
    def template_name(self): return 'workout.json'

class SimpleCard(object):
    def __init__(self, time, template_name):
        self.time = time
        self.template_name = template_name

    def template_vars(self): return {}

class WorkoutTemplate(object):
    def __init__(self, card): self.card = card

    def render_template(self):
        template = jinja.get_template(self.card.template_name)
        return json.loads(template.render(self.card.template_vars()))

class RestCard(object):
    def __init__(self, reps, time, template_name, message, exercise):
        self.time = time
        self.template_name = template_name
        self.message = message
        self.exercise = exercise
        self.reps = reps

    def template_vars(self): 
        return { 
                'message'     : self.message,
                'workout_name': self.exercise,
                'num_reps'    : self.reps,
                'exercise'    : self.exercise,
                'reps'        : self.reps
                }

class FinishCard(object):
    def __init__(self, time, template_name, workout, stats):
        self.template_name = template_name
        self.stats = stats
        self.time = 0
        self.workout = []

    @classmethod
    def create(cls, template_name, workout):
        instance = cls(time=0, template_name=template_name, workout=workout,
                stats={})
        instance.calculate_stats(workout)
        return instance


    def calculate_stats(self, workout):
        self.stats['workout_time'] = sum([w.time for w in workout
            if isinstance(w, WorkoutSet)])
        self.stats['total_time'] = sum([w.time for w in workout])

    def template_vars(self): return self.stats

TYPES = {
    'Exercise': Exercise,
    'SimpleCard': SimpleCard,
    'WorkoutSet': WorkoutSet,
    'RestCard': RestCard,
    'FinishCard': FinishCard,
}

class CustomTypeEncoder(json.JSONEncoder):
    """A custom JSONEncoder class that knows how to encode core custom
    objects.

    Custom objects are encoded as JSON object literals (ie, dicts) with
    one key, '__TypeName__' where 'TypeName' is the actual name of the
    type to which the object belongs.  That single key maps to another
    object literal which is just the __dict__ of the object encoded."""

    def default(self, obj):
        for cls in TYPES.values():
            if isinstance(obj, cls):
                key = '__%s__' % obj.__class__.__name__
                return { key: obj.__dict__ }
        logging.warn("Don't know how to encode %s", str(obj))
        return json.JSONEncoder.default(self, obj)


class CustomTypeDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.default, **kwargs)

    def default(self, dct):
        if len(dct) == 1:
            type_name, value = dct.items()[0]
            type_name = type_name.strip('_')
            if type_name in TYPES:
                return TYPES[type_name](**value)
        return dct

# The sample workout we use for now
pre_workout = [ 
    WorkoutSet(exercise=warmup, reps=15, time=30),
    RestCard(time=17, reps='15', template_name='rest.json', message='squats workout', exercise='warm up'),
    WorkoutSet(exercise=squats, reps=10, time=30),
    RestCard(time=17, reps='10', template_name='rest.json', message='sit ups workout', exercise='squat workout'),
    WorkoutSet(exercise=situps, reps=20, time=30),
    RestCard(time=17, reps='20', template_name='rest.json', message='push ups workout', exercise='situp workout'),
    WorkoutSet(exercise=pushups, reps=11, time=30),
    RestCard(time=17, reps='11', template_name='rest.json', message='ab crunch workout', exercise='push up workout'),
    WorkoutSet(exercise=ab_crunch, reps=11, time=30),
    RestCard(time=17, reps='11', template_name='rest.json', message='plank workout', exercise='ab crunch'),
    WorkoutSet(exercise=plank, reps=11, time=30),
    RestCard(time=17, reps='11', template_name='rest.json', message='side plank workout', exercise='plank'),
    WorkoutSet(exercise=sideplank, reps=11, time=30),
    RestCard(time=17, reps='11', template_name='rest.json', message='bicep curls workout', exercise='side plank'),
    WorkoutSet(exercise=curls, reps=11, time=30),
    RestCard(time=17, reps='11', template_name='rest.json', message='tricep extentions workout', exercise='curl workout'),
    WorkoutSet(exercise=extention, reps=11, time=30),
    RestCard(time=17, reps='11', template_name='rest.json', message='wall sit workout', exercise='tricep extention workout'),
    WorkoutSet(exercise=wallsit, reps=11, time=30),
]

finish_card = FinishCard.create('finish.json', pre_workout)

workout = pre_workout + [finish_card]

def select_workout(name):
    pre_workouts = {
        'beginner' : [
            WorkoutSet(exercise=warmup, reps=10, time=30),
            RestCard(time=17, reps='10', template_name='rest.json',
                message='squats workout', exercise='warmup'),

            WorkoutSet(exercise=squats, reps=10, time=30),
            RestCard(time=17, reps='10', template_name='rest.json',
                message='sit ups workout', exercise='squats workout'),

            WorkoutSet(exercise=situps, reps=10, time=30),
            RestCard(time=17, reps='10', template_name='rest.json',
                message='push ups workout', exercise='sit up workout'),

            WorkoutSet(exercise=pushups, reps=10, time=30),
        ],
        'intermediate' : [
            WorkoutSet(exercise=warmup, reps=15, time=30),
            RestCard(time=17, reps='15', template_name='rest.json',
                message='squats workout', exercise='warm up'),
            
            WorkoutSet(exercise=situps, reps=15, time=30),
            RestCard(time=17, reps='15', template_name='rest.json',
                message='push ups workout', exercise='sit up workout'),

            WorkoutSet(exercise=pushups, reps=15, time=30),
            RestCard(time=17, reps='15', template_name='rest.json',
                message='plank workout', exercise='push up workout'),

            WorkoutSet(exercise=plank, reps=15, time=30),
            RestCard(time=17, reps='15', template_name='rest.json',
                message='side plank workout', exercise='planks'),

            WorkoutSet(exercise=squats, reps=15, time=30),
            RestCard(time=17, reps='15', template_name='rest.json',
                message='sit ups workout', exercise='squat workout'),

            WorkoutSet(exercise=sideplank, reps=15, time=30),
            RestCard(time=17, reps='15', template_name='rest.json',
                message='wall sit workout', exercise='side plank workout'),

            WorkoutSet(exercise=wallsit, reps=15, time=30),
        ],
        'advanced' : [
            WorkoutSet(exercise=warmup, reps=20, time=30),
            RestCard(time=17, reps='20', template_name='rest.json',
                message='squats workout', exercise='tricep extention workout'),

            WorkoutSet(exercise=sideplank, reps=20, time=30),
            RestCard(time=17, reps='20', template_name='rest.json',
                message='bicep curls workout', exercise='tricep extention workout'),

            WorkoutSet(exercise=curls, reps=20, time=30),
            RestCard(time=17, reps='20', template_name='rest.json',
                message='tricep extentions workout', exercise='tricep extention workout'),

            WorkoutSet(exercise=squats, reps=20, time=30),
            RestCard(time=17, reps='20', template_name='rest.json',
                message='sit ups workout', exercise='tricep extention workout'),

            WorkoutSet(exercise=situps, reps=20, time=30),
            RestCard(time=17, reps='20', template_name='rest.json',
                message='push ups workout', exercise='tricep extention workout'),

            WorkoutSet(exercise=pushups, reps=20, time=30),
            RestCard(time=17, reps='20', template_name='rest.json',
                message='ab crunch workout', exercise='tricep extention workout'),

            WorkoutSet(exercise=ab_crunch, reps=20, time=30),
            RestCard(time=17, reps='20', template_name='rest.json',
                message='plank workout', exercise='tricep extention workout'),

            WorkoutSet(exercise=plank, reps=20, time=30),
            RestCard(time=17, reps='20', template_name='rest.json',
                message='side plank workout', exercise='tricep extention workout'),
            
            WorkoutSet(exercise=extention, reps=20, time=30),
            RestCard(time=17, reps='20', template_name='rest.json',
                message='wall sit workout', exercise='tricep extention workout'),
            WorkoutSet(exercise=wallsit, reps=20, time=30),
        ],
    }
    pre_workout = pre_workouts[name]
    return pre_workout + [FinishCard.create('finish.json', pre_workout)]



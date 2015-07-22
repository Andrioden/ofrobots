from google.appengine.ext import ndb

class Robot(ndb.Model):
    name = ndb.StringProperty(required=True)
    damage = ndb.IntegerProperty(required=True)
    max_health = ndb.IntegerProperty(required=True)
    health = ndb.IntegerProperty(required=True)
    code = ndb.TextProperty(required=True)
    crashed = ndb.BooleanProperty(default=False)
    energy = ndb.IntegerProperty(required=True)
    # CPU
    IPS = ndb.IntegerProperty(required=True)  # Instructions Per Second
    # RAM
    memory = ndb.IntegerProperty(required=True)  # Instructions Memory

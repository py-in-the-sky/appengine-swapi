from google.appengine.ext import ndb

from .character import Character


class Faction(ndb.Model):
    _use_cache = False
    _use_memcache = False

    name = ndb.StringProperty(required=True)
    description = ndb.TextProperty()
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)
    updated = ndb.DateTimeProperty(required=True, auto_now=True)

    def get_characters(self):
        "Return characters in faction in alphabetical order."
        q = Character.query(Character.faction_key == self.key).order(Character.name)
        return q.fetch()

    @classmethod
    def get_by_name(cls, name):
        return cls.query(cls.name == name).get()

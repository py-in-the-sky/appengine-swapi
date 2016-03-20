from google.appengine.ext import ndb

from .character import Character


class Faction(ndb.Model):
    name = ndb.StringProperty(required=True)
    description = ndb.TextProperty()
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)
    updated = ndb.DateTimeProperty(required=True, auto_now=True)

    def get_characters(self):
        q = Character.query(Character.faction_key == self.key).order(Character.name)
        return q.fetch()
from google.appengine.ext import ndb

from .character import Character
from .utils import paginated_query


class Faction(ndb.Model):
    name = ndb.StringProperty(required=True)
    description = ndb.TextProperty()
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)
    updated = ndb.DateTimeProperty(required=True, auto_now=True)

    @classmethod
    def get_factions(cls, **kwargs):
        "Return all factions in alphabetical order."
        q = cls.query()
        q_forward = q.order(cls.name)
        q_backward = q.order(-cls.name)
        return paginated_query(q_forward, q_backward, **kwargs)

    def get_characters(self, **kwargs):
        "Return characters in faction in alphabetical order."
        q = Character.query(Character.faction_key == self.key)
        q_forward = q.order(Character.name)
        q_backward = q.order(-Character.name)
        return paginated_query(q_forward, q_backward, **kwargs)

    @classmethod
    def get_by_name(cls, name):
        return cls.query(cls.name == name).get_async()

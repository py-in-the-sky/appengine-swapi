from google.appengine.ext import ndb
from google.appengine.ext.db import BadValueError

from .utils import paginated_query


root = ndb.Key('CharacterRoot', 'character_root')


class Character(ndb.Model):
    name = ndb.StringProperty(required=True)
    description = ndb.TextProperty()
    faction_key = ndb.KeyProperty(required=True, kind='Faction')
    friend_keys = ndb.KeyProperty(repeated=True, kind='Character')
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)
    updated = ndb.DateTimeProperty(required=True, auto_now=True)

    @classmethod
    def get_characters(cls, **kwargs):
        "Return all characters in alphabetical order."
        q = cls.query()
        q_forward = q.order(cls.name)
        q_backward = q.order(-cls.name)
        return paginated_query(q_forward, q_backward, **kwargs)

    def get_friends(self, **kwargs):
        "Return friends in alphabetical order."
        cls = self.__class__
        q = cls.query(cls.friend_keys == self.key)
        q_forward = q.order(cls.name)
        q_backward = q.order(-cls.name)
        return paginated_query(q_forward, q_backward, **kwargs)

    @classmethod
    def get_by_name(cls, name):
        return cls.query(cls.name == name).get_async()

    @classmethod
    @ndb.transactional
    def create(cls, **kwargs):
        cls.ensure_name_not_in_datastore(kwargs.get('name'))

        properties = Character._properties
        input = {k:v for k,v in kwargs.iteritems() if k in properties}
        character_key = cls(parent=root, **input).put()
        new_character = character_key.get()
        return new_character

    @classmethod
    def ensure_name_not_in_datastore(cls, name):
        if name is None:
            return None

        if cls.query(cls.name == name, ancestor=root).count() > 0:
            raise BadValueError('"%s" already exists' % name)

        return name

    @classmethod
    @ndb.transactional
    def create_friendship(cls, character_key_1, character_key_2):
        cls.ensure_friendship_not_in_datastore(character_key_1, character_key_2)

        ch1, ch2 = ndb.get_multi([character_key_1, character_key_2])
        ch1.friend_keys.append(character_key_2)
        ch2.friend_keys.append(character_key_1)
        ndb.put_multi([ch1, ch2])
        return ch1, ch2

    @classmethod
    def ensure_friendship_not_in_datastore(cls, character_key_1, character_key_2):
        q = cls.query(
            cls.key == character_key_1,
            cls.friend_keys == character_key_2,
            ancestor=root
        )

        if q.count() > 0:
            raise BadValueError('Friendship already exists')

        return character_key_1, character_key_2

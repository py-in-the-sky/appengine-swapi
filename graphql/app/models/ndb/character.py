from google.appengine.ext import ndb
from google.appengine.ext.db import BadValueError


root = ndb.Key('CharacterRoot', 'character_root')


class Character(ndb.Model):
    _use_cache = False
    _use_memcache = False

    name = ndb.StringProperty(required=True)
    description = ndb.TextProperty()
    faction_key = ndb.KeyProperty(required=True, kind='Faction')
    friend_keys = ndb.KeyProperty(repeated=True, kind='Character')
    created = ndb.DateTimeProperty(required=True, auto_now_add=True)
    updated = ndb.DateTimeProperty(required=True, auto_now=True)

    def get_friends(self):
        "Return friends in alphabetical order."
        cls = self.__class__
        q = cls.query(cls.friend_keys == self.key).order(cls.name)
        return q.fetch()

    def get_friends_of_friends(self):
        """
        Return friends of friends in alphabetical order.
        Return value does not include self or friends.
        """
        if not self.friend_keys:
            return []

        cls = self.__class__
        q = cls.query(cls.friend_keys.IN(self.friend_keys)).order(cls.name)
        superset_keys = q.fetch(keys_only=True)
        fof_keys = [k for k in superset_keys if k != self.key and k not in self.friend_keys]
        # NB: For scalability, the keys of friends-of-friends for each character
        # should be periodically calculated and stored in the datastore by a cron job.
        # Then for an HTTP request by a user, the calculated value of the keys of
        # friends-of-friends could just be fetched and then the actual entities
        # retrieved in a batched get.
        # For this example app, though, this scalability concern is not a central
        # issue, so the app will be left to simply make this calculation in
        # response to a user request.

        if not fof_keys:
            return []

        return ndb.get_multi(fof_keys)

    @classmethod
    def get_by_name(cls, name):
        return cls.query(cls.name == name).get()

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

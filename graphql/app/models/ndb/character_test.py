import pytest
from google.appengine.ext.db import BadValueError

from app.models.ndb.character import Character
from app.models.ndb.faction import Faction


def test_faction_key(rey):
    assert rey.faction_key.get().name == 'The Resistance'


def test_get_friends(rey, leia):
    friends, _ = rey.get_friends(first=200).get_result()
    friend_names = [f.entity.name for f in friends]

    assert friend_names == ['Finn', 'Han']

    Character.create_friendship(rey.key, leia.key)
    friends, _ = rey.get_friends(first=200).get_result()
    friend_names = [f.entity.name for f in friends]

    assert friend_names == ['Finn', 'Han', 'Leia']


def test_ensure_name_not_in_datastore(fixtures):
    with pytest.raises(BadValueError) as excinfo:
        Character.ensure_name_not_in_datastore('Rey')

    assert str(excinfo.value) == '"Rey" already exists'

    name = Character.ensure_name_not_in_datastore('Vader')

    assert name == 'Vader'


def test_create(fixtures):
    kwargs = dict(name='Rey')

    with pytest.raises(BadValueError) as excinfo:
        Character.create(**kwargs)

    assert str(excinfo.value) == '"Rey" already exists'

    kwargs['name'] = 'Chewie'

    with pytest.raises(BadValueError) as excinfo:
        Character.create(**kwargs)

    assert str(excinfo.value) == 'Entity has uninitialized properties: faction_key'

    resistance_key = Faction.query(Faction.name == 'The Resistance').get(keys_only=True)
    kwargs['faction_key'] = resistance_key
    new_character = Character.create(**kwargs)

    assert new_character.name == 'Chewie'
    assert new_character.faction_key.get().name == 'The Resistance'


def test_ensure_friendship_not_in_datastore(rey, finn, leia):
    with pytest.raises(BadValueError) as excinfo:
        Character.ensure_friendship_not_in_datastore(finn.key, rey.key)

    assert str(excinfo.value) == 'Friendship already exists'

    ch1_key, ch2_key = Character.ensure_friendship_not_in_datastore(rey.key, leia.key)

    assert ch1_key == rey.key
    assert ch2_key == leia.key


def test_create_friendship(rey, finn, leia):
    with pytest.raises(BadValueError) as excinfo:
        Character.create_friendship(rey.key, finn.key)

    assert str(excinfo.value) == 'Friendship already exists'

    ch1, ch2 = Character.create_friendship(rey.key, leia.key)

    # The `friend_keys` property on the instance whose key is passed into
    # `create_friendship` is not mutated/updated.

    assert ch1.name == rey.name
    assert ch1.friend_keys == rey.friend_keys + [leia.key]
    rey2 = rey.key.get()
    assert ch1.friend_keys == rey2.friend_keys

    assert ch2.name == leia.name
    assert ch2.friend_keys == leia.friend_keys + [rey.key]
    leia2 = leia.key.get()
    assert ch2.friend_keys == leia2.friend_keys


def test_get_by_name(rey):
    assert Character.get_by_name(rey.name).get_result() == rey
    assert Character.get_by_name('Chewie').get_result() is None

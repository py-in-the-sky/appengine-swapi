import pytest
from google.appengine.ext.db import BadValueError

from app.models.ndb.character import Character
from app.models.ndb.faction import Faction


def test_faction_key(rey):
    assert rey.faction_key.get().name == 'The Resistance'


def test_get_friends(rey, leia):
    friend_names = [f.name for f in rey.get_friends()]

    assert friend_names == ['Finn', 'Han']

    Character.create_friendship(rey.key, leia.key)
    friend_names = [f.name for f in rey.get_friends()]

    assert friend_names == ['Finn', 'Han', 'Leia']


def test_get_friends_of_friends(rey, leia, r2d2, han, chewie):
    fof_names = lambda character: [fof.name for fof in character.get_friends_of_friends()]

    _, r2d2 = Character.create_friendship(leia.key, r2d2.key)

    assert fof_names(rey) == ['Leia']
    assert rey.name not in fof_names(r2d2)

    _, chewie = Character.create_friendship(han.key, chewie.key)

    assert fof_names(rey) == ['Chewie', 'Leia']
    assert rey.name in fof_names(chewie)

    rey, _ = Character.create_friendship(rey.key, leia.key)

    assert fof_names(rey) == ['Chewie', 'R2D2']
    assert rey.name in fof_names(r2d2)
    assert rey.name in fof_names(chewie)

    # Section below illustrates how the query is dependent on the
    # `friend_keys` property that's on the instance.
    # See the `test_create_friendship` test below.

    _, chewie = Character.create_friendship(rey.key, chewie.key)

    assert rey.name not in fof_names(chewie)
    assert chewie.name in fof_names(rey)

    rey = rey.key.get()

    assert chewie.name not in fof_names(rey)


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
    assert Character.get_by_name(rey.name) == rey
    assert Character.get_by_name('Chewie') is None

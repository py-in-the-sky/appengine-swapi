from google.appengine.ext import ndb

from app.models.ndb.character import Character, root
from app.models.ndb.faction import Faction


def ensure_minimal_data_in_datastore():
    friendships(characters(*factions()))


def friendships(characters):
    _friendships = [
        (characters['han'], characters['leia']),
        (characters['han'], characters['rey']),
        (characters['han'], characters['finn']),
        (characters['rey'], characters['finn']),
        (characters['kylo'], characters['snoke'])
    ]

    for ch1,ch2 in _friendships:
        if ch2.key in ch1.friend_keys:
            continue

        ch1.friend_keys.append(ch2.key)
        ch2.friend_keys.append(ch1.key)
        ndb.put_multi([ch1, ch2])


def characters(resistance_key, first_order_key):
    han = get_by_name_or_create(Character(
        name='Han',
        description='Captain of the Millennium Falcon.',
        faction_key=resistance_key,
        parent=root
    ))

    leia = get_by_name_or_create(Character(
        name='Leia',
        description='Leader of the Resistance.',
        faction_key=resistance_key,
        parent=root
    ))

    rey = get_by_name_or_create(Character(
        name='Rey',
        description='A new awakening in the Force.',
        faction_key=resistance_key,
        parent=root
    ))

    finn = get_by_name_or_create(Character(
        name='Finn',
        description='A former storm trooper who has joined the Resistance.',
        faction_key=resistance_key,
        parent=root
    ))

    kylo = get_by_name_or_create(Character(
        name='Kylo',
        description='Grandson and heir apparent to Darth Vader.',
        faction_key=first_order_key,
        parent=root
    ))

    snoke = get_by_name_or_create(Character(
        name='Snoke',
        description='Supreme Leader of the First Order.',
        faction_key=first_order_key,
        parent=root
    ))

    return dict(han=han, leia=leia, rey=rey, finn=finn, kylo=kylo, snoke=snoke)


def factions():
    resistance = get_by_name_or_create(Faction(
        name='The Resistance',
        description='Led by General Leia Organa, the Resistance fights the First Order.'
    ))

    first_order = get_by_name_or_create(Faction(
        name='The First Order',
        description='Risen from the ashes of the Empire, the First Order is out to impose order on the Galaxy.'
    ))

    return (resistance.key, first_order.key)


def get_by_name_or_create(entity):
    cls = entity.__class__
    db_entity = cls.query(cls.name == entity.name).get()

    if db_entity:
        return db_entity

    entity.put()
    return entity

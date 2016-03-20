from app.models.ndb.faction import Faction
from app.models.ndb.character import Character


def test_get_characters(resistance, first_order):
    first_order_names = [c.name for c in first_order.get_characters()]

    assert first_order_names == ['Kylo', 'Snoke']

    resistance_names = [c.name for c in resistance.get_characters()]

    assert resistance_names == ['Finn', 'Han', 'Leia', 'Rey']

    Character.create(name='Chewie', faction_key=resistance.key)

    resistance_names2 = [c.name for c in resistance.get_characters()]

    assert resistance_names2 == ['Chewie'] + resistance_names


def test_get_by_name(resistance, first_order):
    assert Faction.get_by_name(resistance.name) == resistance
    assert Faction.get_by_name(first_order.name) == first_order
    assert Faction.get_by_name('The Galactic Empire') is None

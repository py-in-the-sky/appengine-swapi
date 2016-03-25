from app.models.ndb.faction import Faction
from app.models.ndb.character import Character


def test_get_characters(resistance, first_order):
    first_order_characters, _ = first_order.get_characters(first=200).get_result()
    first_order_names = [c.entity.name for c in first_order_characters]

    assert first_order_names == ['Kylo', 'Snoke']

    resistance_characters, _ = resistance.get_characters(first=200).get_result()
    resistance_names = [c.entity.name for c in resistance_characters]

    assert resistance_names == ['Finn', 'Han', 'Leia', 'Rey']

    Character.create(name='Chewie', faction_key=resistance.key)

    resistance_characters2, _ = resistance.get_characters(first=200).get_result()
    resistance_names2 = [c.entity.name for c in resistance_characters2]

    assert resistance_names2 == ['Chewie'] + resistance_names


def test_get_by_name(resistance, first_order):
    assert Faction.get_by_name(resistance.name).get_result() == resistance
    assert Faction.get_by_name(first_order.name).get_result() == first_order
    assert Faction.get_by_name('The Galactic Empire').get_result() is None

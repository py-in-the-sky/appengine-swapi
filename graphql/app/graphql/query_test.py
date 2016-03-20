from . import schema


def test_query(fixtures):
    query_template = '''
        query {
            %s(name: "%s") {
                %s
            }
        }
    '''

    result = schema.execute(query_template % ('faction', 'The First Order', 'name'))

    assert not result.errors
    assert result.data == { "faction": { "name": "The First Order" } }

    result = schema.execute(query_template % ('faction', 'The Galactic Empire', 'name'))

    assert not result.errors
    assert result.data == { "faction": None }

    result = schema.execute(query_template % ('character', 'Han', 'description'))

    assert not result.errors
    assert result.data == { "character": { "description": "Captain of the Millennium Falcon." } }

    result = schema.execute(query_template % ('character', 'Chewie', 'name'))

    assert not result.errors
    assert result.data == { "character": None }


def test_query_by_key(resistance, rey):
    query_template = '''
        query {
            %s(key: "%s") {
                name
            }
        }
    '''

    result = schema.execute(query_template % ('character', rey.key.urlsafe()))

    assert not result.errors
    assert result.data == { "character": { "name": "Rey" } }

    result = schema.execute(query_template % ('faction', resistance.key.urlsafe()))

    assert not result.errors
    assert result.data == { "faction": { "name": "The Resistance" } }


def test_query_complex(fixtures):
    result = schema.execute('''
        query {
            faction(name: "The First Order") {
                name
                characters {
                    name
                }
            }
        }
    ''')

    assert not result.errors
    assert result.data == {
        "faction": {
            "name": "The First Order",
            "characters": [
                { "name": "Kylo" },
                { "name": "Snoke" }
            ]
        }
    }

    result = schema.execute('''
        query {
            faction(name: "The Resistance") {
                name
                characters {
                    name
                    suggested {
                        name
                        faction {
                            name
                        }
                    }
                }
            }
        }
    ''')

    assert not result.errors
    assert result.data == {
        "faction": {
            "name": "The Resistance",
            "characters": [
                {
                    "name": "Finn",
                    "suggested": [
                        {
                        "name": "Leia",
                            "faction": { "name": "The Resistance" }
                        }
                    ]
                },
                {
                    "name": "Han",
                    "suggested": []
                },
                {
                    "name": "Leia",
                    "suggested": [
                        {
                            "name": "Finn",
                            "faction": { "name": "The Resistance" }
                        },
                        {
                            "name": "Rey",
                            "faction": { "name": "The Resistance" }
                        }
                    ]
                },
                {
                    "name": "Rey",
                    "suggested": [
                        {
                            "name": "Leia",
                            "faction": { "name": "The Resistance" }
                        }
                    ]
                }
            ]
        }
    }

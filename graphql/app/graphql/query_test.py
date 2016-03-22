import pytest

from . import schema


@pytest.fixture(scope='function')
def query_template():
    return '''
        query {
            %s(%s: "%s") {
                %s
            }
        }
    '''


@pytest.fixture(scope='function')
def query_fragment():
    return '''
        ... on Character {
            name
        }
    '''


def test_object_identification(fixtures, query_template, query_fragment):
    result = schema.execute(query_template % ('character', 'name', 'Rey', 'name\nid'))

    assert not result.errors

    rey_relay_id = result.data['character']['id']

    assert result.data == {
        'character': {
            'id': rey_relay_id,
            'name': 'Rey'
        }
    }

    query_body = 'id \n %s' % query_fragment
    result = schema.execute(query_template % ('node', 'id', rey_relay_id, query_body))

    assert not result.errors
    assert result.data == {
        'node': {
            'id': rey_relay_id,
            'name': 'Rey'
        }
    }


def test_object_identification_failure(fixtures, query_template, query_fragment):
    query_body = 'id \n %s' % query_fragment
    result = schema.execute(query_template % ('node', 'id', 'bad-id', query_body))

    assert not result.errors
    assert result.data == { 'node': None }


def test_query(fixtures, query_template):
    result = schema.execute(query_template % ('faction', 'name', 'The First Order', 'name'))

    assert not result.errors
    assert result.data == { "faction": { "name": "The First Order" } }

    result = schema.execute(query_template % ('faction', 'name', 'The Galactic Empire', 'name'))

    assert not result.errors
    assert result.data == { "faction": None }

    result = schema.execute(query_template % ('character', 'name', 'Han', 'description'))

    assert not result.errors
    assert result.data == { "character": { "description": "Captain of the Millennium Falcon." } }

    result = schema.execute(query_template % ('character', 'name', 'Chewie', 'name'))

    assert not result.errors
    assert result.data == { "character": None }


def test_query_by_key(resistance, rey, query_template):
    result = schema.execute(query_template % ('character', 'key', rey.key.urlsafe(), 'name'))

    assert not result.errors
    assert result.data == { "character": { "name": "Rey" } }

    result = schema.execute(query_template % ('faction', 'key', resistance.key.urlsafe(), 'name'))

    assert not result.errors
    assert result.data == { "faction": { "name": "The Resistance" } }


def test_query_complex(fixtures):
    result = schema.execute('''
        query {
            faction(name: "The First Order") {
                name
                characters {
                    edges {
                        node {
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
            "name": "The First Order",
            "characters": {
                "edges": [
                    { "node": { "name": "Kylo" } },
                    { "node": { "name": "Snoke" } }
                ]
            }
        }
    }

    result = schema.execute('''
        query {
            faction(name: "The Resistance") {
                name
                characters {
                    edges {
                        node {
                            name
                            suggested {
                                edges {
                                    node {
                                        name
                                        faction {
                                            name
                                        }
                                    }
                                }
                            }
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
            "characters": {
                "edges": [
                    {
                        "node": {
                            "name": "Finn",
                            "suggested": {
                                "edges": [
                                    {
                                        "node": {
                                            "name": "Leia",
                                            "faction": { "name": "The Resistance" }
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    {
                        "node": {
                            "name": "Han",
                            "suggested": { "edges": [] }
                        }
                    },
                    {
                        "node": {
                            "name": "Leia",
                            "suggested": {
                                "edges": [
                                    {
                                        "node": {
                                            "name": "Finn",
                                            "faction": { "name": "The Resistance" }
                                        }
                                    },
                                    {
                                        "node": {
                                            "name": "Rey",
                                            "faction": { "name": "The Resistance" }
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    {
                        "node": {
                            "name": "Rey",
                            "suggested": {
                                "edges": [
                                    {
                                        "node": {
                                            "name": "Leia",
                                            "faction": { "name": "The Resistance" }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        }
    }

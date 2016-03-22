import pytest

from . import schema


@pytest.fixture(scope='function')
def create_friendship_template():
    return '''
        mutation {
            createFriendship(input: { clientMutationId: "abc", characterKey1: "%s", characterKey2: "%s" }) {
                clientMutationId
                ok
                character1 {
                    name
                }
                character2 {
                    name
                }
            }
        }
    '''


@pytest.fixture(scope='function')
def create_character_template():
    return '''
        mutation {
            createCharacter(input: { clientMutationId: "abc", name: "%s", factionKey: "%s" }) {
                clientMutationId
                ok
                character {
                    name
                    description
                    faction {
                        name
                    }
                }
            }
        }
    '''


@pytest.fixture(scope='function')
def update_character_template():
    return '''
        mutation {
            updateCharacter(input: { clientMutationId: "abc", description: %s, key: "%s" }) {
                clientMutationId
                ok
                character {
                    name
                    description
                }
            }
        }
    '''


@pytest.fixture(scope='function')
def friends_and_suggested_query():
    return '''
        query {
            character(name: "Rey") {
                friends {
                    edges {
                        node {
                            name
                        }
                    }
                }
                suggested {
                    edges {
                        node {
                            name
                        }
                    }
                }
            }
        }
    '''


def test_create_friendship(rey, leia, create_friendship_template, friends_and_suggested_query):
    mutation = create_friendship_template % (rey.key.urlsafe(), leia.key.urlsafe())

    names = lambda field, result: [character['node']['name'] for character in result.data['character'][field]['edges']]

    result = schema.execute(friends_and_suggested_query)

    assert not result.errors
    assert names('friends', result) == ['Finn', 'Han']
    assert names('suggested', result) == ['Leia']

    result = schema.execute(mutation)

    assert not result.errors
    assert result.data['createFriendship']['ok']
    assert result.data['createFriendship']['character1']['name'] == 'Rey'
    assert result.data['createFriendship']['character2']['name'] == 'Leia'

    result = schema.execute(friends_and_suggested_query)

    assert not result.errors
    assert names('friends', result) == ['Finn', 'Han', 'Leia']
    assert names('suggested', result) == []


def test_create_friendship_failure(rey, finn, create_friendship_template):
    mutation = create_friendship_template % (rey.key.urlsafe(), finn.key.urlsafe())
    result = schema.execute(mutation)

    assert result.errors[0].message == 'Friendship already exists'
    assert result.data['createFriendship'] is None


def test_create_character(resistance, create_character_template):
    mutation = create_character_template % ('C3PO', resistance.key.urlsafe())
    result = schema.execute(mutation)

    assert not result.errors
    assert result.data == {
        'createCharacter': {
            'clientMutationId': 'abc',
            'ok': True,
            'character': {
                'name': 'C3PO',
                'description': None,
                'faction': {
                    'name': resistance.name
                }
            }
        }
    }


def test_create_character_failure(resistance, create_character_template):
    mutation = create_character_template % ('C3PO', resistance.key.urlsafe())
    result = schema.execute(mutation)

    assert not result.errors

    result = schema.execute(mutation)

    assert result.errors[0].message == '"C3PO" already exists'
    assert result.data['createCharacter'] is None


def test_update_character(rey, update_character_template):
    mutation = update_character_template % (
        '"New captain of the Millennium Falcon."',
        rey.key.urlsafe()
    )

    assert rey.description == 'A new awakening in the Force.'

    result = schema.execute(mutation)

    assert rey.key.get().description == 'New captain of the Millennium Falcon.'
    assert not result.errors
    assert result.data == {
        'updateCharacter': {
            'clientMutationId': 'abc',
            'ok': True,
            'character': {
                'name': 'Rey',
                'description': 'New captain of the Millennium Falcon.'
            }
        }
    }


def test_update_character_failure(rey, update_character_template):
    mutation = update_character_template % (1, rey.key.urlsafe())

    assert rey.description == 'A new awakening in the Force.'

    result = schema.execute(mutation)

    assert rey.key.get().description == 'A new awakening in the Force.'
    assert not result.data
    assert 'In field "description": Expected type "String", found 1.' in result.errors[0].message

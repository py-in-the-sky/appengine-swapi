import pytest

from . import schema


@pytest.fixture(scope='function')
def create_friendship_template():
    return '''
        mutation {
            createFriendship(characterKey1: "%s", characterKey2: "%s") {
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
            createCharacter(name: "%s", factionKey: "%s") {
                ok
                character {
                    name
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
            updateCharacter(description: %s, key: "%s") {
                ok
                character {
                    description
                }
            }
        }
    '''


def test_create_friendship(rey, leia, create_friendship_template):
    mutation = create_friendship_template % (rey.key.urlsafe(), leia.key.urlsafe())
    query = '''
        query {
            character(name: "Rey") {
                friends {
                    name
                }
                suggested {
                    name
                }
            }
        }
    '''

    names = lambda field, result: [character['name'] for character in result.data['character'][field]]

    result = schema.execute(query)

    assert not result.errors
    assert names('friends', result) == ['Finn', 'Han']
    assert names('suggested', result) == ['Leia']

    result = schema.execute(mutation)

    assert not result.errors
    assert result.data['createFriendship']['ok']
    assert result.data['createFriendship']['character1']['name'] == 'Rey'
    assert result.data['createFriendship']['character2']['name'] == 'Leia'

    result = schema.execute(query)

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
            'ok': True,
            'character': {
                'name': 'C3PO',
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
            'ok': True,
            'character': {
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
    assert result.errors[0].message == 'Argument "description" has invalid value 1.\nExpected type "String", found 1.'

import json
import urllib

import pytest

from . import create_app
from config import config


@pytest.fixture(scope='module')
def app():
    return create_app(config['test'])


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()


def test_warmup(client):
    response = client.get('/_ah/warmup')
    assert response.data == 'Warmed up!'
    assert response.status == '200 OK'


def test_graphql(client, rey):
    query_template = '''
        query {
            character(%s: "%s") {
                name
            }
        }
    '''

    query = query_template % ('key', rey.key.urlsafe())
    graphql_query_path = '/graphql?query=%s' % urllib.quote(query)
    response = client.post(graphql_query_path)

    assert response.status == '200 OK'
    assert json.loads(response.data) == {
        'data': {
            'character': { 'name': 'Rey' }
        }
    }

    query = query_template % ('name', 'Chewie')
    graphql_query_path = '/graphql?query=%s' % urllib.quote(query)
    response = client.post(graphql_query_path)

    assert response.status == '200 OK'
    assert json.loads(response.data) == {
        'data': {
            'character': None
        }
    }

    query = query_template % ('key', 'BadKeyValue')
    graphql_query_path = '/graphql?query=%s' % urllib.quote(query)
    response = client.post(graphql_query_path)

    assert response.status == '400 BAD REQUEST'

    response_data = json.loads(response.data)

    assert not response_data.get('data')
    assert response_data.get('errors')

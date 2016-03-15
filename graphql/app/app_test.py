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


def test_graphql(client):
    query = '''
        query {
            hello
        }
    '''
    graphql_query_path = '/graphql?query=%s' % urllib.quote(query)
    response = client.post(graphql_query_path)

    assert response.status == '200 OK'
    assert json.loads(response.data) == {
        'data': {
            'hello': 'Hello, world!'
        }
    }

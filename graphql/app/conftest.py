import fix_sys_path  # pragma: no flakes

import os

import pytest
from google.appengine.ext.testbed import Testbed
from google.appengine.ext import ndb

from fixtures import ensure_minimal_data_in_datastore
from app.models.ndb.character import Character
from app.models.ndb.faction import Faction


@pytest.yield_fixture(scope='function')
def testbed():
    testbed = Testbed()
    testbed.activate()
    # testbed.setup_env(app_id='_')
    os.environ['APPLICATION_ID'] = '_'
    # This is a hack to get things working; `testbed.setup_env` does
    # not seem to be doing the job.
    # See: http://einaregilsson.com/unit-testing-model-classes-in-google-app-engine/

    # Will almost always need datastore for tests that use this fixture.
    testbed.init_datastore_v3_stub()
    # ndb uses memcache, so stub it as well.
    testbed.init_memcache_stub()
    # Clear in-context cache before test.
    ndb.get_context().clear_cache()

    yield testbed

    ndb.get_context().clear_cache()
    testbed.deactivate()


@pytest.fixture(scope='function')
def fixtures(testbed):
    ensure_minimal_data_in_datastore()
    ndb.get_context().clear_cache()


@pytest.fixture(scope='function')
def rey(fixtures):
    return Character.query(Character.name == 'Rey').get()


@pytest.fixture(scope='function')
def finn(fixtures):
    return Character.query(Character.name == 'Finn').get()


@pytest.fixture(scope='function')
def leia(fixtures):
    return Character.query(Character.name == 'Leia').get()


@pytest.fixture(scope='function')
def han(fixtures):
    return Character.query(Character.name == 'Han').get()


@pytest.fixture(scope='function')
def r2d2(resistance):
    return Character.create(name='R2D2', faction_key=resistance.key)


@pytest.fixture(scope='function')
def chewie(resistance):
    return Character.create(name='Chewie', faction_key=resistance.key)


@pytest.fixture(scope='function')
def resistance(fixtures):
    return Faction.query(Faction.name == 'The Resistance').get()


@pytest.fixture(scope='function')
def first_order(fixtures):
    return Faction.query(Faction.name == 'The First Order').get()

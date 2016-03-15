import fix_sys_path  # pragma: no flakes

import os

import pytest
from google.appengine.ext.testbed import Testbed
from google.appengine.ext import ndb


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

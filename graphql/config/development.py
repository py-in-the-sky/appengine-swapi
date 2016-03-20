from werkzeug.debug import DebuggedApplication
from werkzeug.contrib.profiler import ProfilerMiddleware

from .config import Config
from fixtures import ensure_minimal_data_in_datastore


DEBUG = 1
PROFILE = 0


class Development(Config):
    FLASK_CONFIG = 'development'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        if DEBUG:
            app.debug = True
            app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True, console_path='/_console')
            # In order for debug to work with GAE, use DebuggedApplication.

        if PROFILE:
            app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=('gae/app', 10))
            # For each HTTP request, log top ten slowest functions from the
            # source code in the `gae/app` directory.

        ensure_minimal_data_in_datastore()

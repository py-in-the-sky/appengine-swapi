from google.appengine.ext import ndb


class Config:

    @classmethod
    def init_app(cls, app):
        app.wsgi_app = ndb.toplevel(app.wsgi_app)
        # See: https://cloud.google.com/appengine/docs/python/ndb/async

def create_app(config):
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object(config)
    config.init_app(app)

    from .graphql import schema
    from flask_graphql import GraphQL
    GraphQL(app, schema=schema)
    # creates and registers graphql blueprint
    # /graphql
    # /graphiql


    @app.route('/_ah/warmup')
    def warmup():
        return 'Warmed up!'


    return app

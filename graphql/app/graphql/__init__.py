import graphene
from graphql.core.execution import Executor

from .query import Query
from .mutation import Mutation
from .ndb_future_middleware import NdbFutureMiddleware


class NdbFutureExecutor(Executor):
    def __init__(self, **kwargs):
        execution_middlewares = kwargs.pop('execution_middlewares', [NdbFutureMiddleware()])
        super(NdbFutureExecutor, self).__init__(execution_middlewares, **kwargs)

    def execute(self, *args, **kwargs):
        return super(NdbFutureExecutor, self).execute(*args, **kwargs).get_result()


schema = graphene.Schema(query=Query, mutation=Mutation, executor=NdbFutureExecutor())

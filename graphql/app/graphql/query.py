import graphene


class Query(graphene.ObjectType):
    hello = graphene.String(names=graphene.List(graphene.String()))
    foo = graphene.String()

    def resolve_hello(self, args, info):
        names = args.get('names')

        if not names:
            return 'Hello, world!'

        return '  '.join('Hello, %s!' % name for name in names)

    def resolve_foo(self, args, info):
        assert False, 'Intentional assertion error.'

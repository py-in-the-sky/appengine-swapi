import graphene
from graphene import relay
from google.appengine.ext import ndb

from .scalar import NdbKey, NdbCursor


class NdbPageInfo(graphene.ObjectType):
    has_next_page = graphene.Boolean(
        required=True,
        description='When paginating forwards, are there more items?'
    )
    has_previous_page = graphene.Boolean(
        required=True,
        description='When paginating backwards, are there more items?'
    )
    start_cursor = NdbCursor(description='When paginating backwards, the cursor to continue.')
    end_cursor = NdbCursor(description='When paginating forwards, the cursor to continue.')


class NdbEdge(graphene.ObjectType):
    "An edge in a connection"
    class Meta:
        type_name = 'NdbEdge'

    cursor = NdbCursor(required=True, description='A cursor for use in pagination.')

    for_node = classmethod(relay.Edge.for_node.__func__)  # Hack
    # Inheriting from relay.Edge and then overriding the cursor attribute throws an
    # error, so we do not inherit from relay.Edge.  In order to easily get the
    # functionality from relay.Edge, we take the unbound funtion (__func__) from
    # relay.Edge's sole class method and make it a class method on NdbEdge.
    # This works, but it poses a maintainability problem: if future versions of
    # the Graphene library introduce new class or instance methods on relay.Edge,
    # we have to be aware of them and explicitly add them to NdbEdge in this way in
    # order for them to be bound to the NdbEdge class and its instances.


class NdbConnection(relay.Connection):
    "A connection to a list of items"
    page_info = graphene.Field(
        NdbPageInfo,
        required=True,
        description='The Information to aid in pagination.'
    )


class NdbConnectionField(relay.ConnectionField):
    def __init__(self, type, connection_type=None, edge_type=None, **kwargs):
        new_kwargs = dict(
            first=graphene.Int(),
            last=graphene.Int(),
            before=NdbCursor(),
            after=NdbCursor(),
            reverse = graphene.Boolean(description='Reverse the order of results.'),
            **kwargs
        )
        super(relay.ConnectionField, self).__init__(type, **new_kwargs)  # Hack
        # This hack is necessary because relay.ConnectionField.__init__ will override
        # the type for `before` and `after`.
        self.connection_type = NdbConnection
        self.edge_type = NdbEdge

    @ndb.tasklet
    def from_list(self, connection_type, resolved, args, info):
        if isinstance(resolved, ndb.Future):
            resolved = yield resolved

        _edges, page_info, entity_transform = resolved
        edges = [connection_type.edge_type(node=entity_transform(e.entity), cursor=e.cursor) for e in _edges]
        connection = connection_type(edges=edges, page_info=NdbPageInfo(**page_info._asdict()))
        raise ndb.Return(connection)


def construct_from_ndb_entity(object_type, ndb_entity):
    field_names = [f.attname for f in object_type._meta.fields]
    kwargs = ndb_entity.to_dict(include=field_names)

    if 'key' in field_names:
        kwargs['key'] = ndb_entity.key

    if 'id' in field_names:
        kwargs['id'] = ndb_entity.key.urlsafe()

    return object_type(**kwargs)


class NdbObjectType(graphene.Interface):
    key = graphene.NonNull(NdbKey)

    from_ndb_entity = classmethod(construct_from_ndb_entity)


class NdbNodeMixin(graphene.Interface):
    key = graphene.NonNull(NdbKey)

    connection_type = NdbConnection
    edge_type = NdbEdge

    from_ndb_entity = classmethod(construct_from_ndb_entity)

    @classmethod
    def get_node(cls, ndb_key_string, info):
        entity = ndb.Key(urlsafe=ndb_key_string).get()
        return cls.from_ndb_entity(entity)

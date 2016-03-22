import graphene
from google.appengine.ext import ndb

from .scalar import NdbKey


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

    from_ndb_entity = classmethod(construct_from_ndb_entity)

    @classmethod
    def get_node(cls, ndb_key_string, info):
        entity = ndb.Key(urlsafe=ndb_key_string).get()
        return cls.from_ndb_entity(entity)

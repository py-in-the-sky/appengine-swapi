import graphene
from graphene import relay

from .compound import NdbNodeMixin
from .scalar import DateTime


def test_ndb_node(rey):
    class CharacterNode(relay.Node, NdbNodeMixin):
        name = graphene.String()
        created = graphene.Field(DateTime)

    key_string = rey.key.urlsafe()
    node = CharacterNode.get_node(key_string, None)

    assert node.name == rey.name
    assert node.created == rey.created
    assert node.key == rey.key
    assert node.id == rey.key.urlsafe()

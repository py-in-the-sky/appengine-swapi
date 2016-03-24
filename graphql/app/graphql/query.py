import graphene
from graphene import relay
from google.appengine.ext import ndb

from app.models.ndb.faction import Faction as NdbFaction
from app.models.ndb.character import Character as NdbCharacter
from .custom_types.compound import NdbNodeMixin, NdbConnectionField
from .custom_types.scalar import DateTime, NdbKey


class Character(relay.Node, NdbNodeMixin):
    name = graphene.String().NonNull
    description = graphene.String()
    created = graphene.NonNull(DateTime)
    updated = graphene.NonNull(DateTime)
    faction = graphene.NonNull('Faction')
    friends = NdbConnectionField('Character')
    suggested = NdbConnectionField('Character')

    @ndb.tasklet
    def resolve_friends(self, args, info):
        friends = yield self.key.get().get_friends()
        raise ndb.Return([Character.from_ndb_entity(f) for f in friends])

    @ndb.tasklet
    def resolve_suggested(self, args, info):
        suggested = yield self.key.get().get_friends_of_friends()
        raise ndb.Return([Character.from_ndb_entity(s) for s in suggested])

    @ndb.tasklet
    def resolve_faction(self, args, info):
        faction = yield self.key.get().faction_key.get_async()
        raise ndb.Return(Faction.from_ndb_entity(faction))


class Faction(relay.Node, NdbNodeMixin):
    name = graphene.String().NonNull
    description = graphene.String()
    created = graphene.NonNull(DateTime)
    updated = graphene.NonNull(DateTime)
    characters = NdbConnectionField(Character)

    @ndb.tasklet
    def resolve_characters(self, args, info):
        characters = yield self.key.get().get_characters()
        raise ndb.Return([Character.from_ndb_entity(c) for c in characters])


class Query(graphene.ObjectType):
    faction = graphene.Field(
        Faction,
        key=graphene.Argument(NdbKey),
        name=graphene.String(),
    )
    factions = NdbConnectionField(Faction)
    character = graphene.Field(
        Character,
        key=graphene.Argument(NdbKey),
        name=graphene.String(),
    )
    characters = NdbConnectionField(Character)
    node = relay.NodeField()

    @ndb.tasklet
    def resolve_faction(self, args, info):
        faction_key = args.get('key')
        if faction_key:
            faction = yield faction_key.get_async()
            if faction:
                raise ndb.Return(Faction.from_ndb_entity(faction))

        faction_name = args.get('name')
        if faction_name:
            faction = yield NdbFaction.get_by_name(faction_name)
            if faction:
                raise ndb.Return(Faction.from_ndb_entity(faction))

    @ndb.tasklet
    def resolve_factions(self, args, info):
        factions = yield NdbFaction.query().fetch_async()
        raise ndb.Return([Faction.from_ndb_entity(f) for f in factions])

    @ndb.tasklet
    def resolve_character(self, args, info):
        character_key = args.get('key')
        if character_key:
            character = yield character_key.get_async()
            if character:
                raise ndb.Return(Character.from_ndb_entity(character))

        character_name = args.get('name')
        if character_name:
            character = yield NdbCharacter.get_by_name(character_name)
            if character:
                raise ndb.Return(Character.from_ndb_entity(character))

    @ndb.tasklet
    def resolve_characters(self, args, info):
        characters = yield NdbCharacter.query().fetch_async()
        raise ndb.Return([Character.from_ndb_entity(c) for c in characters])

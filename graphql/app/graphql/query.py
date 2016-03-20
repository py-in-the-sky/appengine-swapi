import graphene

from app.models.ndb.faction import Faction as NdbFaction
from app.models.ndb.character import Character as NdbCharacter
from .custom_types.compound import NdbObjectType
from .custom_types.scalar import DateTime, NdbKey


class Character(NdbObjectType):
    name = graphene.String().NonNull
    description = graphene.String()
    created = graphene.NonNull(DateTime)
    updated = graphene.NonNull(DateTime)
    friends = graphene.List('Character').NonNull
    suggested = graphene.List('Character').NonNull
    faction = graphene.NonNull('Faction')

    def resolve_friends(self, args, info):
        friends = self.key.get().get_friends()
        return [Character.from_ndb_entity(f) for f in friends]

    def resolve_suggested(self, args, info):
        suggested = self.key.get().get_friends_of_friends()
        return [Character.from_ndb_entity(s) for s in suggested]

    def resolve_faction(self, args, info):
        faction = self.key.get().faction_key.get()
        return Faction.from_ndb_entity(faction)


class Faction(NdbObjectType):
    name = graphene.String().NonNull
    description = graphene.String()
    created = graphene.NonNull(DateTime)
    updated = graphene.NonNull(DateTime)
    characters = graphene.List(Character).NonNull

    def resolve_characters(self, args, info):
        characters = self.key.get().get_characters()
        return [Character.from_ndb_entity(c) for c in characters]


class Query(graphene.ObjectType):
    faction = graphene.Field(
        Faction,
        key=graphene.Argument(NdbKey),
        name=graphene.String(),
    )
    factions = graphene.List(Faction).NonNull
    character = graphene.Field(
        Character,
        key=graphene.Argument(NdbKey),
        name=graphene.String(),
    )
    characters = graphene.List(Character).NonNull

    def resolve_faction(self, args, info):
        faction_key = args.get('key')
        if faction_key:
            faction = faction_key.get()
            if faction:
                return Faction.from_ndb_entity(faction)

        faction_name = args.get('name')
        if faction_name:
            faction = NdbFaction.get_by_name(faction_name)
            if faction:
                return Faction.from_ndb_entity(faction)

    def resolve_factions(self, args, info):
        factions = NdbFaction.query().fetch()
        return [Faction.from_ndb_entity(f) for f in factions]

    def resolve_character(self, args, info):
        character_key = args.get('key')
        if character_key:
            character = character_key.get()
            if character:
                return Character.from_ndb_entity(character)

        character_name = args.get('name')
        if character_name:
            character = NdbCharacter.get_by_name(character_name)
            if character:
                return Character.from_ndb_entity(character)

    def resolve_characters(self, args, info):
        characters = NdbCharacter.query().fetch()
        return [Character.from_ndb_entity(c) for c in characters]

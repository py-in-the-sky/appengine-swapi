import graphene
from graphene import relay

from app.models.ndb.character import Character as NdbCharacter
from .custom_types.scalar import NdbKey
from .query import Character


class CreateCharacter(relay.ClientIDMutation):
    class Input:
        name = graphene.String().NonNull
        description = graphene.String()
        faction_key = graphene.NonNull(NdbKey)

    ok = graphene.Boolean().NonNull
    character = graphene.NonNull(Character)

    @classmethod
    def mutate_and_get_payload(cls, input, info):
        character = NdbCharacter.create(**input)
        return cls(
            ok=bool(character),
            character=Character.from_ndb_entity(character)
        )


class CreateFriendship(relay.ClientIDMutation):
    class Input:
        character_key_1 = graphene.NonNull(NdbKey)
        character_key_2 = graphene.NonNull(NdbKey)

    ok = graphene.Boolean().NonNull
    character_1 = graphene.NonNull(Character)
    character_2 = graphene.NonNull(Character)

    @classmethod
    def mutate_and_get_payload(cls, input, info):
        character_1, character_2 = NdbCharacter.create_friendship(
            input['character_key_1'],
            input['character_key_2']
        )
        return cls(
            ok=bool(character_1) and bool(character_2),
            character_1=Character.from_ndb_entity(character_1),
            character_2=Character.from_ndb_entity(character_2)
        )


class UpdateCharacter(relay.ClientIDMutation):
    class Input:
        key = graphene.NonNull(NdbKey)
        description = graphene.String()

    ok = graphene.Boolean().NonNull
    character = graphene.NonNull(Character)

    @classmethod
    def mutate_and_get_payload(cls, input, info):
        character = input['key'].get()

        if 'description' in input:
            new_description = input['description']
            character.description = new_description

        character.put()
        return cls(
            ok=bool(character),
            character=Character.from_ndb_entity(character)
        )


class Mutation(graphene.ObjectType):
    create_character = graphene.Field(CreateCharacter)
    update_character = graphene.Field(UpdateCharacter)
    create_friendship = graphene.Field(CreateFriendship)

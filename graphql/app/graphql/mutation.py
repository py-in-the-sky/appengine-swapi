import graphene

from app.models.ndb.character import Character as NdbCharacter
from .custom_types.scalar import NdbKey
from .query import Character


class CreateCharacter(graphene.Mutation):
    class Input:
        name = graphene.String().NonNull
        description = graphene.String()
        faction_key = graphene.NonNull(NdbKey)

    ok = graphene.Boolean().NonNull
    character = graphene.NonNull(Character)

    @classmethod
    def mutate(cls, instance, args, info):
        character = NdbCharacter.create(**args)
        return cls(
            character=Character.from_ndb_entity(character),
            ok=bool(character)
        )


class CreateFriendship(graphene.Mutation):
    class Input:
        character_key_1 = graphene.NonNull(NdbKey)
        character_key_2 = graphene.NonNull(NdbKey)

    ok = graphene.Boolean().NonNull
    character_1 = graphene.NonNull(Character)
    character_2 = graphene.NonNull(Character)

    @classmethod
    def mutate(cls, instance, args, info):
        character_1, character_2 = NdbCharacter.create_friendship(
            args['character_key_1'],
            args['character_key_2']
        )
        return cls(
            ok=bool(character_1) and bool(character_2),
            character_1=Character.from_ndb_entity(character_1),
            character_2=Character.from_ndb_entity(character_2)
        )


class UpdateCharacter(graphene.Mutation):
    class Input:
        key = graphene.NonNull(NdbKey)
        description = graphene.String()

    ok = graphene.Boolean().NonNull
    character = graphene.NonNull(Character)

    @classmethod
    def mutate(cls, instance, args, info):
        character = args['key'].get()

        if 'description' in args:
            new_description = args['description']
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

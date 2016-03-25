import datetime

from graphene.core.classtypes import Scalar
from graphql.core.language import ast
from google.appengine.ext import ndb
from google.appengine.datastore import datastore_query


class DateTime(Scalar):
    "DateTime"
    # From: http://graphene-python.org/docs/basic-types/
    @staticmethod
    def serialize(dt):
        return dt.isoformat()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return datetime.datetime.strptime(node.value, "%Y-%m-%dT%H:%M:%S.%f")

    @staticmethod
    def parse_value(value):
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")


class NdbKey(Scalar):
    "NdbKey"
    @staticmethod
    def serialize(key):
        return key.urlsafe()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return ndb.Key(urlsafe=node.value)

    @staticmethod
    def parse_value(value):
        return ndb.Key(urlsafe=value)


class NdbCursor(Scalar):
    "NdbCursor"
    @staticmethod
    def serialize(cursor):
        return cursor.urlsafe()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return datastore_query.Cursor(urlsafe=node.value)

    @staticmethod
    def parse_value(value):
        return datastore_query.Cursor(urlsafe=value)

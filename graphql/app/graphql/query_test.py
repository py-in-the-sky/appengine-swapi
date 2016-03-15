from . import schema


def test_query():
    result = schema.execute('''
        query {
            hello
        }
    ''')

    assert result.data['hello'] == 'Hello, world!'
    assert not result.errors


def test_query_complex():
    result = schema.execute('''
        query {
            hello(names: ["Foo", "Bar", "Baz"])
            foo
        }
    ''')

    assert result.data == {
        'hello': 'Hello, Foo!  Hello, Bar!  Hello, Baz!',
        'foo': None
    }
    assert len(result.errors) == 1
    assert result.errors[0].message == 'Intentional assertion error.'

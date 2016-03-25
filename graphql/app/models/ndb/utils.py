from collections import namedtuple

from google.appengine.ext import ndb
from google.appengine.ext.db import BadArgumentError


PAGE_SIZE = 2
PageInfo = namedtuple('PageInfo', 'start_cursor end_cursor has_next_page has_previous_page')
EdgeInfo = namedtuple('EdgeInfo', 'entity cursor')


def paginated_query(q_forward, q_backward, first=None, last=None, before=None, after=None, reverse=False, **kwargs):
    if reverse:
        q_forward, q_backward = q_backward, q_forward

    if before and not after:
        page_size = last or PAGE_SIZE
        return page_backward(q_backward, page_size, before, **kwargs)
    else:
        page_size = first or PAGE_SIZE
        return page_forward(q_forward, page_size, after, before, **kwargs)


@ndb.tasklet
def page_backward(q_backward, page_size, start_cursor):
    itr = q_backward.iter(start_cursor=start_cursor, limit=page_size, produce_cursors=True)
    reversed_result = []

    while (yield  itr.has_next_async()):
        entity = itr.next()
        reversed_result.append(EdgeInfo(entity, itr.cursor_before()))

    result = reversed(reversed_result)
    _end_cursor = start_cursor

    try:
        _start_cursor = itr.cursor_after()
    except BadArgumentError:
        _start_cursor = None

    has_next_page = bool(start_cursor)
    has_previous_page = itr.probably_has_next()
    page_info = PageInfo(_start_cursor, _end_cursor, has_next_page, has_previous_page)
    raise ndb.Return((result, page_info))


@ndb.tasklet
def page_forward(q_forward, page_size, start_cursor, end_cursor):
    itr = q_forward.iter(start_cursor=start_cursor, end_cursor=end_cursor, limit=page_size, produce_cursors=True)
    result = []

    while (yield itr.has_next_async()):
        entity = itr.next()
        result.append(EdgeInfo(entity, itr.cursor_before()))

    try:
        _end_cursor = itr.cursor_after()
    except BadArgumentError:
        _end_cursor = None

    has_next_page = itr.probably_has_next()
    has_previous_page = bool(start_cursor)
    page_info = PageInfo(start_cursor, _end_cursor, has_next_page, has_previous_page)
    raise ndb.Return((result, page_info))

# coding: utf-8
import os
import json
import logging

logger = logging.getLogger(__name__)

_CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
JOURNALS = {}


def _load_query_from_file(file_name):

    if os.path.isdir(file_name):
        return None

    with open(file_name, 'r') as f:
        try:
            query = json.load(f)
            return query
        except ValueError:
            logger.warning(' Fail to load custom query (invalid json) for: %s' % file_name)
            return None


def _load_queries():

    for f in os.listdir(_CURRENT_DIR + '/templates'):
        issn = f[:9]
        file_name = _CURRENT_DIR + '/templates/%s' % f

        query = _load_query_from_file(file_name)

        if query:
            JOURNALS[issn] = json.dumps(query)


def load(issn):

    return json.loads(JOURNALS.get(issn, '{}'))

_load_queries()
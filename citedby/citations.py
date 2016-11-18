# coding: utf-8
import os
import csv
import logging
import json
import copy

logger = logging.getLogger(__name__)

_CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

_DOCUMENTS = {}

with open(_CURRENT_DIR + '/data/citations.json', 'r') as metrics:

    for line in metrics:

        item = json.loads(line)

        _DOCUMENTS[item['article']['code']] = item


def raw_data(pid):

    return copy.deepcopy(_DOCUMENTS.get(pid, None))

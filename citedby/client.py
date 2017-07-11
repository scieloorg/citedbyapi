# coding: utf-8

import os
import thriftpy
import json
import logging
import time

# URLJOIN Python 3 and 2 import compatibilities
try:
    from urllib.parse import urljoin
except:
    from urlparse import urljoin

import requests
from thriftpy.rpc import make_client

from citedby import citations

logger = logging.getLogger(__name__)


class CitedByExceptions(Exception):
    pass


class ServerError(CitedByExceptions):
    pass


class RestfulClient(object):

    CITEDBY_URL = 'http://citedby.scielo.org'
    PID_ENDPOINT = '/api/v1/pid/'
    METADATA_ENDPOINT = '/api/v1/meta/'
    DOI_ENDPOINT = '/api/v1/doi/'
    ATTEMPTS = 10

    def __init__(self, domain=None):

        if domain:
            self.CITEDBY_URL = 'http://%s' % domain

    def _do_request(self, url, params=None, content=None, timeout=3, method='GET'):

        request = requests.get
        params = params if params else {}

        if method == 'POST':
            request = requests.post
        if method == 'DELETE':
            request = requests.delete

        result = None
        for attempt in range(self.ATTEMPTS):
            # Throttling requests to the API. Our servers will throttle accesses to the API from the same IP in 3 per second.
            # So, to not receive a "too many connections error (249 HTTP ERROR)", do not change this line.
            time.sleep(0.4)
            try:
                result = request(url, params=params, timeout=timeout)
                if result.status_code == 401:
                    logger.error('Unautorized Access for (%s)' % url)
                    logger.exception(UnauthorizedAccess())
                break
            except requests.RequestException as e:
                logger.error('fail retrieving data from (%s) attempt(%d/%d)' % (url, attempt+1, self.ATTEMPTS))
                logger.exception(e)
                continue

        if not result:
            return

        try:
            return result.json()
        except:
            return result.text

    def citedby_pid(self, pid, metaonly=False, from_heap=True):
        """
        Retrieve citedby documents from a given PID number.

        pid: SciELO PID number
        metaonly: will retrieve only the metadata of the requested article citations including the number of citations it has received.
        from_heap: will retrieve the number of citations from a preproduced report, it will not fetch the api. Much faster results but not extremely updated.
        """

        if from_heap is True:
            result = citations.raw_data(pid)

            if result and 'cited_by' in result and metaonly is True:
                del(result['cited_by'])
                return result

            if result:
                return result

        url = urljoin(self.CITEDBY_URL, self.PID_ENDPOINT)

        params = {
            "q": pid,
            "metaonly": "true" if metaonly is True else "false"
        }

        result = self._do_request(url, params=params)

        return result

    def citedby_meta(self, document_title,
        document_first_author=None, document_year=None, metaonly=False):

        url = urljoin(self.CITEDBY_URL, self.METADATA_ENDPOINT)

        params = {
            "title": document_title,
            "author": document_first_author,
            "year": document_year,
            "metaonly": "true" if metaonly is True else "false"
        }

        result = self._do_request(url, params=params)

        return result

    def citedby_doi(self, doi, metaonly=False):

        url = urljoin(self.CITEDBY_URL, self.DOI_ENDPOINT)

        params = {
            "q": doi,
            "metaonly": "true" if metaonly is True else "false"
        }

        result = self._do_request(url, params=params)

        return result


class ThriftClient(object):
    CITEDBY_THRIFT = thriftpy.load(
        os.path.join(os.path.dirname(__file__))+'/thrift/citedby.thrift')

    def __init__(self, domain=None):
        """
        Cliente thrift para o Articlemeta.
        """
        self.domain = domain or 'citedby.scielo.org:11610'
        self._set_address()

    def _set_address(self):

        address = self.domain.split(':')

        self._address = address[0]
        try:
            self._port = int(address[1])
        except:
            self._port = 11620

    @property
    def client(self):

        client = make_client(
            self.CITEDBY_THRIFT.Citedby,
            self._address,
            self._port
        )

        return client

    def citedby_pid(self, pid, metaonly=False, from_heap=True):
        """
        Retrieve citedby documents from a given PID number.

        pid: SciELO PID number
        metaonly: will retrieve only the metadata of the requested article citations including the number of citations it has received.
        from_heap: will retrieve the number of citations from a preproduced report, it will not fetch the api. Much faster results but not extremelly updated.
        """

        if from_heap is True:
            result = citations.raw_data(pid)

            if result and 'cited_by' in result and metaonly is True:
                del(result['cited_by'])
                return result

            if result:
                return result

        result = self.client.citedby_pid(pid, metaonly=metaonly)

        try:
            return json.loads(result)
        except:
            return None

    def citedby_meta(self, document_title, document_first_author=None,
        document_year=None, metaonly=False):

        result = self.client.citedby_meta(document_title, document_first_author,
            document_year, metaonly=metaonly)

        try:
            return json.loads(result)
        except:
            return None

    def citedby_doi(self, doi, metaonly=False):
        result = self.client.citedby_doi(doi, metaonly=metaonly)

        try:
            return json.loads(result)
        except:
            return None

    def search(self, dsl, params):
        """
        Free queries to ES index.

        dsl (string): with DSL query
        params (list): [(key, value), (key, value)]
            where key is a query parameter, and value is the value required for parameter, ex: [('size', '0'), ('search_type', 'count')]
        """

        query_parameters = []
        for key, value in params:
            query_parameters.append(self.CITEDBY_THRIFT.kwargs(str(key), str(value)))

        try:
            result = self.client.search(dsl, query_parameters)
        except self.CITEDBY_THRIFT.ServerError:
            raise ServerError('you may trying to run a bad DSL Query')

        try:
            return json.loads(result)
        except:
            return None

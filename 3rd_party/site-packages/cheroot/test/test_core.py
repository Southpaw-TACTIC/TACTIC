"""Tests for managing HTTP issues (malformed requests, etc)."""
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 :

import errno
import socket

from six.moves import urllib, http_client

import pytest
import six

from cheroot.test import helper


HTTP_BAD_REQUEST = 400
HTTP_LENGTH_REQUIRED = 411
HTTP_NOT_FOUND = 404
HTTP_OK = 200
HTTP_VERSION_NOT_SUPPORTED = 505


class HelloController(helper.Controller):
    def hello(req, resp):
        return 'Hello world!'

    def body_required(req, resp):
        if req.environ.get('Content-Length', None) is None:
            resp.status = '411 Length Required'
            return
        return 'Hello world!'

    def query_string(req, resp):
        return req.environ.get('QUERY_STRING', '')

    def asterisk(req, resp):
        method = req.environ.get('REQUEST_METHOD', 'NO METHOD FOUND')
        tmpl = 'Got asterisk URI path with {method} method'
        return tmpl.format(**locals())

    def _munge(string):
        """
        WSGI 1.0 is a mess around unicode. Create endpoints
        that match the PATH_INFO that it produces.
        """
        if six.PY3:
            return string.encode('utf-8').decode('latin-1')
        return string

    handlers = {
        '/hello': hello,
        '/no_body': hello,
        '/body_required': body_required,
        '/query_string': query_string,
        _munge('/привіт'): hello,
        _munge('/Юххууу'): hello,
        '/\xa0Ðblah key 0 900 4 data': hello,
        '/*': asterisk,
    }


class HTTPTests(helper.CherootWebCase):

    @classmethod
    def setup_server(cls):
        cls.httpserver.wsgi_app = HelloController()
        cls.httpserver.max_request_body_size = 30000000

    def _get_http_connection(self):
        """Instantiate connection object depending on scheme"""
        name = '{interface}:{port}'.format(
            interface=self.interface(),
            port=self.PORT,
        )
        return self._Conn(name)

    @staticmethod
    def _get_http_response(connection, method='GET'):
        c = connection
        kwargs = {'strict': c.strict} if hasattr(c, 'strict') else {}
        # Python 3.2 removed the 'strict' feature, saying:
        # "http.client now always assumes HTTP/1.x compliant servers."
        return c.response_class(c.sock, method=method, **kwargs)

    def test_http_connect_request(self):
        self.getPage('/anything', method='CONNECT')
        self.assertStatus(405)

    def test_normal_request(self):
        self.getPage('/hello')
        self.assertStatus(HTTP_OK)
        self.assertBody(b'Hello world!')

    def test_query_string_request(self):
        self.getPage('/query_string?test=True')
        self.assertStatus(HTTP_OK)
        self.assertBody(b'test=True')

    def _test_parse_acceptable_uri(self, uri):
        self.getPage(uri)
        self.assertStatus(HTTP_OK)

    def test_parse_uri_plain(self):
        self._test_parse_acceptable_uri('/hello')

    def test_parse_uri_query(self):
        self._test_parse_acceptable_uri('/query_string?test=True')

    def test_parse_uri_quoted_unicode(self):
        uri = '/{0}?{1}={2}'.format(
            *map(urllib.parse.quote, ('Юххууу', 'ї', 'йо'))
        )
        self._test_parse_acceptable_uri(uri)

    @pytest.mark.xfail(six.PY2, reason='Fails on Python 2')
    def test_parse_uri_unsafe_uri(self):
        """Test that malicious URI does not allow HTTP injection.

        This effectively checks that sending GET request with URL

        /%A0%D0blah%20key%200%20900%204%20data

        is not converted into

        GET /
        blah key 0 900 4 data
        HTTP/1.1

        which would be a security issue otherwise.
        """
        c = self._get_http_connection()
        resource = '/\xa0Ðblah key 0 900 4 data'.encode('latin-1')
        quoted = urllib.parse.quote(resource)
        assert quoted == '/%A0%D0blah%20key%200%20900%204%20data'
        request = 'GET {quoted} HTTP/1.1'.format(**locals())
        c._output(request.encode('utf-8'))
        c._send_output()
        response = self._get_http_response(c, method='GET')
        response.begin()
        assert response.status == HTTP_OK
        assert response.fp.read(12) == b'Hello world!'
        c.close()

    def test_parse_uri_invalid_uri(self):
        c = self._get_http_connection()
        c._output(u'GET /йопта! HTTP/1.1'.encode('utf-8'))
        c._send_output()
        response = self._get_http_response(c, method='GET')
        response.begin()
        assert response.status == HTTP_BAD_REQUEST
        assert response.fp.read(21) == b'Malformed Request-URI'
        c.close()

    def _test_parse_no_leading_slash_invalid(self, uri):
        """
        URIs with no leading slash produce a 400
        """
        self.getPage(urllib.parse.quote(uri))
        self.assertStatus(HTTP_BAD_REQUEST)
        assert b'starting with a slash' in self.body

    # TODO: the following two tests could be implemented as a
    # parametrized fixture on one test if only this test suite
    # weren't based on unittest.
    def test_parse_no_leading_slash_invalid_ascii(self):
        self._test_parse_no_leading_slash_invalid('hello')

    def test_parse_no_leading_slash_invalid_non_ascii(self):
        self._test_parse_no_leading_slash_invalid('привіт')

    def test_parse_uri_absolute_uri(self):
        self.getPage('http://google.com/')
        self.assertStatus(HTTP_BAD_REQUEST)
        self.assertBody(b'Absolute URI not allowed if server is not a proxy.')

    def test_parse_uri_asterisk_uri(self):
        self.getPage('*', method='OPTIONS')
        self.assertStatus(HTTP_OK)
        self.assertBody(b'Got asterisk URI path with OPTIONS method')

    def test_parse_uri_fragment_uri(self):
        self.getPage('/hello?test=something#fake')
        self.assertStatus(HTTP_BAD_REQUEST)
        self.assertBody(b'Illegal #fragment in Request-URI.')

    def test_no_content_length(self):
        # "The presence of a message-body in a request is signaled by the
        # inclusion of a Content-Length or Transfer-Encoding header field in
        # the request's message-headers."
        #
        # Send a message with neither header and no body.
        c = self._get_http_connection()
        c.request('POST', '/no_body')
        response = c.getresponse()
        self.body = response.fp.read()
        self.status = str(response.status)
        self.assertStatus(HTTP_OK)
        self.assertBody(b'Hello world!')

    def test_content_length_required(self):
        # Now send a message that has no Content-Length, but does send a body.
        # Verify that CP times out the socket and responds
        # with 411 Length Required.

        c = self._get_http_connection()
        c.request('POST', '/body_required')
        response = c.getresponse()
        self.body = response.fp.read()

        self.status = str(response.status)
        self.assertStatus(HTTP_LENGTH_REQUIRED)

    def test_malformed_request_line(self):
        """Test missing or invalid HTTP version in Request-Line."""

        c = self._get_http_connection()
        c._output(b'GET /')
        c._send_output()
        response = self._get_http_response(c, method='GET')
        response.begin()
        assert response.status == HTTP_BAD_REQUEST
        assert response.fp.read(22) == b'Malformed Request-Line'
        c.close()

        c = self._get_http_connection()
        c._output(b'GET / HTTPS/1.1')
        c._send_output()
        response = self._get_http_response(c, method='GET')
        response.begin()
        assert response.status == HTTP_BAD_REQUEST
        assert response.fp.read(36) == b'Malformed Request-Line: bad protocol'
        c.close()

        c = self._get_http_connection()
        c._output(b'GET / HTTP/2.15')
        c._send_output()
        response = self._get_http_response(c, method='GET')
        response.begin()
        assert response.status == HTTP_VERSION_NOT_SUPPORTED
        assert response.fp.read(22) == b'Cannot fulfill request'
        c.close()

    def test_malformed_http_method(self):

        c = self._get_http_connection()
        c.putrequest('GeT', '/malformed_method_case')
        c.putheader('Content-Type', 'text/plain')
        c.endheaders()

        response = c.getresponse()
        self.status = str(response.status)
        self.assertStatus(HTTP_BAD_REQUEST)
        self.body = response.fp.read(21)
        self.assertBody('Malformed method name')

    def test_malformed_header(self):

        c = self._get_http_connection()
        c.putrequest('GET', '/')
        c.putheader('Content-Type', 'text/plain')
        # See http://www.bitbucket.org/cherrypy/cherrypy/issue/941
        c._output(b'Re, 1.2.3.4#015#012')
        c.endheaders()

        response = c.getresponse()
        self.status = str(response.status)
        self.assertStatus(HTTP_BAD_REQUEST)
        self.body = response.fp.read(20)
        self.assertBody('Illegal header line.')

    def test_request_line_split_issue_1220(self):

        Request_URI = (
            '/hello?'
            'intervenant-entreprise-evenement_classaction='
            'evenement-mailremerciements'
            '&_path=intervenant-entreprise-evenement'
            '&intervenant-entreprise-evenement_action-id=19404'
            '&intervenant-entreprise-evenement_id=19404'
            '&intervenant-entreprise_id=28092'
        )
        self.assertEqual(len('GET %s HTTP/1.1\r\n' % Request_URI), 256)
        self.getPage(Request_URI)
        self.assertBody('Hello world!')

    def test_garbage_in(self):
        # Connect without SSL regardless of server.scheme

        c = http_client.HTTPConnection('%s:%s' % (self.interface(), self.PORT))
        c._output(b'gjkgjklsgjklsgjkljklsg')
        c._send_output()
        response = c.response_class(c.sock, method='GET')
        try:
            response.begin()
            self.assertEqual(response.status, HTTP_BAD_REQUEST)
            self.assertEqual(response.fp.read(22), b'Malformed Request-Line')
            c.close()
        except socket.error as ex:
            # "Connection reset by peer" is also acceptable.
            if ex.errno != errno.ECONNRESET:
                raise

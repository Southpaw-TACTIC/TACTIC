"""Tests for TCP connection handling, including proper and timely close."""

import socket
import time

from six.moves import range, http_client, urllib

import six
import pytest

from cheroot.test import helper, webtest


# avpytestmark = pytest.mark.skip(reason="incomplete")


timeout = 1
pov = 'pPeErRsSiIsStTeEnNcCeE oOfF vViIsSiIoOnN'


class Controller(helper.Controller):
    def hello(req, resp):
        return 'Hello, world!'

    def pov(req, resp):
        return pov

    def stream(req, resp):
        if 'set_cl' in req.environ['QUERY_STRING']:
            resp.headers['Content-Length'] = str(10)

        def content():
            for x in range(10):
                yield str(x)

        return content()

    def upload(req, resp):
        if not req.environ['REQUEST_METHOD'] == 'POST':
            raise AssertionError("'POST' != request.method %r" %
                                 req.environ['REQUEST_METHOD'])
        return "thanks for '%s'" % req.environ['wsgi.input'].read()

    def custom_204(req, resp):
        resp.status = '204'
        return 'Code = 204'

    def custom_304(req, resp):
        resp.status = '304'
        return 'Code = 304'

    def err_before_read(req, resp):
        resp.status = '500 Internal Server Error'
        return 'ok'

    def one_megabyte_of_a(req, resp):
        return ['a' * 1024] * 1024

    def wrong_cl_buffered(req, resp):
        resp.headers['Content-Length'] = '5'
        return 'I have too many bytes'

    def wrong_cl_unbuffered(req, resp):
        resp.headers['Content-Length'] = '5'
        return ['I too', ' have too many bytes']

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
        '/pov': pov,
        '/page1': pov,
        '/page2': pov,
        '/page3': pov,
        '/stream': stream,
        '/upload': upload,
        '/custom/204': custom_204,
        '/custom/304': custom_304,
        '/err_before_read': err_before_read,
        '/one_megabyte_of_a': one_megabyte_of_a,
        '/wrong_cl_buffered': wrong_cl_buffered,
        '/wrong_cl_unbuffered': wrong_cl_unbuffered,
    }


class ConnectionCloseTests(helper.CherootWebCase):

    @classmethod
    def setup_server(cls):
        app = Controller()

        def _timeout(req, resp):
            return str(cls.httpserver.timeout)
        app.handlers['/timeout'] = _timeout
        cls.httpserver.wsgi_app = app
        cls.httpserver.max_request_body_size = 1001
        cls.httpserver.timeout = timeout

    def test_HTTP11_persistent_connections(self):
        self.httpserver.protocol = 'HTTP/1.1'
        self.PROTOCOL = 'HTTP/1.1'

        self.persistent = True

        # Make the first request and assert there's no "Connection: close".
        self.getPage('/pov')
        self.assertStatus('200 OK')
        self.assertBody(pov)
        self.assertNoHeader('Connection')

        # Make another request on the same connection.
        self.getPage('/page1')
        self.assertStatus('200 OK')
        self.assertBody(pov)
        self.assertNoHeader('Connection')

        # Test client-side close.
        self.getPage('/page2', headers=[('Connection', 'close')])
        self.assertStatus('200 OK')
        self.assertBody(pov)
        self.assertHeader('Connection', 'close')

        # Make another request on the same connection, which should error.
        self.assertRaises(http_client.NotConnected, self.getPage, '/pov')

    def test_Streaming_no_len_11(self):
        self._streaming_11(set_cl=False)

    def test_Streaming_with_len_11(self):
        self._streaming_11(set_cl=True)

    def test_Streaming_no_len_10(self):
        self._streaming_10(set_cl=False)

    def test_Streaming_with_len_10(self):
        self._streaming_10(set_cl=True)

    def _streaming_11(self, set_cl):
        self.httpserver.protocol = 'HTTP/1.1'
        self.PROTOCOL = 'HTTP/1.1'

        self.persistent = True

        # Make the first request and assert there's no "Connection: close".
        self.getPage('/pov')
        self.assertStatus('200 OK')
        self.assertBody(pov)
        self.assertNoHeader('Connection')

        # Make another, streamed request on the same connection.
        if set_cl:
            # When a Content-Length is provided, the content should stream
            # without closing the connection.
            self.getPage('/stream?set_cl=Yes')
            self.assertHeader('Content-Length')
            self.assertNoHeader('Connection', 'close')
            self.assertNoHeader('Transfer-Encoding')

            self.assertStatus('200 OK')
            self.assertBody('0123456789')
        else:
            # When no Content-Length response header is provided,
            # streamed output will either close the connection, or use
            # chunked encoding, to determine transfer-length.
            self.getPage('/stream')
            self.assertNoHeader('Content-Length')
            self.assertStatus('200 OK')
            self.assertBody('0123456789')

            chunked_response = False
            for k, v in self.headers:
                if k.lower() == 'transfer-encoding':
                    if str(v) == 'chunked':
                        chunked_response = True

            if chunked_response:
                self.assertNoHeader('Connection', 'close')
            else:
                self.assertHeader('Connection', 'close')

                # Make another request on the same connection, which should
                # error.
                self.assertRaises(
                    http_client.NotConnected, self.getPage, '/pov')

            # Try HEAD.
            # See http://www.bitbucket.org/cherrypy/cherrypy/issue/864.
            self.getPage('/stream', method='HEAD')
            self.assertStatus('200 OK')
            self.assertBody('')
            self.assertNoHeader('Transfer-Encoding')

    def _streaming_10(self, set_cl):
        self.httpserver.protocol = 'HTTP/1.0'
        self.PROTOCOL = 'HTTP/1.0'

        self.persistent = True

        # Make the first request and assert Keep-Alive.
        self.getPage('/pov', headers=[('Connection', 'Keep-Alive')])
        self.assertStatus('200 OK')
        self.assertBody(pov)
        self.assertHeader('Connection', 'Keep-Alive')

        # Make another, streamed request on the same connection.
        if set_cl:
            # When a Content-Length is provided, the content should
            # stream without closing the connection.
            self.getPage('/stream?set_cl=Yes',
                         headers=[('Connection', 'Keep-Alive')])
            self.assertHeader('Content-Length')
            self.assertHeader('Connection', 'Keep-Alive')
            self.assertNoHeader('Transfer-Encoding')
            self.assertStatus('200 OK')
            self.assertBody('0123456789')
        else:
            # When a Content-Length is not provided,
            # the server should close the connection.
            self.getPage('/stream', headers=[('Connection', 'Keep-Alive')])
            self.assertStatus('200 OK')
            self.assertBody('0123456789')

            self.assertNoHeader('Content-Length')
            self.assertNoHeader('Connection', 'Keep-Alive')
            self.assertNoHeader('Transfer-Encoding')

            # Make another request on the same connection, which should error.
            self.assertRaises(http_client.NotConnected, self.getPage, '/pov')

    def test_HTTP10_to_10_KeepAlive(self):
        self.httpserver.protocol = 'HTTP/1.0'
        self._keepalive()

    def test_HTTP10_to_11_KeepAlive(self):
        self.httpserver.protocol = 'HTTP/1.1'
        self._keepalive()

    def _keepalive(self):
        self.PROTOCOL = 'HTTP/1.0'
        self.HTTP_CONN = self._Conn

        # Test a normal HTTP/1.0 request.
        self.getPage('/page2')
        self.assertStatus('200 OK')
        self.assertBody(pov)
        self.assertNoHeader('Connection')

        # Test a keep-alive HTTP/1.0 request.
        self.persistent = True

        self.getPage('/page3', headers=[('Connection', 'Keep-Alive')])
        self.assertStatus('200 OK')
        self.assertBody(pov)
        self.assertHeader('Connection', 'Keep-Alive')

        # Remove the keep-alive header again.
        self.getPage('/page3')
        self.assertStatus('200 OK')
        self.assertBody(pov)
        self.assertNoHeader('Connection')

    def test_HTTP11_Timeout(self):
        # If we timeout without sending any data,
        # the server will close the conn with a 408.
        self.httpserver.protocol = 'HTTP/1.1'
        self.PROTOCOL = 'HTTP/1.1'

        # Connect but send nothing.
        self.persistent = True
        conn = self.HTTP_CONN
        conn.auto_open = False
        conn.connect()

        # Wait for our socket timeout
        time.sleep(timeout * 2)

        # The request should have returned 408 already.
        response = conn.response_class(conn.sock, method='GET')
        response.begin()
        self.assertEqual(response.status, 408)
        conn.close()

        # Connect but send half the headers only.
        self.persistent = True
        conn = self.HTTP_CONN
        conn.auto_open = False
        conn.connect()
        conn.send(b'GET /hello HTTP/1.1')
        conn.send(('Host: %s' % self.HOST).encode('ascii'))

        # Wait for our socket timeout
        time.sleep(timeout * 2)

        # The conn should have already sent 408.
        response = conn.response_class(conn.sock, method='GET')
        response.begin()
        self.assertEqual(response.status, 408)
        conn.close()

    def test_HTTP11_Timeout_after_request(self):
        # If we timeout after at least one request has succeeded,
        # the server will close the conn without 408.
        self.httpserver.protocol = 'HTTP/1.1'
        self.PROTOCOL = 'HTTP/1.1'

        # Make an initial request
        self.persistent = True
        conn = self.HTTP_CONN
        conn.putrequest('GET', '/timeout?t=%s' % timeout, skip_host=True)
        conn.putheader('Host', self.HOST)
        conn.endheaders()
        response = conn.response_class(conn.sock, method='GET')
        response.begin()
        self.assertEqual(response.status, 200)
        self.body = response.read()
        self.assertBody(str(timeout))

        # Make a second request on the same socket
        conn._output(b'GET /hello HTTP/1.1')
        conn._output(('Host: %s' % self.HOST).encode('ascii'))
        conn._send_output()
        response = conn.response_class(conn.sock, method='GET')
        response.begin()
        self.assertEqual(response.status, 200)
        self.body = response.read()
        self.assertBody('Hello, world!')

        # Wait for our socket timeout
        time.sleep(timeout * 2)

        # Make another request on the same socket, which should error
        conn._output(b'GET /hello HTTP/1.1')
        conn._output(('Host: %s' % self.HOST).encode('ascii'))
        conn._send_output()
        response = conn.response_class(conn.sock, method='GET')
        try:
            response.begin()
        except Exception as ex:
            if not isinstance(ex,
                              (socket.error, http_client.BadStatusLine)):
                self.fail("Writing to timed out socket didn't fail"
                          ' as it should have: %s' % ex)
        else:
            if response.status != 408:
                self.fail("Writing to timed out socket didn't fail"
                          ' as it should have: %s' %
                          response.read())

        conn.close()

        # Make another request on a new socket, which should work
        self.persistent = True
        conn = self.HTTP_CONN
        conn.putrequest('GET', '/pov', skip_host=True)
        conn.putheader('Host', self.HOST)
        conn.endheaders()
        response = conn.response_class(conn.sock, method='GET')
        response.begin()
        self.assertEqual(response.status, 200)
        self.body = response.read()
        self.assertBody(pov)

        # Make another request on the same socket,
        # but timeout on the headers
        conn.send(b'GET /hello HTTP/1.1')
        # Wait for our socket timeout
        time.sleep(timeout * 2)
        response = conn.response_class(conn.sock, method='GET')
        try:
            response.begin()
        except Exception as ex:
            if not isinstance(ex,
                              (socket.error, http_client.BadStatusLine)):
                self.fail("Writing to timed out socket didn't fail"
                          ' as it should have: %s' % ex)
        else:
            self.fail("Writing to timed out socket didn't fail"
                      ' as it should have: %s' %
                      response.read())

        conn.close()

        # Retry the request on a new connection, which should work
        self.persistent = True
        conn = self.HTTP_CONN
        conn.putrequest('GET', '/pov', skip_host=True)
        conn.putheader('Host', self.HOST)
        conn.endheaders()
        response = conn.response_class(conn.sock, method='GET')
        response.begin()
        self.assertEqual(response.status, 200)
        self.body = response.read()
        self.assertBody(pov)
        conn.close()

    def test_HTTP11_pipelining(self):
        self.httpserver.protocol = 'HTTP/1.1'
        self.PROTOCOL = 'HTTP/1.1'

        # Test pipelining. httplib doesn't support this directly.
        self.persistent = True
        conn = self.HTTP_CONN

        # Put request 1
        conn.putrequest('GET', '/hello', skip_host=True)
        conn.putheader('Host', self.HOST)
        conn.endheaders()

        for trial in range(5):
            # Put next request
            conn._output(
                ('GET /hello?%s HTTP/1.1' % trial).encode('iso-8859-1')
            )
            conn._output(('Host: %s' % self.HOST).encode('ascii'))
            conn._send_output()

            # Retrieve previous response
            response = conn.response_class(conn.sock, method='GET')
            # there is a bug in python3 regarding the buffering of
            # ``conn.sock``. Until that bug get's fixed we will
            # monkey patch the ``reponse`` instance.
            # https://bugs.python.org/issue23377
            if six.PY3:
                response.fp = conn.sock.makefile('rb', 0)
            response.begin()
            body = response.read(13)
            self.assertEqual(response.status, 200)
            self.assertEqual(body, b'Hello, world!')

        # Retrieve final response
        response = conn.response_class(conn.sock, method='GET')
        response.begin()
        body = response.read()
        self.assertEqual(response.status, 200)
        self.assertEqual(body, b'Hello, world!')

        conn.close()

    def test_100_Continue(self):
        self.httpserver.protocol = 'HTTP/1.1'
        self.PROTOCOL = 'HTTP/1.1'

        self.persistent = True
        conn = self.HTTP_CONN

        # Try a page without an Expect request header first.
        # Note that httplib's response.begin automatically ignores
        # 100 Continue responses, so we must manually check for it.
        conn.putrequest('POST', '/upload', skip_host=True)
        conn.putheader('Host', self.HOST)
        conn.putheader('Content-Type', 'text/plain')
        conn.putheader('Content-Length', '4')
        conn.endheaders()
        conn.send(b"d'oh")
        response = conn.response_class(conn.sock, method='POST')
        version, status, reason = response._read_status()
        self.assertNotEqual(status, 100)
        conn.close()

        # Now try a page with an Expect header...
        conn.connect()
        conn.putrequest('POST', '/upload', skip_host=True)
        conn.putheader('Host', self.HOST)
        conn.putheader('Content-Type', 'text/plain')
        conn.putheader('Content-Length', '17')
        conn.putheader('Expect', '100-continue')
        conn.endheaders()
        response = conn.response_class(conn.sock, method='POST')

        # ...assert and then skip the 100 response
        version, status, reason = response._read_status()
        self.assertEqual(status, 100)
        while True:
            line = response.fp.readline().strip()
            if line:
                self.fail(
                    '100 Continue should not output any headers. Got %r' %
                    line)
            else:
                break

        # ...send the body
        body = b'I am a small file'
        conn.send(body)

        # ...get the final response
        response.begin()
        self.status, self.headers, self.body = webtest.shb(response)
        self.assertStatus(200)
        self.assertBody("thanks for '%s'" % body)
        conn.close()

    def test_readall_or_close(self):
        self.httpserver.protocol = 'HTTP/1.1'
        self.PROTOCOL = 'HTTP/1.1'

        self.HTTP_CONN = self._Conn

        # Test a max of 0 (the default) and then reset to what it was above.
        old_max = self.httpserver.max_request_body_size
        for new_max in (0, old_max):
            self.httpserver.max_request_body_size = new_max

            self.persistent = True
            conn = self.HTTP_CONN

            # Get a POST page with an error
            conn.putrequest('POST', '/err_before_read', skip_host=True)
            conn.putheader('Host', self.HOST)
            conn.putheader('Content-Type', 'text/plain')
            conn.putheader('Content-Length', '1000')
            conn.putheader('Expect', '100-continue')
            conn.endheaders()
            response = conn.response_class(conn.sock, method='POST')

            # ...assert and then skip the 100 response
            version, status, reason = response._read_status()
            self.assertEqual(status, 100)
            while True:
                skip = response.fp.readline().strip()
                if not skip:
                    break

            # ...send the body
            conn.send(b'x' * 1000)

            # ...get the final response
            response.begin()
            self.status, self.headers, self.body = webtest.shb(response)
            self.assertStatus(500)

            # Now try a working page with an Expect header...
            conn._output(b'POST /upload HTTP/1.1')
            conn._output(('Host: %s' % self.HOST).encode('ascii'))
            conn._output(b'Content-Type: text/plain')
            conn._output(b'Content-Length: 17')
            conn._output(b'Expect: 100-continue')
            conn._send_output()
            response = conn.response_class(conn.sock, method='POST')

            # ...assert and then skip the 100 response
            version, status, reason = response._read_status()
            self.assertEqual(status, 100)
            while True:
                skip = response.fp.readline().strip()
                if not skip:
                    break

            # ...send the body
            body = b'I am a small file'
            conn.send(body)

            # ...get the final response
            response.begin()
            self.status, self.headers, self.body = webtest.shb(response)
            self.assertStatus(200)
            self.assertBody("thanks for '%s'" % body)
            conn.close()

    def test_No_Message_Body(self):
        self.PROTOCOL = 'HTTP/1.1'

        # Set our HTTP_CONN to an instance so it persists between requests.
        self.persistent = True

        # Make the first request and assert there's no "Connection: close".
        self.getPage('/pov')
        self.assertStatus('200 OK')
        self.assertBody(pov)
        self.assertNoHeader('Connection')

        # Make a 204 request on the same connection.
        self.getPage('/custom/204')
        self.assertStatus(204)
        self.assertNoHeader('Content-Length')
        self.assertBody('')
        self.assertNoHeader('Connection')

        # Make a 304 request on the same connection.
        self.getPage('/custom/304')
        self.assertStatus(304)
        self.assertNoHeader('Content-Length')
        self.assertBody('')
        self.assertNoHeader('Connection')

    def _test_Chunked_Encoding(self):
        self.httpserver.protocol = 'HTTP/1.1'
        self.PROTOCOL = 'HTTP/1.1'

        # Set our HTTP_CONN to an instance so it persists between requests.
        self.persistent = True
        conn = self.HTTP_CONN

        # Try a normal chunked request (with extensions)
        body = (b'8;key=value\r\nxx\r\nxxxx\r\n5\r\nyyyyy\r\n0\r\n'
                b'Content-Type: application/json\r\n'
                b'\r\n')
        conn.putrequest('POST', '/upload', skip_host=True)
        conn.putheader('Host', self.HOST)
        conn.putheader('Transfer-Encoding', 'chunked')
        conn.putheader('Trailer', 'Content-Type')
        # Note that this is somewhat malformed:
        # we shouldn't be sending Content-Length.
        # RFC 2616 says the server should ignore it.
        conn.putheader('Content-Length', '3')
        conn.endheaders()
        conn.send(body)
        response = conn.getresponse()
        self.status, self.headers, self.body = webtest.shb(response)
        self.assertStatus('200 OK')
        self.assertBody("thanks for '%s'" % b'xx\r\nxxxxyyyyy')

        # Try a chunked request that exceeds server.max_request_body_size.
        # Note that the delimiters and trailer are included.
        body = b'3e3\r\n' + (b'x' * 995) + b'\r\n0\r\n\r\n'
        conn.putrequest('POST', '/upload', skip_host=True)
        conn.putheader('Host', self.HOST)
        conn.putheader('Transfer-Encoding', 'chunked')
        conn.putheader('Content-Type', 'text/plain')
        # Chunked requests don't need a content-length
        # conn.putheader("Content-Length", len(body))
        conn.endheaders()
        conn.send(body)
        response = conn.getresponse()
        self.status, self.headers, self.body = webtest.shb(response)
        self.assertStatus(413)
        conn.close()

    def test_Content_Length_in(self):
        # Try a non-chunked request where Content-Length exceeds
        # server.max_request_body_size. Assert error before body send.
        self.httpserver.protocol = 'HTTP/1.1'
        self.PROTOCOL = 'HTTP/1.1'
        self.persistent = True
        conn = self.HTTP_CONN
        conn.putrequest('POST', '/upload', skip_host=True)
        conn.putheader('Host', self.HOST)
        conn.putheader('Content-Type', 'text/plain')
        conn.putheader('Content-Length', '9999')
        conn.endheaders()
        response = conn.getresponse()
        self.status, self.headers, self.body = webtest.shb(response)
        self.assertStatus(413)
        self.assertBody('The entity sent with the request exceeds '
                        'the maximum allowed bytes.')
        conn.close()

    def test_Content_Length_out_preheaders(self):
        # Try a non-chunked response where Content-Length is less than
        # the actual bytes in the response body.
        self.httpserver.protocol = 'HTTP/1.1'
        self.PROTOCOL = 'HTTP/1.1'
        self.persistent = True
        conn = self.HTTP_CONN
        conn.putrequest('GET', '/wrong_cl_buffered', skip_host=True)
        conn.putheader('Host', self.HOST)
        conn.endheaders()
        response = conn.getresponse()
        self.status, self.headers, self.body = webtest.shb(response)
        self.assertStatus(500)
        self.assertBody(
            'The requested resource returned more bytes than the '
            'declared Content-Length.')
        conn.close()

    def test_Content_Length_out_postheaders(self):
        # Try a non-chunked response where Content-Length is less than
        # the actual bytes in the response body.
        self.httpserver.protocol = 'HTTP/1.1'
        self.PROTOCOL = 'HTTP/1.1'
        self.persistent = True
        conn = self.HTTP_CONN
        conn.putrequest('GET', '/wrong_cl_unbuffered', skip_host=True)
        conn.putheader('Host', self.HOST)
        conn.endheaders()
        response = conn.getresponse()
        self.status, self.headers, self.body = webtest.shb(response)
        self.assertStatus(200)
        self.assertBody('I too')
        conn.close()

    @pytest.mark.xfail(reason='Sometimes this test fails due to low timeout')
    def test_598(self):
        self.httpserver.protocol = 'HTTP/1.1'
        self.PROTOCOL = 'HTTP/1.1'
        remote_data_conn = urllib.request.urlopen(
            '%s://%s:%s/one_megabyte_of_a'
            % (self.scheme, self.HOST, self.PORT)
        )
        buf = remote_data_conn.read(512)
        time.sleep(timeout * 0.6)
        remaining = (1024 * 1024) - 512
        while remaining:
            data = remote_data_conn.read(remaining)
            if not data:
                break
            else:
                buf += data
            remaining -= len(data)

        self.assertEqual(len(buf), 1024 * 1024)
        self.assertEqual(buf, b'a' * 1024 * 1024)
        self.assertEqual(remaining, 0)
        remote_data_conn.close()

    def test_No_CRLF(self):
        self.httpserver.protocol = 'HTTP/1.1'
        self.PROTOCOL = 'HTTP/1.1'
        self.persistent = True

        conn = self.HTTP_CONN
        conn.send(b'GET /hello HTTP/1.1\n\n')
        response = conn.response_class(conn.sock, method='GET')
        response.begin()
        self.body = response.read()
        self.assertBody('HTTP requires CRLF terminators')
        conn.close()

        conn.connect()
        conn.send(b'GET /hello HTTP/1.1\r\n\n')
        response = conn.response_class(conn.sock, method='GET')
        response.begin()
        self.body = response.read()
        self.assertBody('HTTP requires CRLF terminators')
        conn.close()

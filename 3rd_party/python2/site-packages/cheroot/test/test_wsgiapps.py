import sys

import pytest

from cheroot.test import helper


@pytest.mark.xfail(reason='issue 1')
class WSGIGraftTests(helper.CherootWebCase):

    @staticmethod
    def setup_server():
        def test_app(environ, start_response):
            status = '200 OK'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            output = ['Hello, world!\n',
                      'This is a wsgi app running within CherryPy!\n\n']
            keys = list(environ.keys())
            keys.sort()
            for k in keys:
                output.append('%s: %s\n' % (k, environ[k]))
            return [x.encode('utf-8') for x in output]

        def test_empty_string_app(environ, start_response):
            status = '200 OK'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            return b'Hello', b'', b' ', b'', b'world'

        class WSGIResponse(object):

            def __init__(self, appresults):
                self.appresults = appresults
                self.iter = iter(appresults)

            def __iter__(self):
                return self

            if sys.version_info >= (3, 0):
                def __next__(self):
                    return next(self.iter)
            else:
                def next(self):
                    return self.iter.next()

            def close(self):
                if hasattr(self.appresults, 'close'):
                    self.appresults.close()

        class ReversingMiddleware(object):

            def __init__(self, app):
                self.app = app

            def __call__(self, environ, start_response):
                results = self.app(environ, start_response)

                class Reverser(WSGIResponse):

                    if sys.version_info >= (3, 0):
                        def __next__(this):
                            line = list(next(this.iter))
                            line.reverse()
                            return bytes(line)
                    else:
                        def next(this):
                            line = list(this.iter.next())
                            line.reverse()
                            return ''.join(line)

                return Reverser(results)

    wsgi_output = '''Hello, world!
This is a wsgi app running within CherryPy!'''

    def test_01_standard_app(self):
        self.getPage('/')
        self.assertBody("I'm a regular CherryPy page handler!")

    def test_04_pure_wsgi(self):
        self.getPage('/hosted/app1')
        self.assertHeader('Content-Type', 'text/plain')
        self.assertInBody(self.wsgi_output)

    def test_05_wrapped_cp_app(self):
        self.getPage('/hosted/app2/')
        body = list("I'm a regular CherryPy page handler!")
        body.reverse()
        body = ''.join(body)
        self.assertInBody(body)

    def test_06_empty_string_app(self):
        self.getPage('/hosted/app3')
        self.assertHeader('Content-Type', 'text/plain')
        self.assertInBody('Hello world')

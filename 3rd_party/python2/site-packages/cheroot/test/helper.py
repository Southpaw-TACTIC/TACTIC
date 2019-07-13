"""A library of helper functions for the Cheroot test suite."""

import datetime
import io
import logging
import os
import subprocess
import sys
import time
import threading
import types

from six.moves import http_client

import portend
import pytest
import six

import cheroot.server
import cheroot.wsgi

from cheroot.test import webtest

log = logging.getLogger(__name__)
thisdir = os.path.abspath(os.path.dirname(__file__))
serverpem = os.path.join(os.getcwd(), thisdir, 'test.pem')


config = {
    'bind_addr': ('127.0.0.1', 54583),
    'server': 'wsgi',
    'wsgi_app': None,
}


class CherootWebCase(webtest.WebCase):

    script_name = ''
    scheme = 'http'

    available_servers = {
        'wsgi': cheroot.wsgi.Server,
        'native': cheroot.server.HTTPServer,
    }

    @classmethod
    def setup_class(cls):
        """Create and run one HTTP server per class."""
        conf = config.copy()
        conf.update(getattr(cls, 'config', {}))

        s_class = conf.pop('server', 'wsgi')
        server_factory = cls.available_servers.get(s_class)
        if server_factory is None:
            raise RuntimeError('Unknown server in config: %s' % conf['server'])
        cls.httpserver = server_factory(**conf)

        cls.HOST, cls.PORT = cls.httpserver.bind_addr
        if cls.httpserver.ssl_adapter is None:
            ssl = ''
            cls.scheme = 'http'
        else:
            ssl = ' (ssl)'
            cls.HTTP_CONN = http_client.HTTPSConnection
            cls.scheme = 'https'

        v = sys.version.split()[0]
        log.info('Python version used to run this test script: %s' % v)
        log.info('Cheroot version: %s' % cheroot.__version__)
        log.info('HTTP server version: %s%s' % (cls.httpserver.protocol, ssl))
        log.info('PID: %s' % os.getpid())

        if hasattr(cls, 'setup_server'):
            # Clear the wsgi server so that
            # it can be updated with the new root
            cls.setup_server()
            cls.start()

    @classmethod
    def teardown_class(cls):
        ''
        if hasattr(cls, 'setup_server'):
            cls.stop()

    @classmethod
    def start(cls):
        """Load and start the HTTP server."""
        threading.Thread(target=cls.httpserver.safe_start).start()
        while not cls.httpserver.ready:
            time.sleep(0.1)

    @classmethod
    def stop(cls):
        cls.httpserver.stop()
        td = getattr(cls, 'teardown', None)
        if td:
            td()

    def base(self):
        if ((self.scheme == 'http' and self.PORT == 80) or
                (self.scheme == 'https' and self.PORT == 443)):
            port = ''
        else:
            port = ':%s' % self.PORT

        return '%s://%s%s%s' % (self.scheme, self.HOST, port,
                                self.script_name.rstrip('/'))

    def exit(self):
        sys.exit()

    def skip(self, msg='skipped '):
        pytest.skip(msg)

    date_tolerance = 2

    def assertEqualDates(self, dt1, dt2, seconds=None):
        """Assert abs(dt1 - dt2) is within Y seconds."""
        if seconds is None:
            seconds = self.date_tolerance

        if dt1 > dt2:
            diff = dt1 - dt2
        else:
            diff = dt2 - dt1
        if not diff < datetime.timedelta(seconds=seconds):
            raise AssertionError('%r and %r are not within %r seconds.' %
                                 (dt1, dt2, seconds))


class Request(object):

    def __init__(self, environ):
        self.environ = environ


class Response(object):

    def __init__(self):
        self.status = '200 OK'
        self.headers = {'Content-Type': 'text/html'}
        self.body = None

    def output(self):
        if self.body is None:
            return []
        elif isinstance(self.body, six.text_type):
            return [self.body.encode('iso-8859-1')]
        elif isinstance(self.body, six.binary_type):
            return [self.body]
        else:
            return [x.encode('iso-8859-1') for x in self.body]


class Controller(object):

    def __call__(self, environ, start_response):
        req, resp = Request(environ), Response()
        try:
            # Python 3 supports unicode attribute names
            # Python 2 encodes them
            handler = self.handlers[environ['PATH_INFO']]
        except KeyError:
            resp.status = '404 Not Found'
        else:
            output = handler(req, resp)
            if (output is not None and
                    not any(resp.status.startswith(status_code)
                            for status_code in ('204', '304'))):
                resp.body = output
                try:
                    resp.headers.setdefault('Content-Length', str(len(output)))
                except TypeError:
                    if not isinstance(output, types.GeneratorType):
                        raise
        start_response(resp.status, resp.headers.items())
        return resp.output()


# --------------------------- Spawning helpers --------------------------- #


class CherootProcess(object):

    pid_file = os.path.join(thisdir, 'test.pid')
    config_file = os.path.join(thisdir, 'test.conf')
    config_template = """[global]
server.socket_host: '%(host)s'
server.socket_port: %(port)s
checker.on: False
log.screen: False
log.error_file: r'%(error_log)s'
log.access_file: r'%(access_log)s'
%(ssl)s
%(extra)s
"""
    error_log = os.path.join(thisdir, 'test.error.log')
    access_log = os.path.join(thisdir, 'test.access.log')

    def __init__(self, wait=False, daemonize=False, ssl=False,
                 socket_host=None, socket_port=None):
        self.wait = wait
        self.daemonize = daemonize
        self.ssl = ssl
        self.host = socket_host
        self.port = socket_port

    def write_conf(self, extra=''):
        if self.ssl:
            serverpem = os.path.join(thisdir, 'test.pem')
            ssl = """
server.ssl_certificate: r'%s'
server.ssl_private_key: r'%s'
""" % (serverpem, serverpem)
        else:
            ssl = ''

        conf = self.config_template % {
            'host': self.host,
            'port': self.port,
            'error_log': self.error_log,
            'access_log': self.access_log,
            'ssl': ssl,
            'extra': extra,
        }
        with io.open(self.config_file, 'w', encoding='utf-8') as f:
            f.write(six.text_type(conf))

    def start(self, imports=None):
        """Start cherryd in a subprocess."""
        portend.free(self.host, self.port, timeout=1)

        args = [
            os.path.join(thisdir, '..', 'cherryd'),
            '-c', self.config_file,
            '-p', self.pid_file,
        ]

        if not isinstance(imports, (list, tuple)):
            imports = [imports]
        for i in imports:
            if i:
                args.append('-i')
                args.append(i)

        if self.daemonize:
            args.append('-d')

        env = os.environ.copy()
        # Make sure we import the cheroot package in which this module is
        # defined.
        grandparentdir = os.path.abspath(os.path.join(thisdir, '..', '..'))
        if env.get('PYTHONPATH', ''):
            env['PYTHONPATH'] = os.pathsep.join(
                (grandparentdir, env['PYTHONPATH']))
        else:
            env['PYTHONPATH'] = grandparentdir
        self._proc = subprocess.Popen([sys.executable] + args, env=env)
        if self.wait:
            self.exit_code = self._proc.wait()
        else:
            portend.occupied(self.host, self.port, timeout=5)

        # Give the engine a wee bit more time to finish STARTING
        if self.daemonize:
            time.sleep(2)
        else:
            time.sleep(1)

    def get_pid(self):
        if self.daemonize:
            return int(open(self.pid_file, 'rb').read())
        return self._proc.pid

    def join(self):
        """Wait for the process to exit."""
        if self.daemonize:
            return self._join_daemon()
        self._proc.wait()

    def _join_daemon(self):
        try:
            try:
                # Mac, UNIX
                os.wait()
            except AttributeError:
                # Windows
                try:
                    pid = self.get_pid()
                except IOError:
                    # Assume the subprocess deleted the pidfile on shutdown.
                    pass
                else:
                    os.waitpid(pid, 0)
        except OSError as ex:
            if ex.args != (10, 'No child processes'):
                raise


from __future__ import print_function

import sys, os

sys.path.insert(0, "/opt/tactic/tactic_data/plugins")
sys.path.insert(0, "/opt/tactic/tactic/3rd_party/common/site-packages")
sys.path.insert(0, "/opt/tactic/tactic/3rd_party/python3/site-packages")

import tacticenv
import spt

from pyasm.common import Environment
from pyasm.search import Search, Sql, DbContainer

try:
    import urlparse
except:
    from urllib import parse as urlparse


global cache
cache = set()

def authenticate(environ):

    cookie = environ.get("HTTP_COOKIE")
    cookies = cookie.split(";")

    login_ticket = None
    for cookie in cookies:
        cookie = cookie.strip()
        if not cookie:
            return None
        (name, value) = cookie.split("=", 1)
        if name == "login_ticket" and value:
            login_ticket = value
            break


    if not login_ticket:
        return None

    from pyasm.security import Batch, XmlRpcInit
    try:
        XmlRpcInit(ticket=login_ticket)
    except Exception as e:
        print("Authenticate Error: ", e)
        return None


    #from pyasm.common import Environment
    #user = Environment.get_user_name().encode()
    #print("user: ", user)

    return login_ticket.encode()


def error403(msg, start_response):

    redirect = False
    if redirect:
        status = "303 Moved Permanently"
        output = ''
        response_headers = [
            ('Location', '/default/user/sign_in')
        ]


    else:
        status = '200 OK'


        output = '''
        <div style="position: fixed; height: 100vh; width: 100vw; background: #DDD; top: 0px; left: 0px">
        <div style="margin: 100px auto; width: 600px; border: solid 1px #DDD; background: #FFF; border-radius: 10px; text-align: center; padding: 30px; box-shadow: 0px 0px 15px rgba(0,0,0,0.1)">%s</div>
        </div>
        '''  % msg

        response_headers = [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(output))),
        ]

    output = output.encode()

    start_response(status, response_headers)
    return [output]





def _application(environ, start_response):

    import time
    start = time.time()

    # check that the url is ok
    request_uri = environ.get("REQUEST_URI")
    #uri_path = request_uri.replace("/wsgi/security/", "")
    uri_path = request_uri.lstrip("/assets/")


    global cache
    #key = "%s|%s" % (login_ticket, uri_path)
    key = uri_path
    if key in cache:
        status = '200 OK'

        base_dir = "/spt/data/sites"
        path = "%s/%s" % (base_dir, uri_path)

        path = urlparse.unquote(path)
        basename = os.path.basename(path)

        response_headers = [
                ('X-Sendfile', '%s' % path),
                #('Content-Type', 'image/jpg'),
        ]

        output = "".encode()
        start_response(status, response_headers)
        return [output]




    end = time.time()
    diff = end - start

    parts = uri_path.split("/")
    if not len(parts) > 3:
        return error403("Url not valid", start_response)


    # FIXME: this does not work on non Portal sites
    if parts[0] == "assets":
        site = ""
        project_code = parts[1]
    else: 
        site = parts[0]
        #assert(parts[1] == "assets")
        project_code = parts[2]

    end = time.time()
    diff = end - start

    # authenticate the user
    login_ticket = authenticate(environ)
    if not login_ticket:
        return error403("Authentication Failed", start_response)

    end = time.time()
    diff = end - start

    # Can only see this asset if they are permitted to see the project
    from pyasm.security import Site
    from pyasm.biz import Project
    site_obj = Site.set_site(site)
    try:
        Project.set_project(project_code)
    except Exception as e:
        print("Error Site: ", e)
        msg = "Permission Denied"
        return error403(msg, start_response)
    finally:
        if site_obj:
            Site.pop_site()



    if not login_ticket:

        status = '200 OK'
        output = '''
        <h1>Not a valid ticket</h1>
        ''' 
        output = output.encode()

        response_headers = [('Content-Type', 'text/html'),
                            ('Content-Length', str(len(output))),
        ]

        start_response(status, response_headers)
        return [output]



    # validate that this person can see this site

    end = time.time()
    diff = end - start

    status = '200 OK'

    base_dir = "/spt/data/sites"
    path = "%s/%s" % (base_dir, uri_path)

    path = urlparse.unquote(path)
    basename = os.path.basename(path)

    response_headers = [
            ('X-Sendfile', '%s' % path),
            #('Content-Type', 'image/jpg'),
    ]

    output = "".encode()


    cache.add(key)


    start_response(status, response_headers)
    return [output]



def application(environ, start_response):

    try:
        return _application(environ, start_response)
    finally:
        DbContainer.commit_thread_sql()



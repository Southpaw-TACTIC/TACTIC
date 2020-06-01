
from __future__ import print_function

import sys, os

sys.path.insert(0, "/opt/tactic/tactic_data/plugins")
sys.path.insert(0, "/opt/tactic/tactic/3rd_party/common/site-packages")
sys.path.insert(0, "/opt/tactic/tactic/3rd_party/python3/site-packages")

import tacticenv


from pyasm.common import Environment
from pyasm.search import Search

try:
    import urlparse
except:
    from urllib import parse as urlparse


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
        status = "300 Redirect"
        output = ''
        response_headers = [
            ('Location', '/default/user/sign_in')
        ]


    else:
        status = '200 OK'


        output = '''
        <h1>%s</h1>
        <meta http-equiv="refresh" content="0;/default/user/sign_in" />
        '''  % msg

        response_headers = [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(output))),
        ]

    output = output.encode()

    start_response(status, response_headers)
    return [output]





def application(environ, start_response):
    import time
    start = time.time()

    # check that the url is ok
    request_uri = environ.get("REQUEST_URI")
    #uri_path = request_uri.replace("/wsgi/security/", "")
    uri_path = request_uri.lstrip("/assets/")

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

    # authenticate the user
    login_ticket = authenticate(environ)
    if not login_ticket:
        return error403("Authentication Failed", start_response)


    from pyasm.security import Site
    from pyasm.biz import Project
    try:
        site_obj = Site.set_site(site)
        Project.set_project(project_code)
    except Exception as e:
        print("Error Site: ", e)
        return error403(e, start_response)
    finally:
        if site_obj:
            Site.pop_site()

    #print("site", site)
    #print("project_code", project_code)




    if not login_ticket:

        status = '200 OK'
        output = '''
        <h1>Not a valid ticket</h1>
        ''' 

        response_headers = [('Content-Type', 'text/html'),
                            ('Content-Length', str(len(output))),
        ]

        output.encode()

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


    start_response(status, response_headers)
    return [output]





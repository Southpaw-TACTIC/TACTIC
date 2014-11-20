###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['CherryPyStartup']

import os, sys, glob, time
import cherrypy

from pyasm.web.app_server import AppServer

from pyasm.common import Environment, Container, Config
from pyasm.web import WebEnvironment
from pyasm.biz import Project

from cherrypy_startup import TacticIndex, _cp_on_http_error
from cherrypy_startup import CherryPyStartup as CherryPyStartup20



class Root:
    '''Dummy Root page'''

    def test(my):
        return "OK"
    test.exposed = True

    def index(my):
        return '''<META http-equiv="refresh" content="0;URL=/tactic">'''
    index.exposed = True





class CherryPyStartup(CherryPyStartup20):


    def execute(my):
        #import pprint
        #pprint.pprint( my.config )

        #try:
        #    import setproctitle
        #    setproctitle.setproctitle("TACTIC")
        #except:
        #    pass


        cherrypy.config.update( my.config )

        cherrypy.config.update({'error_page.404': my.error_page})
        cherrypy.config.update({'error_page.403': my.error_page})

        cherrypy.engine.start()
        cherrypy.engine.block()




    def error_page(my, status, message, traceback, version):

        # check if this project exists
        response = cherrypy.response
        request = cherrypy.request
        path = request.path_info

        parts = path.split("/")
        if len(parts) < 3:
            cherrypy.response.body = '<meta http-equiv="refresh" content="0;url=/tactic" />'
            return 
        else:
            project_code = parts[2]
        from pyasm.security import TacticInit
        TacticInit()
        #import sys,traceback
        #tb = sys.exc_info()[2]
        #stacktrace = traceback.format_tb(tb)
        #stacktrace_str = "".join(stacktrace)
        #print "-"*50
        #print stacktrace_str
        #print "-"*50

        # Dump out the error
        print "WARNING: ", path, status, message
        try:
            eval("cherrypy.root.tactic.%s" % project_code)
        # if project_code is empty , it raises SyntaxError
        except (AttributeError, SyntaxError), e:
            has_project = False
        else:
            has_project = True

        # make sure the appropriate site is set (based on the ticket)
        from pyasm.security import Site
        cookie = cherrypy.request.cookie
        if cookie.has_key("login_ticket"):
            cookie = cookie["login_ticket"].value
            site = Site.get().get_by_ticket(cookie)
        else:
            html_response = '''<html>
            <head><meta http-equiv="Refresh" content="0; url=/"></head>
            </html>'''
            response.body = ''
            return html_response

        Site.set_site(site)


        # if the url does not exist, but the project does, then check to
        # to see if cherrypy knows about it
        project = Project.get_by_code(project_code)
        if not has_project and project and project.get_value("type") != 'resource':

            print "register ..."

            startup = cherrypy.startup
            config = startup.config
            startup.register_site(project_code, config)
            #cherrypy.config.update( config )
            # give some time to refresh
            import time
            time.sleep(1)

            # either refresh ... (LATER: or recreate the page on the server end)
            # reloading in 2 seconds
            html_response = '''<html>
            <head><meta http-equiv="Refresh" content="2"></head>
                <body style='color: #000; min-height: 1200px; background: #DDDDDD'><div>Reloading ...</div></body> 
            </html>
            '''

            # this response.body is not needed, can be commented out in the future
            response.body = ''
            return html_response
     

        # check to see if this project exists in the database?
        #project = Project.get_by_code(project_code)
        #print project
        
        from pyasm.web import Widget, WebApp, AppServer, WebContainer, DivWdg
        from pyasm.widget import Error404Wdg

        # clear the buffer
        WebContainer.clear_buffer()

        class xyz(AppServer):

            def __init__(my, status, message):
                my.hash = None
                my.status = status
                my.message = message

            def get_page_widget(my):

                top = DivWdg()
                top.add_style("background: #444")
                top.add_style("height: 100%")
                top.add_style("width: 100%")

                widget = Error404Wdg()
                widget.status = status
                widget.message = message
                return widget
                top.add(widget)

                return top
       
        xyz = xyz(status, message)
        #response.body = xyz.get_display()
        #return xyz.get_display()
        return xyz.get_display()





    def setup_sites(my):

        context_path = "%s/src/context" % my.install_dir
        doc_dir = "%s/doc" % my.install_dir
        plugin_dir = Environment.get_plugin_dir()
        builtin_plugin_dir = Environment.get_builtin_plugin_dir()
        dist_dir = Environment.get_dist_dir()

        log_dir = "%s/log" % Environment.get_tmp_dir()

        config = {
            
            'global': {
                'server.socket_host': '127.0.0.1',
                'server.socket_port': 80,
                'log.screen': False,
                'request.show_tracebacks': True,
                'tools.log_headers.on': True,
                'server.log_file': "%s/tactic_log" % log_dir,
                'server.max_request_body_size': 0,
                #'server.socket_timeout': 60,
                'response.timeout': 3600,

                'tools.encode.on': True,
                'tools.encode.encoding': 'utf-8',
                'tools.decode.on': True,
                'tools.decode.encoding': 'utf-8',
                #'encoding_filter.on': True,
                #'decoding_filter.on': True
            }
            ,
            '/context': {'tools.staticdir.on': True,
                         'tools.staticdir.dir': context_path,
                         # Need to do this because on windows servers, jar files
                         # are served as text/html
                         'tools.staticdir.content_types': {
                             'jar': 'application/java-archive'
                         }
                        },
            '/assets':  {'tools.staticdir.on': True,
                         'tools.staticdir.dir': Environment.get_asset_dir()
                        },
            '/doc':     {'tools.staticdir.on': True,
                         'tools.staticdir.dir': doc_dir,
                         'tools.staticdir.index': "index.html"
                        },
            # NOTE: expose the entire plugins directory
            '/tactic/plugins': {
                         'tools.staticdir.on': True,
                         'tools.staticdir.dir': plugin_dir,
                        },
            '/tactic/builtin_plugins': {
                         'tools.staticdir.on': True,
                         'tools.staticdir.dir': builtin_plugin_dir,
                        },
            '/tactic/dist': {
                        'tools.staticdir.on': True,
                        'tools.staticdir.dir': dist_dir,
                        }
 

        }

      

        # set up the root directory
        cherrypy.root = Root()
        cherrypy.tree.mount( cherrypy.root, config=config)



        from pyasm.search import Search
        search = Search("sthpw/project")
        search.add_filter("type", "resource", op="!=")
        projects = search.get_sobjects()


        # find out if one of the projects is the root
        root_initialized = False
        """
        for project in projects:
            project_code = project.get_code()
            if False:
                from tactic.ui.app import SitePage
                cherrypy.root.tactic = SitePage(project_code)
                cherrypy.root.projects = SitePage(project_code)
                root_initialized = True
                break
        """

        if not root_initialized:
            project_code = Project.get_default_project()
            if project_code and project_code !='default':
                from tactic.ui.app import SitePage
                cherrypy.root.tactic = SitePage(project_code)
                cherrypy.root.projects = SitePage(project_code)
                root_initialized = True


        if not root_initialized:
            # load in the base site at root
            from tactic_sites.default.context.Index import Index
            cherrypy.root.tactic = Index()
            cherrypy.root.projects = Index()


        for project in projects:
            project_code = project.get_code()
            my.register_site(project_code, config)
        my.register_site("default", config)

        return config





    def register_site(my, site, config):

        # if there happend to be . in the site name, convert to _
        site = site.replace(".", "_")

        if site == "template":
            return

        print "Registering project ... %s" % site

        try:
            from tactic.ui.app import SitePage
            exec("cherrypy.root.tactic.%s = SitePage()" % site)
            exec("cherrypy.root.projects.%s = SitePage()" % site)


        except ImportError:
            #print "... WARNING: SitePage not found"
            exec("cherrypy.root.tactic.%s = TacticIndex()" % site)
            exec("cherrypy.root.projects.%s = TacticIndex()" % site)
        except SyntaxError:
            print "WARNING: skipping project [%s]" % site




        # The rest is only ever executed on the "default" site


        # This is to get admin site working
        if site in ['admin', 'default', 'template', 'unittest']:
            base = "tactic_sites"
        else:
            base = "sites"



        # get the contexts: 
        if site in ("admin", "default", "template", "unittest"):
            context_dir = Environment.get_install_dir().replace("\\", "/")
            context_dir = "%s/src/tactic_sites/%s/context" % (context_dir, site)
        else:
            context_dir = Environment.get_site_dir().replace("\\", "/")
            context_dir = "%s/sites/%s/context" % (context_dir, site)



        if not os.path.exists(context_dir):
            return

        contexts = []
        for context_dir in os.listdir(context_dir):
            if not context_dir.endswith(".py"):
                continue
            if context_dir == "__init__.py":
                continue
            if context_dir.startswith("."):
                continue
            if os.path.isdir(context_dir):
                continue

            context = context_dir.replace(".py", "")
            contexts.append(context)

        for context in contexts:
            try:

                exec("from %s.%s.context.%s import %s" % (base,site,context,context))
                exec("cherrypy.root.tactic.%s.%s = %s()" % (site,context,context) )

            except ImportError, e:
                print str(e)
                print "... failed to import '%s.%s.%s'" % (base, site, context)
                raise
                #return

            
            path = "/tactic/%s/%s" % (site, context)
            settings = {}
            config[path] = settings

            if context in ["XMLRPC", "Api"]:
                #settings['request.dispatch'] = cherrypy.dispatch.XMLRPCDispatcher(),
                settings['tools.xmlrpc.on'] = True
                settings['tools.xmlrpc.encoding'] = 'utf-8'
                settings['tools.xmlrpc.allow_none'] = True 





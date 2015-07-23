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

__all__ = ['CherryPyStartup', "_cp_on_http_error"]

import os, sys, glob
import cherrypy

from pyasm.web.app_server import AppServer

from pyasm.common import Environment, Config
from pyasm.web import WebEnvironment
from pyasm.biz import Project


class FlashWrapper: 
     
    def before_request_body(self): 
        if not cherrypy.config.get("flashwrapper.on", False): 
            return 
         
        h = cherrypy.request.headers 
         
        if h.get('Content-Type').startswith('multipart/'):
            user_agent = h.get('User-Agent', '')
            if user_agent.find('Shockwave Flash') != -1 or\
                user_agent.find('Adobe Flash') != -1: 
                clen = h.get('Content-Length', '0') 
                try: 
                    clen = int(clen) 
                except ValueError: 
                    return 

                from cherrypy.lib import httptools
                wrap = httptools.MultipartWrapper 
                cherrypy.request.rfile = wrap(cherrypy.request.rfile, clen) 

             

def _cp_on_http_error(status, message):
    # check if this project exists
    
    response = cherrypy.response
    path = cherrypy.request.path

    parts = path.split("/")
    if len(parts) < 3:
        cherrypy.response.body = '<meta  http-equiv="refresh" content="0;url=/tactic" />'
        return 
    else:
        project_code = parts[2]
    from pyasm.security import TacticInit
    TacticInit()

    import sys,traceback
    tb = sys.exc_info()[2]
    stacktrace = traceback.format_tb(tb)
    stacktrace_str = "".join(stacktrace)
    print "-"*50
    print stacktrace_str
    print "-"*50


    print path, status, message
    try:
        eval("cherrypy.root.tactic.%s" % project_code)
    # if project_code is empty , it raises SyntaxError
    except (AttributeError, SyntaxError), e:
        has_project = False
    else:
        has_project = True


    # if the url does not exist, but the project does, then check to
    # to see if cherrypy knows about it
    project = Project.get_by_code(project_code)
    if not has_project and project:

        startup = cherrypy.startup
        config = startup.config
        startup.register_project(project_code, config)
        #cherrypy.config.update( config )
        # give some time to refresh
        import time
        time.sleep(1)

        # either refresh ... (LATER: or recreate the page on the server end)
        response.body = '<meta http-equiv="Refresh" content="0; url=%s">' % path
        return
 

    # check to see if this project exists in the database?
    #project = Project.get_by_code(project_code)
    #print project
    
    from pyasm.web import Widget, WebApp, AppServer
    from pyasm.widget import TopWdg, BottomWdg, Error404Wdg
    class xyz(AppServer):

        def __init__(my, status, message):
            my.hash = None
            my.status = status
            my.message = message

        def get_page_widget(my):
            widget = Error404Wdg()
            widget.status = status
            widget.message = message
            return widget
    
    xyz = xyz(status, message)
    response.body = xyz.get_display()
    return 


class Root:
    '''Dummy Root page'''

    _cp_filters = [FlashWrapper()]

    def test(my):
        return "OK"
    test.exposed = True

    def index(my):
        return '''<META http-equiv="refresh" content="0;URL=/tactic">'''


    def _cp_on_http_error(self, status, message):
        return _cp_on_http_error(status, message)




class TacticIndex:
    '''Dummy Index file'''
    def index(my):
        return "OK"
    index.exposed = True






class CherryPyStartup(object):

    def __init__(my, port=''):

        # It is possible on startup that the database is not running.
        from pyasm.common import Environment
        from pyasm.search import DbContainer, DatabaseException, Sql
        plugin_dir = Environment.get_plugin_dir()
        sys.path.insert(0, plugin_dir)

        try:
            sql = DbContainer.get("sthpw")
            if sql.get_database_type() != "MongoDb":
                # before batch, clean up the ticket with a NULL code
                if os.getenv('TACTIC_MODE') != 'production':
                    sql.do_update('DELETE from "ticket" where "code" is NULL;')
                else:
                    start_port = Config.get_value("services", "start_port")
                    if start_port:
                        start_port = int(start_port)
                    else:
                        start_port = 8081
                    if port and int(port) == start_port:
                         sql.do_update('DELETE from "ticket" where "code" is NULL;')
        except DatabaseException, e:
            # TODO: need to work on this
            print "ERROR: could not connect to [sthpw] database"
            #os.environ["TACTIC_CONFIG_PATH"] = Config.get_default_config_path()
            #Sql.set_default_vendor("Sqlite")

            Config.set_tmp_config()
            Config.reload_config()

            # try connecting again
            try:
                sql = DbContainer.get("sthpw")
            except:
                print "Could not connect to the database."
                raise


        # is it CherryPyStartup's responsibility to start batch?
        from pyasm.security import Batch
        Batch()

        my.site_dir = os.getenv("TACTIC_SITE_DIR")
        my.install_dir = os.getenv("TACTIC_INSTALL_DIR")

        # set up a simple environment.  May need a more complex one later
        my.env = Environment()


        my.setup_env()
        my.config = my.setup_sites()

        my.init_only = False

        cherrypy.startup = my


        # this initializes the web.
        # - sets up virtual implied tiggers 
        from web_init import WebInit
        WebInit().execute()

        # Windows should handle fine
        #start up the caching system if it's not windows
        cache_mode = Config.get_value("install", "cache_mode")
        if not cache_mode:
            cache_mode = 'complete'
            if os.name == 'nt':
                cache_mode = 'basic'
            
        from cache_startup import CacheStartup
        cmd = CacheStartup(mode=cache_mode)
        cmd.execute()
        cmd.init_scheduler()

        # DEPRECATED (but keeping it around"
        """
        # start up the queue system ...
        if Config.get_value("sync", "enabled") == "true":
            # start up the sync system ...
            print "Starting Transaction Sync ..."
            from tactic.command import TransactionQueueManager
            TransactionQueueManager.start()

            # start up the sync system ...
            print "Starting Watch Folder Service ..."
            from tactic.command import WatchServerFolderTask
            WatchServerFolderTask.start()
        """

        # start up scheduled triggers
        #from tactic.command import ScheduledTriggerMonitor
        #ScheduledTriggerMonitor.start()

        #from pyasm.web import Translation
        #Translation.install()


        # close all the threads in this startup thread
        from pyasm.search import DbContainer
        DbContainer.close_thread_sql()

        version = Environment.get_release_version()
        print
        print "Starting TACTIC v%s ..." % version
        print




    def set_config(my, path, attr, value):
        settings = my.config.get(path)
        if not settings:
            settings = {}
            my.config[path] = settings

        settings[attr] = value


    def set_windows_service(my):
        # set init_only=True so that start() does not block
        my.init_only = True


    def get_config(my):
        return my.config


    def stop(my):
        cherrypy.server.stop()


    def execute(my):
        cherrypy.config.update( my.config )
        cherrypy.server.start(my.init_only)


    def setup_env(my):
        '''set up environment'''

        # register this as a cherrypy server
        os.environ['TACTIC_APP_SERVER'] = "cherrypy"

	# DEPRECATED: don't need to do this anymore as the default will
	# handled in __init__.py
        """
        if os.name == "nt":
            conf = "tactic_win32-conf.xml"
        else:
            conf = "tactic_linux-conf.xml"

        # set up config path 
        os.environ['TACTIC_CONFIG_PATH'] = "%s/config/%s" % (my.site_dir,conf)
        """




    def setup_sites(my):

        context_path = "%s/src/context" % my.install_dir
        doc_dir = "%s/doc" % my.install_dir

        log_dir = "%s/log" % Environment.get_tmp_dir()

        config = {
            'global':   {'server.socket_host': 'localhost',
                         'server.socket_port': 80,
                         'server.log_to_screen': False,
                         'server.environment': 'production',
                         'server.show_tracebacks': True,
                         'server.log_request_headers': True,
                         'server.log_file': "%s/tactic_log" % log_dir,
                         'server.max_request_body_size': 0,
                         #'server.socket_timeout': 60,
                         'response.timeout': 3600,
                         'log_debug_info_filter.on': False,

                         #'encoding_filter.on': True,
                         #'decoding_filter.on': True,
                        },
            '/context': {'static_filter.on': True,
                         'static_filter.dir': context_path
                        },
            '/assets':  {'static_filter.on': True,
                         'static_filter.dir': Environment.get_asset_dir()
                        },
            '/doc':     {'static_filter.on': True,
                         'static_filter.dir': doc_dir
                        },
            '/doc/':    {'static_filter.on': True,
                         'static_filter.file': "%s/index.html" % doc_dir
                        },
        }


        # set up the root directory
        cherrypy.root = Root()
        from tactic_sites.default.context.TitlePage import TitlePage
        cherrypy.root.tactic = TitlePage()
        cherrypy.root.projects = TitlePage()


       
        sites = []

        # add the tactic projects
        install_dir = Environment.get_install_dir().replace("\\", "/")
        site_dir = "%s/src/tactic_sites" % install_dir
        for context_dir in os.listdir(site_dir):
            if context_dir.startswith(".svn"):
                continue
                
            full_path  = "%s/%s" % (site_dir, context_dir)
            
            if os.path.isdir(full_path):
                sites.append(context_dir)



        # add all the custom projects
        site_dir = Environment.get_site_dir().replace("\\", "/")
        site_dir = "%s/sites" % site_dir
        for context_dir in os.listdir(site_dir):
            if context_dir.startswith(".svn"):
                continue
                
            full_path  = "%s/%s" % (site_dir, context_dir)
            
            if os.path.isdir(full_path):
                sites.append(context_dir)

        for site in sites:
            my.register_project(site, config)

            # set up the images directory
            for subdir in ['images', 'doc']:
                config["/tactic/%s/%s/" % (site,subdir)] = {
                    'static_filter.on': True,
                    'static_filter.dir': '%s/sites/%s/context/%s/' % \
                        (site_dir,site, subdir)
                }

        return config



    def register_project(my, site, config):
        print "Registering project ... %s" % site

        # if there happend to be . in the site name, convert to _
        # NOTE: not sure what the implication of that is???
        site = site.replace(".", "_")

        if site == "template":
            return

        # BIG HACK to get admin site working
        if site in ['admin', 'default', 'template', 'unittest']:
            base = "tactic_sites"
        else:
            base = "sites"

        try:
            #exec("from %s.%s.context.Index import Index" % (base,site) )
            #exec("cherrypy.root.tactic.%s = Index()" % site)
            #exec("cherrypy.root.projects.%s = Index()" % site)

            from tactic.ui.app import SitePage
            exec("cherrypy.root.tactic.%s = SitePage()" % site)
            exec("cherrypy.root.projects.%s = SitePage()" % site)

        except ImportError:
            #print "... WARNING: Index not found"
            exec("cherrypy.root.tactic.%s = TacticIndex()" % site)
            exec("cherrypy.root.projects.%s = TacticIndex()" % site)

            

        # get the contexts: 
        if site in ("admin", "default", "template", "unittest"):
            context_dir = Environment.get_install_dir().replace("\\", "/")
            context_dir = "%s/src/tactic_sites/%s/context" % (context_dir, site)
        else:
            context_dir = Environment.get_site_dir().replace("\\", "/")
            context_dir = "%s/sites/%s/context" % (context_dir, site)

        if not os.path.exists(context_dir):
            #print "WARNING: context directory not found"
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
                settings['xmlrpc_filter.on'] = True

            # NOTE: is this needed anymore?
            if context in ["UploadServer"]:
                settings['flashwrapper.on'] = True




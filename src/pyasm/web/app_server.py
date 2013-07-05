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

__all__ = ['AppServer', 'BaseAppServer', 'XmlrpcServer', 'get_site_import', 'get_main_tab_wdg']

import re, types

from pyasm.common import *
from pyasm.search import SObjectFactory, DbContainer, ExceptionLog, SearchType, Search, Sql, DatabaseException
from pyasm.security import *
from pyasm.biz import PrefSetting

from web_container import WebContainer
from widget import Widget, Html
from web_app import WebApp
from command_delegator import CommandDelegator
from event_container import EventContainer
from web_tools import *
from html_wdg import *
from url_security import *
from translation import *

import os, cStringIO

try:
    import profile, pstats
except ImportError:
    PROFILE = False
else:
    PROFILE = True

class AppServerException(Exception):
    pass


class BaseAppServer(Base):
    '''The base application server class that handles the top level processing
    of a given page.  Different applications will derive off of this class
    to implement how the resulting html will go to the server'''
    

    ONLOAD_EVENT = "body_onload"

    if PROFILE:
        profile.object = None


    def __init__(my):
        my.top = None
        super(BaseAppServer,my).__init__()


    def writeln(my, string):
        my.buffer.write(string)


    def get_display(my):

        profile_flag = False

        if profile_flag:
            BaseAppServer.profile.object = my
            if os.name == 'nt':
                path = "C:/sthpw/profile"
            else:
                path = "/tmp/sthpw/temp/profile"
            profile.run( "from pyasm.web.app_server import BaseAppServer; BaseAppServer.profile()", path)
            p = pstats.Stats(path)
            p.sort_stats('cumulative').print_stats(30)
            print "*"*30
            p.sort_stats('time').print_stats(30)

        else:
            my.execute()

        value = WebContainer.get_buffer().getvalue()
        WebContainer.clear_buffer()
        return value



    def profile():
        my = BaseAppServer.profile.object
        my.execute()
    profile = staticmethod(profile)



    def execute(my):
        my.buffer = cStringIO.StringIO()

        try:
            try:

                # clear the main container for this thread
                Container.create()

                # clear the buffer
                WebContainer.clear_buffer()

                # initialize the web environment object and register it
                adapter = my.get_adapter()
                WebContainer.set_web(adapter)

                # get the display
                my._get_display()

            except SetupException, e:
                '''Display setup exception in the interface'''
                print "Setup exception: ", e.__str__()
                DbContainer.rollback_all()
                ExceptionLog.log(e)
                my.writeln("<h3>Tactic Setup Error</h3>" )
                my.writeln("<pre>" )
                my.writeln(e.__str__() )
                my.writeln("</pre>" )

            except DatabaseException, e:
                from tactic.ui.startup import DbConfigPanelWdg
                config_wdg = DbConfigPanelWdg()
                my.writeln("<pre>")
                my.writeln(config_wdg.get_buffer_display())
                my.writeln("</pre>")


            except Exception, e:
                stack_trace = ExceptionLog.get_stack_trace(e)
                print stack_trace
                my.writeln("<pre>")
                my.writeln(stack_trace)
                my.writeln("</pre>")

                # it is possible that the security object was not set
                security = Environment.get_security()
                if not security:
                    security = Security()
                    WebContainer.set_security(security)

                log = None
                # ensure that database connections are rolled back
                try:
                    DbContainer.rollback_all()
                except Exception, e2:
                    print "Error: Could not rollback: ", e2.__str__()
                    my.writeln("Error: Could not rollback: '%s'" % e2.__str__() )
                    stack_trace = ExceptionLog.get_stack_trace(e2)
                    print stack_trace
                    my.writeln("<pre>")
                    my.writeln(stack_trace)
                    my.writeln("</pre>")
                    raise e
                    #return


                try:
                    # WARNING: if this call causes an exception, the error
                    # will be obscure
                    log = ExceptionLog.log(e)
                except Exception, e2:

                    print "Error: Could not log exception: ", e2.__str__()
                    my.writeln("Error '%s': Could not log exception" % e2.__str__() )
                    stack_trace = ExceptionLog.get_stack_trace(e2)
                    print stack_trace
                    my.writeln("<pre>")
                    my.writeln(stack_trace)
                    my.writeln("</pre>")
                    return

                my.writeln("<pre>")
                my.writeln("An Error has occurred.  Please see your Tactic Administrator<br/>")
                my.writeln( "Error Message: %s" % log.get_value("message") )
                my.writeln("Error Id: %s" % log.get_id() )
                my.writeln( log.get_value("stack_trace") )
                my.writeln("</pre>")


        finally:
            # ensure that database connections are always closed
            DbContainer.close_all()
            # clear the container
            Container.delete()
            WebContainer.get_buffer().write( my.buffer.getvalue() )





    def _get_display(my):

        # set up the security object
        security = Security()

        security = my.handle_security(security)
        is_logged_in = security.is_logged_in()

        # if not logged in then display
        if not is_logged_in:

            # login as guest
            security = Security()
            #my.handle_guest_security(security)

            from pyasm.widget import WebLoginWdg, BottomWdg
            from tactic.ui.app import TitleTopWdg
            widget = Widget()
            top = TitleTopWdg()
            widget.add(top)
            body = top.get_body()
            body.add_gradient("background", "background", 5, -20)
            body.add_color("color", "color")
            web = WebContainer.get_web()

            # see if there is a custom login page
            search = Search("config/url")

            allow_guest = False
            if not allow_guest:
                search.add_filter("url", "/login")
                hash = "/login"
                my.handle_guest_security(security)
            else:
                search.add_filter("url", "/guest")
                hash = "/guest"
                # login as guest
                my.handle_guest_security(security)


            url = search.get_sobject()
            use_default = False
            if url:
                from tactic.ui.panel import HashPanelWdg
                try:
                    custom_wdg = HashPanelWdg.get_widget_from_hash(hash, return_none=True)
                    top.add(custom_wdg)
                except Exception, e:

                    from pyasm.widget import ExceptionWdg
                    exception = ExceptionWdg(e)
                    msg = str(e)
                    top.add(msg)
                    top.add(exception)
                    use_default = True

            else:
                use_default = True

            if use_default:
                reset_request = web.get_form_value('reset_request') =='true'
                if reset_request:
                    from tactic.ui.widget import ResetPasswordWdg
                    top.add(ResetPasswordWdg())
                else:
                    reset_msg = web.get_form_value('reset_msg')
                    if reset_msg:
                        web.set_form_value(WebLoginWdg.LOGIN_MSG, reset_msg)
                    top.add(WebLoginWdg() )

            # create a web app and run it through the pipeline
            web_app = WebApp()
            web_app.get_display(widget)
            return




        is_first_run = Environment.is_first_run()
        if is_first_run:
            from pyasm.widget import WebLoginWdg, BottomWdg
            top = my.get_top_wdg()

            from tactic.ui.app import PageHeaderWdg
            from tactic.ui.startup import DbConfigPanelWdg

            widget = DivWdg()
            #widget.add_color("background", "background2", +10)
            widget.add( top )
            widget.add( DbConfigPanelWdg() )
            widget.add( BottomWdg() )

            web_app = WebApp()
            web_app.get_display(widget)
            return
            






        # handle licensing
        license = security.get_license()
        user_name = security.get_user_name()
        is_licensed = license.is_licensed()

        # This is too restrictive, skip this WebLicense error display for now
        """
        if not user_name == "admin" and not is_licensed:
            from pyasm.widget import WebLicenseWdg, BottomWdg
            from pyasm.command import SignOutCmd
            widget = Widget()
            top = my.get_top_wdg()
            body = top.get_body()
            body.set_class("body_login")
            widget.add( top )
            
            widget.add( WebLicenseWdg() )
            widget.add( BottomWdg() )
            
            cmd = SignOutCmd()
            cmd.set_login_name(Environment.get_user_name())
            cmd.execute()
            # order matters here
            security.sign_out()
            widget.get_display()
            return
        """

        # handle url security
        url_security = UrlSecurity()
        html = url_security.get_display()
        if html:
            widget = Widget()
            widget.add(html.getvalue())
            widget.get_display()
            return

        web = WebContainer.get_web()

        # handle project security
        project = web.get_context_name()

        # FIXME: view should really be "allow" here, but it doesn't seem to work
        if project != 'default':
            security_version = get_security_version()
            if security_version == 1:
                default = "view"
                access = security.check_access("project", project, "view", default="view")
            else:
                default = "deny"
                key = { "code": project }
                key2 = { "code": "*" }
                #keys = [key]
                keys = [key, key2]
                access = security.check_access("project", keys, "allow", default=default)

            #print "security: ", security_version
            #print "access: ", access

            if not access:
                Translation.install()
                from pyasm.widget import WebLicenseWdg, BottomWdg, Error403Wdg
                widget = Widget()
                top = my.get_top_wdg()
                widget.add( top )
                widget.add( Error403Wdg() )
                widget.add( BottomWdg() )
                widget.get_display()
     
                return



        # determine the type of request
        if '/UploadServer' in web.get_request_url().to_string():
            page_type = "upload"
        elif web.get_form_value("ajax") != "":
            page_type = "ajax"
        elif web.get_form_value("dynamic_file") != "":
            # this mode creates a file dynamically
            page_type = "dynamic_file"
        else:
            page_type = "normal"


        # TODO: the following could be combined into a page_init function
        # provide the opportunity to set some templates
        my.set_templates()
        my.add_triggers()

        my.init_web_container()
        # make sure the user is logged in.  If not, no commands can be
        # executed
        if is_logged_in:
            my.handle_commands()


        # install the language
        Translation.install()

        widget = my.get_content(page_type)

        # put an annoying alert if there is a problem with the licensed
        if not is_licensed:
            # to be sure, reread license.  This gets around the problem
            # of the extra error message when uploading a new license
            license = security.reread_license()
            is_licensed = license.is_licensed()
            if not is_licensed:
                widget.add("<script>alert('%s')</script>" % license.get_message())

        # create a web app and run it through the pipeline
        web_app = WebApp()
        web_app.get_display(widget)







    def handle_security(my, security):
        # set the seucrity object
        WebContainer.set_security(security)

        # see if there is an override
        web = WebContainer.get_web()
        ticket_key = web.get_form_value("login_ticket")
        # attempt to login in with a ticket
        if not ticket_key:
            ticket_key = web.get_cookie("login_ticket")

        security.login_with_ticket(ticket_key, add_access_rules=False)

        if not security.is_logged_in():
            reset_password = web.get_form_value("reset_password") == 'true'
            if reset_password:
                from tactic.ui.widget import ResetPasswordCmd
                reset_cmd = ResetPasswordCmd(reset=True)
                try:
                    reset_cmd.execute()
                except TacticException, e:
                    print "Reset failed. %s" %e.__str__()
            else:
                from pyasm.widget import WebLoginCmd
                login_cmd = WebLoginCmd()
                login_cmd.execute()
        else:
            web.set_cookie("login_ticket", ticket_key)


        # set up default securities
        my.set_default_security(security)

        # for now apply the access rules after
        security.add_access_rules()

        return security


    def handle_guest_security(my, security):

        WebContainer.set_security(security)
        security.login_as_guest()

        """
        access_manager = security.get_access_manager()

        xml = Xml()
        xml.read_string('''
        <rules>
          <rule group="project" code="*" access="allow"/>
          <rule group="search_type" code="*" access="allow"/>
        </rules>
        ''')
        access_manager.add_xml_rules(xml)
        """
 


    def handle_commands(my):
        cmd_delegator = CommandDelegator()
        WebContainer.set_cmd_delegator( cmd_delegator )

        # use the command delegator to issue commands
        cmd_delegator = WebContainer.get_cmd_delegator()
        if cmd_delegator != None:
            cmd_delegator.execute()

    def init_web_container(my):
        # add the event container, initialization only
        event_container = EventContainer()
        WebContainer.set_event_container( event_container )


    def get_content(my, request_type):
        web = WebContainer.get_web()

        if request_type in ["upload", "dynamic_file"]:
            widget = Widget()
            page = my.get_page_widget()
            widget.add(page)
            return widget


        #
        # New UI ... WidgetServer still goes through old app server
        #
        request = WebContainer.get_web().get_env("PATH_INFO")
        if request and request.find("/WidgetServer") == -1:
            #from tactic.ui.app import ApplicationWdg
            #application = ApplicationWdg()
            from tactic.ui.app import TopWdg
            application = TopWdg()

            # get the main page widget
            # NOTE: this needs to happen after the body is put in a Container
            page = my.get_page_widget()
            page.set_as_top()
            if type(page) in types.StringTypes:
                page = StringWdg(page)

            application.add(page, 'content')
            return application


        #
        # Old application server ... this is kept around for backwards
        # compatibility
        #


        raise TacticException("is this still being run???")

        # TODO: get rid of this dependency
        from pyasm.web import StringWdg
        from pyasm.widget import IframeWdg, IframePlainWdg, CmdReportWdg, \
            FloatMenuWdg, WarningReportWdg, DebugWdg, BottomWdg, PyMayaInit,\
            PyHoudiniInit, PyXSIInit, PopupMenuWdg


        widget = Widget()


        # create some singletons and store in container
        cmd_delegator = WebContainer.get_cmd_delegator()
        
        # add the event container
        event_container = WebContainer.get_event_container()
        

        # standard empty iframe for overlays
        iframe = IframeWdg()
        Container.put("iframe", iframe)
        iframe_plain = IframePlainWdg()
        Container.put("iframe_plain", iframe_plain)
        # standard cmd_report for drawing of command exceptions
        report = CmdReportWdg()
        # this is used for checking errors for EditWdg
        Container.put("cmd_report", report)
        float_menu = FloatMenuWdg('float_menu')
        Container.put("float_menu", float_menu) 

        help_menu = PopupMenuWdg('help_menu', multi=False)
        help_menu.add_title('help')
        help_menu.set_offset(-50, 0)
        Container.put("help_menu", help_menu) 
        warn_menu = PopupMenuWdg('warn_menu', multi=False)
        warn_menu.add_title('warning')
        warn_menu.set_offset(-50, 0)
        Container.put("warn_menu", warn_menu) 
        warning_report = WarningReportWdg()

        # build the widget hierarchy
        if request_type == "ajax":
            
            # create a new web app object
            page = my.get_page_widget()
            if type(page) in types.StringTypes:
                page = StringWdg(page)
            page.set_as_top()
            widget.add(page)
            widget.add(warning_report)
            widget.add(cmd_delegator)
            # this technically gets written to the page, but does not 
            # work without further parsing  
            event_container.set_mode(EventContainer.DYNAMIC)
            widget.add(event_container)
            request = WebContainer.get_web().get_env("HTTP_REFERER")
            if request and request.find("/Maya") == -1:
                # re-creation of tips (this is run at the bottom of the page)
                onload_script = HtmlElement.script('Effects.tip()')
                onload_script.set_attr('mode','dynamic')
                widget.add(onload_script) 

            return widget



        #
        # Old application
        #
        top = my.get_top_wdg()
        
        event_name = my.ONLOAD_EVENT
        function = WebContainer.get_event_container()\
            .get_event_caller(event_name)
        body = top.get_body()

        Container.put("body", body)

        # HACK: put in maya embed requirement
        request = WebContainer.get_web().get_request_url().to_string()
        if request.find("/Maya") != -1:
            body.add_event("onload", "MWT_Embed('MCP','commandportDefault')")
        
        body.add_event('onload', function)
        body.add_event('onload', 'spt.onload_startup()')    # added for new "spt" core javascript setup
        
        # restore the scroll position
        if WebContainer.get_web().get_browser() != "IE":
            body.add_event('onload', 'Common.scroll_y()')
            body.add_event('onunload', "window.name=document.body.scrollTop")

            body.add_event('onmousedown', "PopupDiv_middle_click(event,'middle_bubble','float_menu','action')")

        # get the main page widget
        # NOTE: this needs to happen after the body is put in a Container
        page = my.get_page_widget()
        page.set_as_top()
        if type(page) in types.StringTypes:
            page = StringWdg(page)

        debug = DebugWdg()
        bottom = BottomWdg()

        widget.add(top)
        widget.add(iframe)
        widget.add(iframe_plain)
        widget.add(report)


        # Set the application widgets
        context = web.get_env("PATH_INFO")
        if context.find("Maya") > 0:
            widget.add( PyMayaInit() )
        elif context.find("Houdini") > 0:
            widget.add( PyHoudiniInit() )
        elif context.find("XSI") > 0:
            widget.add( PyXSIInit() )
        else:
            widget.add( PyMayaInit() )


        # initialize hint bubble
        widget.add(HtmlElement.script("var hint_bubble=new PopupDiv('hints','plain')"))
        widget.add(HtmlElement.script("var comment_bubble=new PopupDiv('comments','comment')"))
        widget.add(HtmlElement.script("var help_menu = new HelpMenu()"))
        widget.add(HtmlElement.script("var warn_menu = new WarnMenu()"))


        widget.add(page)
        widget.add(warning_report)
        widget.add(float_menu)
        widget.add(help_menu)
        widget.add(warn_menu)
        widget.add(cmd_delegator)
        widget.add(event_container)

        widget.add(debug)
        #widget.add(dragdrop)

        # FIXME: IE cannot use the tool tips
        # run at the bottom, not really onload script for now
        if WebContainer.get_web().get_browser() != "IE":
            onload_script = 'Effects.tip()'
            widget.add(HtmlElement.script(onload_script))

        widget.add(bottom)

        return widget






    def log_exception(my, exception):
        import sys,traceback
        tb = sys.exc_info()[2]
        stacktrace = traceback.format_tb(tb)
        stacktrace_str = "".join(stacktrace)
        print "-"*50
        print stacktrace_str
        print str(exception)
        print "-"*50

        user_name = Environment.get_user_name()
        exception_log = SObjectFactory.create("sthpw/exception_log")
        exception_log.set_value("login", user_name)
        exception_log.set_value("class", exception.__class__.__name__)
        exception_log.set_value("message", str(exception) )

        exception_log.set_value("stack_trace", stacktrace_str)

        exception_log.commit()

        del tb, stacktrace



    #
    # virtual functions
    #
    def set_default_security(my, security):
        '''set a number of default security rules to be always implemented'''
        rules = AppServerSecurityRules(security)



    def get_page_widget(my):
        '''get the content widget'''
        return "No Content"

    def get_top_wdg(my):
        #from pyasm.widget import TopWdg
        from tactic.ui.app import TopWdg
        my.top = TopWdg()
        return my.top


    def add_triggers(my):
        '''callback that enables a site to add custom triggers'''
        pass


    def set_templates(my):
        '''callback where sobject templates can be set'''
        pass

    def add_onload_script(script):
        ''' this does not work on Login screen'''
        event = WebContainer.get_event_container()
        event.add_listener(BaseAppServer.ONLOAD_EVENT, script)

    add_onload_script = staticmethod(add_onload_script)    
        


class AppServerSecurityRules(object):
    ''' A set of rules applied at the start up of drawing of a page'''
    def __init__(my, security):
        assert security != None
        my.security = security
        my.access_manager = security.get_access_manager()

        # we just need one instance of my.xml
        my.xml = Xml() 
        my.execute()

    def execute(my):
        my.add_wdg_rules()

        # the main administrator has no default restrictions
        if 'admin' not in my.security.get_group_names():
            my.add_default_rules()

    def add_wdg_rules(my):
        ''' these rules are to be applied to all users'''
        my.xml.read_string('''
        <rules>
          <rule category='secure_wdg' default='deny'/>
          <rule category='public_wdg' access='edit'/>
        </rules>
        ''')
            
        my.access_manager.add_xml_rules(my.xml)

    def add_default_rules(my):
        ''' these rules are to be applied to all but users in the admin group'''

        security_version = get_security_version()

        if security_version == 1:
            my.xml.read_string('''
            <rules>
              <rule group='project' default='view'/>  
              <rule group='project' key='admin' access='deny'/>
              <rule group='tab' key='Admin' access='deny'/>
            </rules>
            ''') 
            my.access_manager.add_xml_rules(my.xml)



# NOTE: this function has to be declared after BaseAppServer
def get_app_server_class():

    app_server = os.getenv('TACTIC_APP_SERVER')
    if app_server == "webware":
        from webware_adapter import get_app_server
    elif app_server == "cherrypy":
        import cherrypy
        if cherrypy.__version__.startswith("3."):
            from cherrypy30_adapter import get_app_server
        else:
            from cherrypy_adapter import get_app_server
    elif app_server == "batch":
        return object
    else:
        #raise AppServerException("Environment variable TACTIC_APP_SERVER not set")
        # default to webware for now
        #print "WARNING: Environment variable TACTIC_APP_SERVER not set"
        #from webware_adapter import get_app_server
        return object

    return get_app_server()


def get_xmlrpc_server_class():
    app_server = os.getenv('TACTIC_APP_SERVER')
    if app_server == "webware":
        from webware_adapter import get_xmlrpc_server
    elif app_server == "cherrypy":
        import cherrypy
        if cherrypy.__version__.startswith("3."):
            from cherrypy30_adapter import get_xmlrpc_server
        else:
            from cherrypy_adapter import get_xmlrpc_server
    elif app_server == "batch":
        return object
    else:
        #raise AppServerException("Environment variable TACTIC_APP_SERVER not set")
        # default to webware for now
        #print "WARNING: Environment variable TACTIC_APP_SERVER not set"
        #from webware_adapter import get_xmlrpc_server
        return object

    return get_xmlrpc_server()


AppServer = get_app_server_class()
XmlrpcServer = get_xmlrpc_server_class()



def get_site_import(file):
    '''function used by entry points into the AppServer to load the necessary
    import function to see site specific modules

    The following 2 lines should be included:

    from pyasm.web import get_site_import
    exec( get_site_import(__file__) )
    '''
    file = file.replace("\\","/")
    p = re.compile( r'\/(\w+)\/context\/' )
    m = p.search(file)
    if not m:
        raise Exception("Can't find context")

    context = m.groups()[0]
    if context == "":
        context = "default"

    if context in ['admin', 'default', 'template', 'unittest']:
        return "from tactic_sites.%s.modules import *" % context
    else:
        return "from sites.%s.modules import *" % context



def get_main_tab_wdg():
    from pyasm.biz import Project
    project = Project.get()
    type = project.get_base_type()
    if type == "":
        raise TacticException("Project: %s has no type" % project.get_code())
    exec( "from pyasm.%s.site import MainTabWdg" % type )
    tab = MainTabWdg()
    return tab



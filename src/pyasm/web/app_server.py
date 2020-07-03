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
from pyasm.search import SObjectFactory, DbContainer, DbResource, ExceptionLog, SearchType, Search, Sql, DatabaseException
from pyasm.security import *
from pyasm.biz import PrefSetting, Translation

from .web_container import WebContainer
from .widget import Widget, Html
from .web_app import WebApp
from .command_delegator import CommandDelegator
from .event_container import EventContainer
from .web_tools import *
from .html_wdg import *
from .url_security import *
from .web_login_cmd import WebLoginCmd

import os

import six
basestring = six.string_types


try:
    from cStringIO import StringIO as Buffer
except:
    from io import StringIO as Buffer



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


    def __init__(self):
        self.top = None
        self.hash = None
        super(BaseAppServer,self).__init__()


    def writeln(self, string):
        self.buffer.write(string)


    def get_display(self):

        profile_flag = False

        if profile_flag:
            BaseAppServer.profile.object = self
            if os.name == 'nt':
                path = "C:/sthpw/profile"
            else:
                path = "/tmp/sthpw/temp/profile"
            profile.run( "from pyasm.web.app_server import BaseAppServer; BaseAppServer.profile()", path)
            p = pstats.Stats(path)
            p.sort_stats('cumulative').print_stats(30)
            print("*"*30)
            p.sort_stats('time').print_stats(30)

        else:
            self.execute()

        value = WebContainer.get_buffer().getvalue()
        WebContainer.clear_buffer()


        return value



    def profile():
        self = BaseAppServer.profile.object
        self.execute()
    profile = staticmethod(profile)



    def execute(self):
        self.buffer = Buffer()
        error = None

        try:
            try:

                # clear the main container for this thread
                Container.create()

                # clear the buffer
                WebContainer.clear_buffer()

                # initialize the web environment object and register it
                adapter = self.get_adapter()
                WebContainer.set_web(adapter)

                # get the display
                self._get_display()

            except SetupException as e:
                '''Display setup exception in the interface'''
                print("Setup exception: ", e.__str__())
                DbContainer.rollback_all()
                ExceptionLog.log(e)
                self.writeln("<h3>Tactic Setup Error</h3>" )
                self.writeln("<pre>" )
                self.writeln(e.__str__() )
                self.writeln("</pre>" )
                error = "405: TACTIC Setup Error"

            except DatabaseException as e:
                from tactic.ui.startup import DbConfigPanelWdg
                config_wdg = DbConfigPanelWdg()
                self.writeln("<pre>")
                self.writeln(config_wdg.get_buffer_display())
                self.writeln("</pre>")
                error = "405: TACTIC Database Error"


            except Exception as e:
                stack_trace = ExceptionLog.get_stack_trace(e)
                #print(stack_trace)
                self.writeln("<pre>")
                self.writeln(stack_trace)
                self.writeln("</pre>")
                error = "405 %s" % str(e)

                # it is possible that the security object was not set
                security = Environment.get_security()
                if not security:
                    security = Security()
                    WebContainer.set_security(security)

                log = None
                # ensure that database connections are rolled back
                try:
                    DbContainer.rollback_all()
                except Exception as e2:
                    print("Error: Could not rollback: ", e2.__str__())
                    self.writeln("Error: Could not rollback: '%s'" % e2.__str__() )
                    stack_trace = ExceptionLog.get_stack_trace(e2)
                    print(stack_trace)
                    self.writeln("<pre>")
                    self.writeln(stack_trace)
                    self.writeln("</pre>")
                    raise e
                    #return


                try:
                    # WARNING: if this call causes an exception, the error
                    # will be obscure
                    log = ExceptionLog.log(e)
                except Exception as e2:

                    print("Error: Could not log exception: ", e2.__str__())
                    self.writeln("Error '%s': Could not log exception" % e2.__str__() )
                    stack_trace = ExceptionLog.get_stack_trace(e2)
                    print(stack_trace)
                    self.writeln("<pre>")
                    self.writeln(stack_trace)
                    self.writeln("</pre>")
                    return

                self.writeln("<pre>")
                self.writeln("An Error has occurred.  Please see your Tactic Administrator<br/>")
                self.writeln( "Error Message: %s" % log.get_value("message") )
                self.writeln("Error Id: %s" % log.get_id() )
                #self.writeln( log.get_value("stack_trace") )
                self.writeln("</pre>")


        finally:
            # ensure that database connections are always closed
            DbContainer.close_all()
            # clear the container
            Container.delete()
            WebContainer.get_buffer().write( self.buffer.getvalue() )

            if error:
                import cherrypy
                print("error: ", error)
                cherrypy.response.status = error
                #raise Exception(error)



    def handle_not_logged_in(self, allow_change_admin=True):


        site_obj = Site.get()
        site_obj.set_site("default")

        DbResource.clear_cache()


        from pyasm.widget import WebLoginWdg, WebLoginWdg2, BottomWdg
        from tactic.ui.app import TitleTopWdg

        from pyasm.biz import Project
        from tactic.ui.panel import HashPanelWdg


        web = WebContainer.get_web()

        widget = Widget()

        top = TitleTopWdg()
        widget.add(top)
        body = top.get_body()

        reset_msg = web.get_form_value('reset_msg')
        if reset_msg:
            web.set_form_value(WebLoginWdg2.LOGIN_MSG_LABEL, reset_msg)

        web_wdg = None
        sudo = Sudo()
        try:
            # get the project from the url because we are still 
            # in the admin project at this stage
            current_project = web.get_context_name()
            try:
                if current_project != "default":
                    project = Project.get_by_code(current_project)
                    assert project
            except Exception as e:
                pass
            else:

                # custom global site login widget
                if not current_project or current_project == "default":
                    current_project = Project.get_default_project()
                if current_project and current_project != "default":
                    try:
                        Project.set_project(current_project)
                    except SecurityException as e:
                        print(e)
                        if 'is not permitted to view project' not in e.__str__():
                            raise


                    if not web_wdg:
                        web_wdg = site_obj.get_login_wdg()

                    if web_wdg:
                        if not isinstance(web_wdg, basestring):
                            web_wdg = web_wdg.get_buffer_display()
                        top.add(web_wdg)
                else:
                    web_wdg = None

            # display default web login
            if not web_wdg:
                # get login screen from Site
                link = "/%s" % "/".join(self.hash)
                web_wdg = site_obj.get_login_wdg(link)
                if not web_wdg:
                    # else get the default one
                    web_wdg = WebLoginWdg2(allow_change_admin=allow_change_admin, hide_back_btn=True)
                
                top.add(web_wdg)

        finally:
            # sudo out of scope here
            sudo.exit()
            pass


        # create a web app and run it through the pipeline
        web_app = WebApp()
        web_app.get_display(widget)
        return







    def _get_display(self):

        # set up the security object
        from pyasm.security import Security, Sudo
        from pyasm.biz import Project
        from pyasm.web import WebContainer
        web = WebContainer.get_web()


        
        # guest mode
        #
        allow_guest = Config.get_value("security", "allow_guest")
        if allow_guest == 'true':
            allow_guest = True
        else:
            allow_guest = False

        site_obj = Site.get()
        site_allow_guest = site_obj.allow_guest()
        if site_allow_guest != None:
            allow_guest = site_allow_guest



        security = Security()
        try:
            security = self.handle_security(security)
            is_logged_in = security.is_logged_in()
        except Exception as e:
            print("AppServer Exception: ", e)
            raise
            return self.handle_not_logged_in()


        guest_mode = Config.get_value("security", "guest_mode")
        if not guest_mode:
            guest_mode = 'restricted'


        # Test
        #allow_guest = True
        #guest_mode = "full"

        # if not logged in, then log in as guest
        if not is_logged_in:
            if not allow_guest:
                return self.handle_not_logged_in()
            else:
                # login as guest
                security = Security()
                self.handle_guest_security(security)


        # for here on, the user is logged in
        login_name = Environment.get_user_name()

        is_upload = '/UploadServer' in web.get_request_url().to_string()

        # check if the user has permission to see this project
        project = web.get_context_name()
        if project == 'default':
            override_default = Project.get_default_project()
            if override_default:
                project = override_default
        if is_upload:
            print("IS UPLOAD")
            access = True

        elif project != 'default':

            # make sure the security check is done on the appropriate site
            path_info = site_obj.get_request_path_info()
            if path_info:
                site = path_info.get("site")
                Site.set_site(site)
                s = Environment.get_security()
                has_site = True
            else:
                s = security
                has_site = False

            try:
                security_version = get_security_version()
                if security_version == 1:
                    default = "view"
                    access = s.check_access("project", project, "view", default="view")
                else:
                    default = "deny"
                    key = { "code": project }
                    key2 = { "code": "*" }
                    keys = [key, key2]
                    access = s.check_access("project", keys, "allow", default=default)
            finally:
                if has_site:
                    Site.pop_site()


        else:
            # you always have access to the default project
            access = True



        if not access:
            if login_name == "guest":
                from pyasm.widget import WebLoginWdg

                msg = web.get_form_value(WebLoginWdg.LOGIN_MSG)
                if not msg:
                    msg = "User [%s] is not allowed to see this project [%s]" % (login_name, project)
                    web.set_form_value(WebLoginWdg.LOGIN_MSG, msg)
                return self.handle_not_logged_in(allow_change_admin=False)

            else:
                from pyasm.widget import BottomWdg, Error403Wdg
                widget = Widget()
                top = self.get_top_wdg()
                widget.add( top )
                widget.add( Error403Wdg() )
                widget.add( BottomWdg() )
                widget.get_display()
                if is_upload:
                    print("WARNING: User [%s] is not allowed to upload to project [%s]."%(login_name, project))
                return


        if login_name == 'guest':
            # let the site handle the guest completely
            guest_wdg = site_obj.get_guest_wdg(self.hash)
            if guest_wdg:
                web_app = WebApp()
                web_app.get_display(guest_wdg)
                return



        # some extra precautions in guest mode
        if login_name == 'guest' and guest_mode != "full":
            # show a restricted guest mode
            from pyasm.widget import WebLoginWdg, BottomWdg
            from tactic.ui.app import TitleTopWdg

            from pyasm.biz import Project
            from tactic.ui.panel import HashPanelWdg
            web = WebContainer.get_web()



            widget = Widget()
            top = TitleTopWdg()
            widget.add(top)
            body = top.get_body()

            has_site = False

            # use the path to set the project and/or site
            path_info = site_obj.get_request_path_info()
            if path_info:
                path_site = path_info.get("site")

                try:
                    Site.set_site(path_site)
                    has_site = True
                except Exception as e:
                    print("WARNING: ", e)
                    current_project = web.get_context_name()
                else:
                    current_project = path_info.get("project_code")
                    if not current_project:
                        current_project = web.get_context_name()

            else:
                # get the project from the url because we are still 
                # in the admin project at this stage
                current_project = web.get_context_name()



            sudo = Sudo()
            try:
                if current_project != "default":
                    project = Project.get_by_code(current_project, use_cache=False)
                    if not project:
                        raise Exception("Project [%s] does not exist" % current_project)
            except Exception as e:
                print("WARNING: ", e)
                web_wdg = None
            else:
                if not current_project or current_project == "default":
                    current_project = Project.get_default_project()

                if current_project and current_project != "default":
                    try:
                        Project.set_project(current_project)
                    except SecurityException as e:
                        print(e)
                        if 'is not permitted to view project' in e.__str__():
                            pass
                        else:
                            raise


                    # find the guest views
                    #search = Search("config/url")
                    #urls = search.get_sobjects()
                    #open_hashes = [x.get("url").lstrip("/").split("/")[0] for x in urls]

                    link = "/%s" % "/".join(self.hash)

                    # guest views
                    open_hashes = site_obj.get_guest_hashes()

                    if len(self.hash) >= 1 and self.hash[0] in open_hashes:
                        web_wdg = HashPanelWdg.get_widget_from_hash(link, return_none=True)
                    else:
                        web_wdg = None

                    if not web_wdg:
                        web_wdg = HashPanelWdg.get_widget_from_hash("/guest", return_none=True, kwargs={"hash": link})
                    if web_wdg:
                        if not isinstance(web_wdg, basestring):
                            web_wdg = web_wdg.get_buffer_display()
                        top.add(web_wdg)
                else:
                    web_wdg = None
            finally:
                sudo.exit()

                if has_site:
                    Site.pop_site()



            if not web_wdg:
                msg = "No default page defined for guest user. Please set up /guest in Custom URL."
                web.set_form_value(WebLoginWdg.LOGIN_MSG, msg)
                return self.handle_not_logged_in(allow_change_admin=False)


            # create a web app and run it through the pipeline
            web_app = WebApp()
            web_app.get_display(widget)
            return



        # Full access


        # if a guest has full access, then handle it here
        if login_name == 'guest' and guest_mode == "full":
            # some extra security for guest users
            guest_url_allow = Config.get_value("security", "guest_url_allow")
            if guest_url_allow:
                items = guest_url_allow.split("|")
                allowed = False
                if self.hash:
                    url = self.hash[0]
                else:
                    url = "index"
                for item in items:
                    item = item.strip("/")
                    if item == url:
                        allowed = True
                        break
                if not allowed:
                    return self.handle_not_logged_in()




        # Welcome message for first time run
        is_first_run = Environment.is_first_run()
        if is_first_run:
            from pyasm.widget import WebLoginWdg, BottomWdg
            top = self.get_top_wdg()

            from tactic.ui.app import PageHeaderWdg
            from tactic.ui.startup import DbConfigPanelWdg

            widget = DivWdg()
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


        # handle url security
        url_security = UrlSecurity()
        html = url_security.get_display()
        if html:
            widget = Widget()
            widget.add(html.getvalue())
            widget.get_display()
            return

        web = WebContainer.get_web()

        # FIXME: although this works, it should be cleaned up

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
        self.set_templates()
        self.add_triggers()

        self.init_web_container()


        # install the language
        Translation.install()



        path_info = site_obj.get_request_path_info()
        if path_info and path_info.get("site") != "default":
            Site.set_site(path_info.get("site"))
            project_code = path_info.get("project_code")


        # handle the case where the project does not exist
        project = Project.get(no_exception=True)
        if not project:
            from pyasm.widget import BottomWdg, Error404Wdg
            Project.set_project("admin")
            widget = Widget()
            top = self.get_top_wdg()
            widget.add( top )
            widget.add( Error404Wdg() )
            widget.add( BottomWdg() )
            widget.get_display()
            return widget



        # get the content of the page
        try:

            widget = self.get_content(page_type)

        except Exception as e:
            print("ERROR: ", e)
            from pyasm.widget import BottomWdg, Error403Wdg
            widget = Widget()
            top = self.get_top_wdg()
            widget.add( top )
            widget.add( Error403Wdg() )
            widget.add( BottomWdg() )
            widget.get_display()

        # put an annoying alert if there is a problem with the license
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




    def handle_security(self, security, allow_guest=False):
        # set the security object

        WebContainer.set_security(security)

        # see if there is an override
        web = WebContainer.get_web()
        is_from_login = web.get_form_value("is_from_login")
        
        ticket_key = web.get_form_value("login_ticket")

        # attempt to login in with a ticket
        if not ticket_key and is_from_login !='yes':
            ticket_key = web.get_cookie("login_ticket")


        # We can define another place to look at ticket values and use
        # that. ie: Drupal session key
        session_key = Config.get_value("security", "session_key")

        login = web.get_form_value("login")
        password = web.get_form_value("password")


        site_obj = Site.get()
        path_info = site_obj.get_request_path_info()
        if path_info:
            site = path_info['site']
            if site == "default":
                site = web.get_form_value("site")
            if not site:
                site = "default"

        else:
            site = web.get_form_value("site")

        if session_key:
            ticket_key = web.get_cookie(session_key)
            if ticket_key:
                security.login_with_session(ticket_key, add_access_rules=False)
        elif login and password:

            # get the site for this user
            sudo = Sudo()
            try:
                login_site = site_obj.get_by_login(login)
            finally:
                sudo.exit()

            if login_site:
                site = login_site

            if site:
                site_obj.set_site(site)

            if login == "guest":
                pass
            else:
                login_cmd = WebLoginCmd()
                login_cmd.execute()

                ticket_key = security.get_ticket_key()
              
                if not ticket_key:
                    if site:
                        site_obj.pop_site()
                    return security

        elif ticket_key:
          
            if site:
                site_obj.set_site(site)

            login = security.login_with_ticket(ticket_key, add_access_rules=False, allow_guest=allow_guest)
            # In the midst of logging out, login is None
            if not login:
                if site:
                    site_obj.pop_site()
                return security

        if not security.is_logged_in():
            reset_password = web.get_form_value("reset_password") == 'true'
            new_password = web.get_form_value("new_password") == 'true'
            resend_code = web.get_form_value('resend_code') == 'true'
            send_code = web.get_form_value("send_code") == 'true'
            if reset_password:
                pass
            elif new_password:
                from tactic.ui.widget import NewPasswordCmd
                reset_cmd = NewPasswordCmd()
                try:
                    reset_cmd.execute()
                except TacticException as e:
                    print("Reset failed. %s" %e.__str__())
            elif send_code or resend_code:
                from tactic.ui.widget import ResetOptionsCmd
                reset_cmd = ResetOptionsCmd(reset=True)
                try:
                    reset_cmd.execute()
                except TacticException as e:
                    print("Reset failed. %s" %e.__str__())

            # let empty username or password thru to get feedback from WebLoginCmd
            else:
                login_cmd = WebLoginCmd()
                login_cmd.execute()
                ticket_key = security.get_ticket_key()
	
        # clear the password
        web.set_form_value('password','')

        if session_key:
            web.set_cookie("login_ticket", ticket_key)
        elif ticket_key:
            web.set_cookie("login_ticket", ticket_key)



        # TEST TEST TEST
        """
        try:
            ticket = security.get_ticket()
            if ticket:
                site_obj.handle_ticket(ticket)
        except Exception as e:
            print("ERROR in handle_ticket: ", e)
        """



        # set up default securities
        #self.set_default_security(security)

        # for now apply the access rules after
        security.add_access_rules()

        return security


    def handle_guest_security(self, security):
       
        # skip storing current security since it failed
        Site.set_site("default", store_security=False)
        try:

            WebContainer.set_security(security)
            
            security.login_as_guest()
            
            ticket_key = security.get_ticket_key()

            
            web = WebContainer.get_web()
            web.set_cookie("login_ticket", ticket_key)

            access_manager = security.get_access_manager()
            xml = Xml()
            xml.read_string('''
            <rules>
              <rule column="login" value="{$LOGIN}" search_type="sthpw/login" access="deny" op="!=" group="search_filter"/>
            </rules>
            ''')
            access_manager.add_xml_rules(xml)
        finally:
            Site.pop_site(pop_security=False)
           


    def init_web_container(self):
        # add the event container, initialization only
        event_container = EventContainer()
        WebContainer.set_event_container( event_container )


    def get_content(self, request_type):
        web = WebContainer.get_web()

        # NOTE: is this needed anymore?
        if request_type in ["upload", "dynamic_file"]:
            print("DEPRECATED: dynamic file in app_server.py")
            widget = Widget()
            page = self.get_page_widget()
            widget.add(page)
            return widget


        # find hash of url
        self.custom_url = None
        if self.hash:
            hash = "/".join(self.hash)
            hash = "/%s" % hash
            from tactic.ui.panel import HashPanelWdg
            self.custom_url = HashPanelWdg.get_url_from_hash(hash)
            if self.custom_url:
                content_type = self.custom_url.get_value("content_type", no_exception=True)
            # TODO: we may want to handle this differently for content types
            # other that text/html




        return self.get_application_wdg()



    def log_exception(self, exception):
        import sys,traceback
        tb = sys.exc_info()[2]
        stacktrace = traceback.format_tb(tb)
        stacktrace_str = "".join(stacktrace)
        print("-"*50)
        print(stacktrace_str)
        print(str(exception))
        print("-"*50)

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
    def set_default_security(self, security):
        '''set a number of default security rules to be always implemented'''
        rules = AppServerSecurityRules(security)


    def get_application_wdg(self):

        application = self.get_top_wdg()

        # get the main page widget
        # NOTE: this needs to happen after the body is put in a Container
        page = self.get_page_widget()
        page.set_as_top()
        if isinstance(page, six.string_types):
            page = StringWdg(page)

        application.add(page, 'content')
        return application



    def get_page_widget(self):
        '''get the content widget'''
        return "No Content"

    def get_top_wdg(self):
        from tactic.ui.app import TopWdg
        self.top = TopWdg()
        return self.top


    def get_single_widget(self, widget, minimal=True):

        from pyasm.widget import BottomWdg
        from tactic.ui.app import TitleTopWdg
        if minimal: 
            top = TitleTopWdg()
        else:
            top = self.get_top_wdg()

        container = Widget()

        container.add( top )
        top.add( widget )
        container.add( BottomWdg() )
        container.get_display()
        return container


    def add_triggers(self):
        '''callback that enables a site to add custom triggers'''
        pass


    def set_templates(self):
        '''callback where sobject templates can be set'''
        pass

    def add_onload_script(script):
        ''' this does not work on Login screen'''
        event = WebContainer.get_event_container()
        event.add_listener(BaseAppServer.ONLOAD_EVENT, script)

    add_onload_script = staticmethod(add_onload_script)    
        






# NOTE: this function has to be declared after BaseAppServer
def get_app_server_class():

    app_server = os.getenv('TACTIC_APP_SERVER')
    if app_server == "webware":
        from webware_adapter import get_app_server
    elif app_server == "cherrypy":
        import cherrypy
        try:
            cherrypy_major_version = int(cherrypy.__version__.split('.')[0])
        except:
            cherrypy_major_version = 3
        if cherrypy_major_version >= 3:
            from .cherrypy30_adapter import get_app_server
        else:
            from .cherrypy_adapter import get_app_server
    elif app_server == "batch":
        return object
    else:
        #raise AppServerException("Environment variable TACTIC_APP_SERVER not set")
        # default to webware for now
        #print("WARNING: Environment variable TACTIC_APP_SERVER not set")
        #from webware_adapter import get_app_server
        return object

    return get_app_server()


def get_xmlrpc_server_class():
    app_server = os.getenv('TACTIC_APP_SERVER')
    if app_server == "webware":
        # DEPRECATED
        from .webware_adapter import get_xmlrpc_server
    elif app_server == "cherrypy":
        import cherrypy
        try:
            cherrypy_major_version = int(cherrypy.__version__.split('.')[0])
        except:
            cherrypy_major_version = 3
        if cherrypy_major_version >= 3:
            from .cherrypy30_adapter import get_xmlrpc_server
        else:
            from .cherrypy_adapter import get_xmlrpc_server
    elif app_server == "batch":
        return object
    else:
        #raise AppServerException("Environment variable TACTIC_APP_SERVER not set")
        # default to webware for now
        #print("WARNING: Environment variable TACTIC_APP_SERVER not set")
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



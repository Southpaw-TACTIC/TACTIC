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

__all__ = [ 'PyMayaInit', 'PyFlashInit', 'PyRepoActionInit', 'PyHoudiniInit', 'PyXSIInit']


from pyasm.biz import PrefSetting, Project
from pyasm.web import Html, WebContainer, Widget, DivWdg
from pyasm.widget import HiddenWdg

class PyMayaInit(Widget):

    def get_display(my):
        div = DivWdg()

        # this is to prevent this function from being run in other tabs
        web = WebContainer.get_web()
        user = WebContainer.get_user_name()
        local_dir = web.get_local_dir()
        context_url = web.get_site_context_url().to_string()
        http_server = web.get_base_url().to_string()
        upload_url = web.get_upload_url()
        project_code =  Project.get_project_code()
        div.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            var js_files = [
                "/context/javascript/PyMaya.js",
            ];
            var supp_js_files = [
                "/context/spt_js/fx_anim.js",
                "/context/javascript/PyHoudini.js",
                "/context/javascript/PyXSI.js"
            ];
            

            var set_up =  function() {

            try {
               
                app = new PyMaya(); }
            catch(e) {
               
                app = null;
            }

            if (app) {
                app.user = '%(user)s';
                app.local_dir = '%(local_dir)s';
                app.context_url = '%(context_url)s';
                app.base_url = '%(server)s';
                app.upload_url = '%(upload_url)s';
                app.project_code = '%(project_code)s';
            }
            }

            spt.dom.load_js(js_files, function() {PyMaya(); set_up();});
            spt.dom.load_js(supp_js_files, function() {});
            '''%{
               'user': user,
               'local_dir': local_dir,
               'context_url' : context_url,
               'server': http_server,
               'upload_url':  upload_url,
               'project_code': project_code }
            })

        #pref = PrefSetting.get_value_by_key("use_java_maya")
        #if pref == "true":
        #    html.writeln("<script>app.use_java = true</script>")

        
       

        handoff_dir = web.get_client_handoff_dir(no_exception=True)
        if not handoff_dir:
            print "WARNING: handoff_dir is empty in the TACTIC config file"
        server = web.get_http_host()
        application = "maya"

        div.add( HiddenWdg("user", user) )
        div.add( HiddenWdg("handoff_dir", handoff_dir) )
        div.add( HiddenWdg("project_code", project_code) )
        div.add( HiddenWdg("local_dir", local_dir) )
        div.add( HiddenWdg("server_name", server) )
        div.add( HiddenWdg("application", application) )
        #div.add( HiddenWdg("base_url", server) )
        #div.add( HiddenWdg("upload_url", upload_url) )

        return div



class PyFlashInit(Widget):

    def get_display(my):
        web = WebContainer.get_web()

        html = Html()

        html.writeln("<script>var pyflash=new PyFlash()</script>")

        # add in parameters for pyflash
        user = WebContainer.get_user_name()
        html.writeln("<script>pyflash.user = '%s'</script>" % user)
        local_dir = web.get_local_dir()
        html.writeln("<script>pyflash.local_dir = '%s'</script>" % local_dir)

        server = web.get_base_url().to_string()
        html.writeln("<script>pyflash.server_url = '%s'</script>" % server)
       
        context_url = web.get_site_context_url().to_string()
        html.writeln("<script>pyflash.context_url = '%s%s'</script>" % (server, context_url))

        upload_url = web.get_upload_url()
        html.writeln("<script>pyflash.upload_url = '%s'</script>" % upload_url)

        return html    



class PyHoudiniInit(Widget):

    def get_display(my):

        web = WebContainer.get_web()
        user = WebContainer.get_user_name()
        local_dir = web.get_local_dir()
        context_url = web.get_site_context_url().to_string()
        server = web.get_base_url().to_string()
        upload_url = web.get_upload_url()

        html = Html()
        html.writeln('<script language="JavaScript" src="resource:///res/RunHCommand.js"></script>')

        html.writeln('''\n<script>try{ app = new PyHoudini(); }
                                catch(e){
                                    app = null;}
        if (app) {
            app.user = '%(user)s';
            app.local_dir = '%(local_dir)s';
            app.context_url = '%(context_url)s';
            app.base_url = '%(server)s';
            app.upload_url = '%(upload_url)s';
            app.project_code = '%(project_code)s';} </script>'''%{'user': user,
                                           'local_dir': local_dir,
                                           'context_url' : context_url,
                                           'server': server,
                                           'upload_url':  upload_url,
                                           'project_code':  Project.get_project_code()})
        return html



class PyXSIInit(Widget):

    def get_display(my):

        web = WebContainer.get_web()
        user = WebContainer.get_user_name()
        local_dir = web.get_local_dir()
        context_url = web.get_site_context_url().to_string()
        server = web.get_base_url().to_string()
        upload_url = web.get_upload_url()

        html = Html()

        html.writeln('''\n<script>try{ app = new PyXSI(); }
                                catch(e){
                                    app = null;}
        if (app) {
            app.user = '%(user)s';
            app.local_dir = '%(local_dir)s';
            app.context_url = '%(context_url)s';
            app.base_url = '%(server)s';
            app.upload_url = '%(upload_url)s';
            app.project_code = '%(project_code)s';} </script>'''%{'user': user,
                                           'local_dir': local_dir,
                                           'context_url' : context_url,
                                           'server': server,
                                           'upload_url':  upload_url,
                                           'project_code':  Project.get_project_code()})
                            


        return html




class PyRepoActionInit(Widget):

    def get_display(my):
        html = Html()
        html.writeln("<script>var pyp4=new PyPerforce()</script>")
        
        upload_url = WebContainer.get_web().get_upload_url()
        html.writeln("<script>var tactic_repo=new TacticRepo()</script>")
        html.writeln("<script>tactic_repo.upload_url='%s'</script>" %upload_url)
        return html





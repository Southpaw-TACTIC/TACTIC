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

__all__ = [
# DEPRECATED: these really haven't been used in a long time
'PyMayaInit', 'PyFlashInit', 'PyPerforceInit', 'PyHoudiniInit', 'PyXSIInit',
##

'BottomWdg', 'DynTopWdg', 'DynBottomWdg', 'EditLinkWdg', 'ProdSettingLinkWdg', 'SubmissionLinkWdg', 'RenderLinkWdg', 'FileAppendLinkWdg',
'InsertLinkWdg', 'IframeInsertLinkWdg', 'DeleteLinkWdg', 'RetireLinkWdg',
'ReactivateLinkWdg', 'SwapDisplayWdg', 'DebugWdg', 'WebLoginWdg', 'WebLoginWdg2', 'BaseSignInWdg',
'WebLoginCmd', 'WebLicenseWdg', 'TacticLogoWdg',
'SignOutLinkWdg', 'UndoButtonWdg', 'RedoButtonWdg',
'CmdReportWdg', 'WarningReportWdg', 'MessageWdg', 'HintWdg', 'HelpMenuWdg',
'HelpItemWdg', 'WarningMenuWdg', 'FloatMenuWdg', 'ExtraInfoWdg', 'UserExtraInfoWdg',
'ProgressWdg', 'SiteMenuWdg', 'DateSelectWdg', 'CloseWdg', 'PopupWindowLinkWdg',
'PublishLinkWdg', 'FileUploadUpdateWdg', 'FilterboxWdg', 'ExceptionWdg',
'SObjectLevelWdg'
]

import types

from pyasm.common import *
from pyasm.security import *
from pyasm.command import Command, PasswordAction, SignOutCmd
from pyasm.biz import Schema
from pyasm.web import *

from tactic.command import Scheduler, SchedulerTask
from .input_wdg import *
from .shadowbox_wdg import *
from .icon_wdg import *
from pyasm.checkin import FileCheckin
from pyasm.search import SObject, SearchType, TransactionLog, SearchKey, Search
from pyasm.biz import Project, PrefSetting
from .widget_config import WidgetConfigView
from pyasm.search import ExceptionLog
from pyasm.prod.biz import ProdSetting
from pyasm.common import jsonloads
import os, re


class PyMayaInit(Widget):

    def get_display(self):
        html = Html()

        # this is to prevent this function from being run in other tabs
        # (with new Application tab)
        web = WebContainer.get_web()
        if web.get_form_value("main_tab") != "Application" and \
                web.get_selected_app() != "Maya":
            return html


        # define the global application
        html.writeln("<script>app = new PyMaya()</script>")

        # add in parameters for pymaya
        user = WebContainer.get_user_name()
        html.writeln("<script>app.user = '%s'</script>" % user)

        local_dir = web.get_local_dir()
        html.writeln("<script>app.local_dir = '%s'</script>" % local_dir)

        context_url = web.get_site_context_url().to_string()
        html.writeln("<script>app.context_url = '%s'</script>" % context_url)

        server = web.get_base_url().to_string()
        html.writeln("<script>app.base_url = '%s'</script>" % server)

        upload_url = web.get_upload_url()
        html.writeln("<script>app.upload_url = '%s'</script>" % upload_url)

        pref = PrefSetting.get_value_by_key("use_java_maya")
        if pref == "true":
            html.writeln("<script>app.use_java = true</script>")

        
        project_code = Project.get_project_code()
        html.writeln("<script>app.project_code = '%s'</script>" % project_code)

        handoff_dir = web.get_client_handoff_dir()
        server = web.get_http_host()
        application = "maya"

        widget = Widget()
        widget.add( HiddenWdg("user", user) )
        widget.add( HiddenWdg("handoff_dir", handoff_dir) )
        widget.add( HiddenWdg("project_code", project_code) )
        widget.add( HiddenWdg("local_dir", local_dir) )
        widget.add( HiddenWdg("server_name", server) )
        widget.add( HiddenWdg("application", application) )
        #widget.add( HiddenWdg("base_url", server) )
        #widget.add( HiddenWdg("upload_url", upload_url) )
        html.writeln( widget.get_display() )


        return html



class PyFlashInit(Widget):

    def get_display(self):
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


class PyPerforceInit(Widget):

    def get_display(self):
        html = Html()
        html.writeln("<script>var pyp4=new PyPerforce()</script>")
        
        upload_url = WebContainer.get_web().get_upload_url()
        html.writeln("<script>var tactic_repo=new TacticRepo()</script>")
        html.writeln("<script>tactic_repo.upload_url='%s'</script>" %upload_url)
        return html


class PyHoudiniInit(Widget):

    def get_display(self):

        web = WebContainer.get_web()

        html = Html()
        html.writeln('<script language="JavaScript" src="resource:///res/RunHCommand.js"></script>')

        html.writeln("<script>app = new PyHoudini()</script>")

        # add in parameters for pymaya
        user = WebContainer.get_user_name()
        html.writeln("<script>app.user = '%s'</script>" % user)

        local_dir = web.get_local_dir()
        html.writeln("<script>app.local_dir = '%s'</script>" % local_dir)

        context_url = web.get_site_context_url().to_string()
        html.writeln("<script>app.context_url = '%s'</script>" % context_url)

        server = web.get_base_url().to_string()
        html.writeln("<script>app.base_url = '%s'</script>" % server)

        upload_url = web.get_upload_url()
        html.writeln("<script>app.upload_url = '%s'</script>" % upload_url)
        html.writeln("<script>app.project_code = '%s'</script>" % Project.get_project_code())
        return html



class PyXSIInit(Widget):

    def get_display(self):

        web = WebContainer.get_web()

        html = Html()

        html.writeln("<script>app = new PyXSI()</script>")

        # add in parameters for pymaya
        user = WebContainer.get_user_name()
        html.writeln("<script>app.user = '%s'</script>" % user)

        local_dir = web.get_local_dir()
        html.writeln("<script>app.local_dir = '%s'</script>" % local_dir)

        context_url = web.get_site_context_url().to_string()
        html.writeln("<script>app.context_url = '%s'</script>" % context_url)

        server = web.get_base_url().to_string()
        html.writeln("<script>app.base_url = '%s'</script>" % server)

        upload_url = web.get_upload_url()
        html.writeln("<script>app.upload_url = '%s'</script>" % upload_url)

        html.writeln("<script>app.project_code = '%s'</script>" % Project.get_project_code())

        return html







class BottomWdg(Widget):

    def get_display(self):

        html = Html()
        # put a real button on the bottom of the page.  The form needs at least
        # one for submit on enter to work.  In Firefox, this button can be
        # hidden
        if WebContainer.get_web().is_IE():
            html.writeln("<input style='float: right; height: 1px; width: 1px' type=submit name='' value=''/>")
        else:
            html.writeln("<input style='display: none; float: right' type=submit name='' value=''/>")

        html.writeln("</form>")
        
        # Add in copyright notice and license holder info ...
        from tactic.ui.app import TacticCopyrightNoticeWdg
        tactic_copyright = TacticCopyrightNoticeWdg( show_license_info=True )
        html.writeln( tactic_copyright.get_buffer_display() )


        # put some useless tables at the end for Maya interface.  For some
        # bizarre reason this prevents the Tactc/Maya connection from breaking
        request = WebContainer.get_web().get_request_url().to_string()
        if request.find("/Maya") != -1:
            for i in range(0, 100):
                html.writeln("<table><tr><td></td></tr></table>")

        

        html.writeln("</body>")
        html.writeln("</html>")

        return html



class DynTopWdg(Widget):

    def get_display(self):

        html = Html()
        html.writeln("<html>")
        html.writeln("<head>")

        # first load context css
        context_url = WebContainer.get_web().get_context_url().to_string()
        Container.append_seq("Page:css", "%s/style/overlay.css" % context_url)

        # load context overrides
        context_url = WebContainer.get_web().get_site_context_url().to_string()
        Container.append_seq("Page:css", "%s/style/main.css" % context_url)

        # get all of the registered css file
        css_files = Container.get_seq("Page:css")
        for css_file in css_files:
            html.writeln('<link rel="stylesheet" href="%s" type="text/css"></link>' % css_file )




        context_name = WebContainer.get_web().get_context_name()
        html.writeln("<title>%s</title>" % context_name.capitalize() )

        html.writeln("</head>")


        js_url = "%s/javascript" % context_url
        Container.append_seq("Page:js", "%s/Common.js" % js_url)
        Container.append_seq("Page:js", "%s/PopupWindow.js" % js_url)
        Container.append_seq("Page:js", "%s/DynamicLoader.js" % js_url)
        Container.append_seq("Page:js", "%s/EventContainer.js" % js_url)
        Container.append_seq("Page:js", "%s/PyMaya.js" % js_url)

        js_files = Container.get("Page:js")
        for js_file in js_files:
            html.writeln('<script src="%s"></script>' % js_file )



        loader_id = WebContainer.get_web().get_form_value("dynamic_loader_id")
        body = HtmlElement("body")
        body.add_event("onload", 'parent.%s.move_content()' % loader_id)
        html.writeln(body.get_display())



        html.writeln("<script>loader = new DynamicLoader()</script>")

        return html



class DynBottomWdg(Widget):

    def get_display(self):

        html = Html()
        html.writeln("</body>")
        html.writeln("</html>")

        return html



class EditLinkWdg(HtmlElement):

    def __init__(self, search_type, search_id, text="Edit", config_base='edit', \
            widget='tactic.ui.panel.EditWdg', long=False, action=''):
        super(EditLinkWdg,self).__init__("div")
        self.text = text
        self.search_type = search_type
        self.search_id = search_id
        self.long = long
        #self.add_style("padding: 0 5px 0 5px")
        self.config_base = config_base
        self.view = config_base
        self.widget = widget 
        # layout can be 'default' or 'plain'
        self.layout = 'default'
        self.refresh_mode = None
        # this is used in adding arbitrary values to the behavior
        self.value_dict = {}
        self.action = action # what is this?

    def get_button(self):
        button = IconButtonWdg(self.text, IconWdg.EDIT, self.long)
        return button

    def set_layout(self, layout):
        self.layout = layout


    def set_refresh_mode(self, refresh_mode):
        assert refresh_mode in ['page', 'table', 'row']
        # NOTE: only page is supported
        self.refresh_mode = refresh_mode


    def add_url_options(self, url):
        '''DEPRECATED'''
        pass

    def modify_behavior(self, bvr):
        '''subclasses update the edit behavior here'''
        pass

    def get_hidden(self):
        search_type_base = SearchType.get(self.search_type).get_base_key()
        # check if it is an EditLinkWdg, with a valid search_id
        hidden = None
        key = "%s|search_ids_str" % self.search_type
        if self.sobjects:
            values = SObject.get_values( self.sobjects, 'id', unique=False)
            values = [ str(x) for x in values if isinstance(x, int)]
            search_ids_str = "|".join(values)
            if search_ids_str:
                hidden = HiddenWdg("%s_search_ids" %search_type_base)
                hidden.set_value(search_ids_str)
               
        return hidden

    def get_display(self):

        search_type_base = SearchType.get(self.search_type).get_base_key()
       
        button = self.get_button()
        behavior = EditLinkWdg.get_edit_behavior(self.widget, self.search_type, \
            self.search_id, self.view)
        self.modify_behavior(behavior)
        button.add_behavior(behavior)
        

        self.add(button)

        return super(EditLinkWdg,self).get_display()

    def set_value_dict(self, value_dict):
        '''this is used in adding arbitrary values to the behavior'''
        self.value_dict = value_dict

    def set_iframe_width(self, width):
        self.iframe_width = width

    def _set_iframe_width(self, iframe):
        if self.layout == 'default':
            iframe.set_width(self.iframe_width)
        else:
            iframe.set_width(self.iframe_width - 18)

    def get_edit_behavior(class_name, search_type, search_id, view):
        '''get the default edit behavior'''
        behavior = {
            "type": "click_up",
            #"cbfn_action": "spt.dg_table_action.get_popup_wdg",
            "cbfn_action": "spt.popup.get_widget",
            "options": {
                "title": "Edit: %s" % search_type,
                "class_name": class_name, "popup_id": 'edit_popup'
            },
            "args": {
                "search_type": search_type,
                "search_id": search_id,
                "view": view,
                "input_prefix": 'edit'
                #"popup_id": "EditWdg"

            }
        }
        return behavior
    get_edit_behavior = staticmethod(get_edit_behavior)

class ProdSettingLinkWdg(EditLinkWdg):
    def __init__(self,  search_id, search_type='config/prod_setting', text="Edit Project Setting", long=False, \
            config_base='edit', widget="tactic.ui.panel.EditWdg"):
        super(ProdSettingLinkWdg, self).__init__(search_type, search_id, text, config_base, widget)
        self.set_refresh_mode('page') 
        
    def _set_iframe_width(self, iframe):
        if self.layout == 'default':
            iframe.set_width(74)
        else:
            iframe.set_width(56)
    
    def modify_behavior(self, bvr):
        '''values is for web form values'''
        bvr['values'] = self.value_dict

class SubmissionLinkWdg(EditLinkWdg):
    def __init__(self, search_type, search_id, text="Submit", long=False, \
            config_base='submit', widget='pyasm.prod.web.SubmissionWdg', **kwargs):
           
        self.long = long

        self.parent_search_type = search_type
        self.parent_search_id = search_id

        search_type = "vfx/submission"
        search_id = "-1"
        config_base = "insert"

        super(SubmissionLinkWdg,self).__init__(search_type,search_id,text,config_base, widget, **kwargs)

    def modify_behavior(self, bvr):
        '''values is for web form values'''
        val = {}
        val["parent_search_type"] = self.parent_search_type
        val["parent_search_id"] = self.parent_search_id
        bvr['values'] = val


    def _set_iframe_width(self, iframe):
        if self.layout == 'default':
            iframe.set_width(74)
        else:
            iframe.set_width(56)

    def get_button(self):
        from tactic.ui.widget.button_new_wdg import IconButtonWdg
        button = IconButtonWdg(title=self.text, icon=IconWdg.FILM)
        #button = IconButtonWdg(self.text, IconWdg.FILM, self.long)
        return button


class RenderLinkWdg(EditLinkWdg):
    def __init__(self, search_type, search_id, text="Render", long=False, \
            config_base='submit', widget='pyasm.prod.web.RenderSubmissionWdg'):
           
        self.long = long

        self.parent_search_type = search_type
        self.parent_search_id = search_id

        search_type = "sthpw/queue"
        search_id = "-1"
        config_base = "submit"

        EditLinkWdg.__init__(self, search_type,search_id,text,config_base, widget)

    def modify_behavior(self, bvr):
        val = {}
        val["parent_search_type"] = self.parent_search_type
        val["parent_search_id"] = self.parent_search_id
        bvr['values'] = val




    def _set_iframe_width(self, iframe):
        if self.layout == 'default':
            iframe.set_width(74)
        else:
            iframe.set_width(56)

    def get_button(self):
        button = IconButtonWdg(self.text, IconWdg.RENDER, self.long)
        return button



class FileAppendLinkWdg(EditLinkWdg):
    def __init__(self, search_type, search_id, text="Append Files", long=False, \
            config_base='append', widget='tactic.ui.panel.FileAppendWdg'):

        self.long = long
           
        EditLinkWdg.__init__(self, search_type,search_id,text,config_base, widget)

    def modify_behavior(self, bvr):
        val = {}
        from pyasm.biz import Snapshot
        snapshot = Search.get_by_id(self.search_type, self.search_id)
        val["search_type"] = self.search_type
        val["search_id"] = self.search_id
        bvr['values'] = val


    def _set_iframe_width(self, iframe):
        if self.layout == 'default':
            iframe.set_width(74)
        else:
            iframe.set_width(56)

    def get_button(self):
        button = IconButtonWdg(self.text, IconWdg.INSERT, self.long)
        return button







class InsertLinkWdg(EditLinkWdg):
    def __init__(self, search_type, text="Insert", long=True, config_base='insert'):
        # check if the insert config exists
        search_id = -1
        search_type_obj = SearchType.get(search_type)
        config = WidgetConfigView.get_by_search_type( search_type_obj, config_base )
        if not config:    
            config_base='edit'
        super(InsertLinkWdg,self).__init__(search_type, search_id, text, config_base, widget='tactic.ui.panel.InsertWdg', long=long)

    def get_button(self):
        button = IconButtonWdg(self.text, IconWdg.INSERT, self.long)
        return button

class PublishLinkWdg(EditLinkWdg):
    def __init__(self, search_type, search_id, text="Publish", long=False, config_base='publish', icon=IconWdg.PUBLISH):
       
        self.long = long
        super(PublishLinkWdg,self).__init__(search_type, search_id, text, \
                config_base=config_base, widget='tactic.ui.panel.PublishWdg')
        self.icon = icon
        #self.set_refresh_mode('page')

    def get_button(self):
        button = IconButtonWdg(self.text, self.icon, self.long)
        return button
  

    def modify_behavior(self, bvr):
        '''values is for web form values'''
        bvr['values'] = self.value_dict
    

class IframeInsertLinkWdg(InsertLinkWdg):
     def __init__(self, search_type, text="Insert", long=True, config_base='insert'):
        
        super(IframeInsertLinkWdg, self).__init__(search_type, text, long, config_base)
        self.set_layout('plain')
    

class DeleteLinkWdg(HtmlElement):
    '''Icon link to delete an SObject.
    NOTE: use this with caution at it deletes the sobject.
    TODO: merge the duplicated code between this and RetireLinkWdg
    '''

    def __init__(self, search_type, search_id, display_name, sobject=None):
        self.search_type = search_type
        self.search_id = search_id
        self.display_name = display_name

        # if sobject is passed in, just use that
        if not sobject:
            self.sobject = Search.get_by_id(self.search_type, self.search_id)
        else:
            self.sobject = sobject

        super(DeleteLinkWdg,self).__init__("div")
        self.add_style("display", "inline")

    def init(self):
        button = IconButtonWdg("Delete", IconWdg.DELETE)
        """
        from pyasm.web import AjaxCmd
        ajax = AjaxCmd("delete_%s" % self.search_id )
        ajax.register_cmd("pyasm.command.DeleteCmd")
        ajax.set_option("search_type", self.search_type)
        ajax.set_option("search_id", self.search_id)
        div = ajax.generate_div()
        div.add_style("display", "inline")
        self.add(div)
        """

        display_name = self.sobject.get_name()

        js_action = "TacticServerCmd.execute_cmd('pyasm.command.DeleteCmd', \
                '', {'search_type': '%s', 'search_id': '%s'}, {});" %(self.search_type, self.search_id)

        # build the search key
        search_key = "%s|%s" % (self.search_type, self.search_id)
        
        button.add_behavior({'type': 'click_up', 'cbjs_action': " if (delete_sobject('%s','%s')==true){ %s}" \
            %(search_key, display_name, js_action)})

        self.add(button)
        

class RetireLinkWdg(HtmlElement):

    def __init__(self, search_type, search_id, display_name):
        self.search_type = search_type
        self.search_id = search_id
        self.display_name = display_name
        super(RetireLinkWdg,self).__init__("div")
        self.add_style("display", "inline")

    def init(self):
        button = IconButtonWdg("Retire", IconWdg.RETIRE)

        js_action = "TacticServerCmd.execute_cmd('pyasm.command.RetireCmd', \
                '', {'search_type': '%s', 'search_id': '%s'}, {});" %(self.search_type, self.search_id)

        # build the search key
        search_key = "%s|%s" % (self.search_type, self.search_id)
        
        button.add_behavior({'type': 'click_up', 'cbjs_action': " if (retire_sobject('%s','%s')==true){ %s}" \
            %(search_key, self.display_name, js_action)})
            
        self.add(button)




class ReactivateLinkWdg(HtmlElement):

    def __init__(self, search_type, search_id, dispay_name):
        self.search_type = search_type
        self.search_id = search_id
        self.dispay_name = dispay_name
        super(ReactivateLinkWdg,self).__init__("div")
        self.add_style("display", "inline")

    def init(self):
        button = IconButtonWdg("Reactivate", IconWdg.CREATE)

        from pyasm.web import AjaxCmd
        ajax = AjaxCmd("reactivate_%s" % self.search_id )
        ajax.register_cmd("pyasm.command.ReactivateCmd")
        ajax.set_option("search_type", self.search_type)
        ajax.set_option("search_id", self.search_id)
        div = ajax.generate_div()
        div.add_style("display", "inline")
        self.add(div)
        on_script = ajax.get_on_script(show_progress=False)
        
        button.add_event("onclick", " if (confirm('Are you sure you want to REACTIVATE this asset [%s]?')"\
            "==false) return; %s"  % (self.dispay_name, on_script))
            
        self.add(button)

        event_container = WebContainer.get_event_container()
        caller = event_container.get_event_caller(SiteMenuWdg.EVENT_ID)
        search_key = "%s|%s" % (self.search_type, self.search_id)
        caller2 = event_container.get_event_caller("refresh|%s" % (search_key))

        div.set_post_ajax_script("%s;%s" %(caller,caller2))







class SwapDisplayWdg(HtmlElement):
    '''Widget which switches one image for another when clicked on'''
    ON = "on_wdg"
    OFF = "off_wdg"
    
    def __init__(self, on_event_name=None, off_event_name=None, icon_tip_on="", icon_tip_off=""):
        if on_event_name != None:
            assert off_event_name != None
        self.on_event_name = on_event_name
        self.off_event_name = off_event_name
        self.no_events = False
        self.swap1_id = None
        self.swap2_id = None
        super(SwapDisplayWdg,self).__init__("span")
        self.wdg1 = None
        self.wdg2 = None

        self.icon_tip_on = icon_tip_on
        self.icon_tip_off = icon_tip_off

        self.is_on = False

    def set_off(self):
        self.is_on = True
       
    def set_no_events(self):
        self.no_events = True
   
    def init(self):
        self.on_wdg = HtmlElement.span()
        self.off_wdg = HtmlElement.span()

        self.add(self.on_wdg,"div1")
        self.add(self.off_wdg,"div2")

        # generate a random reference number
        ref_count = Common.randint(0,10000)
        self.swap1_id = "swap_%s" % str(ref_count)
        self.swap2_id = "swap_%s" % str(ref_count+1)


        top = DivWdg()
        if self.on_event_name != None and self.off_event_name != None:
            behavior = {
                'type': 'smart_click_up',
                'bvr_match_class': 'SPT_SWAP_ON_EVENT',
                'cb_fire_named_event': self.on_event_name,
            }
            top.add_behavior(behavior)

            behavior = {
                'type': 'smart_click_up',
                'bvr_match_class': 'SPT_SWAP_OFF_EVENT',
                'cb_fire_named_event': self.off_event_name,
            }
            top.add_behavior(behavior)




    def get_display(self):

        self.add_class("spt_swap_top")

        swap_script = self.get_swap_script()
       
        #event = WebContainer.get_event_container()

        # set up events
        if self.no_events:
            pass
        elif self.on_event_name != None and self.off_event_name != None:
            behavior = {
                'type': 'click_up',
                'cb_fire_named_event': self.on_event_name,
            }
            self.on_wdg.add_behavior(behavior)

            behavior = {
                'type': 'click_up',
                'cb_fire_named_event': self.off_event_name,
            }
            self.off_wdg.add_behavior(behavior)

            # add some listeners for the swap.  It doesn't matter which
            # dom element these are put on
            behavior = {
                'type': 'listen',
                'event_name': self.on_event_name,
                'cbjs_action': swap_script
            }
            self.on_wdg.add_behavior( behavior )
            behavior = {
                'type': 'listen',
                'event_name': self.off_event_name,
                'cbjs_action': swap_script
            }
            self.off_wdg.add_behavior( behavior )


        else:
            self.on_wdg.add_behavior({"type": "click_up", 
                "cbjs_action": swap_script})
            self.off_wdg.add_behavior({"type": "click_up", 
                "cbjs_action": swap_script})


        self.on_wdg.set_id(self.swap1_id)
        self.on_wdg.add_class("hand")
        #self.on_wdg.add_class("swap_link")
        if self.is_on:
            self.on_wdg.add_style("display: none")
        else:
            self.on_wdg.add_style("display: inline")

        self.off_wdg.set_id(self.swap2_id)
        self.off_wdg.add_class("hand")
        #self.off_wdg.add_class("swap_link")
        if self.is_on:
            self.off_wdg.add_style("display: inline")
        else:
            self.off_wdg.add_style("display: none")

        if not self.wdg1 or not self.wdg2:
            # use the default arrow
            self.wdg1 = IconWdg(self.icon_tip_on, IconWdg.INFO_CLOSED_SMALL, width='20px')
            self.wdg2 = IconWdg(self.icon_tip_off, IconWdg.INFO_OPEN_SMALL , width='20px')

        # add in the content
        self.on_wdg.add( self.wdg1 )
        self.off_wdg.add( self.wdg2 )

        return super(SwapDisplayWdg, self).get_display()


    def add_action_script(self, action_script1, action_script2=None):
        '''adds an action javascript to the first widget'''

        div1 = self.get_widget("div1")
        div2 = self.get_widget("div2")
        
        #event = WebContainer.get_event_container()
        # self.on_event_name is the primary event we look for
        if self.on_event_name != None:
            behavior = {
                'type': 'listen',
                'event_name': self.on_event_name,
                'cbjs_action': action_script1
            }
            self.on_wdg.add_behavior( behavior )

            #event.add_listener(self.on_event_name, action_script1)
            if action_script2 != None:
                 behavior = {
                'type': 'listen',
                'event_name': self.off_event_name,
                'cbjs_action': action_script2
            }
            else:
                behavior = {
                'type': 'listen',
                'event_name': self.off_event_name,
                'cbjs_action': action_script1
            }
            self.off_wdg.add_behavior( behavior )
            
        else:
            div1.add_behavior({"type": "click_up",
                            "cbjs_action": action_script1})
            if action_script2 != None:
                div2.add_behavior({"type": "click_up",
                            "cbjs_action": action_script2})
            else:
                div2.add_behavior({"type": "click_up",
                            "cbjs_action": action_script1})

    def set_display_widgets(self, widget1, widget2):
        """override the displays of the clickable widget"""
        self.wdg1 = widget1
        self.wdg2 = widget2

    def get_on_widget(self):
        return self.on_wdg
    
    def get_off_widget(self):
        return self.off_wdg

    def get_on_script(self):
        script = "spt.named_events.fire_event('%s', bvr);" %self.on_event_name
        return script

    def get_off_script(self):
        script = "spt.named_events.fire_event('%s', bvr);" %self.off_event_name
        return script

    def get_swap_script(self, bias=None):
        script = ''
        if not bias:
            script = "var state = spt.swap_display('%s','%s');" % (self.swap1_id, self.swap2_id)
        elif bias == self.ON:
            script = "var state = spt.swap_display('%s','%s','%s');" % (self.swap1_id, self.swap2_id, self.swap1_id)
        elif bias == self.OFF:
            script = "var state = spt.swap_display('%s','%s','%s');" % (self.swap1_id, self.swap2_id, self.swap2_id)
        else:
            raise TacticException("bias is either SwapDisplayWdg.ON or SwapDisplayWdg.OFF")

         
        return script

    def get_triangle_wdg(is_open=False):
        swap_wdg = SwapDisplayWdg()
        #swap_wdg.add_style('float','left')
        theme = DivWdg().get_theme()
        if theme == "default":
            icon1 = IconWdg('closed', IconWdg.ARROWHEAD_DARK_RIGHT)
            icon2 = IconWdg('open', IconWdg.ARROWHEAD_DARK_DOWN)
        else:
            icon1 = IconWdg('closed', IconWdg.INFO_CLOSED_SMALL)
            icon2 = IconWdg('open', IconWdg.INFO_OPEN_SMALL)

        if is_open:
            swap_wdg.set_display_widgets(icon2, icon1)
        else:
            swap_wdg.set_display_widgets(icon1, icon2)
        return swap_wdg

    get_triangle_wdg = staticmethod(get_triangle_wdg)


    def create_swap_title(title, swap, div=None, is_open=False, action_script=None):
        '''creates a title bar with an arrow that toggles display
           @title - the HtmlElement holding the title
           @swap - the S#wapDisplayWdg
           @div - the container of the content'''


        # action script auto gen here to toggle the content box (div)
        if not action_script:
            content_id = div.get_id()
            if not content_id:
                content_id = div.set_unique_id()
            action_script = '''spt.toggle_show_hide('%s');''' % content_id

        swap.add_action_script(action_script)
        if title:
           
            title.add_class('SPT_DTS')
            title.add_class('hand')

            if not swap.on_event_name and not swap.off_event_name:
                title.add_behavior( {
                'type': 'click_up',
                'cbjs_action': action_script
                } )

                title.add_behavior( {
                'type': 'click_up',
             
                'cbjs_action': swap.get_swap_script()
                } )
            else:
                on_event = swap.on_event_name
                off_event = swap.off_event_name
             
                title.add_behavior( {
                'type': 'click_up',
                'on_event': on_event,
                'off_event': off_event,
                'cbjs_action': '''
                if (bvr.src_el.getAttribute("spt_is_open") == "true") {
                    bvr.src_el.setAttribute("spt_is_open", "false");
                    spt.named_events.fire_event(bvr.off_event);
                }
                else {
                    bvr.src_el.setAttribute("spt_is_open", "true");
                    spt.named_events.fire_event(bvr.on_event);
                }
                '''
                } )

            if is_open:
                title.add_attr("spt_is_open", "true")
            else:
                title.add_attr("spt_is_open", "false")


        if is_open:
            swap.set_off()

        if div:
            if not is_open:
                div.add_style('display: none')
            else:
                div.add_style('display: block')
    create_swap_title = staticmethod(create_swap_title)






class DebugWdg(Widget):

    def get_display(self):

        # if debug is off, then just return an empty widget
        pref = PrefSetting.get_value_by_key("debug")
        if pref != "true":
            return Widget()

        web = WebContainer.get_web()

        div = DivWdg(css='left_content')

        href = HtmlElement.href("Debug", "javascript:toggle_display('debug')")
        div.add(href)
        self.add(div)

        debug = DivWdg()
        debug.set_id("debug")
        debug.add_style("display: none")

        debug.add("<hr/>")
        debug.add("<b>Web Form Values</b>")

        table = Table()
        keys = web.get_form_keys()
        keys.sort()
        for key in keys:
            # skipping the upload data
            if not key:
                continue
            pat = re.compile(r'(\|files|\|images|\|snapshot|\|submission|\|publish_icon|\|publish_main)$')
            if pat.search(key):
                continue
            table.add_row()
            field = web.get_form_values(key)
            table.add_cell(key)
            table.add_cell(str(field))

        # sql counts
        table.add_row()
        table.add_cell('sql_counts')
        table.add_cell(Container.get('Search:sql_query'))
        debug.add(table)

        # add project settings
        from pyasm.prod.biz import ProdSetting
        dict = ProdSetting.get_cache_dict()
        if dict:
            debug.add("<hr/>")
            debug.add("<b>Project Settings</b><br/>")
            table = Table()
            for key, value in dict.items():
                table.add_row()
                if key.count(":"):
                    key, search_type = key.split(":",1)
                else:
                    key, search_type = (key, "None")
                table.add_cell(key)
                table.add_cell(search_type)

                if not value:
                    table.add_cell("-- Not set --")
                else:
                    if not isinstance(value, basestring):
                        value = value.get_value("value")
                    table.add_cell(value)

            debug.add(table)



        debug.add("<hr/>")

        # show access rules
        debug.add("<b>Access Rules</b><br/>")

        security = WebContainer.get_security()
        access_manager = security.get_access_manager()

        # get all of the cached groups
        access = access_manager.get_access_summary()

        table = Table()
        keys = access.keys()
        keys.sort()
        for key in keys:
            value = access[key]
            table.add_row()
            table.add_cell(key)
            table.add_cell(value)
        debug.add(table)
        #debug.add( access_manager )
        debug.add("<hr/>")


        # show environment
        debug.add("<b>Environment Variables</b><br/>")
        keys = web.get_env_keys()
        keys.sort()

        table = Table()
        for key in keys:
            table.add_row()
            table.add_cell(key)
            table.add_cell(web.get_env(key))

        debug.add(table)

        div.add(debug)

        return super(DebugWdg,self).get_display()


class TacticLogoWdg(Widget):
    def get_display(self):

        div = DivWdg(css='centered')
        div.add_color("color", "color")
        
        div.center()
        
        div.add(HtmlElement.br(2))
        small_div = DivWdg()
        small_div.add("&nbsp;")
        small_div.add_style("height: 3px")
        small_div.add_style("width: 100%")
        small_div.add_class("div_login")
        div.add(HtmlElement.br(1))


        div.add( "<img src='/context/icons/logo/logo.png'/>") 
    #div.add( "<img src='/context/icons/logo/tactic_silver.png

        div.add(HtmlElement.br(2))
        div.add("Release: %s" %Environment.get_release_version() )
        div.add(HtmlElement.br(4))

        return div



class WebLoginWdg(Widget):

    LOGIN_MSG = 'login_message'

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        # hidden is for inline login when a session expires
        self.hidden = kwargs.get('hidden') in  [True, 'True']
        super(WebLoginWdg,self).__init__("div")


    def get_display(self):
        name_label = self.kwargs.get('name_label')
        password_label = self.kwargs.get('password_label')
        override_background = self.kwargs.get('override_background') == "true"
        override_logo = self.kwargs.get('override_logo') == "true"
        override_company_name = self.kwargs.get('override_company_name') == "true"
        override_password = self.kwargs.get('override_password') == "true"
        override_login = self.kwargs.get('override_login') == "true"
        bottom_link = self.kwargs.get('bottom_link')


        if not name_label:
            if override_background:
                name_label = "Username"
            else:
                name_label = "Name"
        if not password_label:
            password_label = "Password"


        web = WebContainer.get_web()
            
        box = DivWdg()
        if override_background:
            box.add_class("spt_tactic_background")
        else:
            box.add_style("margin: auto auto")
            box.add_style("width: 400px")
            box.add_style("text-align: center")

        box.add_event("onkeyup", "tactic_login(event)")
        script = HtmlElement.script('''function tactic_login(e) {
                if (!e) var e = window.event;
                if (e.keyCode == 13) {
                    document.form.submit();
                }}
                ''')
        
        div = DivWdg()
        if override_background:
            div.add_class("spt_margin_center")
        else:    
            div.add_style("margin: 0px 0px")
        div.add_class("centered")


        allow_change_admin = self.kwargs.get("allow_change_admin")
        if allow_change_admin in [False, 'false']:
            allow_change_admin = False
        else:
            allow_change_admin = True

        # if admin password is still the default, force the user to change it
        change_admin = False
        if allow_change_admin:
            from pyasm.security import Sudo
            sudo = Sudo()
            try:
                admin_login = Search.eval("@SOBJECT(sthpw/login['login','admin'])", single=True, show_retired=True)
            finally:
                sudo.exit()
            if admin_login and admin_login.get_value('s_status') =='retired':
                admin_login.reactivate()
                web = WebContainer.get_web()
                web.set_form_value(self.LOGIN_MSG, "admin user has been reactivated.")
                admin_password = admin_log.get_value("password")
                if admin_password == Login.get_default_encrypted_password():
                    change_admin = True

         
            if admin_login:
                password = admin_login.get_value("password")
                if password == Login.get_default_encrypted_password() or not password:

                    change_admin = True
            else:
                # FIXME: This should use logic in Login.get_by_login
                # that creates the admin login with certain Config settings 
                 
                admin_login = SearchType.create("sthpw/login")
                admin_login.set_value('login','admin')
                admin_login.commit()
                change_admin = True


        if override_logo:
            div.add("<div class='spt_tactic_logo'></div>")
        else:
            div.add("<img src='/context/icons/logo/TACTIC_logo_white.png'/>")
            div.add("<br/>"*2)

        if not override_background:

            div.add_gradient("color", "color3")
            div.add_gradient("background", "background3", -10, 10)
            div.add_style("border: solid 2px %s" % div.get_color("border",-15))
            div.set_box_shadow("0px 5px 20px", color="rgba(0,0,0,0.6)")
            div.set_round_corners(15)
        if change_admin:
            if override_background:
                div.add_class("spt_change_admin")
            else:
                div.add_style("height: 250px")
                div.add_style("padding-top: 20px")
        else:
            if override_background:
                div.add_class("spt_not_change_admin")

            else:
                div.add_style("padding-top: 25px")


        #div.add_style("padding-top: 95px")
        sthpw = SpanWdg("SOUTHPAW TECHNOLOGY INC", css="login_sthpw")
        if override_company_name:
            sthpw.add_class("spt_login_company")
        else:
            #sthpw.add_style("color: #CCCCCC")
            sthpw.add_color("color", "color")
        
        div.add( sthpw )
        div.add( HtmlElement.br() )

        box.add(div)


        # hidden element in the form to pass message that this was not
        # actually a typical submitted form, but rather the result
        # of a login page
        div.add( HiddenWdg("is_from_login", "yes") )
        div.add_style("font-size: 10px")

        table = Table()
        table.add_color("color", "color")
        table.center()
        table.set_attr("cellpadding", "3px")
        table.add_row()



        # look for defined domains
        domains = Config.get_value("active_directory", "domains")
        if not domains:
            # backwards compatibility
            domains = Config.get_value("security", "authenticate_domains")

        if domains:
            domains = domains.split('|')

        hosts = Config.get_value("active_directory", "hosts")
        if not hosts:
            hosts = Config.get_value("security", "hosts")
            
        if hosts:
            hosts = hosts.split('|')
       
        if hosts and len(hosts) != len(domains):
            msg = 'When specified, the number of IP_address has to match the number of domains'
            web.set_form_value(self.LOGIN_MSG, msg)

        host = web.get_http_host()
        if host.find(':') != -1:
            host = host.split(':')[0]
        if domains:
            
            th = table.add_header( "<b>Domain: </b>")
            domain_wdg = SelectWdg("domain")
            domain_wdg.set_persist_on_submit()
            if len(domains) > 1:
                domain_wdg.add_empty_option("-- Select --")
            domain_wdg.set_option("values", domains)
            try:
                matched_idx = hosts.index(host)
            except ValueError:
                matched_idx = -1
            # select the matching domain based on host/IP in browser URL
            if host and matched_idx > -1:
                domain_wdg.set_value(domains[matched_idx])
            
            if override_password:
                domain_wdg.add_style("")
            else:
                domain_wdg.add_style("background-color: #EEE")
                domain_wdg.add_style("height: 20px")
            table.add_cell( domain_wdg )
            table.add_row()

        

        th = table.add_header( "<b> %s: </b>"%name_label)
        th.add_style("padding: 5px")

        text_wdg = TextWdg("login")
        if override_login:
            text_wdg.add_class("spt_login_textbox")
            text_wdg.add_class("form-control")

        else:
            text_wdg.add_style("width: 130px")
            text_wdg.add_style("color: black")
            text_wdg.add_style("padding: 2px")
        if self.hidden:
            login_name = Environment.get_user_name()
            text_wdg.set_value(login_name)
        else:
            # check if it's first time login
            custom_projects = Search.eval("@COUNT(sthpw/project['code','not in','sthpw|admin|unittest'])")
            if custom_projects == 0:
                text_wdg.set_value('admin')
                
       
        login_placeholder = self.kwargs.get("login_placeholder")
        if login_placeholder:
            text_wdg.add_attr("placeholder", login_placeholder)

        #text_wdg.add_event("onLoad", "this.focus()")
        table.add_cell( text_wdg )

        if change_admin:
            text_wdg.add_attr("readonly", "readonly")
            text_wdg.add_style("background: #CCC")
            text_wdg.set_value("admin")

            tr = table.add_row()
            td = table.add_cell("Please change the \"admin\" password")
            td.add_styles('height: 24px; padding-left: 6px')
        else:
            if override_password:
                text_wdg.add_style("")
            else:
                text_wdg.add_style("background: #EEE")


        table.add_row()
        password_wdg = PasswordWdg("password")
        if override_password:
            password_wdg.add_class("spt_login_textbox")
            password_wdg.add_class("form-control")
        else:
            password_wdg.add_style("color: black")
            password_wdg.add_style("background: #EEE")
            password_wdg.add_style("padding: 2px")
            password_wdg.add_style("width: 130px")
        
        password_placeholder = self.kwargs.get("password_placeholder")
        if password_placeholder:
            password_wdg.add_attr("placeholder", password_placeholder)

        th = table.add_header( "<b> %s: </b>"%password_label )
        th.add_style("padding: 5px")
        table.add_cell( password_wdg )


        if change_admin:
            table.add_row()
            password_wdg2 = PasswordWdg("verify_password")
            if override_password:
                password_wdg2.add_class("spt_login_textbox")
                password_wdg2.add_class("form-control")
            else:
                password_wdg2.add_style("color: black")
                password_wdg2.add_style("background: #EEE")
                password_wdg2.add_style("padding: 2px")
                password_wdg2.add_style("width: 130px")
            th = table.add_header( "<b>Verify Password: </b>" )
            th.add_style("padding: 5px")
            table.add_cell( password_wdg2 )






        table2 = Table()
        table2.center()
        table2.add_style("width: 280px")

        table2.add_row()

        # build the button manually
        span = SpanWdg()

        if override_login:
            up = SpanWdg()
            span.add("<div class='spt_login_button'>Login</div>")
        else:
            up = HtmlElement.img('/context/icons/logo/submit_on.png')
        up.set_id("submit_on")

        if override_login:
            down = HtmlElement.img('')
            span.add("")
        else:
            down = HtmlElement.img('/context/icons/logo/submit_over.png')
        down.add_styles( "cursor: pointer;" )
        down.set_id("submit_over")
        down.add_style("display: none")

        span.add(up)
        span.add(down)
        span.add(HiddenWdg("Submit"))
            
        span.add_event("onmouseover", "getElementById('submit_on').style.display='none';getElementById('submit_over').style.display='';")
        span.add_event("onmouseout", "getElementById('submit_over').style.display='none';getElementById('submit_on').style.display='';")
        span.add_event("onclick", "document.form.elements['Submit'].value='Submit';document.form.submit()")
        th = table2.add_header(span)
        th.add_style("text-align: center")


        table2.add_row()
        
        msg = web.get_form_value(self.LOGIN_MSG)
        td = table2.add_cell(css='center_content')

        if bottom_link:
            bottom_dict = jsonloads(bottom_link)
            for key, value in bottom_dict.items():
                td.add("<div class='spt_bottom_link'><a href=%s> %s </a></div>" % (value,key))
        else:
            td.add_style("")
        
        if self.hidden:
            msg = 'Your session has expired. Please login again.'
            div.add_style("height: 230px")

        if msg:
            from tactic.ui.widget import CodeConfirmationWdg
            if msg == CodeConfirmationWdg.RESET_MSG:
                td.add(IconWdg("INFO", IconWdg.INFO))
            else:
                pass

            td.add(HtmlElement.b(msg))
            td.add_style('line-height', '14px')
            td.add_style('padding-top', '10px')

            tr = table2.add_row()
            tr.add_style('line-height: 70px')
            td = table2.add_cell(css='center_content')
            hidden = HiddenWdg('reset_request')
            td.add(hidden)

            authenticate_class = Config.get_value("security", "authenticate_class")
            if msg != CodeConfirmationWdg.RESET_MSG and not authenticate_class:
                access_msg = "Forgot your password?"
                login_value = web.get_form_value('login')
                js = '''document.form.elements['reset_request'].value='true';document.form.elements['login'].value='%s'; document.form.submit()'''%login_value
                link = HtmlElement.js_href(js, data=access_msg)
                link.add_color('color','color', 60)
                td.add(link)

        else:
            if override_background:
                div.add_style("")
            else:
                div.add_style("height: 250px")

        div.add(HtmlElement.br())
        div.add(table)

        div.add( HtmlElement.spacer_div(1,14) )
        div.add(table2)
        div.add(HiddenWdg(self.LOGIN_MSG))

        box.add(script)

        widget = Widget()
        #widget.add( HtmlElement.br(3) )
        table = Table()
        table.add_class('spt_login_screen')
        if self.hidden:
            table.add_style('display','none')
            table.add_style('top','0px')
            table.add_style('position','absolute')


        table.add_row()
        td = table.add_cell()
        td.add_style("vertical-align: middle")
        td.add_style("text-align: center")
        td.add_style("background: transparent")
        td.add(box)
        widget.add(table)

        styles = self.get_styles()
        widget.add(styles)
        
        return widget

    def get_styles(self):

        styles = HtmlElement.style()
        styles.add(""" 
            .spt_login_screen {
                width: 100%;
                height: 85%;
            }
        """)

        return styles


class BaseSignInWdg(Widget):
    LOGIN_MSG_LABEL = 'login_message'
    RESET_MSG_LABEL = 'reset_msg'
    RESET_COMPLETE_MSG = 'Reset completed.'

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        # hidden is for inline login when a session expires
        self.hidden = kwargs.get('hidden') in  [True, 'True']
        super(BaseSignInWdg,self).__init__("div")


    def get_styles(self):

        styles = HtmlElement.style('''

        .tactic-container {
            position: relative;

            display: flex;
            flex-direction: column;
            align-items: center;

            margin: 0px;
            padding: 25px;

            border: 1px solid #ccc;
            border-radius: 3px;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
            background: white;

            font-size: 10px;
        }

        .content-container {
            margin-top: 40px;
            width: 100%;
        }

        .sign-in-text {
            position: absolute;
            top: 100px;
            font-size: 18px;
            margin: 10px 0;
            background: white;
            z-index: 2;
            padding: 0 10px;
            color: #666;
        }

        .sign-in-line {
            position: absolute;
            width: 100%;
            height: 1px;
            background: #ccc;
            top: 120px;
        }

        .sign-in-input {
            position: relative;
            width: 100%;
        }

        .board-man-gets-PAID {
            styl: paid;
            board: man;
            board: man;
            board: mans;
            gets: paid;
            styl: board;
            man: kawhi;
        }

        .sign-in-input .label {
            position: absolute; 
            top: -6;
            left: 8;
            
            padding: 0 5px;
            
            background: white;
            font-weight: normal;
            color: #aaa;
            font-size: 12px;
        }

        .sign-in-input input {
            color: black;
            width: 100%;
            padding: 16px;
            border: 1px solid #ccc;
            border-radius: 3px;
            margin-bottom: 20px;
            font-size: 16px;
        }

        .sign-in-input select {
            color: black;
            width: 100%;
            height: 52px;
            border: 1px solid #ccc;
            border-radius: 3px;
            margin-bottom: 20px;
            font-size: 16px;
        }

        .sign-in-btn {
            align-self: flex-end;
            background: #ccc;
            color: white;
            padding: 10px 16px;
            font-size: 14px;
            border-radius: 3px;
            box-shadow: 0px 2px 4px 0px #bbb;
        }

        .sign-in-btn:hover {
            background: #aaa;
        }

        .bottom-container {
            display: flex;
            justify-content: space-between;
            width: 100%;
        }

        .msg-container {
            display: flex;
            align-self: start;
            color: red;
            margin-top: 5px;
        }

        .msg-container i {
            margin-top: 1px;
            margin-right: 5px;
        }

        .msg-container span {
            text-align: start;
        }

        .floating-back-btn {
            position: absolute;
            top: 105;
            left: 10;

            display: flex;
            align-items: center;
            padding: 5px;
            box-shadow: 0px 2px 4px 0px #ccc;
            border-radius: 15px;
            background: #ccc;
            overflow: hidden;
            width: 20px;
            height: 20px;

            font-size: 14px;
            color: white;
            cursor: hand;
            
            transition: width 0.25s;
        }

        .floating-back-btn:hover {
            width: 120px;
        }

        .floating-back-btn .fa {
            margin-left: 3px;
        }

        .floating-back-btn span {
            width: 100px;
            position: absolute;
            left: 20;
        }

        .spt_tactic_background {
            margin: auto auto;
            width: 400px;
            text-align: center;
        }

        .spt_login_screen {
            width: 100%;
            height: 85%;
        }

        .spt_tactic_logo {
            height: 40px;
            margin-top: 10px;
        }

        ''')

        return styles
        

    def get_display(self):
        '''
            Return the login container.
            When overriding for custom login screens, embed result of get_content() in this return value.
        '''

        override_logo = self.kwargs.get('override_logo') == "true"
        override_company_name = self.kwargs.get('override_company_name') == "true"
            
        box = DivWdg()
        box.add_class("spt_tactic_background")

        box.add_event("onkeyup", "tactic_login(event)")
        script = HtmlElement.script('''function tactic_login(e) {
                if (!e) var e = window.event;
                if (e.keyCode == 13) {
                    document.form.submit();
                }}
                ''')
        box.add_event("onkeyup", "tactic_login(event)")
        
        div = DivWdg()
        box.add(div)
        div.add_class("tactic-container")
        div.add_class("centered")


        if override_logo:
            div.add("<div class='spt_tactic_logo'></div>")
        else:
            div.add("<img class='spt_tactic_logo' src='/context/icons/logo/TACTIC.png'/>")


        #div.add_style("padding-top: 95px")
        sthpw = SpanWdg("SOUTHPAW TECHNOLOGY INC", css="login_sthpw")
        sthpw.add_styles("margin-top: 4; color: #666;")
        if override_company_name:
            sthpw.add_class("spt_login_company")
            #sthpw.add_style("color: #CCCCCC")
        
        div.add( sthpw )
        div.add( HtmlElement.br() )

        div.add("<div class='sign-in-line'></div>")

        title = self.kwargs.get("title")
        if title:
            div.add("<div class='sign-in-text'>%s</div>" % title)

        div.add( HtmlElement.br() )

        hide_back_btn = self.kwargs.get("hide_back_btn")
        if not hide_back_btn:
            back_btn = DivWdg("<i class='fa fa-chevron-left'></i>")
            div.add(back_btn)
            back_btn.add_class("floating-back-btn")
            back_btn.add("<span>Back to login</span>")

            hidden = HiddenWdg('back_to_login')
            back_btn.add(hidden)
            back_btn.add_event('onclick',"document.form.elements['back_to_login'].value='true'; document.form.submit()")

        ####### CONTENT #######
        content_container = DivWdg()
        div.add(content_container)
        content_container.add_class("content-container")

        content_container.add(self.get_content())


        widget = Widget()
        #widget.add( HtmlElement.br(3) )
        table = Table()
        table.add_class('spt_login_screen')
        if self.hidden:
            table.add_style('display','none')
            table.add_style('top','0px')
            table.add_style('position','absolute')

        box.add(script)

        table.add_row()
        td = table.add_cell()
        td.add_style("vertical-align: middle")
        td.add_style("text-align: center")
        td.add_style("background: transparent")
        td.add(box)
        widget.add(table)

        styles = self.get_styles()
        widget.add(styles)
        
        return widget


    def get_content(self):

        return ""




class WebLoginWdg2(BaseSignInWdg):

    def get_content_styles(self):
        '''Styling for content (form) box, may be overrided.'''

        styles = HtmlElement.style('''
            .password-inputs {
                display: flex;
                flex-direction: column;
            }

            .password-inputs .sign-in-btn {
                align-self: center;
            }

            .reset-container {
                display: flex;
                flex-direction: column;
            }

            .sign-in-btn.email-reset-btn {
                align-self: flex-start;
            }

            .code-msg-container {
                margin: 20 0;
                color: #666;
                font-size: 12px;
                text-align: left;
            }

            .msg-user {
                text-decoration: underline;
            }

            .spt_code_div {
                display: flex;
                flex-direction: column;
            }


        ''')

        return styles

    def get_content(self):
        '''Determine appropriate form content based on web form data and return it.'''

        from pyasm.web import WebContainer
        web = WebContainer.get_web()

        reset_password = web.get_form_value('reset_password') == 'true'
        reset_request = web.get_form_value('reset_request') == 'true'
        new_password = web.get_form_value('new_password') == 'true'
        resend_code = web.get_form_value('resend_code') == 'true'
        send_code = web.get_form_value('send_code') == 'true'
        is_err = web.get_form_value('is_err') == 'true'

        back_to_login = web.get_form_value("back_to_login") == 'true'
        if back_to_login:
            reset_password = False
            reset_request = False
            send_code = False

        if reset_password:
            if is_err:
                return self.get_code_confirmation_content()
            else:
                code = web.get_form_value('code')
                login_name = web.get_form_value('login')
                login = Login.get_by_login(login_name, use_upn=True)

                code_correct = False
                if login:
                    data = login.get_json_value('data')
                    if data:
                        temporary_code = data.get('temporary_code')
                        if code == temporary_code:
                            code_correct = True
                            return self.get_new_password_content()
                        else:
                            web.set_form_value(BaseSignInWdg.RESET_MSG_LABEL, "The code entered was incorrect")
                    else:
                        web.set_form_value(BaseSignInWdg.RESET_MSG_LABEL, "The code has not been initialized. Please try again.")
                else:
                    web.set_form_value(BaseSignInWdg.RESET_MSG_LABEL, 'This user [%s] does not exist or has been disabled. Please contact the Administrator.' % login_name)
                if not code_correct:
                    self.get_code_confirmation_content()
        elif send_code:
            if is_err:
                return self.get_reset_options_content()
            else:
                return self.get_code_confirmation_content()
        elif resend_code:
            return self.get_code_confirmation_content()
        elif reset_request:
            return self.get_reset_options_content()
        else:
            if new_password and is_err:
                return self.get_new_password_content()
            else:
                return self.get_login_content()

    def get_new_password_content(self):
        '''Return new password form.'''

        web = WebContainer.get_web()
        login_name = web.get_form_value('login')
        hidden = HiddenWdg('login', login_name)

        div = DivWdg()
        div.add_style("margin: 0px 0px")
        div.add(hidden)


        # hidden element in the form to pass message that this was not
        # actually a typical submitted form, but rather the result
        # of a login page
        div.add( HiddenWdg("is_from_login", "yes") )
        div.add_style("font-size: 10px")

        login_div = DivWdg()
        div.add(login_div)
        login_div.add_class("password-inputs")

        password_container = DivWdg()
        login_div.add(password_container)
        password_container.add_class("sign-in-input")
        password_container.add("<div class='label'>Password</div>")

        password_wdg = PasswordWdg("my_password")
        password_container.add(password_wdg)

        confirm_password_container = DivWdg()
        login_div.add(confirm_password_container)
        confirm_password_container.add_class("sign-in-input")
        confirm_password_container.add("<div class='label'>Confirm Password</div>")

        confirm_password_wdg = PasswordWdg("confirm_password")
        confirm_password_container.add(confirm_password_wdg)

        reset_button = DivWdg('Reset')
        login_div.add(reset_button)
        reset_button.add_class("sign-in-btn hand")
        reset_button.add_attr('title', 'Reset Password')
        code = web.get_form_value('code')
        reset_button.add_event("onclick", "document.form.setAttribute('action', document.location.pathname); document.form.elements['code'].value='%s'; document.form.elements['new_password'].value='true'; document.form.submit();" % code)

        hidden = HiddenWdg("new_password")
        login_div.add(hidden)
        hidden = HiddenWdg("code")
        login_div.add(hidden)

        msg = web.get_form_value(BaseSignInWdg.RESET_MSG_LABEL)
        if msg:
            err_msg_container = DivWdg()
            div.add(err_msg_container)
            err_msg_container.add_class("msg-container")

            err_msg_container.add("<i class='fa fa-exclamation-circle'></i><span>%s</span>" % msg)

        div.add(self.get_content_styles())

        return div

    def get_code_confirmation_content(self):
        '''Return code confirmation form.'''

        web = WebContainer.get_web()
        login_name = web.get_form_value('login')
        hidden = HiddenWdg('login', login_name)

        div = DivWdg()
        div.add_style("margin: 0px 0px")

        div.add(hidden)

        # hidden element in the form to pass message that this was not
        # actually a typical submitted form, but rather the result
        # of a login page
        div.add( HiddenWdg("is_from_login", "yes") )
        div.add_style("font-size: 10px")
        div.add_class("reset-container")

        div.add("<div class='code-msg-container'>A code was sent to <span class='msg-user'>%s</span>'s email. Please enter the code to reset your password:</div>" % login_name)

        code_container = DivWdg()
        div.add(code_container)
        code_container.add_class("sign-in-input")
        code_container.add("<div class='label'>Code</div>")

        code_wdg = TextWdg("code")
        code_container.add(code_wdg)

        bottom_container = DivWdg()
        div.add(bottom_container)
        bottom_container.add_class("bottom-container")

        resend_container = DivWdg()
        bottom_container.add(resend_container)

        next_button = DivWdg('Next')
        bottom_container.add(next_button)
        next_button.add_class('sign-in-btn hand')
        next_button.add_attr('title', 'Next')
        next_button.add_event("onclick", "document.form.elements['reset_password'].value='true'; document.form.submit()")

        hidden = HiddenWdg('reset_password')
        div.add(hidden)

        msg = web.get_form_value(BaseSignInWdg.RESET_MSG_LABEL)
        if msg:
            err_msg_container = DivWdg()
            div.add(err_msg_container)
            err_msg_container.add_class("msg-container")

            err_msg_container.add("<i class='fa fa-exclamation-circle'></i><span>%s</span>" % msg)


            resend_container.add_class("forgot-password-container")
            hidden = HiddenWdg('resend_code')
            resend_container.add(hidden)

            access_msg = "Resend email"
            js = '''document.form.elements['resend_code'].value='true'; document.form.submit()'''
            link = HtmlElement.js_href(js, data=access_msg)
            link.add_color('color','color', 60)
            resend_container.add(link)


        div.add(self.get_content_styles())

        return div

    def get_reset_options_content(self):
        '''Return reset options form.'''

        web = WebContainer.get_web()
        login_name = web.get_form_value('login')

        div = DivWdg()
        div.add_style("margin: 0px 0px")

        # hidden element in the form to pass message that this was not
        # actually a typical submitted form, but rather the result
        # of a login page
        div.add( HiddenWdg("is_from_login", "yes") )
        div.add_style("font-size: 10px")
        div.add_class("reset-container")

        reset_div = DivWdg()
        div.add(reset_div)
        reset_div.add_class("spt_reset_div")

        name_container = DivWdg()
        reset_div.add(name_container)
        name_container.add_class("sign-in-input")
        name_container.add("<div class='label'>Name</div>")

        name_wdg = TextWdg("login")
        name_container.add(name_wdg)
        if login_name:
            name_wdg.set_value(login_name)

        if self.kwargs.get("login_placeholder"):
            name_wdg.add_attribute("placeholder", "Enter Login")

        # build the button manually
        email_reset_btn = DivWdg('Reset via Email')
        reset_div.add(email_reset_btn)
        email_reset_btn.add_class('sign-in-btn hand')
        email_reset_btn.add_attr('title', 'Reset via Email')
        email_reset_btn.add_event('onclick',"document.form.elements['send_code'].value='true'; document.form.submit()")

        hidden = HiddenWdg('send_code')
        div.add(hidden)

        msg = web.get_form_value(BaseSignInWdg.RESET_MSG_LABEL)
        if msg:
            err_msg_container = DivWdg()
            div.add(err_msg_container)
            err_msg_container.add_class("msg-container")

            err_msg_container.add("<i class='fa fa-exclamation-circle'></i><span>%s</span>" % msg)

        div.add(self.get_content_styles())

        return div

    def get_login_content(self):
        '''Return default login form.'''

        name_label = self.kwargs.get('name_label') or "Name"
        password_label = self.kwargs.get('password_label') or "Password"
        override_password = self.kwargs.get('override_password') == "true"
        override_login = self.kwargs.get('override_login') == "true"
        bottom_link = self.kwargs.get('bottom_link')


        web = WebContainer.get_web()
        msg = web.get_form_value(self.LOGIN_MSG_LABEL)

        allow_change_admin = self.kwargs.get("allow_change_admin")
        if allow_change_admin in [False, 'false']:
            allow_change_admin = False
        else:
            allow_change_admin = True

        # if admin password is still the default, force the user to change it
        change_admin = False
        if allow_change_admin:
            from pyasm.security import Sudo
            sudo = Sudo()
            try:
                # FIXME: This expression returns None causing security hole.
                # admin_login = Search.eval("@SOBJECT(sthpw/login['login','admin'])", single=True, show_retired=True)
                login_s = Search("sthpw/login")
                login_s.add_filter("login", "admin")
                admin_login = login_s.get_sobject()
                
                if admin_login and admin_login.get_value('s_status') =='retired':
                    admin_login.reactivate()
                    web = WebContainer.get_web()
                    web.set_form_value(self.LOGIN_MSG_LABEL, "admin user has been reactivated.")
                    admin_password = admin_log.get_value("password")
                    if admin_password == Login.get_default_encrypted_password():
                        change_admin = True

                elif admin_login:
                    password = admin_login.get_value("password")
                    if password == Login.get_default_encrypted_password() or not password:
                        change_admin = True
                
                else: 
                    # FIXME: This should use logic in Login.get_by_login
                    # that creates the admin login with certain Config settings 
                    #admin_login = Login.get_by_login("admin")
                    admin_login = SearchType.create("sthpw/login")
                    admin_login.set_value('login','admin')
                    admin_login.commit()
                    change_admin = True
            finally:
                sudo.exit()

        ####### CONTENT #######
        div = DivWdg()

        # hidden element in the form to pass message that this was not
        # actually a typical submitted form, but rather the result
        # of a login page
        div.add( HiddenWdg("is_from_login", "yes") )

        login_container = DivWdg()
        div.add(login_container)
        login_container.add_class("login-container")

        # look for defined domains
        domains = Config.get_value("active_directory", "domains")
        if not domains:
            # backwards compatibility
            domains = Config.get_value("security", "authenticate_domains")

        if domains:
            domains = domains.split('|')

        hosts = Config.get_value("active_directory", "hosts")
        if not hosts:
            hosts = Config.get_value("security", "hosts")
            
        if hosts:
            hosts = hosts.split('|')
       
        if hosts and len(hosts) != len(domains):
            msg = 'When specified, the number of IP_address has to match the number of domains'
            web.set_form_value(self.LOGIN_MSG_LABEL, msg)

        host = web.get_http_host()
        if host.find(':') != -1:
            host = host.split(':')[0]
        if domains:
            
            domain_container = DivWdg()
            login_container.add(domain_container)
            domain_container.add_class("sign-in-input")
            domain_container.add("<div class='label'>Domain</div>")

            domain_wdg = SelectWdg("domain", border_mode='custom')
            domain_wdg.set_persist_on_submit()
            if len(domains) > 1:
                domain_wdg.add_empty_option("")
            domain_wdg.set_option("values", domains)
            try:
                matched_idx = hosts.index(host)
            except ValueError:
                matched_idx = -1
            # select the matching domain based on host/IP in browser URL
            if host and matched_idx > -1:
                domain_wdg.set_value(domains[matched_idx])

            domain_container.add( domain_wdg )
        
        username_container = DivWdg()
        login_container.add(username_container)
        username_container.add_class("sign-in-input")
        username_container.add("<div class='label'>%s</div>" % name_label)

        text_wdg = TextWdg("login")
        
        login_placeholder = self.kwargs.get("login_placeholder")
        if login_placeholder:
            text_wdg.add_attr("placeholder", login_placeholder)
        
        
        username_container.add(text_wdg)

        if self.hidden:
            login_name = Environment.get_user_name()
            text_wdg.set_value(login_name)
        else:
            # check if it's first time login
            custom_projects = Search.eval("@COUNT(sthpw/project['code','not in','sthpw|admin|unittest'])")
            if custom_projects == 0:
                text_wdg.set_value('admin')

        #text_wdg.add_event("onLoad", "this.focus()")
        #table.add_cell( text_wdg )

        if change_admin:
            text_wdg.add_attr("readonly", "readonly")
            text_wdg.add_styles("color: #ccc; cursor: not-allowed;")
            text_wdg.add_behavior({
                'type': 'click',
                'cbjs_action': ''''''
                })
            text_wdg.set_value("admin")

        password_container = DivWdg()
        login_container.add(password_container)
        password_container.add_class("sign-in-input")
        password_container.add("<div class='label'>%s</div>" % password_label)

        password_wdg = PasswordWdg("password")
        password_container.add(password_wdg)
        
        password_placeholder = self.kwargs.get("password_placeholder")
        if password_placeholder:
            password_wdg.add_attr("placeholder", password_placeholder)

        if change_admin:
            password_container2 = DivWdg()
            div.add(password_container2)
            password_container2.add_class("sign-in-input")
            password_container2.add("<div class='label'>Verify Password</div>")

            password_wdg2 = PasswordWdg("verify_password")
            password_container2.add(password_wdg2)

            div.add("<div class='msg-container'>Please change the \"admin\" password</div>")


        bottom_container = DivWdg()
        div.add(bottom_container)
        bottom_container.add_class("bottom-container")

        forgot_password_container = DivWdg()
        bottom_container.add(forgot_password_container)

        if (not override_login):
            submit_btn = DivWdg("Sign In")
            submit_btn.add_class("sign-in-btn hand")
            submit_btn.add(HiddenWdg("Submit"))
            submit_btn.add_event("onclick", "document.form.elements['Submit'].value='Submit';document.form.submit()")
            bottom_container.add(submit_btn)


        err_msg_container = DivWdg()
        div.add(err_msg_container)
        err_msg_container.add_class("msg-container")

        if bottom_link:
            bottom_dict = jsonloads(bottom_link)
            for key, value in bottom_dict.items():
                err_msg_container.add("<div class='spt_bottom_link'><a href=%s> %s </a></div>" % (value,key))
        
        if self.hidden:
            msg = 'Your session has expired. Please login again.'

        if msg:
            if msg == BaseSignInWdg.RESET_COMPLETE_MSG:
                err_msg_container.add(IconWdg("INFO", IconWdg.INFO))

            err_msg_container.add("<i class='fa fa-exclamation-circle'></i><span>%s</span>" % msg)

            forgot_password_container.add_class("forgot-password-container")
            hidden = HiddenWdg('reset_request')
            forgot_password_container.add(hidden)

            authenticate_class = Config.get_value("security", "authenticate_class")
            if msg != BaseSignInWdg.RESET_COMPLETE_MSG and not authenticate_class:
                access_msg = "Forgot your password?"
                login_value = web.get_form_value('login')
                js = '''document.form.elements['reset_request'].value='true';document.form.elements['login'].value='%s'; document.form.submit()'''%login_value
                link = HtmlElement.js_href(js, data=access_msg)
                link.add_color('color','color', 60)
                forgot_password_container.add(link)


        div.add(HiddenWdg(self.LOGIN_MSG_LABEL))
        div.add(self.get_content_styles())
        return div



# DEPRECATED: moved lower to pyasm/web
"""
class WebLoginCmd(Command):

    def check(self):
        return True

    def is_undoable(cls):
        return False
    is_undoable = classmethod(is_undoable)

    def reenable_user(self, login_sobject, delay):
        class EnableUserTask(SchedulerTask):
            def execute(self):
                Batch()
                reset_attempts = 0
                login_sobject = self.kwargs.get('sobject')
                login_sobject.set_value("license_type", "user")
                login_sobject.set_value("login_attempt", reset_attempts)
                login_sobject.commit(triggers=False)

        scheduler = Scheduler.get()
        task = EnableUserTask(sobject=login_sobject, delay=delay)
        scheduler.add_single_task(task, delay)
        scheduler.start_thread()

              
    def execute(self):

        web = WebContainer.get_web()

        # If the tag <force_lowercase_login> is set to "true"
        # in the TACTIC config file,
        # then force the login string argument to be lowercase.
        # This tag is false by default.
        self.login = web.get_form_value("login")
        if Config.get_value("security","force_lowercase_login") == "true":
            self.login = self.login.lower()
        self.password = web.get_form_value("password")
        self.domain = web.get_form_value("domain")

        if self.login == "" and self.password == "":
            return False

        
        if self.login == "" or  self.password == "":
            web.set_form_value(WebLoginWdg.LOGIN_MSG, \
                "Empty username or password") 
            return False
        
        security = WebContainer.get_security()

        # handle windows domains
        #if self.domain:
        #    self.login = "%s\\%s" % (self.domain, self.login)


        verify_password = web.get_form_value("verify_password")
        if verify_password:
            if verify_password != self.password:
                web.set_form_value(WebLoginWdg.LOGIN_MSG, \
                    "Passwords do not match.") 
                return False

            self.password = Login.get_default_password()

        try:
            security.login_user(self.login, self.password, domain=self.domain)
        except SecurityException as e:
            msg = str(e)
            if not msg:
                msg = "Incorrect username or password"
            web.set_form_value(WebLoginWdg.LOGIN_MSG, msg)

            login_code = "admin"

            search = Search("sthpw/login")
            search.add_filter('login',self.login)
            login_sobject = search.get_sobject()
            max_attempts=-1
            try:
                max_attempts = int(Config.get_value("security", "max_login_attempt"))
            except:
                pass
            if max_attempts >0:
                login_attempt = login_sobject.get_value('login_attempt')

                login_attempt = login_attempt+1
                login_sobject.set_value('login_attempt', login_attempt)

                if login_attempt == max_attempts:
                    #set license_Type to disabled and set off the thread to re-enable it
                    login_sobject.set_value('license_type', 'disabled')
                    disabled_time = Config.get_value("security", "account_lockout_duration")
                    if not disabled_time:
                        disabled_time = "30 minutes"


                    delay,unit = disabled_time.split(" ",1)
                    if "minute" in unit:
                        delay = int(delay)*60
                    
                    elif "hour" in unit:
                        delay =int(delay)*3600
                    
                    elif "second" in unit:
                        delay = int(delay)
                    else:
                        #make delay default to 30 min
                        delay = 30*60

                    self.reenable_user(login_sobject, delay)

                
                login_sobject.commit(triggers=False)
            
        if security.is_logged_in():

            # set the cookie in the browser
            web = WebContainer.get_web()
            ticket = security.get_ticket()
            if ticket:
                web.set_cookie("login_ticket", ticket.get_value("ticket"))


            login = security.get_login()
            if login.get_value("login") == "admin" and verify_password:
                login.set_password(verify_password)
"""




class WebLicenseWdg(Widget):

    LOGIN_MSG = 'login_message'
    def get_display(self):

        box = ShadowBoxWdg()
        box = DivWdg(css='login')
        
        div = DivWdg()
        div.add_style("margin: 0px 0px")
        div.add_class("centered")
        box.add(div)


        div.add(HtmlElement.br(7))

        # hidden element in the form to pass message that this was not
        # actually a typical submitted form, but rather the result
        # of a login page
        div.add( HiddenWdg("is_from_login", "yes") )

        table = Table(css="login")
        table.center()
        table.set_attr("cellpadding", "3px")
        table.add_row()

        error_div = DivWdg()
        error_div.add_class("maq_search_bar")
        error_div.add_style("font-size: 1.5em")
        error_div.add_style("padding: 5px")
        error_div.add_style("margin: 0 5px 0 5px")
        error_div.add_style("text-align: center")
        icon = IconWdg("LicenseError", IconWdg.ERROR)
        error_div.add(icon)
        error_div.add("License Error")
        table.add_cell( error_div)

        license = WebContainer.get_security().get_license()
        table.add_row()
        td = table.add_cell( "<b>%s</b>" % license.get_message() )
        td.add_style("padding: 5px 20px 5px 20px")
        table.add_row()
        td = table.add_cell( "<b>Please contact your representative. In the meantime, you can login with 'admin'</b>" )
        td.add_style("padding: 5px 20px 5px 20px")
        table.add_row()
        table.add_row()
        OK = ProdIconSubmitWdg('Return to Login')
        
        base_url = WebContainer.get_web().get_project_url().to_string()
        script = "window.location.href='%s'" % base_url
        OK.add_event('onclick', script)
        table.add_cell(OK, css='center_content')
        div.add(table)

        widget = Widget()
        widget.add( HtmlElement.br(3) )
        widget.add(box)
        
        return widget




class ChangePasswordWdg(Widget):

    PASSWORD = 'password'
    def init(self):

        marshaller = WebContainer.register_cmd( "pyasm.command.PasswordAction" )
        marshaller.set_option("commit_flag", "True")

        login = Environment.get_security().get_login()
        marshaller.set_option("search_key",login.get_search_key())

    def get_display(self):
        from pyasm.prod.web import ProdIconSubmitWdg

        top = DivWdg()
        top.add_style("padding: 10px")
        top.add_border()
        top.add_color("color", "color")
        top.add_color("background", "background")

        table = Table()
        top.add(table)

        table.set_max_width()
        table.add_class('collapse')
        table.set_style("margin: auto; margin-top: 40px")
        table.add_row()
        table.add_cell( "New Password:" )
        password = PasswordWdg(self.PASSWORD)
        table.add_cell( password )
        table.add_row()
        table.add_cell( "Re-enter Password:" )

        table.add_cell( PasswordWdg("password re-enter") )
        table.add_row()
        table.add_blank_cell()
        
        table.add_row()

        td = table.add_cell( ProdIconSubmitWdg("Submit") )
        td.add_class('center_content')
        td.set_attr('colspan','2')

        return top




# DEPRECATED

class SignOutLinkWdg(Widget):
    def __init__(self):
        super(SignOutLinkWdg,self).__init__("div")
    
    def init(self):

        web = WebContainer.get_web()
        base_url = web.get_project_url().to_string()

        href = SpanWdg()
        href.add( "[sign-out]")
        href.add_behavior( {
        'type': 'click_up',
        'login': web.get_user_name(),
        'cbjs_action': '''
        if ( confirm("Are you sure you wish to sign out?") ) {
            var server = TacticServerStub.get();
            server.execute_cmd("SignOutCmd", {login: bvr.login} );
            window.location.href='%s';
        }
        ''' % base_url
        } )

        palette = web.get_palette()
        hover = palette.color("color2", 40)
        href.add_behavior( {
        'type': 'hover',
        'mod_styles': 'color: %s' % hover
        } )

        href.add_class("hand")
       
        self.add(href)


"""
class ChangePasswordLinkWdg(Widget):

    def init(self):
        xpos = '0'
        if WebContainer.get_web().is_IE():
            xpos = '-500'
        overlay = ModalBoxWdg(name='iframe_password', \
            title_wdg=_('Change Password'), xpos=xpos, nav_links=False)
        div = DivWdg()
        div.set_id("change_password")
        div.add_style("display: none")
        ajax = AjaxLoader()
        ajax.set_display_id("change_password")
        ajax.set_load_class("pyasm.widget.ChangePasswordWdg")
        overlay.add( div )
        self.add( overlay )

        overlay_script = overlay.get_on_script()
        ajax_script = ajax.get_on_script()

        link = HtmlElement.js_href('%s;%s' %(overlay_script, ajax_script), \
                data='[change-password]')
        self.add( link )
"""



class UndoButtonWdg(IconButtonWdg):
    def __init__(self,long=True):
        #super(UndoButtonWdg,self).__init__(_("Undo"), IconWdg.UNDO,long)
        super(UndoButtonWdg,self).__init__("Undo", IconWdg.UNDO,long)
        transaction = TransactionLog.get_last('undo')

        # if there aren't any transaction, just return
        if not transaction:
            return

        desc = transaction.get_description().strip()
        desc = Common.escape_tag(desc)
        if len(desc) > 60:
            desc = '%s&nbsp;.....' % desc[:60]
        if transaction:
            self.add_tip(desc, title='Undo')
                
        cmd = AjaxCmd("UndoCmd")
        cmd.register_cmd("pyasm.command.UndoCmd")
        script = cmd.get_on_script(False)

        div = cmd.generate_div()
        div.add_style('display: none')

        # FIXME: disabling for now ... too buggy
        #update_script = self.get_update_script(transaction)
        #div.set_post_ajax_script(update_script)
        div.set_post_ajax_script('document.form.submit()')


        self.add(div)
        self.add_event('onclick', script)



    def get_update_script(self, transaction):
        if not transaction:
            return "alert('Nothing to undo')"

        xml = transaction.get_xml_value("transaction")

        nodes = xml.get_nodes("transaction/*")
        nodes.reverse()

        # if there is an error, report it but do what you can
        event_container = WebContainer.get_event_container()
        refresh_scripts = []
        for node in nodes:
            if node.nodeName == "sobject":
                search_type = Xml.get_attribute(node,"search_type")
                search_id = Xml.get_attribute(node,"search_id")

                search_key = "%s|%s" % (search_type, search_id)

                action = Xml.get_attribute(node,"action")
                if action == "update":
                    refresh_script = event_container.get_event_caller("refresh|%s" % search_key )
                elif action == "insert":
                    refresh_script = event_container.get_event_caller("refresh|%s" % search_type )
                else:
                    refresh_script = "document.form.submit()"

                # if there are more than 3 updates, then just update the whole
                # table
                refresh_scripts.append(refresh_script)
                if len(refresh_scripts) > 3:
                    refresh_scripts = []
                    refresh_script = event_container.get_event_caller("refresh|%s" % search_type )
                    refresh_scripts.append(refresh_script)
                    break

        # now refresh any tables that think they should be update on any data
        # change
        refresh_script = event_container.get_event_caller("refresh|data_update")
        refresh_scripts.append(refresh_script)


        # refresh the undo widgets
        refresh_script = event_container.get_event_caller("SiteMenuWdg_refresh")
        refresh_scripts.append(refresh_script)

        return ";".join(refresh_scripts)
        

class RedoButtonWdg(UndoButtonWdg):
    def __init__(self,long=True):
        # This is intentionally skipping the __init__ of UndoButtonWdg
        #super(UndoButtonWdg,self).__init__(_("Redo"), IconWdg.REDO,long)
        super(UndoButtonWdg,self).__init__("Redo", IconWdg.REDO,long)
        transaction = TransactionLog.get_next_redo()
        if transaction:
            desc = transaction.get_description().strip()
            desc = Common.escape_tag(desc)
            if len(desc) > 60:
                desc = '%s&nbsp;.....' % desc[:60]
            self.add_tip(desc, title='Redo')
        else:
            self.add_tip('n/a', title='Redo')
        cmd = AjaxCmd("RedoCmd")
        cmd.register_cmd("pyasm.command.RedoCmd")
        script = cmd.get_on_script(False)

        div = cmd.generate_div()
        div.add_style('display: none')

        # FIXME: disabling for now ... too buggy
        #update_script = self.get_update_script(transaction)
        #div.set_post_ajax_script(update_script)
        div.set_post_ajax_script('document.form.submit()')

        self.add(div)
        self.add_event('onclick', script)




class CmdReportWdg(Widget):
    '''report all of the errors from the commands'''
    def __init__(self):
        self.total_errors = []
        super(CmdReportWdg,self).__init__()
        

    def init(self):
        # add in summary from commands
        cmd_delegator = WebContainer.get_cmd_delegator()
        executed_cmds = cmd_delegator.get_executed_cmds()
        
            
        #if len(executed_cmds) == 0:
        #    return

        
        # assemble all of the errors
        for cmd in executed_cmds:
            errors = cmd.get_errors()
            for error in errors:
                self.total_errors.append(error)

        # get error from error.txt
        error_path = '%s/error.txt' %FileCheckin.get_upload_dir()
        if os.path.exists(error_path):
            try: 
                file = open(error_path, "r")
                client_error = "".join(file.readlines())
                
                file.close()
                # must remove the file since some commands stop
                # if they find the file exist
                os.unlink(error_path)
                self.total_errors.append(client_error)
            except IOError as e:
                self.total_errors.append("Error reading error.txt")

        if not self.total_errors:
            return
        
        error_table = Table()
        error_table.set_max_width()
        error_table.set_class("table")
        error_table.add_row()


        # fill in the error table
        error_table.add_header(IconWdg("Errors", IconWdg.ERROR, True) )
        error_table.add_col(css='small')
        error_table.add_col()
        for error in self.total_errors:
            error_table.add_row()
            error_table.add_blank_cell()
            error_str = str(error)
            pat = re.compile('<|>')
            error = pat.sub('', error)
            error = error.replace('\\n','<br/>')
            error_table.add_cell(error, "warning")

        self.add(error_table)
    
    def get_errors(self):
        return self.total_errors
       
class WarningReportWdg(Widget):

    def get_display(self):
        wdg_warnings = WebContainer.get_warning()

        # get warning from warning.txt
        error_path = '%s/warning.txt' %FileCheckin.get_upload_dir()
        if os.path.exists(error_path):
            try: 
                file = open(error_path, "r")
                client_warning = "".join(file.readlines())
                pat = re.compile('<|>')
                client_warning = pat.sub('', client_warning)
                file.close()
                
                warnings = client_warning.split('\n')
                # must remove the file since some commands stop
                # if they find the file exist
                for warning in warnings:
                    if not warning.strip():
                        continue
                    items = warning.split('||', 2)
                    type = ''
                    if len(items) == 2:
                        label, msg = items[0], items[1]
                    elif len(items) == 3:
                        label, msg, type = items[0], items[1], items[2]
                    # cannot process double quotes
                    msg = msg.replace('"', '')
                    warn = TacticWarning(label, msg, type)
                    wdg_warnings.append(warn)

                os.unlink(error_path)
            except IOError as e:
                raise TacticException("Error reading warning.txt")

        for warning in wdg_warnings:
            self._add_item(warning)

        # add a view_all item 
        if len(wdg_warnings) > 0:
            all_warnings = '<br/>'.join([warn.get_msg() for warn in wdg_warnings])
            warning = TacticWarning('- View All -', all_warnings)
            self._add_item(warning)
            
        # add blinking effect
        script = HtmlElement.script("if (warn_menu.help_actions.length > 0) \
            {var warning_interval = window.setInterval(\"Effects.blink('warning_menu')\", 1000);\
            if ($('warning_menu'))  $('warning_menu').setStyle('visiblity','visible');} ")
        script.set_attr('mode','dynamic')
        self.add(script)
        
        super(WarningReportWdg, self).get_display()

    def _add_item(self, warning):
        msg = warning.get_msg()
        label = warning.get_label()
        type = warning.get_type()

        script = "Effects.slide_in('%s', '%s')"%(HelpMenuWdg.SLIDE_PANEL, msg)
        escaped_script = Common.escape_quote(script)
        script_wdg = HtmlElement.script("warn_menu.add('%s','%s')" \
            %(label, escaped_script))
        self.add(script_wdg)

        if type=='urgent':
            BaseAppServer.add_onload_script(script)

        warn_menu = WebContainer.get_menu('warn_menu')
        span = SpanWdg(label, css='hand')
        span.add_event('onclick', script)
        warn_menu.add(span)
        
class MessageWdg(DivWdg):
    def __init__(self, message, css=None, icon=None):
        assert message
        if not css:
            css = 'warning'
        if not icon:
            icon = IconWdg.ERROR
            
        span = SpanWdg(IconWdg('message', icon))   
        span.add(message)

        # create an OK button to close the window
        
        from pyasm.prod.web import ProdIconButtonWdg
        iframe = WebContainer.get_iframe()
        ok = ProdIconButtonWdg("OK")
        iframe_close_script = "window.parent.%s" % iframe.get_off_script() 
        ok.add_event("onclick", iframe_close_script)
        
        span.add(HtmlElement.br(2))
        span.add(ok)
        super(MessageWdg,self).__init__(span, css)
        
class HintWdg(SpanWdg):
    def __init__(self, message, css='small', icon="BS_QUESTION_SIGN", title=''):
        assert message
        message = message.replace('\n','<br/>')
        icon_wdg = IconWdg("", icon)
        if title:
            message = '%s::%s' %(title, message)
        icon_wdg.set_attr('title', message)
        icon_wdg.add_class('tactic_tip')
        
        super(HintWdg,self).__init__(icon_wdg, css)

    
    def get_on_script(msg):
        ''' get the js to show the hint bubble '''
        msg = Common.escape_quote(msg).replace('\n','<br/>')
        return "hint_bubble.show(event, '%s')" %msg
                
    get_on_script = staticmethod(get_on_script)

    

class HelpMenuWdg(Widget):

    SLIDE_PANEL = 'slide_panel'
    SLIDE_PANEL_CONTAINER = 'slide_panel_cont'
    SLIDE_PANEL_BODY = 'slide_panel_body'
    def get_display(self):
        span = SpanWdg(IconWdg('help', IconWdg.HELP), css='small hand')
        # DEPRECATED
        #span.add_event('onmouseover', "help_menu.show(event)")
        help_menu = WebContainer.get_menu('help_menu')
        span.add_event('onmouseover', help_menu.get_on_script())
        self.add(span)
        
        BaseAppServer.add_onload_script("Effects.slide_hide('%s')" % self.SLIDE_PANEL)
        return super(HelpMenuWdg, self).get_display()

    def get_panel(self):
        '''a single panel needs to be placed in the page'''
        # add a slide panel
        div = DivWdg(id=self.SLIDE_PANEL, css=self.SLIDE_PANEL )
        div.add_style('display','none') 
        container = DivWdg(id = self.SLIDE_PANEL_CONTAINER, css=self.SLIDE_PANEL_CONTAINER)
        close = CloseWdg("Effects.slide_out('%s')" % self.SLIDE_PANEL, is_absolute=True)
        container.add(close)
        body_div = DivWdg(id=self.SLIDE_PANEL_BODY)
        div.add(body_div)
        container.add(div)

        return container

class HelpItemWdg(Widget):
    '''this is used for displaying help infomation
       Nothing really gets drawn here, just adding to the help menu in WebContainer
       @label - a label in the help popup menu
       @script - a link to a html file or a string message
       @is_link - True if script is a link ref '''
    def __init__(self, label, script, is_link=False):
        assert script
        if is_link:
            script = IframeWdg.get_popup_script(ref=script, width=100)
        else:
            script = "Effects.slide_in('%s', '%s')"%(HelpMenuWdg.SLIDE_PANEL, script)
        #help_menu = WebContainer.get_menu('help_menu')
        #span = SpanWdg(label, css='hand')
        #span.add_event('onclick', script)
        #help_menu.add(span)
        super(HelpItemWdg, self).__init__()
   
class WarningMenuWdg(Widget):
    def init(self):
        span = SpanWdg(IconWdg('', IconWdg.ERROR), css='small hand')
        warn_menu = WebContainer.get_menu('warn_menu')
        span.add_event('onmouseover', "%s; Effects.blink('warning_menu', warning_interval)" \
                %warn_menu.get_on_script())
        span.set_id('warning_menu')
        span.add_style('visibility: hidden')
        self.add(span)
        


class FloatMenuWdg(DivWdg):
    '''a float menu for quick access to info or buttons''' 
    def __init__(self, id, content=None, css='hidden popup_hint'):
        self.title = ''
        self.id = id
        super(FloatMenuWdg,self).__init__(content, css)
        self.set_id(id)
        self.add_style('display','none')
        self.add_style('padding: 2px 8px 10px 8px')
        
    def init(self):
        self.add(CloseWdg("set_display_off('%s')" %self.id))
        self.span = DivWdg('actions')
        self.span.add('&nbsp;', 'title')
        self.span.add_style('border-bottom: 1px dotted #888')
        self.add(self.span)
        self.add(HtmlElement.br())
        

    def set_title(self, title):
        self.title = title

    def get_display(self):
        if self.title:
            self.span.set_widget(SpanWdg('- %s ' %self.title, css='small'), 'title')
        
        return super(FloatMenuWdg, self).get_display()
  
    def get_icon(self):
        icon = IconWdg('float_menu', icon=IconWdg.FLOAT, css='hand')
        icon.add_event('onclick', self.get_on_script())
        return icon

    def get_on_script(self):
        return "Common.follow_click(event, '%s', -60, -80); Effects.fade_in('%s', 100)"\
                %(self.id, self.id)

class ExtraInfoWdg(SpanWdg):


    def init(self):
        self.mouseout_flag = True
        self.id = "ExtraInfoWdg_%s" % self.generate_unique_id()
        self.div_css = ''
        self.span = SpanWdg()
        self.content = ""
        
    def set_content(self, content):
        self.content = content

    def set_mouseout_flag(self, flag):
        self.mouseout_flag = flag

    def set_class(self, css):
        self.div_css = css
        
    def add(self, widget):
        self.span.add(widget)
        
    def get_display(self):
        self._add_widget(self.span)
        self.span.add_class('hand')
        # hidden container
        if not self.div_css:
            self.div_css = 'popup_hint'
           
        div = DivWdg(css=self.div_css, id=self.id)

        # inner div is needed for all sorts of display effects
        inner_div = DivWdg(id = '%s_inner' %self.id)
        inner_div.add_style('display', 'block')
        div.add(inner_div)

        div.add_style('display','none')
        div.add_style('cursor','default')
        '''
        div.add_style('position','absolute')
        div.add_style('border-style','solid')
        div.add_style('border-width','1px')
        div.add_style('background','#ffffff')
        div.add_style('padding','10px')
        '''
        inner_div.add(self.content)
        self._add_widget(div)
        self.span.add_event("onmousedown", self.get_mousedown_script())
        if self.mouseout_flag:
            self.span.add_event("onmouseout", "e=document.getElementById('%s');e.style.display='none';" % self.id)

        return super(ExtraInfoWdg,self).get_display()


    def get_mousedown_script(self, height='115'):
        #return "set_display_on('%s');" % self.id
        return "Effects.roll('%s','down', '%s')" %(self.id, height)

    def get_off_script(self):
        script = "Effects.roll('%s','up')" %self.id
        #script = "e=document.getElementById('%s');e.style.display='none';"\
        #    % self.id
        return script
        

class UserExtraInfoWdg(ExtraInfoWdg):

    def __init__(self, user=None):
        self.user = user 
        assert self.user
        super(UserExtraInfoWdg,self).__init__()

    def init(self):
        assert self.user
        
        # run the init of ExtraInfoWdg
        super(UserExtraInfoWdg, self).init()
        from pyasm.security import Login

        # create the content
        content = DivWdg()

        login = Login.get_by_login(self.user)

        if not login:
            return
        thumb = self.get_thumb(login)
        content.add(thumb)
        content.add(login.get_full_name())
        content.add(HtmlElement.br())
        content.add(login.get_value("email"))

        self.set_content(content)
        self.set_mouseout_flag(True)
        user_name = HtmlElement.b(' %s' %self.user)
        user_name.add_class('user_name')
        self.add(user_name)
        
        

    def get_thumb(self, login):
        '''get and cache the thumb image'''
        img = Container.get('UserExtraInfoWdg:%s' %login.get_login())
        if not img:
            from .file_wdg import ThumbWdg
            
            thumb = ThumbWdg()
            thumb.set_sobject( login )
            img = thumb.get_buffer_display()
            Container.put('UserExtraInfoWdg:%s' %login.get_login(), img)
        return img
        
class ProgressWdg(DivWdg):
    ''' an overlay progress indicator with an option progress meter'''

    def __init__(self, message='Processing. . .', css='progress_container', \
            icon=IconWdg.PROGRESS):
        
        super(ProgressWdg,self).__init__(css=css, id='tactic_busy')
        self.add_style('display','none')
        self.busy_icon = icon
        self.show_busy_icon = True
        self.message = message
        
    def set_busy_icon(self, show):
        self.show_busy_icon = show

    def get_display(self):
        div = DivWdg(css='content')
        div.center()
        msg_div = DivWdg(self.message, css='progress_message', id='tactic_busy_msg')
        msg_div.add_style('margin-left','10px')
        icon = IconWdg('busy', self.busy_icon)
        icon.set_id('tactic_progress_icon')
        #icon.add_style('margin-left', '105px')
         
        top_div = DivWdg()
        top_div.add(msg_div)
        top_div.add(icon)
        top_div.add_style('margin-top','8px')
        
        meter = DivWdg(css='small',  id='tactic_progress_meter')
        meter.add_style('margin-left','10px')
        meter.add_style('height: 40px')
        meter.add_style('display: none')

        # this bar provides a reference length
        bar = DivWdg('&nbsp', id='tactic_progress_ref_bar')
        bar.add_style('width','216px')
       
        # the bar that moves
        bar2 = DivWdg('&nbsp', css='progress_bar', id='tactic_progress_bar')
        bar2.add_style('width','0px')
        bar2.add_style('position', 'absolute')
        bar.add(bar2)
        
        meter.add(bar)
        value_div = FloatDivWdg('0 %', css='progress_meter_value', id='tactic_progress_value')
        bar.add(value_div)
       
        # this animated gif is dead most of the time anyways, remove it for now
        
        div.add(top_div)
        div.add(meter)
        self.add(div)
        
        return super(ProgressWdg, self).get_display() 
        
    def get_on_script(message='Processing', show_meter='false'):
        return "Overlay.display_progress('%s',%s)" %(message, show_meter)

    get_on_script = staticmethod(get_on_script)

    def get_off_script():
        return "Overlay.hide_progress()"

    get_off_script = staticmethod(get_off_script)

    def get_response_script(message):
        return '<script>%s;%s</script>' \
                %(ProgressWdg.get_on_script(message=message),\
                ProgressWdg.get_off_script())
    get_response_script = staticmethod(get_response_script)

class SiteMenuWdg(SpanWdg, AjaxWdg):

    ID = 'SiteMenuWdg'
    EVENT_ID = 'SiteMenuWdg_refresh'
    def init(self):
        self.init_setup()
        
        
    def get_display(self):
        event_container = WebContainer.get_event_container()
        script = SiteMenuWdg.get_self_refresh_script(show_progress=False)
        event_container.add_listener(self.EVENT_ID, script, replace=True )
        
        self.add(WarningMenuWdg()) 
        self.add(UndoButtonWdg())
        self.add(RedoButtonWdg())
        self.add(IconRefreshWdg())
        self.add(SpanWdg(css='small'))
        super(SiteMenuWdg, self).get_display()
        
    def init_setup(self):
        self.set_id(self.ID)
        self.set_ajax_top(self)


class DateSelectWdg(SelectWdg):
    '''A SelectWdg that filters out database entries based on time interval.
       e.g. label_list = ['Today','1 Hour Ago', 'Last 2 days', 'Last 5 days', 'Last 30 days']
            value_list = ['today','1 Hour', '1 Day', '4 Day','29 Day']'''
        
    def __init__(self, name='date_select', label='Date: ', is_filter=True,\
            label_list=['Today','1 Hour Ago', 'Last 2 days', 'Last 5 days', 'Last 30 days'],\
            value_list=['today','1 Hour', '1 Day', '4 Day','29 Day']):
            
        
        self.label_list = label_list
        self.value_list = value_list
        self.label = label
        super(DateSelectWdg, self).__init__(name, label=label)
        # these have to be set in the constructor
        if is_filter:
            self.set_persistence()
            self.set_submit_onchange()
        
    def set_label(self, label_list):
        self.label_list = label_list
   
    def set_value(self, value_list):
        self.value_list = value_list

    
    def get_display(self):
        self.add_empty_option(label='--  All  --', value=SelectWdg.NONE_MODE)
        self.set_option('labels', "|".join(self.label_list))
        self.set_option('values', "|".join(self.value_list))

        return super(DateSelectWdg, self).get_display()
        '''
        if self.label:
            span = SpanWdg('%s: ' %self.label, css='small')
            select = FilterSelectWdg.get_class_display(self)
            span.add(select)
            return span
        else:
        '''     
        

    def get_where(time_interval):
        ''' get the where sql statement for search '''
        from pyasm.search import Select
        return Select.get_interval_where(time_interval)

    get_where = staticmethod(get_where)



class CloseWdg(Widget):
    
    def __init__(self, off_script, is_absolute=True):
        self.off_script = off_script
        self.is_absolute = is_absolute
        super(CloseWdg, self).__init__()

    def init(self):
        div = FloatDivWdg("X", css='hand right_content',  width='1em')
        div.add_event('onclick', self.off_script)
        if self.is_absolute:
            div.add_style('position: absolute') 
        div.add_style('right: 0.5em')
        div.add_style('color: black')
        self.add(div)

class PopupWindowLinkWdg(HtmlElement):
    ''' a link for a pop-up window '''
    def __init__(self, search_type, widget='FlashSwfViewWdg', element_list=[] ):
        super(PopupWindowLinkWdg,self).__init__("span")
       
        self.add_style("padding: 0 5px 0 5px")
        self.search_type = search_type
        self.widget = widget 
        self.button = IconButtonWdg("pop_up", long=False)
        self.element_list = element_list

    def set_button(self, button):
        self.button = button
        
    def get_display(self):

        web_state = WebState.get()
       
        url = WebContainer.get_web().get_widget_url()
        url.set_option("widget", self.widget)
        url.set_option("search_type", self.search_type) 

        url.add_web_state()
        ref = url.get_url()
        button = self.button

        action = PopupWindowWdg.get_on_script(ref, self.element_list)
        button.add_event("onclick", action)
        self.add(button)

        return super(PopupWindowLinkWdg,self).get_display()


class FileUploadUpdateWdg(AjaxWdg):
    '''It updates the upload progress'''

    def init_cgi(self):
        self.file_name = ''
        keys = self.web.get_form_keys()
        for key in keys:
            pat = re.compile(r'(\|files|\|images|\|snapshot|\|submission|\|publish_main)$')
            if pat.search(key):
                self.file_name = self.web.get_form_value(key)
                if self.file_name:
                    self.file_name = File.process_file_path(os.path.basename(self.file_name))

    def get_display(self):
        if not self.file_name:
            return Widget()
        
        path ="%s/%s_progress" % ( Environment.get_upload_dir(), self.file_name)
        file_size = ''
        try:
            f = open(path, 'r')
            file_size = f.readline()
            print("file size ",file_size)
            if file_size:
                file_size = float(file_size)/ 1048576
                file_size = '%.2f' %file_size
            f.close()
        except IOError as e:
            pass 
       
        update_label = ''
        if file_size:
            update_label = '%s Mb' %file_size
        div = DivWdg(update_label)
        return div


class FilterboxWdg(DivWdg):
    ''' A Filter box that can be expanded to display more complicated filters'''
    ATTR_WIDTH = 100
    def __init__(self, name='filter_box'):
        
        super(FilterboxWdg, self).__init__(css='filter_box')
        self.add_style('width: 100%')
        self.advanced_filters = []
        self.bottom_wdgs = []
        self.left_span = FloatDivWdg()
        self.left_span.add_style('margin: 6px 0 2px 10px')
        self.content_div = DivWdg(id='%s_content' %name)
        self.content_div.add_style('margin-top','6px')
        self.content_div.add_style('clear', 'left')
        swap = SwapDisplayWdg()
        
        is_toggle_open = ProdSetting.get_value_by_key('is_toggle_open')
        if is_toggle_open == 'true':
            is_toggle_open = True
            swap.set_off()
        else:
            is_toggle_open = False
        SwapDisplayWdg.create_swap_title('', swap, self.content_div, is_open=is_toggle_open)
        self.add(swap) 

    def _is_input(self, widget):
        ''' return True if it is a Filter '''
        from pyasm.prod.web import BaseSelectFilterWdg
        return isinstance(widget, BaseInputWdg) or isinstance(widget, BaseSelectFilterWdg)

    def add_advanced_filter(self, filter, label=''):
        ''' add filters or regular widgets (hints and stuff) into the 
        advanced section of the filter box'''
        if not label and self._is_input(filter):
            label = filter.get_label()
            label = label.replace(':', '').strip()
        self.advanced_filters.append((filter, label))

    def add(self, widget):
        div = FloatDivWdg(widget)
        self.left_span.add(div)

    def add_bottom(self, widget):
        self.bottom_wdgs.append(widget)
    
    def get_display(self):
        from pyasm.prod.web import ProdIconButtonWdg
        # add a refresh button
        icon = ProdIconButtonWdg('Filter')
        icon.add_event('onclick', 'document.form.submit()')
        icon_div = FloatDivWdg(icon)
        icon_div.add_style('margin-top', '2px')
        self.left_span._add_widget(icon_div)
        # value_list stores values for display
        value_list = []
        # label_list keeps track of uniqueness
        label_list = []
        count = 0
        for idx, (filter, label) in enumerate(self.advanced_filters):
            self.content_div.add(filter)
            if self._is_input(filter):
                values = filter.get_values()
                values = [x for x in values if x]
                if values == ['']:
                    continue
                #TODO: display the label_display instead
                if label not in label_list and values:
                    if len(values) > 1:
                        values = Common.get_unique_list(values)
                    value_display = SpanWdg(','.join(values), css='label_over').get_buffer_display()
                    display = '%s: %s' % (label, value_display)
                    count += len(display)
                    label_list.append(label)
                    '''
                    # insert line breaks if it exceeds the ATTR_WIDTH
                    if count > self.ATTR_WIDTH:
                        display = '%s<br/>' %display
                        count = 0
                    '''
                    value_list.append(display)
        attr_div = FloatDivWdg(', '.join(value_list), css='smaller left_content')
        attr_div.add_style('width','500')
        attr_div.add_style('margin-left', '40px')
        
        bottom_div =  FloatDivWdg(css='smaller left_content')
        #bottom_div.add_style('clear', 'left')
        bottom_div.add_style('margin', '2px 0 10px 30px')
        for wdg in self.bottom_wdgs:
            bottom_div.add(wdg)

        self._add_widget(self.left_span)
        self._add_widget(attr_div)
        #self._add_widget(HtmlElement.br())
        self._add_widget(bottom_div)
        self._add_widget(HtmlElement.br(3))
        self._add_widget(self.content_div)

        return super(FilterboxWdg, self).get_display()
        

class ExceptionWdg(Widget):

    def __init__(self, e):
        self.exception = e
        super(ExceptionWdg, self).__init__(self)

    def init(self):
        e = self.exception
        stacktrace = ExceptionLog.log(e)
        from pyasm.command import FileUploadException
        from tactic.ui.widget import ActionButtonWdg
        from tactic.ui.container import DialogWdg

        message = stacktrace.get_value("message")
        trace = stacktrace.get_value("stack_trace")

        widget = DivWdg()
        self.add(widget)

        widget.add_attr("spt_error", "true")
        widget.set_round_corners()
        widget.set_box_shadow()
        widget.add_border()
        widget.add_style("background: #444")
        widget.add_style("color: #CCC")
        widget.add_style("margin: 10px")
        widget.add_style("padding: 10px 20px 30px 20px")
        widget.add_style("max-width: 600px")
 
        pat1 = re.compile('Errno 1|Errno 3|Errno 4')
        pat2 = re.compile('Errno 2')
        pat3 = re.compile('SELECT')
        from .icon_wdg import IconWdg
        h3 = DivWdg()
        h3.add(IconWdg("Error: %s" % message, IconWdg.WARNING, False))
        h3.add("TACTIC has encountered an error.<br/><br/>")
        h3.add("Reported Error: \"%s\"" % message)
        h3.add_style("font-style: bold")
        h3.add_style("font-size: 12px")
        widget.add(HtmlElement.br())
        widget.add(h3)
        # url 


        web = WebContainer.get_web()
        url = web.get_project_url().to_string()

        h3.add('<br/><br/>')


        # TODO: if caught properly, we can tell what errno it is from the
        # OSError or IOError itself
        if pat1.search(message):
            h3.add('TACTIC is trying to manipulate/copy a file but has run into an OS error. Please consult your system administrator to verify that this path is accessible and writeable by TACTIC.')
        elif pat2.search(message):
            h3.add('TACTIC is instructed to manipulate a file or directory that does not exist in the server. Contact your system administrator to address the issue.')
        elif pat3.search(message):
            h3.add('TACTIC has encountered a Search Error. It could be caused by an invalid search parameter entered.  Click on the current link again to refresh it')
        elif isinstance(e, FileUploadException):
            h3.add('File Uploaded is empty or does not exist.')
        elif isinstance(e, ValueError):
            h3.add('Invalid data entered. Click on the current link again to refresh it')


        table = Table()
        widget.add(table)
        table.add_style("color", "#CCC")
        table.add_style("margin: 0px 20px 0px 20px")
        table.add_style("min-width: 200px")

        dialog = DialogWdg(show_pointer=False)
        widget.add(dialog)

        security = WebContainer.get_security()
        if security.is_admin():
            # show stack trace
            button = ActionButtonWdg(title="Stack Trace")
            button.add_style("white-space: nowrap")
            table.add_row()
            table.add_cell("Show the Stack Trace for the Error: ")
            table.add_cell(button)

            dialog.set_as_activator(button)
            dialog.add_title("Stack Trace")

        div = DivWdg()
        dialog.add(div)
        div.add_color("background", "background")
        div.add_style("padding: 20px")
        
        pre = HtmlElement.pre()
        pre.add( "<b>Error: %s</b>\n\n" % message )
        pre.add( trace )
        div.add(pre)


        security = WebContainer.get_security()
        if security.is_admin():
            # show system info
            button = ActionButtonWdg(title="System Info")
            button.add_style("white-space: nowrap")
            table.add_row()
            table.add_cell("Show the System Info: ")
            table.add_cell(button)

            button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var class_name = 'tactic.ui.app.SystemInfoWdg';
                var kwargs = {
                };
                spt.panel.load_popup("System Info", class_name, kwargs);
                '''
            } )


        # ignore
        table.add_row()
        td = table.add_cell()
        div = DivWdg('Ignore and go to default project page:')
        td.add(div)

        button = ActionButtonWdg(title="Ignore >>")
        button.add_style("white-space: nowrap")
        table.add_cell(button)

        # click the top layout and jump to default page
        button.add_behavior({'type': 'click_up',
            'cbjs_action': '''spt.api.Utility.save_widget_setting('top_layout',''); window.location='%s'
            '''%url })



__all__.append("ExceptionMinimalWdg")
class ExceptionMinimalWdg(Widget):

    def __init__(self, e):
        self.exception = e
        super(ExceptionMinimalWdg, self).__init__(self)

    def add_style(self, name, value=None):
        self.top.add_style(name, value)
        

    def init(self):
        widget = DivWdg()
        self.top = widget

        self.add(widget)

        message = str(self.exception)

        widget.add_style("text-align: center")

        widget.add_attr("spt_error", "true")
        widget.set_round_corners()
        widget.set_box_shadow()
        widget.add_border()
        widget.add_color("background", "background3")
        widget.add_color("color", "color3")
        widget.add_style("margin: 10px")
        widget.add_style("padding: 10px 20px 30px 20px")
        widget.add_style("max-width: 400px")
 
        pat1 = re.compile('Errno 1|Errno 3|Errno 4')
        pat2 = re.compile('Errno 2')
        pat3 = re.compile('SELECT')
        from icon_wdg import IconWdg
        h3 = DivWdg()
        h3.add(IconWdg("Error: %s" % message, IconWdg.WARNING, False))
        h3.add("TACTIC has encountered an error.<br/><br/>")
        h3.add("Reported Error: \"%s\"" % message)
        h3.add_style("font-style: bold")
        h3.add_style("font-size: 12px")
        widget.add(HtmlElement.br())
        widget.add(h3)
        # url 


        web = WebContainer.get_web()
        url = '/tactic/admin'

        h3.add('<br/><br/>')


        # show stack trace
        from tactic.ui.widget import ActionButtonWdg


        # ignore
        button_div = DivWdg()
        widget.add(button_div)
        button_div.add_style("width: 75px")
        button_div.add_style("margin: 0 auto")

        button = ActionButtonWdg(title="Go to Admin")
        button_div.add(button)

        # click the top layout and jump to default page
        button.add_event('onclick', '''window.location='%s' '''%url )





class SObjectLevelWdg(Widget):
    # widget that indicates what level you are at
    def get_display(self):
        web = WebContainer.get_web()
        search_type = web.get_form_value("filter|search_type")
        search_id = web.get_form_value("filter|search_id")

        if not search_type:
            return ""
        
        schema = Schema.get()
        if not schema:
            return ""

        # get the parent of the level_type
        level_types = []
        level_types.append(search_type)
        tmp_type = search_type
        while 1:
            parent_type = schema.get_parent_type(tmp_type)
            if not parent_type:
                break
            level_types.append(parent_type)
            tmp_type = parent_type

        level_types.reverse()

        div = DivWdg()
        div.add_style("text-align: left")
        div.add("Levels: ")

        for level_type in level_types:
            div.add(" / ")
            level_type_obj = SearchType.get(level_type)
            title = level_type_obj.get_title()
            div.add(title)

        if search_id:
            sobject = Search.get_by_id(search_type, search_id)
            div.add(" / ")
            div.add(sobject.get_code())

        return div
            


# DEPRECATED
"""
__all__.append('SwfEmbedWdg')
class SwfEmbedWdg(Widget):
    def __init__(self, name=None):
        self.search_type = None
        self.code = None
        self.connector_type = None
        super(SwfEmbedWdg, self).__init__(name)

    def set_search_type(self, search_type):
        self.search_type = search_type

    def set_code(self, code):
        self.code = code
        
    def set_connector_type(self, connector_type):
        self.connector_type = connector_type

    def get_display(self):
       
        # if not overridden, get it from the web
        web = WebContainer.get_web()
        if not self.search_type:
            self.search_type = web.get_form_value("search_type")
        if not self.code:
            self.code = web.get_form_value("code")
        if not self.connector_type:
            self.connector_type = web.get_form_value("connector_type")


        if not self.connector_type:
            self.connector_type = "dependency"
            #self.connector_type = "hierarchy"

        # build the pipeline xml request
        import urllib
        widget_url = web.get_widget_url()
        widget_url.set_option("dynamic_file", "true")
        widget_url.set_option("widget", "pyasm.admin.creator.GetPipelineXml")
        widget_url.set_option("search_type", self.search_type)
        widget_url.set_option("pipeline_code", self.code)
        xml_request = widget_url.to_string()
        xml_request = urllib.quote(xml_request)

        base_url = WebContainer.get_web().get_http_host()
        project_code = Project.get_project_code()
        #base_url += "/tactic/%s/Sthpw/" % project_code
        base_url += "/tactic/default/WidgetServer/?project=%s" % project_code



        login_ticket = WebContainer.get_security().get_ticket_key()

        url = "/context/pipeline_creator.swf?load_xml=%s&login_ticket=%s&pipeline_code=%s&hide_title=true&connector_type=%s&url=%s" % (xml_request, login_ticket, self.code, self.connector_type, base_url)

        id = "pipeline_creator"
        height = "800"

        if WebContainer.get_web().is_IE():
            width = "1000"
        else:
            width = "100%"

        swf = '''
<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0" width="%s" height="%s" id="%s" align="middle">
<param name="movie" value="%s" />
<param name="quality" value="high" />
<embed src="%s" quality="high" wmode='transparent' width="%s" height="%s" name="%s" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" />
</object>
        ''' % (width, height, id, id, url, width, height, id)
        return swf
"""









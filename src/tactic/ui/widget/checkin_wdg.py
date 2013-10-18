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

__all__ = ['CheckinWdg', 'CheckoutWdg',  'CheckinQueueWdg', 'SObjectCheckinHistoryWdg', 'CheckinInfoPanelWdg', 'CheckinSandboxListWdg', 'CheckinSandboxNotExistsWdg', 'FileSelectorWdg']
import re
from pyasm.common import Common, TacticException, Config, Environment, Container
from pyasm.biz import File, Snapshot, Pipeline, Context, Project
from pyasm.search import Search, SObjectFactory, SearchType, SearchKey
from pyasm.command import Command
from pyasm.web import HtmlElement, SpanWdg, DivWdg, Table, WebContainer, Widget, FloatDivWdg, StringWdg, WidgetSettings
from pyasm.widget import ButtonWdg, TextWdg, SelectWdg, TextAreaWdg, HiddenWdg, IconWdg, IconButtonWdg, ProdIconButtonWdg, ThumbWdg, HintWdg, CheckboxWdg, SwapDisplayWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg, ButtonRowWdg, ButtonNewWdg
from tactic.ui.container import Menu, MenuItem, GearMenuWdg, SmartMenu

from swap_display_wdg import SwapDisplayWdg as NewSwapDisplayWdg
from button_wdg import TextBtnWdg, TextBtnSetWdg
from misc_input_wdg import SearchTypeSelectWdg
from upload_wdg import SimpleUploadWdg
from pyasm.prod.biz import ProdSetting

import os



class CheckinWdg(BaseRefreshWdg):

    ARGS_KEYS = {
        'search_key': 'the search key of the object boing checked into',
        'snapshot_code': 'code of the snapshot this widget is working on',
        'process': 'force set the process',
        'context': 'force set the initial context',
        'lock_process': 'true|false',
        'sandbox_dir': 'a virtual sandbox dir',
        'validate_script_path': 'path to the validate publish script',
        'checkin_script_path': 'path to the publish script',

        'checkin_script': 'inline action to publish',
        'create_sandbox_script_path': 'inline action to create the sandbox folder and subfolders',
        'checkin_relative_dir': 'a predefined relative dir to the sandbox to construct a preselected checkin-in path',
        'checkout_script_path': 'path to the check-out script',
        'checkin_options_view': 'custom layout view to define a custom check-in options UI to appear on the left side of the UI',

        'mode': 'sequence|file|dir|add|versionless: determines whether this widget can only check-in sequences',

        'transfer_mode': '',
        'checkin_ui_options': 'a json string of dictionary of ui options like is_current',
        'command': 'when mode == command, this is the command that is called',
        'width': 'width of the widget',
        'show_context': 'true|false: determines whether to show context or not', 
        'show_links': 'true|false: determines whether show the button rows at the top'

        #'show_sub_context': 'true|false: determines whether to show subcontext or not',
    }



    def get_value(my, key):
        web = WebContainer.get_web()
        value = web.get_form_value(key)
        if not value:
            value = my.kwargs.get(key)
        return value



    def init(my):
        my.search_key = my.kwargs.get('search_key')
        my.validate_script_path = my.kwargs.get('validate_script_path')
        my.create_sandbox_script_path = my.kwargs.get('create_sandbox_script_path')
        my.checkin_script_path = my.kwargs.get('checkin_script_path')
        my.sobject = Search.get_by_search_key(my.search_key)
        if not my.sobject:
            raise TacticException('This search_key [%s] is no longer valid. It may have been retired or deleted.' %my.search_key)
        my.search_type = my.sobject.get_base_search_type()
        assert my.sobject

        my.snapshot_code = my.kwargs.get("snapshot_code")
        if my.snapshot_code:
            my.snapshot = Snapshot.get_by_code(my.snapshot_code)
        elif isinstance(my.sobject, Snapshot):
            my.snapshot = my.sobject
            my.snapshot_code = my.snapshot.get_code()
        else:
            my.snapshot = None

        # the one in the UI should take prescedence
        web = WebContainer.get_web()
        my.transfer_mode = web.get_form_value('transfer_mode')
        if not my.transfer_mode:
            my.transfer_mode = my.kwargs.get('transfer_mode')
        # don't set default here as auto detection in js will take care
        # of the rest.  Also note, that the transfer mode can be dictated by
        # the process later one
        """
        if not my.transfer_mode:
            my.transfer_mode = 'upload'
        """


        my.mode = my.kwargs.get('mode')
        my.checkin_command = my.kwargs.get('checkin_command')
        my.show_file_selector = my.kwargs.get('show_file_selector') != 'false'
        my.checkout_script_path = my.kwargs.get('checkout_script_path')
        my.checkin_ui_options = my.kwargs.get('checkin_ui_options')


        my.panel_cls = None

        #my.process = my.kwargs.get("process")
        #my.context = my.kwargs.get("context")
        #my.subcontext = web.get_form_value('subcontext')

        my.process = my.get_value("process")
        my.context = my.get_value("context")
        my.show_context = my.kwargs.get("show_context") in [True, 'true']
        my.subcontext = my.get_value("subcontext")
        my.folder_state = my.get_value("folder_state")
 
        # get the pipeline
        my.pipeline = Pipeline.get_by_sobject(my.sobject)
        my.auto_process = False
        if not my.pipeline:
            my.processes = ['publish']
            my.auto_process = True
        else:
            my.processes = my.pipeline.get_process_names()
            if not my.processes:
                my.processes = ['publish']
                my.auto_process = True
        if not my.process:
            # get the last process
            current_process = WidgetSettings.get_value_by_key("current_process")
            if current_process and current_process in my.processes:
                my.process = current_process
            else:
                my.process = my.processes[0]
        WidgetSettings.set_value_by_key("current_process", my.process)

        if not my.context:
            my.context = my.process

        # if a subcontext is provided, then replace it in the current
        # context
        if my.subcontext:
            parts = my.context.split("/")
            my.context = "%s/%s" % (parts[0], my.subcontext)


        if not my.subcontext and my.context.find("/") != -1:
            parts = my.context.split("/")
            if len(parts) > 1:
                my.subcontext = "/".join(parts[1:])
            else:
                my.subcontext = ""
        else:
            my.subcontext = ""

        """
        print "process: ", my.process
        print "context: ", my.context
        print "subcontext: ", my.subcontext
        """



    def get_title_wdg(my):
        
        title_div = DivWdg()
        #title_div.add_class("maq_search_bar")
        title_div.add_gradient("background", "background", -10)
        title_div.add_style("height: 20px")
        title_div.add_style("padding: 5px")
        title_div.add_style("font-weight: bold")
        title_div.add_style("overflow: hidden")
        title_div.add_style("font-size: 14px")


        button = ActionButtonWdg(title="?", size='s' )
        title_div.add(button)
        button.add_style("float: right")
        button.add_style("margin-top: -5")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.help.set_top();
            spt.help.load_alias("general-checkin|what-are-checkins|general-checkin-wdg");
            '''
        } )



        thumb_div = DivWdg()
        title_div.add(thumb_div)
        thumb_div.add_style("margin-left: -4")
        thumb_div.add_style("margin-top: -4")
        thumb_div.add_style("float: left")
        thumb_div.add_style("margin-right: 10px")

        thumb = ThumbWdg()
        thumb_div.add(thumb)
        thumb.set_sobject(my.sobject)
        thumb.set_icon_size(28)
        thumb.set_option("aspect", "height")

        if not my.sobject.column_exists("name"):
            title = "%s" % my.sobject.get_code() 
        else:
            name = my.sobject.get_value("name", no_exception=True)
            code = "<span style='opacity: 0.5; font-size: 0.8em; font-style: italic'/>( %s )</span>" % my.sobject.get_code()
            title = "%s %s" % (name, code )

        if my.snapshot:
            title = "Append Check-in - %s" % my.sobject.get_code() 
            title_div.add_style('background: #5B7A3A')
        title_div.add(title)
        return title_div



    def get_display(my): 

        my.lock_process = my.kwargs.get("lock_process") == 'true'
        if my.lock_process and not my.process:
            raise TacticException("Cannot lock to a process without specifying a process")

        checkin_relative_dir = my.kwargs.get('checkin_relative_dir')
        # avoid sending None as a string later
        if not checkin_relative_dir:
            checkin_relative_dir = ''

        is_refresh = my.kwargs.get('is_refresh')== 'true'
        default_sandbox_dir = my._get_sandbox_dir(use_default=True)

        title_div = my.get_title_wdg()

        if is_refresh:
            top = Widget()
            title_div.add_behavior({'type' : 'load',
                'default_sandbox_dir' : default_sandbox_dir,
                'cbjs_action': '''
                var top = spt.checkin.top;
                top.setAttribute('spt_default_sandbox_dir', bvr.default_sandbox_dir);
                '''})
        else:
            top = DivWdg()
            top.add_color("background", "background")
            top.add_color("color", "color")
            my.set_as_panel(top)
            width = my.kwargs.get('width')
            if width:
                top.add_style("width", width)
            top.add_class("spt_checkin_top")
            # it is needed or it will be wider than ur screen in sub tabs
            top.add_style("max-width: 1000px")
            top.add_style("width: 100%")

            top.add_attr("spt_sandbox_dir", my._get_sandbox_dir())


            js_div = DivWdg()
            top.add(js_div)
            if not Container.get_dict("JSLibraries", "spt_checkin"):
                js_div.add_behavior( {
                    'type': 'load',
                    'cbjs_action': my.get_onload_js()
                } )


            # initialize the widget
            js_div.add_behavior( {
                'type': 'load',
                'search_key': my.search_key,
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_checkin_top");
                spt.checkin.set_top(top);
                spt.checkin.search_key = bvr.search_key;
                '''
            } )




            # check to see if handoff and repository are accessible from
            # the client
            env = Environment.get()
            handoff_dir = env.get_client_handoff_dir(include_ticket=False, no_exception=True)
            asset_dir = env.get_client_repo_dir()


            # set the transfer mode based on the users environment
            # TODO: maybe should have a separate transfer mode for checkin
            # and checkout?
            js_div.add_behavior( {
            'type': 'load',
            'handoff_dir': handoff_dir,
            'asset_dir': asset_dir,
            'wdg_transfer_mode': my.transfer_mode,
            'cbjs_action': '''
            
            var env = spt.Environment.get();
            if (bvr.wdg_transfer_mode) {
                //each widget can be different, should not set here
                //env.set_transfer_mode(bvr.wdg_transfer_mode);
                return;
            }

            if (env.is_local_url()) {
                env.set_transfer_mode("copy");
            }

            if (!env.get_transfer_mode()) {
                var applet = spt.Applet.get();
                var handoff_state = applet.exists(bvr.handoff_dir);
                var asset_state = applet.exists(bvr.asset_dir);
                if (asset_state == false) {
                    env.set_transfer_mode("web");
                }
                else if (handoff_state == false) {
                    env.set_transfer_mode("web");
                }
                else {
                    env.set_transfer_mode("copy");
                }
            }



            '''
            } )




           

            
            top.add_attr("spt_default_sandbox_dir", default_sandbox_dir)

        
           

        top.add(title_div)

        top.add(my.get_action_wdg() )

        # we are interested in the parent for snapshots
        if isinstance(my.sobject, Snapshot):
            sobject = my.sobject.get_parent()
            my.search_key = SearchKey.get_by_sobject(sobject)
        

        pipeline_code = None
        if my.pipeline:
            pipeline_code = my.pipeline.get_code()

        show_history = my.kwargs.get("show_history")
        show_links = my.kwargs.get("show_links")
        close_on_publish = my.kwargs.get("close_on_publish")


        # put many of the options in a data structure so we don't
        # have to keep passing each down individually
        options = {
            'show_links': show_links,
            'show_history': show_history,
            'close_on_publish': close_on_publish,
            'folder_state': my.folder_state,
        }




        if not my.panel_cls:
            my.panel_cls = 'tactic.ui.widget.CheckinInfoPanelWdg'
       
        panel_kwargs = {
                'search_key':my.search_key,
                'context':my.context,
                'show_context': my.show_context,
                'process':my.process,
                'snapshot_code':my.snapshot_code,
                'pipeline_code' : pipeline_code,
                'transfer_mode':my.transfer_mode,
                'mode':my.mode,
                'checkin_command':my.checkin_command,
                'show_file_selector':my.show_file_selector,
                'checkout_script_path':my.checkout_script_path,
                'checkin_script_path': my.checkin_script_path,
                'validate_script_path': my.validate_script_path,
                'create_sandbox_script_path': my.create_sandbox_script_path,
                'sandbox_dir': my._get_sandbox_dir(),
                'checkin_relative_dir':checkin_relative_dir,
                'checkin_ui_options' : my.checkin_ui_options,
                'show_history': show_history,
                'show_links': show_links,
                'options': options
        }

        info_panel = Common.create_from_class_path(my.panel_cls, {}, panel_kwargs)
        top.add(info_panel)


        return top



  



    def get_action_wdg(my):
        '''displays the checkin buttons'''

        div = DivWdg()
        div.add_style("height: 25px")
        div.add_style("float: left")
        div.add_style("position: absolute")

        if my.snapshot:
            snapshot_div = DivWdg()
            snapshot_div.add("Snapshot Code: %s<br/>" % my.snapshot.get_code() )
            #snapshot_div.add("Process: %s<br/>" % my.snapshot.get_value("process") )
            snapshot_div.add("Context: %s<br/>" % my.snapshot.get_value("context") )
            snapshot_div.add("Version: v%0.3d<br/>" % my.snapshot.get_value("version") )
            snapshot_div.add("Revision: v%0.3d<br/>" % my.snapshot.get_value("revision") )
            snapshot_div.add("Desc: %s<br/>" % my.snapshot.get_value("description") )
            snapshot_div.add_style("padding: 10px")
            snapshot_div.add_style("border: solid %s 1px" % snapshot_div.get_color("border"))
            div.add(snapshot_div)

            my.context = my.snapshot.get_value("context")
            
            # these are not needed.. just for js to run smoothly
            hidden = HiddenWdg("process")
            hidden.add_class("spt_checkin_process")
            div.add(hidden)
            hidden = HiddenWdg("context", my.context)
            hidden.add_class("spt_checkin_context")
            div.add(hidden)
            hidden = HiddenWdg("subcontext")
            hidden.add_class("spt_checkin_subcontext")
            div.add(hidden)

            """
            div.add("Action: ")

            select = SelectWdg("action")
            select.set_option("values", "create_empty|add_files")
            select.set_option("labels", "Create Empty Snapshot|Add Selected Files")
            """


        else:

            div.add_style("margin: 15px 12px 12px 12px")
            # width prevents it from jumping in IE during refresh
            div.add_style("min-width: 700px")
            process_div = FloatDivWdg('Process: &nbsp;')
            process_div.add_style("font-weight: bold")
            process_div.add_style("font-size: 14px")
            process_div.add_style("padding-top: 5px")
          
            if my.processes == ['publish'] and my.auto_process == True:
                # in case a single pipeline with one process called "publish" is defined
                # we should not hide it
                process_div.add_style("display: none")


            if my.lock_process:
                div.add(process_div)

                # show the full context
                locked_div = FloatDivWdg(my.context)


                div.add(locked_div)
                locked_div.add_style('margin-left: 8px')
                locked_div.add_styles('font-weight: bold; font-size: 1.1em')
                locked_div.add_style("margin-top: 6px")
                hidden = HiddenWdg("process", my.process)
                process_div.add(hidden)
                hidden.add_class("spt_checkin_process")

                context_div = ContextPanelWdg(process=my.process, search_type=my.search_type, context= my.context)
                my.context = context_div.get_context()

                div.add(context_div)
            else:
                div.add(process_div)

                
                if my.subcontext:
                    show_sub_context = True
                else:
                    show_sub_context = my.kwargs.get("show_sub_context") in [True, 'true']

                # create a process selector
                process_select = SelectWdg("process")
                process_div.add(process_select)
                process_select.add_class("spt_checkin_process")
                process_select.set_option("values", my.processes)
                show_links = my.kwargs.get("show_links") not in [False, 'false']
                if show_links:
                    process_select.add_behavior( {
                    'type': 'change',
                    'cbjs_action': '''

                    spt.app_busy.show("Switching Process ...");

                    var top = bvr.src_el.getParent(".spt_checkin_top");
                    var process = top.getElement(".spt_checkin_process").value;
                    top.setAttribute("spt_process", process);

                    var info_el = top.getElement(".spt_checkin_info");
                    // Is this even valid anymore?
                    var context_el = top.getElement(".spt_checkin_context");
                    spt.panel.refresh(context_el, {process : process, context: process});

                    // reset the folder_state
                    folder_state_el = top.getElement(".spt_folder_state");
                    if (folder_state_el) {
                        folder_state_el.value = "";
                    }


                    top.setAttribute("spt_sandbox_override", "false");
                    spt.panel.refresh(top);
                    spt.app_busy.hide();
                    '''
                    } )
                else:

                    process_select.add_behavior( {
                    'type': 'change',
                    'cbjs_action': '''
                        spt.api.Utility.save_widget_setting('current_process', bvr.src_el.value);
                    '''
                    } )
                    
                
            
                if my.process:
                    process_select.set_value(my.process)
                else:
                    if not my.processes:
                        my.process = 'publish'
                    else:
                        my.process = my.processes[0]


                #TODO: do not apply but some mode rely on it. clean up later
                context_div = DivWdg()
                context_wdg = ContextPanelWdg(process=my.process, search_type=my.search_type, context=my.context, show_context=my.show_context, show_sub_context=show_sub_context)
                context_div.add(context_wdg)
                context_div.add_style("padding-top: 5px")

                my.context = context_wdg.get_context()

                if my.show_context:
                    context_title_div = FloatDivWdg('Context: &nbsp;')
                    context_title_div.add_style("margin: 5px 0 0 0")
                    context_title_div.add_style("font-weight: bold")
                    context_title_div.add_style("font-size: 14px")
                    # since it is now on the right, have to line break
                    div.add(HtmlElement.br(2))
                    div.add(context_title_div)
                    div.add_style("height: 65px")

                div.add(context_div)

            div.add_style("margin-bottom: 20px")


        return div




    # FIXME: this method is defined twice in this file!!!!!
    def _get_sandbox_dir(my, use_default=False):
        '''get the sandbox directory'''

        if not use_default and my.kwargs.get("sandbox_override") == "true":
            sandbox_dir = my.kwargs.get("sandbox_dir")
            if sandbox_dir:
                return sandbox_dir

        cb = CheckboxWdg('link_sandbox', label='link')
        cb.set_persistence()
        if not cb.is_checked():
            # find current snapshot for this:
            snapshot = Snapshot.get_current_by_sobject(my.sobject, context=my.context)
            if snapshot:
                sandbox_dir = snapshot.get_sandbox_dir(file_type='main')
            else:
                type ='main'
                virtual_snapshot = Snapshot.create_new()
                virtual_snapshot_xml = '<snapshot><file type=\'%s\'/></snapshot>' %(type)
                virtual_snapshot.set_value("snapshot", virtual_snapshot_xml)
                virtual_snapshot.set_value("process", my.process)

                # for purposes of the sandbox folder for the checkin widget,
                # the context is the process
                virtual_snapshot.set_value("context", my.process)
                virtual_snapshot.set_sobject(my.sobject)
                sandbox_dir = virtual_snapshot.get_sandbox_dir(file_type='main')
        else:
            sandbox_dir = my.kwargs.get('sandbox_dir')
        return sandbox_dir



    def get_onload_js(cls):

        return '''

if (spt.checkin) {
    return;
}

spt.Environment.get().add_library("spt_checkin");

spt.checkin = {};

spt.checkin.top = null;

spt.checkin.set_top = function(top) {
    if (!top.hasClass("spt_checkin_top")) {
        top = bvr.src_el.getParent(".spt_checkin_top");
    }
    spt.checkin.top = top;
}



spt.checkin.open = function(search_key, process, options) {
    var kwargs = {};
    kwargs['search_key'] = search_key;
    kwargs['process'] = process;

    if (typeof(options) == 'undefined') {
        options = {};
    }
    kwargs['context'] = options['context'];

    var class_name = 'tactic.ui.widget.CheckinWdg';
    spt.panel.load_popup("Check-in Tool", class_name, kwargs);
}



spt.checkin.refresh = function() {
    spt.panel.refresh(spt.checkin.top);
}




spt.checkin.switch_sandbox = function(dirname) {

    dirname = dirname.replace(/\\\\/g, "/");
   
    var top = spt.checkin.top;

    var applet = spt.Applet.get();
    top.setAttribute("spt_sandbox_dir", dirname);
    top.setAttribute("spt_sandbox_override", "true");

    var values = {sandbox_dir: dirname};
    spt.panel.refresh(top, values);
}


// if is_sandbox is false, it does direct browse for files or dir for check-in
spt.checkin.browse_folder = function(current_dir, is_sandbox, refresh, select_dir) {
    var applet = spt.Applet.get();
    var select_dir = true;
    var file_paths = applet.open_file_browser(current_dir, select_dir);

    if (file_paths.length == 0) {
        return;
    }

    var values = {};
    var top = spt.checkin.top;

    if (is_sandbox == null)
        is_sandbox = true;


    // take the first one make sure it is a directory
    var dir = file_paths[0];
    if (is_sandbox) {
        if (applet.is_dir(dir) && file_paths.length==1) {
        dir = dir.replace(/\\\\/g, "/");

        top.setAttribute("spt_sandbox_dir", dir);
        top.setAttribute("spt_sandbox_override", "true");
        }
        else {
             spt.alert("You may only select a single working folder(sandbox).");
             return;
        }


    }
    else {
        var file_info_list = [];
        var fixed_file_paths = [];
        for (var k=0; k<file_paths.length; k++) {
            var file_type = 'file';
            if (applet.is_dir(file_paths[k])) {
                
                // add a slash to indicate it's a dir for DirlistWdg
                file_paths[k] = file_paths[k] + '/';
                file_type = 'dir';
            }
            
            file_info_list.push({file_type: file_type});
            fixed_file_paths.push(file_paths[k].replace(/\\\\/g, "/"));
        }
        
        // file_info is not used right now
        values = {file_paths: fixed_file_paths, file_info: file_info_list}
    }
    if (refresh != false) {
        spt.panel.refresh(top, values);
    }
    return values

}




spt.checkin.get_selected_paths = function() {

    var top = spt.checkin.top;
    var el = top.getElement(".spt_file_selector");

    var file_paths = [];
    var items = el.getElements(".spt_dir_list_item");
    for (var i = 0; i < items.length; i++) {
        var item = items[i];
        if (item.is_selected != true)
            continue;

        var file_path = item.getAttribute("spt_path");
        file_paths.push(file_path);
    }

    return file_paths;
}




spt.checkin.get_selected_subcontexts = function(cls) {
    var top = spt.checkin.top;
    var el = top.getElement(".spt_file_selector");

    if (!cls)
        cls = 'spt_subcontext';

    var subcontexts = [];
    var items = el.getElements(".spt_dir_list_item");
    for (var i = 0; i < items.length; i++) {
        var item = items[i];
        if (item.is_selected != true)
            continue;

        var subcontext = item.getAttribute(cls);
        subcontexts.push(subcontext);
    }

    return subcontexts;
}

spt.checkin.get_selected_contexts = function() {
    return spt.checkin.get_selected_subcontexts('spt_context');
}

spt.checkin.get_checkin_data = function() {

    var data = {};

    //var top = bvr.src_el.getParent("."+bvr.top);
    //var search_key = bvr.search_key;

    var top = spt.checkin.top;
    var search_key = spt.checkin.search_key;
    data['search_key'] = search_key;

    var sandbox_dir = top.getAttribute("spt_sandbox_dir");
    data['sandbox_dir'] = sandbox_dir;


    var file_paths = spt.checkin.get_selected_paths();

    var info = top.getElement('.spt_checkin_info')
    var is_context = info.getAttribute('context_mode') == 'true';
    if (is_context) {
        var contexts = spt.checkin.get_selected_contexts();
        data['contexts'] = contexts;
    } else {
        var subcontexts = spt.checkin.get_selected_subcontexts();
        data['subcontexts'] = subcontexts;
    }

    data['file_paths'] = file_paths;


    var range = '';
    var type = top.getElement(".spt_checkin_type").value;
    var is_current_el = top.getElement(".spt_is_current");
    is_current = is_current_el.checked || is_current_el.value=='true';

    var process = top.getElement(".spt_checkin_process").value;
    var context = top.getElement(".spt_checkin_context").value;
    if (context == '') {
        context = process;
    }

    data['process'] = process;
    data['context'] = context;

    var description = top.getElement(".spt_checkin_description").value;
    var file_type = 'main';
    if (bvr.snapshot_code){
        var file_type_el = top.getElement(".spt_checkin_file_type");
        if (file_type_el) {file_type = file_type_el.value;}
    }
    var transfer_mode = bvr.transfer_mode;
    if (!transfer_mode)
        transfer_mode = spt.Environment.get().get_transfer_mode();

    data['file_type'] = file_type;
    data['transfer_mode'] = transfer_mode;

    return data;

}


/* This transfer the paths to a place where the serve can check it in. */
spt.checkin.transfer_path = function(file_path, transfer_mode, options) {

    var server = TacticServerStub.get();
    var ticket = server.get_transaction_ticket();
    var applet = spt.Applet.get();

    // if the transfer mode is custom, then run a custom script to transfer
    // the files using whatever means desired.
    if (transfer_mode == 'custom') {
        var script_path = options['script_path'];
        var script;
        if ( script_path != null) {
            script = spt.CustomProject.get_script_by_path(script_path);
            options.script = script;
        }
        else {
            script = options['script'];
        }
        // add some data to options
        options.file_path = file_path;
        spt.CustomProject.exec_custom_script({}, options);
    }
    // if the transfer mode is upload, then handle the upload mode
    else if (transfer_mode == 'upload' || transfer_mode =='web') {
        var is_dir = applet.is_dir(file_path);

        spt.app_busy.show("Uploading", file_path);
        spt.notify.show_message("Uploading: " + file_path);
        if (is_dir) {
            server.upload_directory(file_path, ticket);
        }
        else {
            server.upload_file(file_path, ticket);
        }
        spt.app_busy.hide();
        spt.notify.hide();
    }
    else if (transfer_mode == 'copy') {
        var handoff_dir = server.get_handoff_dir();
        applet.makedirs(handoff_dir);
        var parts = file_path.split("/");
        var file_name = parts[parts.length-1];
        var handoff_path = handoff_dir + "/" + file_name;
        applet.copy_file(file_path, handoff_path);
        spt.notify.show_message("Copied [" + file_path + "] to handoff folder.");
    }
    else {
        throw("Transfer mode ["+transfer_mode+"] is not supported");
    }
}


spt.checkin.transfer_paths = function(file_paths, transfer_mode, options) {
    for (var i = 0; i < file_paths.length; i++) {
        var file_path = file_paths[i];
        spt.checkin.transfer_path(file_path, transfer_mode, options);
    }
}


spt.checkin.transfer_selected_paths = function(transfer_mode, options) {
    var paths = spt.checkin.get_selected_paths();
    spt.checkin.transfer_paths(paths, transfer_mode, options);
    return paths;
}



spt.checkin.checkin_path = function(search_key, file_path, process, options) {

    // This function assumes that the files, by default, are already at the
    // server

    var applet = spt.Applet.get();
    var server = TacticServerStub.get();

    // get the last context
    var ticket = server.get_transaction_ticket();

    if (typeof(options) == 'undefined') {
        options = {};
    }



    var transfer_mode = options['transfer_mode'];
    if (transfer_mode == null) {
        transfer_mode = 'uploaded';
        //transfer_mode = 'local';
        transfer_mode = 'copy';
    }

    var description = options['description'];
    if (description == null) {
        description = "";
    }

    var is_current = options['is_current'];
    if (is_current == null) {
        is_current = true;
    }


    var subcontext = options['subcontext'];
    var use_file_name = false;
    var checkin_type = 'strict';
    if (subcontext == "(auto)") {
        subcontext = null;
        use_file_name = true;
        checkin_type = 'auto';
    }
    else if (subcontext == null) {
        subcontext = null;
        use_file_name = true;
        checkin_type = null;
    }

    var snapshot = null;

    // NOT supported
    //var checkin_command = 'pyasm.checkin.FileCheckin';

    // handle a directory
    if (applet.is_dir(file_path) == true) {

        if (checkin_type == 'auto') {
            // get all the files in the directory
            var sub_file_paths = applet.list_recursive_dir(file_path);
            for (var j = 0; j < sub_file_paths.length; j++) {
                // recursively checkin in this file
                var file_path = sub_file_paths[j];
                spt.checkin.checkin_path(search_key, file_path, process, options);
            }
        }
        else {
            snapshot = server.directory_checkin(search_key, this_context, file_path, {description: description, mode: transfer_mode, is_current: is_current, context_index_padding: padding, checkin_type: checkin_type});
        }

    }
    else {
        // build the context
        var this_context;
        if (subcontext) {
            this_context = process + "/" + subcontext;
        }
        else if (use_file_name) {
            file_path = file_path.replace(/\\\\/g, "/");
            var this_sub_context = file_path.replace(options.sandbox_dir+"/", "");
            if (this_sub_context == file_path) {
                // nothing was found so just use the filename
                var parts = file_path.split(/[\\/\\\\]/);
                var file_name = parts[parts.length-1];
                this_context = process + "/" + file_name;
            }
            else {
                this_context = process + "/" + this_sub_context;
            }
        }
        else {
            this_context = process;
        }

        // FIXME: this is not really used, but kept here is case it is revived
        // This sets the padding level for auto_process of context with
        // numbers: ie: design0023
        var padding = 0;

        spt.app_busy.show("Checking in ...", file_path)
        if (transfer_mode == 'preallocate') {
            // if the mode is preallocate, then a snapshot code must be given
            var snapshot_code = options.get['snapshot_code'];
            snapshot = server.add_file(snapshot_code, file_path, { mode: "preallocate"});
        }
        else {

            snapshot = server.simple_checkin(search_key, this_context, file_path, {description: description, mode: transfer_mode, is_current: is_current, context_index_padding: padding, checkin_type: checkin_type});
        }

        // disable this for now
        //checkin_data[file_path] = snapshot;

    }

    return snapshot;
}

        '''
    get_onload_js = classmethod(get_onload_js)



class CheckoutWdg(CheckinWdg):
    
    def get_args_keys(my):
        return {
        'search_key': 'the search key of the object boing checked into',
        'process': 'force set the process',
        'context': 'set the initial context',
        'lock_process': 'true|false',
        'checkout_script_path': 'path to the check-out script',
        'mode': 'TBA',
        'transfer_mode': '',
        }

    def init(my):
        super(CheckoutWdg, my).init()
        my.show_file_selector = 'false'
   
    def get_title_wdg(my):
        
        title_div = DivWdg()
        title_div.add_class("maq_search_bar")
        
        title = "Check-out [%s]" % my.sobject.get_code() 
        if my.snapshot:
            title = "Check-out snapshot [%s]" % my.sobject.get_code() 
            title_div.add_style('background: #5B7A3A')
        title_div.add(title)
        return title_div






class CheckinInfoPanelWdg(BaseRefreshWdg):
    '''stores the 3 components for CheckinWdg'''

    def init(my):
        my.search_key = my.kwargs.get('search_key')
        my.sobject = Search.get_by_search_key(my.search_key)
        my.search_type = my.sobject.get_base_search_type()
        assert my.sobject

        my.snapshot_code = my.kwargs.get("snapshot_code")
        if my.snapshot_code:
            my.snapshot = Snapshot.get_by_code(my.snapshot_code)
        elif isinstance(my.sobject, Snapshot):
            my.snapshot = my.sobject
        else:
            my.snapshot = None


        my.pipeline_code = my.kwargs.get('pipeline_code')
        my.pipeline = Pipeline.get_by_code(my.pipeline_code)

        my.show_links = my.kwargs.get('show_links')
        my.options = my.kwargs.get('options')

        my.warning_msg = []



        
        # these may be changed by the user in the UI, which take prescedence
        web = WebContainer.get_web()
        my.process = web.get_form_value('process')
        if not my.process:
            my.process = my.kwargs.get('process')

        my.context = web.get_form_value('context')
        subcontext = web.get_form_value('subcontext')
        

        if not my.context:
            my.context = my.kwargs.get('context')
        elif subcontext:
            my.context = '%s/%s'%(my.context, subcontext)

        my.show_context = my.kwargs.get("show_context") in [True, 'true']
        
        # get all of the process sobjects for this pipeline
        if my.pipeline:
            pipeline_code = my.pipeline.get_value("code")

            pipe_proj_code = my.pipeline.get_value('project_code')
            #search = Search("config/process")
            #search.add_filter("pipeline_code", pipeline_code)
            #my.process_sobjs = search.get_sobjects()
            search = Search("config/process", project_code=pipe_proj_code)
            search.add_filter("pipeline_code", pipeline_code)
            search.add_filter("process", my.process)
            my.process_sobj = search.get_sobject()

        else:
            #my.process_sobjs = []
            my.process_sobj = None


        my.transfer_mode = my.kwargs.get('transfer_mode')

        # get the repo type
        if my.process_sobj:
            my.repo_type = my.process_sobj.get_value("repo_type", no_exception=True)
            if not my.transfer_mode:
                my.transfer_mode = my.process_sobj.get_value("transfer_mode", no_exception=True)
        else:
            my.repo_type = None

        if not my.repo_type:
            my.repo_type = Config.get_value("checkin", "repo_type")
        if not my.repo_type:
            my.repo_type = 'tactic'


        my.create_sandbox_script_path = my.kwargs.get("create_sandbox_script_path")
        if not my.create_sandbox_script_path and my.process_sobj:
            my.create_sandbox_script_path = my.process_sobj.get_value("sandbox_create_script_path", no_exception=True)


        my.mode = my.kwargs.get("mode")
        my.context_options = []
        my.subcontext_options = []
        
        if not my.mode and my.process_sobj:
            my.mode = my.process_sobj.get_value("checkin_mode", no_exception=True)

        if my.process_sobj:
            # we are not passing in this thru kwargs
            my.context_options = my.process_sobj.get_value("context_options", no_exception=True)
            my.context_options = my.context_options.strip()
            
            if re.search(r'\(auto\)|\(main\)|\(text\)', my.context_options):
                my.warning_msg.append('context_options do not use (main), (auto) or (text). They should be set in subcontext_options.')
            if my.context_options:
                my.context_options = my.context_options.split("|")
            else:
                my.context_options = []
            
            
            # get the subcontext_options
            my.subcontext_options = my.kwargs.get("subcontext_options")

            if not my.subcontext_options:
                my.subcontext_options = my.process_sobj.get_value("subcontext_options", no_exception=True)

            if re.search(r'\(text\).+|.+\(text\)', my.subcontext_options):
                my.warning_msg.append('(text) cannot be mixed with others options in subcontext_options.')
            elif re.search(r'{main}|{text}|{auto}', my.subcontext_options):
                my.warning_msg.append('Use ( ) instead of { } for (main), (auto), or (text) in subcontext_options.')
            my.subcontext_options = my.subcontext_options.strip()
            if my.subcontext_options:
                my.subcontext_options = my.subcontext_options.split("|")
            else:
                my.subcontext_options = []

      


        my.checkin_command = my.kwargs.get("checkin_command")
        my.show_file_selector = my.kwargs.get('show_file_selector') not in ['false', False]
        my.checkout_script_path = my.kwargs.get('checkout_script_path')

        # get the sandbox directory
        my.sandbox_dir = my._get_sandbox_dir()

        my.checkin_relative_dir = my.kwargs.get('checkin_relative_dir')
        my.checkin_ui_options = my.kwargs.get('checkin_ui_options')

        if my.checkin_ui_options and isinstance(my.checkin_ui_options, basestring):
            # avoid using jsonloads for simple dict,
            # since it requires replacing ' with ''

            #my.checkin_ui_options = my.checkin_ui_options.replace("'", '"')
            #my.checkin_ui_options = jsonloads(my.checkin_ui_options)
            my.checkin_ui_options = eval(my.checkin_ui_options)



    def _get_sandbox_dir(my):
        '''get sandbox dir thru the currently selected process instead of the passed-in one
            if necessary'''

        sandbox_dir = my.kwargs.get("sandbox_dir")
        if sandbox_dir:
            return sandbox_dir

        cb = CheckboxWdg('link_sandbox', label='link')
        cb.set_persistence()
        if not cb.is_checked():
            # find current snapshot for this:
            snapshot = Snapshot.get_current_by_sobject(my.sobject, context= my.context)
            if snapshot:
                sandbox_dir = snapshot.get_sandbox_dir(file_type='main')
            else:
                type ='main'
                virtual_snapshot = Snapshot.create_new()
                virtual_snapshot_xml = '<snapshot><file type=\'%s\'/></snapshot>' %(type)
                virtual_snapshot.set_value("snapshot", virtual_snapshot_xml)
                virtual_snapshot.set_value("process", my.process)

                # for purposes of the sandbox folder for the checkin widget,
                # the context is the process
                virtual_snapshot.set_value("context", my.process)
                virtual_snapshot.set_sobject(my.sobject)
                sandbox_dir = virtual_snapshot.get_sandbox_dir(file_type='main')
        else:
            sandbox_dir = my.kwargs.get('sandbox_dir')
        return sandbox_dir

    def get_display(my):
        top = DivWdg()
        my.set_as_panel(top)
        top.add_class("spt_checkin_info")
        if my.context_options:
            top.add_attr('context_mode','true')


        from tactic.ui.container import ResizableTableWdg
        #table = ResizableTableWdg()
        table = Table()
        table.add_color("color", "color")
        top.add(table)
        table.add_border()
     
        table.add_row()
        #table.add_style("margin: 8px 5px 5px 5px")
        table.add_style("width: 100%")
        if my.warning_msg:
            top.add_behavior( {'type': 'load',
                        'msg': "Warning: %s" %'<br>'.join(my.warning_msg),
                        'cbjs_action' : 'spt.alert(bvr.msg, {type: "html"})'})


        file_path = ''
        if my.checkin_relative_dir:
            file_path = '%s/%s' %(my.sandbox_dir, my.checkin_relative_dir)



        td = table.add_cell()
        # control the max width for the publish desc area
        td.add_style('max-width: 250px')
        td.add_border()
        publish_wdg = my.get_publish_wdg(my.search_key, my.snapshot, my.process, my.pipeline, my.transfer_mode)  
        td.add( publish_wdg )
        td.add_color("background", "background3")
        td.add_style("vertical-align: top")


        # show the widget which allows you to select a file or 
        # directory to checkin
        td = table.add_cell()

        td.add_style("vertical-align: top")
        # control the min width for the sandbox area
        td.add_style('min-width: 500px')
        td.add_border()

        from tactic.ui.container import TabWdg
        tab = TabWdg(show_add=False, tab_offset="5px", selected="Sandbox", show_remove=False)
        tab.add_style("margin: 5px -2px -2px -2px")
        td.add(tab)


        if my.show_file_selector:
            kwargs = {
                'search_key': my.search_key,
                'process': my.process,
                'pipeline_code': my.pipeline_code,
                'context': my.context,
                'mode': my.mode,
                'file_path': file_path,
                'sandbox_dir': my.sandbox_dir,
                'context_options': my.context_options,
                'subcontext_options': my.subcontext_options,
                'create_sandbox_script_path': my.create_sandbox_script_path,
                'options': my.options,
                'show_links': my.show_links
                
            }


            if my.repo_type == 'perforce':
                from tactic.ui.checkin import ScmFileSelectorWdg
                selector = ScmFileSelectorWdg(**kwargs)
            else:
                selector = FileSelectorWdg(**kwargs)

            tab.add(selector)
            selector.set_name("Sandbox")


        show_history = my.kwargs.get("show_history")
        if show_history not in ['false', False]:
            new_context = my.context 
            if re.match(r'.*/.*\d{3}', my.context):
                new_context = my.context.split("/")[0]
        
            history = SObjectCheckinHistoryWdg(search_key=my.search_key, history_context=new_context)
            tab.add(history)
            history.set_name("History")


        """
        show_history = my.kwargs.get("show_history")
        if show_history not in ['false', False]:
            history = CheckinHistoryWdg(search_key=my.search_key, context=my.context, sandbox_dir=my.sandbox_dir)

            table.add_row()
            td = table.add_cell( history )
            td.add_attr("colspan", "3")
            td.add_border()
        """

        return top



    def get_publish_options_wdg(my):


        options_div = DivWdg()
        #options_div.add_style("padding-left: 15px")
        options_div.add_color("background", "background3", -5)
        options_div.add_styles('padding: 4px; margin-top: 4px')

        # display the options like transfer mode, is_current
        transfer_div = DivWdg()
        transfer_div.add_style('margin-bottom: 6px')
        transfer_div.add_behavior( {
            'type': 'load',
            'transfer_mode': my.transfer_mode,
            'cbjs_action': '''
            var env = spt.Environment.get();
            var transfer_mode = bvr.transfer_mode;
            if (!transfer_mode)
                transfer_mode = env.get_transfer_mode();
            bvr.src_el.innerHTML = "Transfer mode: " + transfer_mode;
            '''
        } )
        #transfer_div.add_style("font-weight: bold")
        
        # COMMENT this out until it is needed
        """    
        hidden = HiddenWdg('transfer_mode', my.transfer_mode)
        hidden.add_class("spt_checkin_transfer_mode")
        transfer_div.add(hidden)
        transfer_div.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            var env = spt.Environment.get();
            var transfer_mode = env.get_transfer_mode();
            bvr.src_el.value = transfer_mode;
            '''
        } )
 

        """
        #transfer_div.add_style("margin: 10px 0 10px 0")
        options_div.add(transfer_div)

        






        current_cb = CheckboxWdg('current_snapshot', label='Is Current')
        # check is_current
        is_current = None
        if my.checkin_ui_options:
           is_current =  my.checkin_ui_options.get('is_current')
        if is_current != None:
            if is_current=='false':
                current_cb = HiddenWdg('current_snapshot', 'false' )
                span = SpanWdg(IconWdg(icon=IconWdg.INVALID))
                span.add('Is Current?')
                span.add_style('padding-left: 8px')
                options_div.add(span)

            elif is_current=='true':
                current_cb = HiddenWdg('current_snapshot', 'true')
                span = SpanWdg(IconWdg(icon=IconWdg.CHECK))
                span.add_style('padding-left: 8px')
                span.add('Is Current?')
                options_div.add(span)
            elif is_current=='optional':
                pass
            else:
                current_cb.set_default_checked()
        else:
            current_cb.set_default_checked()

            #span.add_class('disabled')

        current_cb.add_class("spt_is_current")
        options_div.add(current_cb)


        options_div.add("<br/>"*2)


        # add the publish mode
        checkin_wdg = DivWdg()
        options_div.add(checkin_wdg)
        checkin_wdg.add("File type: ")
 
        select = SelectWdg("checkin_type")
        checkin_wdg.add(select)
        select.add_class("spt_checkin_type")
        select.set_persistence()
        select.add_style("margin: 4px")
        file_type = None
        hint = None
        mode = my.mode
    

      
        if mode == 'sequence':
            select.set_option("labels", "A Sequence")
            select.set_option("values", "group_checkin")
        elif mode == 'file':
            select.set_option("labels", "A File")
            select.set_option("values", "file_checkin")
        elif mode in ['directory','dir']:
            select.set_option("labels", "A Directory")
            select.set_option("values", "dir_checkin")

        elif mode == 'add':
            select.set_option("labels", "Add Directory|Add File")
            select.set_option("values", "add_dir|add_file")
            file_type = SpanWdg('file type: ')
            file_type_txt = TextWdg('file_type')
            file_type_txt.add_class('spt_checkin_file_type')
            file_type_txt.set_value('main')
            file_type.add(file_type_txt)
            hint = HintWdg('You may get an error if your naming convention outputs the same name for this appending check-in. Suggestion: Try to include {file_type} in your naming.')



        elif mode == 'multi_file':
            select.set_option("labels", "Multiple Individual Files")
            select.set_option("values", "multi_file_checkin")


        else:
            select.set_option("labels", "A File|A Sequence|A Directory|Multiple Individual Files")
            select.set_option("values", "file_checkin|group_checkin|dir_checkin|multi_file_checkin")

            if my.pipeline:
                my.process_obj = my.pipeline.get_process(my.process)
                if my.process_obj:
                    attributes = my.process_obj.get_attributes()
                    if attributes.get("mode") == 'directory':
                        select.set_value("dir_checkin")

            web = WebContainer.get_web()
            values = web.get_form_values('file_info')

            # basic cases
            if len(values) == 1 and values[0].get('file_type') == 'dir':
                select.set_value("dir_checkin")
            elif len(values) == 1 and values[0].get('file_type') == 'file':
                select.set_value("file_checkin")
            elif len(values) > 1:
                select.set_value("multi_file_checkin")

            paths = my.kwargs.get('paths')
            select.add_behavior({'type': 'change', 'cbjs_action': select.get_save_script()})

        if file_type:
            checkin_wdg.add(file_type)
            checkin_wdg.add(hint)



        if my.validate_script_path:
            validate_div = DivWdg('Validate: %s'%my.validate_script_path)
            validate_div.add_style("margin: 2px")
            options_div.add(validate_div)




        toggle = SwapDisplayWdg.get_triangle_wdg()
        options_title = SpanWdg('Check-in Options')
        swap_title = SwapDisplayWdg.create_swap_title(options_title, toggle, options_div)
        widget = Widget()
        
        widget.add(toggle)
        widget.add(options_title)
        widget.add(swap_title)
        widget.add(options_div)
        return widget


    def get_publish_wdg(my, search_key, snapshot, process, pipeline, transfer_mode):

        if my.repo_type == 'perforce':
            from tactic.ui.checkin import ScmPublishWdg
            top = ScmPublishWdg(sobject=my.sobject)
            return top


        top = DivWdg()
        top.add_class("spt_checkin_publish")
        top.add_style("padding: 10px")
        show_context = my.kwargs.get("show_context") in [True, 'true']
        if show_context:
            margin_top = '60px'
        else:
            margin_top = '40px'

        top.add_style("margin-top", margin_top)
        top.add_style("position: relative")


        top.add("Publish Description<br/>")
        text = TextAreaWdg("description")
        # this needs to be set or it will stick out to the right
        text.add_style("width: 220px")
        text.add_class("spt_checkin_description")
        top.add(text)


        # handle deliveries to other processes
        if pipeline:
            output_processes = pipeline.get_output_processes(process)
        else:
            output_processes = None
        if output_processes:

            """
            for p in output_processes:
                pipeline_code = p.parent_pipeline_code
                if pipeline_code:
                    pipeline = Pipeline.get_by_code(pipeline_code)
                    search_type = pipeline.get_value("search_type")

                    sobject = Search.get_by_search_key(search_key)
                    related = Search.eval("@SOBJECT(%s)" % search_type, sobject)
            """


            process_names = [x.get_name() for x in output_processes]

            delivery_div = DivWdg()

            checkbox = CheckboxWdg("deliver")
            delivery_div.add(checkbox)
            delivery_div.add_style("padding-top: 15px")
            delivery_div.add("Deliver to: ")
            top.add(delivery_div)

            select = SelectWdg("deliver_process")
            delivery_div.add(select)
            select.set_option("values", process_names)
            select.set_value(process_names[0])


        # add as a note
        note_div = DivWdg()
        top.add(note_div)
        note_div.add_style("padding-top: 15px")
        note_div.add_class("spt_add_note")
        checkbox = CheckboxWdg("add_note")
        checkbox.add_class("spt_checkin_add_note")
        note_div.add(checkbox)
        note_div.add("Also add a note")




        web = WebContainer.get_web()
        browser = web.get_browser()
        if browser in ['Qt']:
            checkbox.add_style("margin-top: -4px")
            checkbox.add_style("margin-right: 3px")
            note_div.add_style("margin-top: 3px")

        top.add("<br/><br/>")

        # Put in some custom UI
        options_div = DivWdg()
        options_div.add_class("spt_custom_options_top")

        try:
            custom_options_view = my.kwargs.get("checkin_options_view")
            if not custom_options_view and my.process_sobj:
                custom_options_view = my.process_sobj.get_value("checkin_options_view", no_exception=True)

            if custom_options_view:
                from tactic.ui.panel import CustomLayoutWdg
                custom_layout = CustomLayoutWdg(view=custom_options_view)
                options_div.add(custom_layout.get_buffer_display())
                top.add(options_div)
        except Exception, e:
            from pyasm.widget import ExceptionWdg
            options_div.add( ExceptionWdg(e) )
            #options_div.add("Error")
            top.add(options_div)




        my.validate_script_path = my.get_checkin_script_path(key='validate_script_path')
        if not my.validate_script_path and my.process_sobj:
            my.validate_script_path = my.process_sobj.get_value("checkin_validate_script_path", no_exception=True)



       
        script = my.kwargs.get("checkin_script")
        if not script:
            script_path = my.get_checkin_script_path()
            script = None
        else:
            script_path = None

       
        snapshot_code = ''
        if snapshot:
            snapshot_code = snapshot.get_code()

        """
        # TEST: using api
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''
var server = TacticServerStub.get();
server.start( {description: "Checking in files"} );
try {
    var paths = spt.checkin.transfer_selected_paths("upload");

    var options = spt.checkin.get_checkin_data();

    var process = options.process;
    var search_key = options.search_key;

    for (var i = 0; i < paths.length; i++) {
        options.subcontext = options.subcontexts[i];
        spt.checkin.checkin_path(search_key, paths[i], process, options);
    }

    server.finish( {description: "Checking in files: " + paths } );
}
catch(e) {
    spt.alert(e);
    server.abort();
}
            '''
        }


        # Dropbox check-in
        behavior = {
            'type': 'click_up',
            'cbjs_action': '''

var server = TacticServerStub.get();
var applet = spt.Applet.get();

server.start( {description: "Checking in files"} );

try {

    //var paths = spt.checkin.transfer_selected_paths("copy");
    var paths = spt.checkin.get_selected_paths();

    var options = spt.checkin.get_checkin_data();
    //options.transfer_mode = 'local';

    var process = options.process;
    var search_key = options.search_key;

    for (var i = 0; i < paths.length; i++) {
        options.subcontext = options.subcontexts[i];
        var snapshot = spt.checkin.checkin_path(search_key, paths[i], process, options);

        // in local mode, the local checkin paths are returned so that they
        // can be moved to the local repo
        var repo_paths = snapshot.__paths__;
        for (var j = 0; j < repo_paths.length; j++) {
            applet.copytree(paths[i], repo_paths[i]);
        }
    }

    server.finish( {description: "Checking in files: " + paths } );

}
catch(e) {
    spt.alert(e);
    server.abort();
}

spt.app_busy.hide();

        '''
        }
"""

        # checkin_mode is true if context_options are set
        # main check-in
        my.sandbox_dir = my.sandbox_dir.rstrip('/') 

        behavior = {
            'type': 'click_up',
            'search_key': search_key,
            'snapshot_code': snapshot_code,
            'transfer_mode': transfer_mode,
            'checkin_command': my.checkin_command,
            'script_path': script_path,
            'validate_script_path': my.validate_script_path,
            'inline_script': script,
            'sandbox_dir': my.sandbox_dir,
            'top': 'spt_checkin_top',
            'options': my.options,
            'cbjs_action': r'''

var file_paths = [];
var contexts = [];
var subcontexts = [];

var top = bvr.src_el.getParent("."+bvr.top);
spt.checkin.top = top;

var search_key = bvr.search_key;
spt.checkin.search_key = search_key;


var el = top.getElement(".spt_file_selector");
var info = top.getElement(".spt_checkin_info");

var is_context = info.getAttribute('context_mode') == 'true';
if (is_context) {
    contexts = spt.checkin.get_selected_contexts();

} else {
    subcontexts = spt.checkin.get_selected_subcontexts();
}


file_paths = spt.checkin.get_selected_paths()



if (!file_paths || file_paths.length == 0) {
    spt.alert("No files selected");
    return;
}


var range = '';
var type = top.getElement(".spt_checkin_type").value;
var is_current_el = top.getElement(".spt_is_current");
is_current = is_current_el.checked || is_current_el.value=='true';

var process = top.getElement(".spt_checkin_process").value;
//var context = top.getElement(".spt_checkin_context").value;
context = process;




var description = top.getElement(".spt_checkin_description").value;
var add_note = top.getElement(".spt_checkin_add_note");


var file_type = 'main';
if (bvr.snapshot_code){
    var file_type_el = top.getElement(".spt_checkin_file_type");
    if (file_type_el) {file_type = file_type_el.value;}
}
var transfer_mode = bvr.transfer_mode;
if (!transfer_mode) {
    transfer_mode = spt.Environment.get().get_transfer_mode();
}



// add in custom elements
var custom_options_el = top.getElement(".spt_custom_options_top");
var custom_options = spt.api.Utility.get_input_values(custom_options_el, null, false);
bvr.custom_options = custom_options;



// check to see if the check-in process is to be delivered elsewhere
if (custom_options.deliver == "on") {
    process = custom_options.deliver_process;
}




// the context variable is only used for initialization, since we use contexts
var values = {
    'search_key': search_key,
    'description': description,
    'context': context,
    'process': process,
    'is_current': is_current,
    'type': type,
    'file_paths': file_paths,
    'transfer_mode': transfer_mode,
    'contexts': contexts,
    'subcontexts': subcontexts
};
bvr.values = values;


spt.app_busy.show("Check-in", file_paths[0]);


setTimeout( function() {

var server = TacticServerStub.get();
server.start({title: 'Check-in', description: transfer_mode + ' ' + type + ' ' + search_key});

var checkin_data = {}


try {

    
    var has_error = false;

    var _get_context = function(context, subcontext, is_context, file_path, use_file_name){
        var this_context = context;
        if (is_context)
            return this_context;

        if (subcontext) {
            this_context = context + "/" + subcontext;
        }
        else if (use_file_name) {
            file_path = file_path.replace(/\\\\/g, "/");
            var this_sub_context = file_path.replace(bvr.sandbox_dir+"/", "");
            //this_sub_context = file_path;
            if (this_sub_context == file_path) {
                // nothing was found so just use the filename
                var parts = file_path.split(/[\\/\\\\]/);
                var file_name = parts[parts.length-1];
                this_context = process + "/" + file_name;
            }
            else {
                this_context = process + "/" + this_sub_context;
            }
        }
        else {
            this_context = context;
        }
        return this_context
    }

    // if there is a validation script, execute it
    // execute the validation trigger?
    //spt.trigger.fire_named_event("validate|project/asset");

    if (bvr.validate_script_path){
        var script = spt.CustomProject.get_script_by_path(bvr.validate_script_path);
        bvr['script'] = script;
        spt.app_busy.show("Running Validation", bvr.validate_script_path);
        spt.CustomProject.exec_custom_script(evt, bvr);
    } 


    // Run any inline scripts defined
    if (bvr.inline_script != null) {
        eval(bvr.inline_script);
    }
    // Run a custom checkin script
    else if (bvr.script_path != null) {
        script = spt.CustomProject.get_script_by_path(bvr.script_path);
        bvr['script'] = script;
        spt.CustomProject.exec_custom_script(evt, bvr);
    }
    // Handle the default check-in functionality
    else {

        // if the transfer mode is upload, then handle the upload mode
        //var transfer_mode = bvr.transfer_mode
        if (transfer_mode == 'upload' || transfer_mode =='web') {
          
            var is_dir = false; 
            if (type == 'add_dir' || type == 'dir_checkin') {
                is_dir = true;
            }
            var ticket = server.get_transaction_ticket();
            for (var i = 0; i < file_paths.length; i++) {
                spt.app_busy.show("Uploading", file_paths[i]);
                spt.notify.show_message("Uploading: " + file_paths[i]);
                if (is_dir) {
                    server.upload_directory(file_paths[i], ticket);
                }
                else {
                    //spt.progress.add_path(file_path, {ticket: ticket});
                    //spt.progress.run_jobs();

                    var file_path = file_paths[i].replace(/\\\\/g, "/");

                    var startswith = file_path.indexOf(bvr.sandbox_dir);
                    if (startswith != -1) {
                        file_path = file_path.replace(bvr.sandbox_dir+"/", "");
                        var parts = file_path.split("/");
                        parts.pop();
                        var subdir = parts.join("/");
                    }
                    else {
                        subdir = "";
                    }

                    server.upload_file(file_paths[i], ticket, subdir);
                }
            }
            transfer_mode = 'uploaded';
        }
        
        var snapshot;
        if (transfer_mode == 'preallocate') {
            if (type == 'add_dir' || type == 'add_file') {
                throw('Since it is easy to overwrite files in PREALLOCATE transfer mode during Append Check-in,' +
                    ' please use <transfer_mode>copy</transfer> instead.');
            }
            if (file_paths.length > 1) {
                throw('In preallocated check-in mode, you may only select 1 item.');
            }
            var basename = spt.path.get_basename(file_paths[0]);
            
            if (is_context)
                context = contexts[0];
            var applet = spt.Applet.get();
            
            if (['file_checkin','dir_checkin'].contains(type)) {
                var snapshot_type = 'file';
                if (applet.is_dir(file_paths[0])) { snapshot_type = 'dir' };
                var kwargs =   { description: description, snapshot_type: snapshot_type, is_current: is_current};
                var snapshot = server.create_snapshot(search_key, context, kwargs);
                bvr.snapshot_code = snapshot.code
            }
            var kwargs =   {'protocol' : 'client_repo', 'file_name': basename, 'file_type': 'main'};
            var preallocated_path = server.get_preallocated_path(bvr.snapshot_code, kwargs); 
            
            spt.app_busy.show("Prealloated Copying", file_paths[0]);
            applet.copytree(file_paths[0], preallocated_path);

            spt.app_busy.hide();
            file_paths[0] = preallocated_path;
        }
        if (type == 'group_checkin') {
            spt.app_busy.show("Group Check-in", file_paths[0] + '...');
            // we use default context here 
            snapshot = server.group_checkin(search_key, context, file_paths, range, {description: description, mode: transfer_mode, command: bvr.checkin_command});
        }
        else if (type == 'dir_checkin') {
            if (file_paths.length > 1) {
                throw('In directory check-in mode, you may only select 1 directory.');
            }
             
            spt.app_busy.show("Directory Check-in", file_paths[0]);
            var checkin_type = 'strict';
            var use_file_name = false;

            var subcontext = subcontexts[0];
            if (is_context)
                context = contexts[0];

            if (subcontext == "(auto)") {
                subcontext = null;
                use_file_name = true;
                checkin_type = 'auto';
            }
            else if (subcontext == '(main)') {
                subcontext = null;
                checkin_type = 'strict';
            }
            else if (!is_context && !subcontext) {
                use_file_name = true;
                checkin_type = '';
            }
            var this_context = _get_context(context, subcontext, is_context, file_paths[0], use_file_name);

            if (transfer_mode == 'preallocate')
                snapshot = server.add_directory(snapshot.code, file_paths[0], { mode: transfer_mode});
            
            else 
                snapshot = server.directory_checkin(search_key, this_context, file_paths[0], {description: description, mode: transfer_mode, snapshot_type: 'directory', command: bvr.checkin_command, is_current: is_current, checkin_type: checkin_type});
        }


        // check-in of multiple individual files
        else if (type == 'multi_file_checkin' || type =='file_checkin') {

            var applet = spt.Applet.get();

            var padding = 4;

            for (var i = 0; i < file_paths.length; i++ ) {

                var ticket = server.get_transaction_ticket();

                var file_path = file_paths[i];
                var subcontext = subcontexts[i];
                if (is_context)
                    context = contexts[i];

                var use_file_name = false;
                var checkin_type = 'strict';

                if (subcontext == "(auto)") {
                    subcontext = null;
                    use_file_name = true;
                    checkin_type = 'auto';
                }
                else if (subcontext == '(main)') {
                    subcontext = null;
                    checkin_type = 'strict';
                }
                else if (!is_context && !subcontext) {
                    use_file_name = true;
                    checkin_type = '';
                }

                if (applet.is_dir(file_path) == true) {
                    // get all the files in the directory
                    var sub_file_paths = applet.list_recursive_dir(file_path);
                    for (var j = 0; j < sub_file_paths.length; j++) {

                        var file_path = sub_file_paths[j];

                        var this_context = _get_context(context, subcontext, is_context, file_path, use_file_name);
                        padding = 0;

                        spt.app_busy.show("Checking in ...", file_path)
                        server.upload_file(file_path, ticket);

                        snapshot = server.simple_checkin(search_key, this_context, file_path, {description: description, mode: transfer_mode, is_current: is_current, context_index_padding: padding, checkin_type: checkin_type});

                        checkin_data[file_path] = snapshot;
                    }

                }
                else {
                    var this_context = _get_context(context, subcontext, is_context, file_path, use_file_name);

                    padding = 0 ;
                    spt.app_busy.show("Checking in ...", file_path)
                    if (transfer_mode == 'preallocate')
                        snapshot = server.add_file(snapshot.code, file_path, { mode: transfer_mode});
                    else {

                        snapshot = server.simple_checkin(search_key, this_context, file_path, {description: description, mode: transfer_mode, is_current: is_current, context_index_padding: padding, checkin_type: checkin_type});
                    }
                    checkin_data[file_path] = snapshot;


                }
            }
        }




        else if (type == 'add_dir') {
            spt.app_busy.show("Add Directory Check-in", file_paths[0]);
            var kwargs = {mode: transfer_mode};
            if (file_type)
                kwargs.file_type = file_type;
            snapshot = server.add_directory(bvr.snapshot_code, file_paths[0], kwargs);
        }
        else if (type == 'add_file') {
            spt.app_busy.show("Add File Check-in", file_paths[0]);
            var kwargs = {mode: transfer_mode};
            if (file_type)
                kwargs.file_type = file_type;
            snapshot = server.add_file(bvr.snapshot_code, file_paths[0], kwargs);
        }    

    }


    // save info to the file
    var cached_data = spt.checkin.get_cached_data();
    for (var key in checkin_data) {
        var file_data = cached_data[key];
        // this is unused now
        if (file_data)
            file_data['snapshot'] = checkin_data[key];
            
    }
    spt.checkin.write_cached_data(cached_data, true);

    if (add_note.checked) {
        var note = [];
        note.push('CHECK-IN');
        for (var path in checkin_data) {
            var snapshot = checkin_data[path];
            var version = snapshot.version;
            var parts = path.split("/");
            var filename = parts[parts.length-1];
            note.push(filename+' (v'+version+')');
        }
        note.push(': ');
        note.push(description);

        note = note.join(" ");
        server.create_note(bvr.search_key, note, {process: process});
    }


}
catch(e) {
    server.abort();
    spt.alert(spt.exception.handler(e));
    has_error = true;
        
}



if (! has_error) {
    server.finish();
    //var history = top.getElement(".spt_checkin_history");
    //spt.panel.refresh(history, {'context': context});
    spt.panel.refresh(top);

    var close_on_publish = bvr.options['close_on_publish'];
    if (close_on_publish) {
        var popup = top.getParent(".spt_popup");
        spt.popup.close(popup);
    }

}
spt.app_busy.hide();


if (has_error) {
    spt.notify.show_message("Check-in failed.");
}
else {
    spt.notify.show_message("Check-in succeeded.");
}

}, 100);

        '''
        }


        button = ActionButtonWdg(title="Check-in", icon=IconWdg.PUBLISH, size='medium')
        top.add(button)
        button.add_behavior(behavior)


        button.add_style("margin-right: auto")
        button.add_style("margin-left: auto")
        button.add_style("margin-top: 20px")
        button.add_style("margin-bottom: 20px")



        top.add("<br clear='all'/>")
        top.add("<hr/>")


        # add the publish options
        top.add(my.get_publish_options_wdg())




        top.add("<br/>")



        grey_out_div = DivWdg()
        top.add(grey_out_div)
        grey_out_div.add_class("spt_publish_disable")
        grey_out_div.add_style("position: absolute")
        grey_out_div.add_style("left: 0px")
        grey_out_div.add_style("top: 10px")
        grey_out_div.add_style("opacity: 0.6")
        grey_out_div.add_color("background", "background")
        grey_out_div.add_style("height: 100%")
        grey_out_div.add_style("width: 100%")
        #grey_out_div.add_border()



        return top




    def get_checkin_script_path(my, key='checkin_script_path'):

        script_path = my.kwargs.get(key)
        if script_path:
            return script_path

        event_names = []
        # CheckinWdg|key|<search_type>
        event_name = 'CheckinWdg|%s|%s' % (key, my.search_type)
        event_names.append(event_name)

        # CheckinWdg|key|<search_type>|<process>
        event_name = 'CheckinWdg|%s|%s|%s' % (key, my.search_type, my.process)
        event_names.append(event_name)

        # get triggers with this event
        from pyasm.search import Search
        search = Search("config/client_trigger")
        search.add_filters("event", event_names)
        search.add_order_by("event desc")
        triggers = search.get_sobjects()

        if triggers:
            for trigger in triggers:
                #callback = trigger.get_value("custom_script_code")
                callback = trigger.get_value("callback")
                return callback

        else:
            return None


class ContextPanelWdg(BaseRefreshWdg):

    def get_context(my):
        return my.context


    def init(my):
        web = WebContainer.get_web()
        my.process= web.get_form_value('process')
        if not my.process:
            my.process = my.kwargs.get('process')
        my.context = web.get_form_value('context')
        if not my.context:
            my.context = my.kwargs.get('context')

        if my.context.find("/") != -1:
            parts = my.context.split("/")
            my.subcontext = "/".join(parts[1:])
        else:
            my.subcontext = ''


        my.search_type = my.kwargs.get('search_type')
        my.refresh = my.kwargs.get('is_refresh')

        context_obj = Context(my.search_type, my.process)
        my.context_list = context_obj.get_context_list()
        if not my.context_list:
            # TODO: we need some way to tell the user that either
            # the search type or the pipeline code doesn't belong to the current
            # project
            my.context_list = [my.process]
        if not my.context:
            my.context = my.context_list[0]

        my.context_option = my.kwargs.get('context_list')
        my.context_expr_option = my.kwargs.get('context_expr')
       


    def get_subcontext_wdg(my, context, subcontext_value):
        # if specified as a project setting, add a sub_context SelectWdg
        settings = ProdSetting.get_value_by_key(
                "%s/sub_context" % context, my.search_type)
        sub_context = None
        
        if settings:
            sub_context = SelectWdg("subcontext")
            sub_context.set_option("values", settings)
            sub_context.set_submit_onchange()
            sub_context.add_empty_option("<- Select ->")
        else:
            # provide a text field
            sub_context = TextWdg("subcontext")
            sub_context.set_attr('size','10') 

        sub_context.add_behavior({
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_checkin_top");
            spt.panel.refresh(top);
            '''
        })

       
        if subcontext_value:
            sub_context.set_value(subcontext_value)

        sub_context.add_class("spt_checkin_subcontext")
        sub_context.add_attr('title', 'subcontext')
        return sub_context

    def get_display(my):

        show_context = my.kwargs.get("show_context") in [True, 'true','True']
        show_sub_context = my.kwargs.get("show_sub_context") in [True, 'true', 'True']
        if my.refresh:
            div = Widget()
        else:
            div = FloatDivWdg(css='spt_context_panel')
            #div.add_style('margin-top: 1px')
            my.set_as_panel(div)
        #div.add(SpanWdg("-", css='small'))

        """
        swap = None 
        if my.context_list:
            swap = SwapDisplayWdg()
            subcontext = SpanWdg('/ ', css='small spt_subcontext')
           
            # see if this has been overridden, otherwise use the
            # value passed in the ocnstructor
            web = WebContainer.get_web()
            sub_context_value = web.get_form_value('subcontext')
            if not sub_context_value:
                sub_context_value = my.subcontext

            if sub_context_value:
                swap.set_display_widgets(SpanWdg('[-]',css='smaller'), SpanWdg('[+]', css='smaller'))
                off_script = "var el = bvr.src_el.getParent('.spt_context_panel').getElement('.spt_subcontext'); spt.show(el);"
                on_script = "var el = bvr.src_el.getParent('.spt_context_panel').getElement('.spt_subcontext'); el.getElement('.spt_input').value=''; spt.hide(el);"
            else:
                swap.set_display_widgets(SpanWdg('[+]',css='smaller'), SpanWdg('[-]', css='smaller'))
                subcontext.add_style('display','none')
                on_script = "var el = bvr.src_el.getParent('.spt_context_panel').getElement('.spt_subcontext'); spt.show(el);"
                off_script = "var el = bvr.src_el.getParent('.spt_context_panel').getElement('.spt_subcontext'); el.getElement('.spt_input').value=''; spt.hide(el);"

            subcontext_wdg = my.get_subcontext_wdg(my.context, sub_context_value)
            subcontext.add(subcontext_wdg)
            
            
            swap.add_action_script(on_script, off_script)
        """


        if show_context:
            context_select = SelectWdg("context")
            context_select.add_class("spt_checkin_context")
            if my.context_expr_option:
                context_select.set_option('values_expr', my.context_expr_option)
            elif my.context_option:
                context_select.set_option('values', my.context_option)
            else:
                context_select.set_option("values", my.context_list)
                context_select.set_option("labels", my.context_list)
            if my.context:
                context_select.set_value(my.context)
            context_select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_checkin_top");
            var process = top.getElement(".spt_checkin_process");
            var history_el = top.getElement(".spt_checkin_history");
            var selector_el = top.getElement(".spt_file_selector");
            var context = bvr.src_el.value;
            spt.panel.refresh(selector_el, {context: context});
            spt.panel.refresh(history_el, {context: context});
            spt.panel.refresh(bvr.src_el, {process: process.value, context: context});
            '''
            } )
            div.add(context_select)
        else:

            context_hidden = HiddenWdg("context")
            context_hidden.add_class("spt_checkin_context")
            if my.context:
                context_hidden.set_value(my.context)
            div.add(context_hidden)

        # DEPRECATED: subcontext is now on each file
        #if show_sub_context:
        #    div.add(SpanWdg(swap, css='small'))
        #    div.add(subcontext)
        #else:
        #    subcontext = HiddenWdg("subcontext")
        #    subcontext.add_class("spt_checkin_subcontext")
        #    div.add(subcontext)


        return div




class FileSelectorWdg(BaseRefreshWdg):

    def get_args_keys(cls):
        return {
        'search_key': 'search key to find sandbox path',
        'file_paths': 'all of the selected paths',
        'file_info': 'info all of the selected paths',
        'pipeline_code': 'code of the pipeline',
        'process': 'process selected',
        'context': 'context selected',
        'mode': 'directory|sequence|file',
        'file_path': 'preselected file path',
        'sandbox_dir': 'sandbox dir',
        'context_options': 'context options',
        'subcontext_options': 'subcontext options',
        'create_sandbox_script_path': 'script path to create sandbox folder structure',
        'show_links': 'Show the links button at the top of the UI'
        }

    get_args_keys = classmethod(get_args_keys)




    def get_display(my):
        web = WebContainer.get_web()
        file_path = my.kwargs.get('file_path')
        my.sandbox_dir = my.kwargs.get('sandbox_dir')
        
        file_paths = web.get_form_values("file_paths")
        if not file_paths:
            file_paths = my.kwargs.get("file_paths")
            if not file_paths:
                file_paths = []
      
        my.file_paths = file_paths
        file_info = web.get_form_values("file_info")
        if not file_info:
            file_info = my.kwargs.get("file_info")
            if not file_info:
                file_info = []


        my.search_key = my.kwargs.get("search_key")

        my.pipeline_code = web.get_form_value("pipeline_code")
        if not my.pipeline_code:
            my.pipeline_code = my.kwargs.get("pipeline_code")

        my.process = web.get_form_value("process")
        if not my.process:
            my.process = my.kwargs.get("process")

        my.context = web.get_form_value("context")
        subcontext = web.get_form_value('subcontext')
        if not my.context:
            my.context = my.kwargs.get("context")
        elif subcontext:
            my.context = '%s/%s' %(my.context, subcontext)

        my.mode = my.kwargs.get('mode')

        my.create_sandbox_script_path = my.kwargs.get("create_sandbox_script_path")
        my.show_links = my.kwargs.get('show_links')
        top = DivWdg()
        #top.add_style("padding: 15px")
        #top.add_style("margin: 5px")
        #top.add_style('margin-bottom','8px')

        my.set_as_panel(top);
        top.add_class("spt_file_selector")

        content = DivWdg()
        top.add(content)
        content.add_style("margin: 0px 5px 0px 5px")


        # add the local files in the sandbox
        content.add( my.get_dir_list_wdg() )


        if my.kwargs.get("is_refresh"):
            return content
        else:
            return top


    def get_dir_list_wdg(my):
        div = DivWdg()
        div.add_style("min-width: 300px")

        load_div = DivWdg()
        div.add(load_div)
        load_div.add("Reading Sandbox Folder ...")
        load_div.add_style("padding: 15px")
        load_div.add_style("font-size: 14px")

        context_options = my.kwargs.get("context_options")
        subcontext_options = my.kwargs.get("subcontext_options")
        my.options = my.kwargs.get("options")

        # find all the files for this asset and this process
        # get all of the files
        sobject = Search.get_by_search_key(my.search_key)
        search = Search("sthpw/file")
        search.add_column("source_path", distinct=True)
        search2 = Search("sthpw/snapshot")
        search2.add_parent_filter(sobject)
        #search2.add_filter("process", my.process)
        search2.add_filter("process", my.process)

        search.add_relationship_search_filter(search2)

        files = search.get_sobjects()
        source_paths = [x.get_value("source_path") for x in files]

        if my.show_links == False:
            show_links = 'false'
        else:
            show_links = 'true'

        div.add_behavior( {
        'type': 'load',
        'file_paths': my.file_paths,
        'sandbox_dir': my.sandbox_dir,
        'source_paths': source_paths,
        'pipeline_code': my.pipeline_code,
        'process': my.process,
        #'search_key': my.sobject.get_search_key(),
        'search_key': my.search_key,
        'context_options': context_options,
        'subcontext_options': subcontext_options,
        'options': my.options,
        'create_sandbox_script_path': my.create_sandbox_script_path,
        'show_links': show_links,
        'cbjs_action': '''

// have to initialize here for Chrome
var applet = spt.Applet.get();
spt.checkin.sandbox_dir = bvr.sandbox_dir;
spt.checkin.tactic_path = spt.checkin.sandbox_dir+"/.tactic/info.txt";
spt.checkin.get_cached_data = function() {
    var tactic_path = spt.checkin.tactic_path;
    var cached_data = {};
    var applet = spt.Applet.get();
    if (applet.exists(tactic_path)) {
        cached_data = applet.read_file(tactic_path);
        try {
            cached_data = JSON.parse(cached_data);
        } catch(e) {
            cached_data = {};
        }
    }
    return cached_data;
}

spt.checkin.write_cached_data = function(cached_data, check) {
    //var tactic_path = spt.checkin.sandbox_dir+"/.tactic/info.txt";
    var tactic_path = spt.checkin.tactic_path;
    var applet = spt.Applet.get();
    if (applet.exists(tactic_path)) {
        applet.rmtree(tactic_path);
        if (applet.exists(tactic_path)) {
            spt.alert("Cannot delete file: "% tactic_path);
            return;
        }

    }
    if (check) {
        if (applet.exists(spt.checkin.sandbox_dir)) 
            applet.create_file(tactic_path, JSON.stringify(cached_data));
    }
    else {
        applet.create_file(tactic_path, JSON.stringify(cached_data));
    }
}




//spt.app_busy.show("Loading ...");

setTimeout(function() {

var cached_data = spt.checkin.get_cached_data();
var js_paths;

// these are strings here
var show_base_dir = true;
var preselected = false;
var sandbox_dir = bvr.sandbox_dir;
//base_dir is preferred for arbitrary file/dir selection
var base_dir;

// arbitrary file or dir selection
if (bvr.file_paths.length > 0) {
    js_paths = bvr.file_paths;
    show_base_dir = false;
    preselected = true;
    var path_1 = js_paths[0];
    // remove trailing slashes for dir
    path_1 = path_1.replace(/[\/]+$/, '');
    var tmps = path_1.split('/');
    tmps.pop();
    base_dir = tmps.join('/')

    if (applet.is_dir(path_1)) {
    var paths = applet.list_dir(path_1, 3);
    js_paths = [];
    
    for (var i = 0; i < paths.length; i++) {
        var js_path = paths[i] + "";
        js_path = js_path.replace(/\\\\/g, "/");
        if (applet.is_dir(js_path))
            js_path = js_path + "/";

        // skip . files and folders
        var parts = js_path.split('/');
        var skip = false;
        for (var j = 0; j < parts.length; j++) {
            if (parts[j].substr(0, 1) == '.' ) {
                skip = true;
                break;
            }
        }
        if (skip) {
            continue;
        }

        js_paths.push(js_path);
    }
    }
}
else if (! applet.exists(sandbox_dir) ) {
    js_paths = null;
    base_dir = sandbox_dir;
}
else {
    base_dir = sandbox_dir;
    // regular sandbox folder selected
    var paths = applet.list_dir(sandbox_dir, 3);
    js_paths = [];
    for (var i = 0; i < paths.length; i++) {
        var js_path = paths[i] + "";
        js_path = js_path.replace(/\\\\/g, "/");
        if (applet.is_dir(js_path))
            js_path = js_path + "/";

        // skip . files and folders
        var parts = js_path.split('/');
        var skip = false;
        for (var j = 0; j < parts.length; j++) {
            if (parts[j].substr(0, 1) == '.' ) {
                skip = true;
                break;
            }
        }
        if (skip) {
            continue;
        }

        js_paths.push(js_path);
        file_data = cached_data[js_path];
        if (!file_data) {
            cached_data[js_path] = {};
        }

    }
}

var md5s = {}; 
var sizes = {};
if (js_paths != null) {
    for (var i = 0; i < js_paths.length; i++) {

        var js_path = js_paths[i];
        var cache_info = cached_data[js_path];

        var cache_mtime;
        var cache_md5;
        if (cache_info) {
            cache_mtime = cache_info.mtime;
            cache_md5 = cache_info.md5;
        }
        else {
            cache_info = {};
        }
        if (!cache_mtime) {
            cache_mtime = 0;
        }
        if (!cache_md5) {
            cache_mtime = 0;
        }

        // get current path info
        var path_info = applet.get_path_info(js_path);
        var mtime = path_info.mtime;

        // only calculate md5 if the file has been checkedin
        var is_checked_in = false;
        var js_parts = js_path.split("/");
        var js_name = js_parts[js_parts.length-1];
        for (var j = 0; j < bvr.source_paths.length; j++) {
            // since the source path is often not available, just use
            // the file name
            var source_parts = bvr.source_paths[j].split("/");
            var source_name = source_parts[source_parts.length-1];

            //if (bvr.source_paths[j] == js_path) {
            if (source_name == js_name) {
                is_checked_in = true;
                break;
            }
        }

        if (is_checked_in) {
            var md5;
            if (cache_mtime < mtime) {
                //console.log("Calculating MD5: " + js_path);
                md5 = applet.get_md5(js_path);
            } else {
                //console.log("cached MD5: " + js_path);
                md5 = cache_md5;
            }
            md5s[js_path] = md5;
        }
        else {
            md5s[js_path] = "";
        }

        sizes[js_path] = path_info.size;

        cache_info['md5'] = md5;
        cache_info['mtime'] = mtime;
        cache_info['size'] = path_info.size;
    }
}
// avoid creating sandbox_dir by accident
if (applet.exists(sandbox_dir)) {
    spt.checkin.write_cached_data(cached_data);
}



var class_path = 'tactic.ui.widget.CheckinSandboxListWdg';
var kwargs = {
    paths: js_paths,
    folder_state: bvr.folder_state,
    md5s: md5s,
    sizes: sizes,
    pipeline_code: bvr.pipeline_code,
    process: bvr.process,
    base_dir: base_dir,
    search_key: bvr.search_key,
    context_options: bvr.context_options,
    subcontext_options: bvr.subcontext_options,
    //file_data: JSON.stringify(cached_data)
    show_base_dir: show_base_dir,
    preselected: preselected,
    create_sandbox_script_path: bvr.create_sandbox_script_path,
    show_links: bvr.show_links,
    options: bvr.options
}
spt.panel.load( bvr.src_el, class_path, kwargs);

spt.app_busy.hide();

}, 10);

    '''
        } )
        return div



class CheckinSandboxListWdg(BaseRefreshWdg):

    def get_display(my):
        top = my.top
        top.add_class("spt_checkin_sandbox_top")

        my.base_dir = my.kwargs.get("base_dir")
        my.pipeline_code = my.kwargs.get("pipeline_code")
        my.pipeline = Pipeline.get_by_code(my.pipeline_code)
        my.process = my.kwargs.get("process")

        my.show_base_dir = my.kwargs.get("show_base_dir") 
        my.preselected = my.kwargs.get("preselected")

        paths = my.kwargs.get("paths")
        search_key = my.kwargs.get("search_key")
        md5s = my.kwargs.get("md5s")
        sizes = my.kwargs.get("sizes")

        my.search_key = search_key
        my.sobject = Search.get_by_search_key(search_key)

        my.create_sandbox_script_path = my.kwargs.get("create_sandbox_script_path")

        file_data = my.kwargs.get("file_data")

        my.options = my.kwargs.get('options')
        if isinstance(my.options, basestring):
            my.options = eval(my.options)


        inner = DivWdg()
        top.add(inner)

        table = Table()
        inner.add(table)
        table.add_style("width: 100%")
        table.add_row()
        table.add_color("color", "color")

        td = table.add_cell()
        td.add_style("vertical-align: top")

        bg_color = table.get_color("background")
        hilight_color =  table.get_color("background", -20)

        
        show_links = my.kwargs.get("show_links")
        if show_links not in ['false', False]:
            action_wdg = my.get_button_action_wdg()
            action_wdg.add_style("float: right")
            td.add(action_wdg)


            links_wdg = my.get_links_wdg()
            td.add(links_wdg)
            hr = HtmlElement.hr()
            hr.add_style('width: 100%')
            td.add(hr)


        subcontext_options = my.kwargs.get("subcontext_options")
        context_options = my.kwargs.get("context_options")
        if subcontext_options == '[]':
            subcontext_options = []

        # do not set default, let the Check-in logic determine it
        #if not subcontext_options:
        #    subcontext_options = ["(auto)"]
                
        file_info = my.kwargs.get("file_info")

        folder_state = my.options.get("folder_state")


        dir_div = DivWdg()
        td.add(dir_div)
        dir_div.add_style("min-height: 300px")
        dir_div.add_style("height: 300px")
        dir_div.add_class("spt_checkin_content")
        dir_div.add_class("spt_resizable")
        dir_div.add_style("min-width: 500px")
        #dir_div.add_style("width: auto")
        if paths or paths == []:
            dir_div.add_style("overflow-y: auto")
            depth = 1

            folder_mode = my.kwargs.get("folder_mode")
            if folder_mode == "thumb":
                # TEST TEST TEST
                list_dir_div = DivWdg()
                dir_div.add(list_dir_div)
                from tactic.ui.panel import ThumbWdg2
                for path in paths:
                    print "path: ", path
                    path_div = DivWdg()
                    list_dir_div.add(path_div)
                    thumb = ThumbWdg2()
                    path_div.add(thumb)
                    thumb.set_path(path)

            else:
                from tactic.ui.checkin import CheckinDirListWdg
                list_dir_wdg = CheckinDirListWdg(base_dir=my.base_dir, location="client", show_base_dir=my.show_base_dir, all_open=False, paths=paths,  search_key=search_key, md5s=md5s, subcontext_options=subcontext_options, context_options=context_options, depth=depth, sizes=sizes, preselected=my.preselected, show_selection=True, process=my.process, folder_state=folder_state)
                dir_div.add(list_dir_wdg)

 
            if not paths:
                none_div = DivWdg()
                none_div.add_style("padding: 20px")
                none_div.add_style("text-align: center")
                none_div.add_style("font-style: italic")
                none_div.add("Folder is empty")
                dir_div.add(none_div)         
        else:

            msg_div = DivWdg()
            dir_div.add(msg_div)

            #arrow_div = DivWdg()
            #msg_div.add(arrow_div)
            #arrow_div.add(IconWdg("", IconWdg.ARROW_UP_GREEN))
            #arrow_div.add("&nbsp;"*10)
            #arrow_div.add(IconWdg("", IconWdg.ARROW_UP_GREEN))
            #arrow_div.add("&nbsp;"*10)
            #arrow_div.add(IconWdg("", IconWdg.ARROW_UP_GREEN))
            #arrow_div.add_style("margin: -10 0 10px 120px")


            msg_div.add(IconWdg("", IconWdg.ARROW_UP_LEFT_32))
            msg_div.add("Use the above buttons to browse for files or folders to be checked in.")
            msg_div.add_style("padding: 20px")
            msg_div.add_style("margin: 20px")
            msg_div.add_border()
            msg_div.add_color("background", "background3")





            # toggle collapsed by default
            content_div = DivWdg()
            dir_div.add(content_div)
            content_div.add_style("padding: 20px")
            content_div.add_style("margin: 20px")
            content_div.add_border()
            content_div.add_color("background", "background3")

            content_div.add("<b style='font-size: 15px'>OR</b>")
            content_div.add("&nbsp;"*5)
            content_div.add("work in the Sandbox Folder for this process:</b>" )

            table = Table()
            content_div.add(table)
            table.add_row()
            td = table.add_cell()
            icon = IconWdg("Sandbox Folder does not exist", IconWdg.SANDBOX_32)
            td.add(icon)

            td = table.add_cell()

            title_div = DivWdg()
            td.add(title_div)

            msg_div = DivWdg()
            td.add(msg_div)
            msg_div.add('<b>"%s"</b><br/><br/>' % my.base_dir)
            msg_div.add('The sandbox folder is a work folder allocated for this process.  It does not yet exist.  If you wish to work in the sandbox folder, press the "Create" button.')
            msg_div.add_styles("margin-top: 8px;margin-left: 16px")


            checkin = ActionButtonWdg(title="Create >>")
            checkin_div = FloatDivWdg(checkin)
            checkin_div.add_style('margin-left: 12px')
            checkin_div.add_style('margin-top: 5px')
            checkin_div.add_style('float: right')
            content_div.add(checkin_div)


            checkin.add_behavior( {
            'type': 'click_up',
            'sandbox_dir': my.base_dir,
            'create_sandbox_script': my.create_sandbox_script_path,
            'cbjs_action': '''

            if (bvr.create_sandbox_script){
                var script = spt.CustomProject.get_script_by_path(bvr.create_sandbox_script);
                bvr['script'] = script;
                spt.CustomProject.exec_custom_script(evt, bvr);
            } 
            else {
                var applet = spt.Applet.get();
                applet.makedirs(bvr.sandbox_dir);
            }

            var top = bvr.src_el.getParent(".spt_checkin_top");
            spt.panel.refresh(top);
            '''
            } )


            content_div.add("<br clear='all'/>")

            dir_div.add("<br clear='all'/>")



        return top


 


    def get_links_wdg(my):
        web = WebContainer.get_web() 
        client_os = web.get_client_os()

        from tactic.ui.widget import SingleButtonWdg

        links_div = DivWdg()

        button_row = ButtonRowWdg()
        links_div.add(button_row)
        button_row.add_style("float: left")

        button = ButtonNewWdg(title="Refresh", icon=IconWdg.REFRESH, long=False)
        button_row.add(button)

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_checkin_top");
        //spt.app_busy.show("Reading file system ...")
        spt.panel.refresh(top);
        //spt.app_busy.hide();
        '''
        } )
 


        button = ButtonNewWdg(title="Browse", icon=IconWdg.FOLDER)
        button.set_show_arrow_menu(True)
        button_row.add(button)

        menus = [my.get_folder_menu()]
        SmartMenu.add_smart_menu_set( button.get_arrow_wdg(), { 'FOLDER_BUTTON_CTX': menus } )
        SmartMenu.assign_as_local_activator( button.get_arrow_wdg(), "FOLDER_BUTTON_CTX", True )


        behavior = {
        'type': 'click_up',
        'base_dir': my.base_dir,
        'cbjs_action': '''
            var current_dir = bvr.base_dir;
            var is_sandbox = false;
            var select_dir = false;
            spt.checkin.browse_folder(current_dir, is_sandbox, true, select_dir);
        '''
        }
        button.add_behavior( behavior )





        """
        
        browse_div = DivWdg()
        links_div.add(browse_div)

        browse_button = ButtonNewWdg(title='Set Custom Working Folder', icon=IconWdg.FOLDER_EXPLORE )
        button_row.add(browse_button)

        behavior = {
        'type': 'click_up',
        'base_dir': my.base_dir,
        'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_checkin_top");
            spt.checkin.set_top(top);
            var current_dir = bvr.base_dir;
            var is_sandbox = true;
            var select_dir = true;
            spt.checkin.browse_folder(current_dir, is_sandbox, true, select_dir);
        '''
        }
        browse_button.add_behavior( behavior )
        browse_div.add_style("float: left")


        button = ButtonNewWdg(title="Set to My Documents", icon=IconWdg.DETAILS)
        button_row.add(button)
        if client_os == 'nt':
            behavior = {
            'type': 'click_up',
            'cbjs_action': '''
                var applet = spt.Applet.get();
                applet.reset_current_dir();
                var homedrive = applet.getenv("HOMEDRIVE");
                var homepath = applet.getenv("HOMEPATH");
                var dirname;
                if (homedrive && homepath) {
                    dirname = homedrive + homepath + "/Documents";
                } else {
                    spt.alert("User's HOMEPATH undetermined.");
                    return;
                }
                var top = bvr.src_el.getParent('.spt_checkin_top');
                spt.checkin.set_top(top);
                spt.checkin.switch_sandbox(dirname);
            '''
            }
        else:
            behavior = {
            'type': 'click_up',
            'cbjs_action': '''
                var applet = spt.Applet.get();
                applet.reset_current_dir();
                var homepath = applet.getenv("HOME");
                var dirname = homepath + "/Documents";
                var top = bvr.src_el.getParent('.spt_checkin_top');
                spt.checkin.set_top(top);
                spt.checkin.switch_sandbox(dirname);
            '''
            }
 

        button.add_behavior( behavior )

        
        button = ButtonNewWdg(title="Set to Desktop", icon=IconWdg.APP_VIEW_TILE)
        button_row.add(button)
        if client_os == 'nt':
            behavior = {
            'type': 'click_up',
            'cbjs_action': '''
                var applet = spt.Applet.get();
                applet.reset_current_dir();
                var homedrive = applet.getenv("HOMEDRIVE");
                var homepath = applet.getenv("HOMEPATH");
                var dirname;
                if (homedrive && homepath) {
                    dirname = homedrive + homepath + "/Desktop";
                } else {
                    spt.alert("User's HOMEPATH undetermined.");
                    return;
                }
                var top = bvr.src_el.getParent(".spt_checkin_top");
                spt.checkin.set_top(top);
                spt.checkin.switch_sandbox(dirname);
            '''
            }
        else:
            behavior = {
            'type': 'click_up',
            'cbjs_action': '''
                var applet = spt.Applet.get();
                applet.reset_current_dir();
                var homepath = applet.getenv("HOME");
                var dirname = homepath + "/Desktop";
                var top = bvr.src_el.getParent('.spt_checkin_top');
                spt.checkin.set_top(top);
                spt.checkin.switch_sandbox(dirname);
            '''
            }
 



        button.add_behavior( behavior )
        """






        # DISABLING for now
        button = ButtonNewWdg(title="Set to Sandbox", icon=IconWdg.SANDBOX)
        #button_row.add(button)
        button.set_show_arrow_menu(True)
        behavior = {
        'type': 'click_up',
        'base_dir': my.base_dir,
        'cbjs_action': '''
            var applet = spt.Applet.get();
            applet.reset_current_dir();

            var dirname = bvr.base_dir;
            var top = bvr.src_el.getParent(".spt_checkin_top");
            var default_sandbox_dir = top.getAttribute("spt_default_sandbox_dir");
            spt.checkin.set_top(top);
            spt.checkin.switch_sandbox(default_sandbox_dir, true);
        '''
        }
        button.add_behavior( behavior )

        menu = Menu(width=220)
        menu_item = MenuItem(type='title', label='Navigate to ...')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Browse Folder')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Desktop')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
            var button = spt.smenu.get_activator(bvr);
            var applet = spt.Applet.get();
            applet.reset_current_dir();

            var homedrive = applet.getenv("HOMEDRIVE");
            var homepath = applet.getenv("HOMEPATH");
            var dirname = homedrive + homepath + '/Desktop';

            var top = button.getParent(".spt_checkin_top");
            spt.checkin.set_top(top);
            spt.checkin.switch_sandbox(dirname);
        ''' 
        } )
        menu_item = MenuItem(type='action', label='My Documents')
        menu.add(menu_item)

        SmartMenu.add_smart_menu_set( button.get_arrow_wdg(), { 'BUTTON_MENU': menu } )
        SmartMenu.assign_as_local_activator( button.get_arrow_wdg(), "BUTTON_MENU", True )












        # Browse button for browsing files and dirs directly
        """
        browse_div = DivWdg()
        links_div.add(browse_div)
        browse_div.add_style("float: left")

        button = ActionButtonWdg(title="Browse", tip="Select Files or Folder to Check in")
        browse_div.add(button)


        behavior = {
        'type': 'click_up',
        'base_dir': my.base_dir,
        'cbjs_action': '''
            var current_dir = bvr.base_dir;
            var is_sandbox = false;
            var select_dir = false;
            spt.checkin.browse_folder(current_dir, is_sandbox, true, select_dir);
        '''
        }
        button.add_behavior( behavior )
        """

        links_div.add("<br clear='all'/>")


        return links_div



    def get_folder_menu(my):

        web = WebContainer.get_web() 
        client_os = web.get_client_os()

        menu = Menu(width=220)
        menu_item = MenuItem(type='title', label='Navigate to ...')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Browse ...')
        menu.add(menu_item)
        behavior = {
        'type': 'click_up',
        'base_dir': my.base_dir,
        'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_checkin_top");
            spt.checkin.set_top(top);
            var current_dir = bvr.base_dir;
            var is_sandbox = true;
            var select_dir = true;
            spt.checkin.browse_folder(current_dir, is_sandbox, true, select_dir);
        '''
        }
        menu_item.add_behavior( behavior )



        menu_item = MenuItem(type='action', label='My Documents')
        menu.add(menu_item)
        if client_os == 'nt':
            behavior = {
            'type': 'click_up',
            'cbjs_action': '''
                var applet = spt.Applet.get();
                applet.reset_current_dir();
                var homedrive = applet.getenv("HOMEDRIVE");
                var homepath = applet.getenv("HOMEPATH");
                var dirname;
                if (homedrive && homepath) {
                    dirname = homedrive + homepath + "/Documents";
                } else {
                    spt.alert("User's HOMEPATH undetermined.");
                    return;
                }
                var activator = spt.smenu.get_activator(bvr);
                var top = activator.getParent('.spt_checkin_top');
                spt.checkin.set_top(top);
                spt.checkin.switch_sandbox(dirname);
            '''
            }
        else:
            behavior = {
            'type': 'click_up',
            'cbjs_action': '''
                var applet = spt.Applet.get();
                applet.reset_current_dir();
                var homepath = applet.getenv("HOME");
                var dirname = homepath + "/Documents";
                var activator = spt.smenu.get_activator(bvr);
                var top = activator.getParent('.spt_checkin_top');
                spt.checkin.set_top(top);
                spt.checkin.switch_sandbox(dirname);
            '''
            }
        menu_item.add_behavior( behavior )

 
        menu_item = MenuItem(type='action', label='Desktop')
        menu.add(menu_item)
        if client_os == 'nt':
            behavior = {
            'type': 'click_up',
            'cbjs_action': r'''
                var applet = spt.Applet.get();
                applet.reset_current_dir();
                var homedrive = applet.getenv("HOMEDRIVE");
                var homepath = applet.getenv("HOMEPATH");
                var dirname;
                if (homedrive && homepath) {
                    dirname = homedrive + homepath + "/Desktop";
                } else {
                    spt.alert("User's HOMEPATH undetermined.");
                    return;
                }

                var activator = spt.smenu.get_activator(bvr);
                var top = activator.getParent('.spt_checkin_top');
                spt.checkin.set_top(top);
                spt.checkin.switch_sandbox(dirname);
            '''
            }
        else:
            behavior = {
            'type': 'click_up',
            'cbjs_action': '''
                var applet = spt.Applet.get();
                applet.reset_current_dir();
                var homepath = applet.getenv("HOME");
                var dirname = homepath + "/Desktop";

                var activator = spt.smenu.get_activator(bvr);
                var top = activator.getParent('.spt_checkin_top');
                spt.checkin.set_top(top);
                spt.checkin.switch_sandbox(dirname);
            '''
            }
        menu_item.add_behavior( behavior )


        title = "Default Sandbox Folder"
        menu_item = MenuItem(type='action', label=title)
        menu.add(menu_item)
        behavior = {
        'type': 'click_up',
        'base_dir': my.base_dir,
        'cbjs_action': '''
            var applet = spt.Applet.get();
            applet.reset_current_dir();

            var dirname = bvr.base_dir;

            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent('.spt_checkin_top');
            var default_sandbox_dir = top.getAttribute("spt_default_sandbox_dir");

            spt.checkin.set_top(top);
            spt.checkin.switch_sandbox(default_sandbox_dir, true);


        '''
        }
        menu_item.add_behavior( behavior )



        return menu



    def get_button_action_wdg(my):

        my.base_dir = my.kwargs.get("base_dir")


        div = DivWdg()

        from pyasm.widget import IconWdg
        from tactic.ui.widget.button_new_wdg import ButtonNewWdg, ButtonRowWdg

        button_row = ButtonRowWdg(show_title=True)
        div.add(button_row)

        project_code = Project.get_project_code()



       
        # Don't set the transfer mode
        transfer_mode = None

        # get the latest snapshot code
        #snapshot = Snapshot.get_latest(my.sobject.get_search_type(), my.sobject.get_id(), my.context)
        #if snapshot:
        #    snapshot_code = snapshot.get_code()
        #else:
        #    snapshot_code = '__NONE__'

        search = Search("sthpw/snapshot")
        search.add_sobject_filter(my.sobject)
        search.add_filter("process", my.process)
        search.add_filter("is_latest", True)
        snapshots = search.get_sobjects()
        snapshot_codes = [x.get_code() for x in snapshots]

        button = ButtonNewWdg(title='Check-out Tools', icon=IconWdg.CHECK_OUT_SM, show_arrow=True )
        button_row.add(button)

        menu = Menu(width=220)
        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        cbjs_action = my.get_checkout_cbjs_action(my.process)

        menu_item = MenuItem(type='action', label='Check-out Files')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        # Don't specify the sanbox dir at the moment because it will
        # remove the relative sub directories
        #'sandbox_dir': my.base_dir,
        'snapshot_codes': snapshot_codes,
        'transfer_mode': transfer_mode,
        'file_types': ['main'],
        'cbjs_action': cbjs_action,
        'filename_mode': 'source'
        } )

        
        menu_item = MenuItem(type='separator')
        menu.add(menu_item)


        # TODO: This is likely not useful
        """
        menu_item = MenuItem(type='action', label='Check-out all w/ Source Name')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        # Don't specify the sanbox dir at the moment because it will
        # remove the relative sub directories
        #'sandbox_dir': my.base_dir,
        'snapshot_codes': snapshot_codes,
        'transfer_mode': transfer_mode,
        'cbjs_action': cbjs_action,
        'filename_mode': 'source'
        } )
        """



        menu_item = MenuItem(type='action', label='Check-out w/ Version Name')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        # Don't specify the sanbox dir at the moment because it will
        # remove the relative sub directories
        #'sandbox_dir': my.base_dir,
        'snapshot_codes': snapshot_codes,
        'transfer_mode': transfer_mode,
        'cbjs_action': cbjs_action,
        'file_types': ['main'],
        'filename_mode': 'repo'
        } )



        menu_item = MenuItem(type='action', label='Check-out all w/ Version Name')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        # Don't specify the sanbox dir at the moment because it will
        # remove the relative sub directories
        #'sandbox_dir': my.base_dir,
        'snapshot_codes': snapshot_codes,
        'transfer_mode': transfer_mode,
        'cbjs_action': cbjs_action,
        'filename_mode': 'repo'
        } )




        # TODO: This should work now. To be uncommented out.
        # this should give the versionless name, but it doesn't
        # work, so commenting out
        """
        menu_item = MenuItem(type='action', label='Check-out all w/ Versionless Name')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        # Don't specify the sanbox dir at the moment because it will
        # remove the relative sub directories
        #'sandbox_dir': my.base_dir,
        'snapshot_codes': snapshot_codes,
        'transfer_mode': transfer_mode,
        'cbjs_action': cbjs_action,
        'filename_mode': 'versionless'
        } )
        """

        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Repository Browser')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'search_key': my.search_key,
        'process': my.process,
        'cbjs_action': '''
        var class_name = 'tactic.ui.checkin.SObjectDirListWdg'
        var kwargs = {
            search_key: bvr.search_key,
            process: bvr.process,
            show_title: false,
            show_shelf: false
        }

        var activator = spt.smenu.get_activator(bvr);
        var top = activator.getParent(".spt_checkin_top");
        var el = top.getElement(".spt_checkin_content");
        spt.panel.load(el, class_name, kwargs);

        '''
        } )




        SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'BUTTON_MENU': menu } )
        SmartMenu.assign_as_local_activator( button.get_button_wdg(), "BUTTON_MENU", True )







        button = ButtonNewWdg(title="File Actions", icon=IconWdg.FOLDER_EDIT, show_arrow=True)

        menu = Menu(width=180)
        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)
        menu_item = MenuItem(type='action', label='New File')
        menu.add(menu_item)
        menu_item = MenuItem(type='action', label='New Folder')
        menu.add(menu_item)

        subdir = "New Folder"
        menu_item.add_behavior( {
        'type': 'click_up',
        'subdir': subdir,
        'sandbox_dir': my.base_dir,
        'cbjs_action': '''
        var applet = spt.Applet.get();
        applet.makedirs(bvr.sandbox_dir + "/" + bvr.subdir);

        var top = bvr.src_el.getParent(".spt_checkin_top");
        spt.app_busy.show("Reading file system ...")
        spt.panel.refresh(top);
        spt.app_busy.hide();

        '''
        } )



        SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'BUTTON_MENU': menu } )
        SmartMenu.assign_as_local_activator( button.get_button_wdg(), "BUTTON_MENU", True )



        button = ButtonNewWdg(title="Explore Sandbox (%s)" % my.base_dir, icon=IconWdg.FOLDER_GO)
        button_row.add(button)

        button.add_behavior( {
        'type': 'click_up',
        'sandbox_dir': my.base_dir,
        'cbjs_action': '''
        var applet = spt.Applet.get();
        if (! applet.exists(bvr.sandbox_dir)) {
            applet.makedirs(bvr.sandbox_dir);
        }
        applet.open_explorer(bvr.sandbox_dir);
        '''
        } )





        button = ButtonNewWdg(title="More Options", icon=IconWdg.GEAR, show_arrow=True)
        button_row.add(button)

        gear_menu = my.get_gear_menu()
        SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'BUTTON_MENU': gear_menu } )
        SmartMenu.assign_as_local_activator( button.get_button_wdg(), "BUTTON_MENU", True )


 
        return div






    def get_gear_menu(my):
        from tactic.ui.container import DialogWdg, Menu, MenuItem
        menu = Menu(width=200)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        security = Environment.get_security()
        if my.pipeline and security.check_access("builtin", "view_site_admin", "allow"):
            if my.pipeline:
                pipe_proj_code = my.pipeline.get_value('project_code')
                project_code = Project.get_project_code()
                menu_item = MenuItem(type='action', label='Edit Process')
                menu.add(menu_item)

                menu_item.add_behavior( {
                    'type': 'click_up',
                    'pipeline_code' : my.pipeline.get_code(),
                    'project_code': project_code,
                    'pipeline_project_code': pipe_proj_code,
                    'process': my.process,
                    'cbjs_action': '''
                    var server = TacticServerStub.get();
                    if (bvr.project_code != bvr.pipeline_project_code) {
                        server.set_project(bvr.pipeline_project_code);
                    }

                    var expr = "@SOBJECT(config/process['process','"+bvr.process+"']['pipeline_code', '" + bvr.pipeline_code +"'])";
                    var process = server.eval(expr, {single: true});
                    var class_name = 'tactic.ui.panel.EditWdg';
                    var kwargs = {
                        search_key: process.__search_key__,
                        search_type: 'config/process',
                        view: 'edit',
                    };
                    if (process && !process.__search_key__) {
                        var default_data = {'process': bvr.process, 'pipeline_code': bvr.pipeline_code}; 
                        var rtn = server.insert('config/process', default_data);
                        kwargs.search_key = rtn.__search_key__;
                    }
                    
                    spt.panel.load_popup("Edit Process", class_name, kwargs);
                    server.set_project(bvr.project_code);

                    '''
                } )



            menu_item = MenuItem(type='action', label='List Processes')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'type': 'click_up',
                'process': my.process,
                'cbjs_action': '''
                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    search_type: 'config/process',
                    view: 'table',
                };
                spt.tab.set_main_body_tab()
                spt.tab.add_new("processes", "Processes", class_name, kwargs);
                '''
            } )




            menu_item = MenuItem(type='separator')
            menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Show Server Transaction Log')
        behavior = {
            'cbjs_action': "spt.popup.get_widget(evt, bvr)",
            'options': {
                'class_name': 'tactic.ui.popups.TransactionPopupWdg',
                'title': 'Transaction Log',
                'popup_id': 'TransactionLog_popup'
            }
        }
        menu_item.add_behavior(behavior)
        menu.add(menu_item)


        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Undo Last Server Transaction')
        behavior = {'cbjs_action': "spt.undo_cbk(evt, bvr);"}
        menu_item.add_behavior(behavior)
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Redo Last Server Transaction')
        behavior = {'cbjs_action': "spt.redo_cbk(evt, bvr);"}
        menu_item.add_behavior(behavior)
        menu.add(menu_item)


        return menu


    def get_checkout_cbjs_action(process, show_status=False):
        '''used by Check-out Tools and Simple Check-out Widget in SimpleCheckinWdg'''
        if show_status:
            show_status = 'true'
        else:
            show_status = 'false'
        
        cbjs_action = '''
        var button = spt.smenu.get_activator(bvr);
        var filename_mode = bvr.filename_mode;
        if (!filename_mode) {
            filename_mode = 'source';
        }
        var snapshot_codes = bvr.snapshot_codes;
        var server = TacticServerStub.get();
        if (snapshot_codes.length == 0 ) {
            if (bvr.real_time && bvr.search_key) {
                var context = '%s';
                var versionless = (bvr.versionless == true);
                var snapshot = server.get_snapshot(bvr.search_key, {context: context, versionless: versionless});
                snapshot_codes = [snapshot.code];
                if (!snapshot.code) {
                    var label = versionless ? 'versionless': '';
                    spt.alert("Can't find " + context + ' ' +  label + " snapshot to check out");
                    return;
                }
            } else { 
                spt.alert("Nothing to check out");
                return;
            }
        }

        var msg = bvr.sandbox_dir ? 'To: '+ bvr.sandbox_dir : ''
       
        spt.app_busy.show("Checking out", msg );

        var transfer_mode = bvr.transfer_mode;
        if (!transfer_mode) {
            transfer_mode = spt.Environment.get().get_transfer_mode();
        }
        // NOTE: reusing checkin transfer mode
        if (transfer_mode == 'copy') {
            transfer_mode = 'client_repo';
        }
        if (transfer_mode == null) {
            transfer_mode = 'web';
        }

        var file_types = bvr.file_types;
        if (!file_types) {
            file_types = [];
        }

        setTimeout( function() {
            var sandbox_paths = []
            for (var i = 0; i < snapshot_codes.length; i++) {
                var label = 1 + i;
                spt.app_busy.show("Checking out latest snapshots in [%s] #"+ label +" ..." );
                sandbox_paths = server.checkout_snapshot(snapshot_codes[i], bvr.sandbox_dir, {mode: transfer_mode, filename_mode: filename_mode, file_types: file_types} );
                //console.log('sandbox ' + sandbox_paths)
            }
            if (button) {
                var top = button.getParent(".spt_checkin_top");
                spt.app_busy.show("Reading file system ...")
                spt.panel.refresh(top);
            }
            if (%s) {
                var status_div = bvr.src_el.getParent('.spt_simple_checkin').getElement('.spt_status_area');
                
                var last_path = sandbox_paths[0];
                var message = last_path;
                status_div.set('text', message );
                //status_div.reveal({duration: '1500'});
                status_div.setStyle('opacity','0').fade('in');
            }
                
            spt.app_busy.hide();

        }, 50);
        '''%(process, process, show_status)

        return cbjs_action

    get_checkout_cbjs_action = staticmethod(get_checkout_cbjs_action)

__all__.append("SandboxButtonWdg")
__all__.append("CheckoutButtonWdg")
__all__.append("FileActionButtonWdg")
__all__.append("ExploreButtonWdg")
__all__.append("GearMenuButtonWdg")

class SandboxButtonWdg(ButtonNewWdg):

    def get_display(my):

        my.base_dir = my.kwargs.get("base_dir")
        my.process = my.kwargs.get("process")

        assert my.base_dir
        assert my.process

        button = ButtonNewWdg(title="Set to Sandbox Folder for %s" % my.process, icon=IconWdg.SANDBOX)
        button.add_style("float: left")
        behavior = {
        'type': 'click_up',
        'base_dir': my.base_dir,
        'cbjs_action': '''
            var applet = spt.Applet.get();
            applet.reset_current_dir();

            var dirname = bvr.base_dir;
            var top = bvr.src_el.getParent(".spt_checkin_top");
            var default_sandbox_dir = top.getAttribute("spt_default_sandbox_dir");
            spt.checkin.set_top(top);
            spt.checkin.switch_sandbox(default_sandbox_dir, true);
        '''
        }
        button.add_behavior( behavior )

        return button

class CheckoutButtonWdg(ButtonNewWdg):       

    def get_display(my):

        my.sobject = my.kwargs.get("sobject")
        my.search_key = my.sobject.get_search_key()
        my.process = my.kwargs.get("process")
        my.base_dir = my.kwargs.get("base_dir")

        # Don't set the transfer mode
        transfer_mode = None

        # get the latest snapshot code
        #snapshot = Snapshot.get_latest(my.sobject.get_search_type(), my.sobject.get_id(), my.context)
        #if snapshot:
        #    snapshot_code = snapshot.get_code()
        #else:
        #    snapshot_code = '__NONE__'

        search = Search("sthpw/snapshot")
        search.add_sobject_filter(my.sobject)
        search.add_filter("process", my.process)
        search.add_filter("is_latest", True)
        snapshots = search.get_sobjects()
        snapshot_codes = [x.get_code() for x in snapshots]

        button = ButtonNewWdg(title='Check-out Tools', icon=IconWdg.CHECK_OUT_SM, show_arrow=True )
        menu = Menu(width=220)
        menu_item = MenuItem(type='title', label='Check-out')
        menu.add(menu_item)


        cbjs_action = '''
        var button = spt.smenu.get_activator(bvr);

        var filename_mode = bvr.filename_mode;
        if (!filename_mode) {
            filename_mode = 'source';
        }

        if (bvr.snapshot_codes.length == 0) {
            spt.alert("There are no files to check out.");
            return;
        }

        spt.app_busy.show("Checking out", 'To: '+ bvr.sandbox_dir);

        var transfer_mode = bvr.transfer_mode;
        if (!transfer_mode) {
            transfer_mode = spt.Environment.get().get_transfer_mode();
        }
        // NOTE: reusing checkin transfer mode
        if (transfer_mode == 'copy') {
            transfer_mode = 'client_repo';
        }
        if (transfer_mode == null) {
            transfer_mode = 'web';
        }

        setTimeout( function() {
            var server = TacticServerStub.get();
            for (var i = 0; i < bvr.snapshot_codes.length; i++) {
                spt.app_busy.show("Checking out snapshot ["+i+"] ..." );
                server.checkout_snapshot(bvr.snapshot_codes[i], bvr.sandbox_dir, {mode: transfer_mode, filename_mode: filename_mode} );
            }

            var top = button.getParent(".spt_checkin_top");
            spt.app_busy.show("Reading file system ...")
            spt.panel.refresh(top);
            spt.app_busy.hide();

        }, 50);
        '''


        menu_item = MenuItem(type='action', label='Check-out w/ Source Name')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'sandbox_dir': my.base_dir,
        'snapshot_codes': snapshot_codes,
        'transfer_mode': transfer_mode,
        'cbjs_action': cbjs_action,
        'filename_mode': 'source'
        } )


        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Check-out w/ Repository Name')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'sandbox_dir': my.base_dir,
        'snapshot_codes': snapshot_codes,
        'transfer_mode': transfer_mode,
        'cbjs_action': cbjs_action,
        'filename_mode': 'repo'
        } )


        menu_item = MenuItem(type='action', label='Check-out w/ Versionless Name')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'sandbox_dir': my.base_dir,
        'snapshot_codes': snapshot_codes,
        'transfer_mode': transfer_mode,
        'cbjs_action': cbjs_action,
        'filename_mode': 'versionless'
        } )


        menu_item = MenuItem(type='action', label='Repository Browser')
        menu.add(menu_item)
        menu_item.add_behavior( {
        'type': 'click_up',
        'search_key': my.search_key,
        'process': my.process,
        'cbjs_action': '''
        var class_name = 'tactic.ui.checkin.SObjectDirListWdg'
        var kwargs = {
            search_key: bvr.search_key,
            process: bvr.process,
            show_title: false,
            show_shelf: false
        }

        var activator = spt.smenu.get_activator(bvr);
        var top = activator.getParent(".spt_checkin_top");
        var el = top.getElement(".spt_checkin_content");
        spt.panel.load(el, class_name, kwargs);

        '''
        } )




        SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'BUTTON_MENU': menu } )
        SmartMenu.assign_as_local_activator( button.get_button_wdg(), "BUTTON_MENU", True )


        return button



class FileActionButtonWdg(ButtonNewWdg):

    def get_display(my):

        my.base_dir = my.kwargs.get("base_dir")

        button = ButtonNewWdg(title="File Actions", icon=IconWdg.FOLDER_EDIT, show_arrow=True)

        menu = Menu(width=180)
        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)
        menu_item = MenuItem(type='action', label='New File')
        menu.add(menu_item)
        menu_item = MenuItem(type='action', label='New Folder')
        menu.add(menu_item)

        subdir = "New Folder"
        menu_item.add_behavior( {
        'type': 'click_up',
        'subdir': subdir,
        'sandbox_dir': my.base_dir,
        'cbjs_action': '''
        var applet = spt.Applet.get();
        applet.makedirs(bvr.sandbox_dir + "/" + bvr.subdir);

        var top = bvr.src_el.getParent(".spt_checkin_top");
        spt.app_busy.show("Reading file system ...")
        spt.panel.refresh(top);
        spt.app_busy.hide();

        '''
        } )

        SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'BUTTON_MENU': menu } )
        SmartMenu.assign_as_local_activator( button.get_button_wdg(), "BUTTON_MENU", True )


        return button



class ExploreButtonWdg(ButtonNewWdg):

    def get_display(my):
        my.base_dir = my.kwargs.get("base_dir")

        button = ButtonNewWdg(title="Explore Sandbox (%s)" % my.base_dir, icon=IconWdg.FOLDER_GO)

        button.add_behavior( {
        'type': 'click_up',
        'sandbox_dir': my.base_dir,
        'cbjs_action': '''
        var applet = spt.Applet.get();
        if (! applet.exists(bvr.sandbox_dir)) {
            applet.makedirs(bvr.sandbox_dir);
        }
        applet.open_explorer(bvr.sandbox_dir);
        '''
        } )


        return button



class GearMenuButtonWdg(ButtonNewWdg):

    def get_display(my):

        my.pipeline_code = my.kwargs.get("pipeline_code")
        my.pipeline = Pipeline.get_by_code(my.pipeline_code)
        my.process = my.kwargs.get("process")


        button = ButtonNewWdg(title="More Options", icon=IconWdg.GEAR, show_arrow=True)

        gear_menu = my.get_gear_menu()
        SmartMenu.add_smart_menu_set( button.get_button_wdg(), { 'BUTTON_MENU': gear_menu } )
        SmartMenu.assign_as_local_activator( button.get_button_wdg(), "BUTTON_MENU", True )

 
        return button


    def get_gear_menu(my):
        from tactic.ui.container import DialogWdg, Menu, MenuItem
        menu = Menu(width=200)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        security = Environment.get_security()
        if my.pipeline and security.check_access("builtin", "view_site_admin", "allow"):
            if my.pipeline:
                menu_item = MenuItem(type='action', label='Edit Process')
                menu.add(menu_item)
                menu_item.add_behavior( {
                    'type': 'click_up',
                    'pipeline_code' : my.pipeline.get_code(),
                    'process': my.process,
                    'cbjs_action': '''
                    var server = TacticServerStub.get();
                    var expr = "@SOBJECT(config/process['process','"+bvr.process+"']['pipeline_code', '" + bvr.pipeline_code +"'])";
                    var process = server.eval(expr, {single: true});
                    var class_name = 'tactic.ui.panel.EditWdg';
                    var kwargs = {
                        search_key: process.__search_key__,
                        search_type: 'config/process',
                        view: 'edit',
                    };
                    if (!process.__search_key__) {
                        var default_data = {'process': bvr.process, 'pipeline_code': bvr.pipeline_code}; 
                        var rtn = server.insert('config/process', default_data);
                        kwargs.search_key = rtn.__search_key__;
                    }
                    spt.panel.load_popup("Edit Process", class_name, kwargs);
                    '''
                } )



            menu_item = MenuItem(type='action', label='List Processes')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'type': 'click_up',
                'process': my.process,
                'cbjs_action': '''
                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    search_type: 'config/process',
                    view: 'table',
                };
                spt.tab.set_main_body_tab()
                spt.tab.add_new("Processes", "processes", class_name, kwargs);
                '''
            } )




            menu_item = MenuItem(type='separator')
            menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Show Server Transaction Log')
        behavior = {
            'cbjs_action': "spt.popup.get_widget(evt, bvr)",
            'options': {
                'class_name': 'tactic.ui.popups.TransactionPopupWdg',
                'title': 'Transaction Log',
                'popup_id': 'TransactionLog_popup'
            }
        }
        menu_item.add_behavior(behavior)
        menu.add(menu_item)


        menu_item = MenuItem(type='separator')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Undo Last Server Transaction')
        behavior = {'cbjs_action': "spt.undo_cbk(evt, bvr);"}
        menu_item.add_behavior(behavior)
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Redo Last Server Transaction')
        behavior = {'cbjs_action': "spt.redo_cbk(evt, bvr);"}
        menu_item.add_behavior(behavior)
        menu.add(menu_item)


        return menu





class CheckinSandboxNotExistsWdg(BaseRefreshWdg):

    def get_display(my):
        top = my.top

        my.process = my.kwargs.get("process")
        my.base_dir = my.kwargs.get("sandbox_dir")
        my.create_sandbox_script_path = my.kwargs.get("create_sandbox_script_path")

        msg_div = DivWdg()
        top.add(msg_div)

        #arrow_div = DivWdg()
        #msg_div.add(arrow_div)
        #arrow_div.add(IconWdg("", IconWdg.ARROW_UP_GREEN))
        #arrow_div.add("&nbsp;"*10)
        #arrow_div.add(IconWdg("", IconWdg.ARROW_UP_GREEN))
        #arrow_div.add("&nbsp;"*10)
        #arrow_div.add(IconWdg("", IconWdg.ARROW_UP_GREEN))
        #arrow_div.add_style("margin: -10 0 10px 120px")


        #msg_div.add(IconWdg("", IconWdg.CREATE))
        msg_div.add(IconWdg("", IconWdg.ARROW_UP_LEFT_32))
        msg_div.add("Use the above buttons to browse for files or folders to be checked in.")
        msg_div.add_style("padding: 20px")
        msg_div.add_style("margin: 20px")
        msg_div.add_border()
        msg_div.add_color("background", "background3")





        # toggle collapsed by default
        content_div = DivWdg()
        top.add(content_div)
        content_div.add_style("padding: 20px")
        content_div.add_style("margin: 20px")
        content_div.add_border()
        content_div.add_color("background", "background3")

        content_div.add("<b style='font-size: 15px'>OR</b>")
        content_div.add("&nbsp"*5)
        content_div.add("work in the Sandbox Folder for this process:</b>")

        table = Table()
        content_div.add(table)
        table.add_row()
        td = table.add_cell()
        icon = IconWdg("Sandbox Folder does not exist", IconWdg.SANDBOX_32)
        td.add(icon)

        td = table.add_cell()

        title_div = DivWdg()
        td.add(title_div)

        msg_div = DivWdg()
        td.add(msg_div)
        msg_div.add('"%s"<br/><br/>' % my.base_dir)
        msg_div.add('The sandbox folder is a work folder allocated for this process.  It does not yet exist.  If you wish to work in the sandbox folder, press the "Create" button.')
        msg_div.add_styles("margin-top: 8px;margin-left: 16px")


        checkin = ActionButtonWdg(title="Create >>")
        checkin_div = FloatDivWdg(checkin)
        checkin_div.add_style('margin-left: 12px')
        checkin_div.add_style('margin-top: 5px')
        checkin_div.add_style('float: right')
        content_div.add(checkin_div)


        checkin.add_behavior( {
        'type': 'click_up',
        'sandbox_dir': my.base_dir,
        'create_sandbox_script': my.create_sandbox_script_path,
        'cbjs_action': '''

        if (bvr.create_sandbox_script){
            var script = spt.CustomProject.get_script_by_path(bvr.create_sandbox_script);
            bvr['script'] = script;
            spt.CustomProject.exec_custom_script(evt, bvr);
        } 
        else {
            var applet = spt.Applet.get();
            applet.makedirs(bvr.sandbox_dir);
        }

        var top = bvr.src_el.getParent(".spt_checkin_top");
        spt.panel.refresh(top);
        '''
        } )


        content_div.add("<br clear='all'/>")

        top.add("<br clear='all'/>")

        return top




class CheckinHistoryWdg(BaseRefreshWdg):

    def get_args_keys(cls):
        return {
        'search_key': 'search_key of the sobject to show the history',
        'context': 'context to filter on',
        'sandbox_dir': 'original sandbox dir when this is first opened'
        }


    def get_display(my):
        parent_key = my.kwargs.get("search_key")
        sobject = Search.get_by_search_key(parent_key)
        sandbox_dir = my.kwargs.get('sandbox_dir')
        web = WebContainer.get_web()
        context = web.get_form_value("context")
        subcontext = web.get_form_value('subcontext')
        if not context:
            context = my.kwargs.get('context')
        #elif subcontext:
        #    context = '%s/%s'%(context, subcontext)


        state = my.get_state()
        state = {}
        state['context'] = context
        my.set_state(state)


        # this links the sandbox to the original task, regardless if the user has switched to another
        # process in the Checkin/out Wdg
        cb = CheckboxWdg('link_sandbox', label='link')
        cb.add_class('link_sandbox')
        cb.set_persistence()
        cb.add_behavior({'type': 'click_up',
            'cbjs_action': '''
                if (bvr.src_el.checked)
                    spt.app_busy.show("Refreshing", "Linking to original sandbox...");
                else
                    spt.app_busy.show("Refreshing", "Unlinking from original sandbox...");

            setTimeout( function(){
                var top = bvr.src_el.getParent(".spt_checkin_top");
                spt.panel.refresh(top);
                spt.app_busy.hide();
                })

            '''})


        from tactic_client_lib import TacticServerStub
        server = TacticServerStub.get()
        client_lib_dir = server.get_client_dir(parent_key, mode='client_repo')


        # check-in history

        top = DivWdg()
        my.set_as_panel(top)
        top.add_class("spt_checkin_history")
        top.add_style("padding: 10px")


        content = DivWdg()
        top.add(content)

        title_div = DivWdg()

        title = "Check-in History"
        swap = NewSwapDisplayWdg(title=title, icon='HISTORY')
        title_div.add(swap)
        content.add(title_div)


        # set the history
        search_type = 'sthpw/snapshot'
        view = 'checkout'


        hist_div = DivWdg()
        unique_id = hist_div.set_unique_id("content")
        swap.set_content_id(unique_id)

        hist_div.add_style("margin: 10 -10 10 -10")
        hist_div.add_style("padding-top: 5px")
        hist_div.add_style("overflow-x: hidden")
        hist_div.add_style("overflow-y: auto")
        hist_div.add_style("max-height: 600px")
        hist_div.add_style("display: none")
        content.add(hist_div)
        hist_div.add_color("background", "background")
        hist_div.add_color("color", "color")


        hist_table = SObjectCheckinHistoryWdg(search_key=parent_key, history_context=context)
        hist_div.add(hist_table)

        """
        #NOTE: connection feature commented out for now
        title_div = DivWdg()
        title = "Connection"
        swap = NewSwapDisplayWdg(title=title, icon='CONNECT')
        title_div.add(swap)
        content.add(title_div)

        connect_div = DivWdg()
        unique_id = connect_div.set_unique_id("content")
        swap.set_content_id(unique_id)

        connect_div.add_style("padding-top: 5px")
        connect_div.add_style("overflow-x: hidden")
        connect_div.add_style("overflow-y: auto")
        connect_div.add_style("max-height: 600px")
        connect_div.add_style("display: none")
        content.add(connect_div)
        connect_div.add_color("background", "background")
        connect_div.add_color("color", "color")


        from tactic.ui.panel import ViewPanelWdg
        depend_table = ViewPanelWdg(search_type="sthpw/connection", view="table")
        connect_div.add(depend_table)
        """


        if my.kwargs.get("is_refresh"):
            return content
        else:
            return top









__all__.append('CustomCheckinInfoPanelWdg')
class CustomCheckinInfoPanelWdg(CheckinInfoPanelWdg):
    '''stores the 3 components for CheckinWdg. We are customizing the publish options'''

    def get_publish_options_wdg(my):
        widget = super(CustomCheckinInfoPanelWdg, my).get_publish_options_wdg()
        render_cb = CheckboxWdg('checkin_render',label='Check-in Render')
        render_cb.add_class('custom_checkin_render')
        widget.add(HtmlElement.br())
        span = SpanWdg(render_cb, css='large')
        widget.add(span)
        widget.add(HtmlElement.br())
        
        return widget







class CheckinGearMenuWdg(GearMenuWdg):

    def __init__(my, client_lib_dir, sandbox_dir):

        my.client_lib_dir = client_lib_dir
        my.sandbox_dir = sandbox_dir

        super(CheckinGearMenuWdg,my).__init__()


    def init(my):

        super(CheckinGearMenuWdg,my).init()
        menus = [my.get_main_menu(), my.get_more_menu()]
        my.menus = [x.get_data() for x in menus]


    def get_main_menu(my):
        menu = Menu(width=210)
        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Full Check-out Selected')
        behavior = {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_checkin_top");
            var table = top.getElement(".spt_table");
            var link = top.getElement(".link_sandbox");
            var search_keys = spt.dg_table.get_selected_search_keys(table);
            if (search_keys.length == 0) {
                spt.alert('Please check the checkbox(es) to check out a version.');
            }
            var sandbox_dir = '';
            var sandbox_input = top.getElement('.spt_sandbox_dir');
            if (sandbox_input && link.checked) {
                sandbox_dir = sandbox_input.value;
            }
            spt.app_busy.show("Full Check-out snapshot", "Copying to Sandbox...");
            setTimeout( function(){
                var server = TacticServerStub.get();
                for (var i =0; i < search_keys.length; i++) {
                    
                    //split_key = server.split_search_key(search_keys[i]);
                    server.checkout_snapshot(search_keys[i], sandbox_dir);
                }
                spt.app_busy.hide();
            }, 50);

            '''
        }
        menu_item.set_behavior(behavior)
        menu.add(menu_item)
        
        menu_item = MenuItem(type='action', label='Full Remote Check-out Selected')
        behavior = {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_checkin_top");
            var link = top.getElement(".link_sandbox");
            var table = top.getElement(".spt_table");
            var search_keys = spt.dg_table.get_selected_search_keys(table);
            if (search_keys.length == 0) {
                spt.alert('Please check the checkbox(es) to check out a version.');
            }
            var sandbox_dir = '';
            var sandbox_input = top.getElement('.spt_sandbox_dir');
            if (sandbox_input && link.checked) {
                sandbox_dir = sandbox_input.value;
            }
            spt.app_busy.show("Full Remote Check-out snapshot", "Downloading to Sandbox...");
            setTimeout( function(){
                var server = TacticServerStub.get();
                for (var i =0; i < search_keys.length; i++) {
                    server.checkout_snapshot(search_keys[i], sandbox_dir, {mode: 'web'});
                }
                spt.app_busy.hide();
            }, 50);

            '''
        }
        menu_item.set_behavior(behavior)
        menu.add(menu_item)

        menu_item = MenuItem(type='separator')
        menu.add(menu_item)
        # sandbox dir
        menu_item = MenuItem(type='action', label='Explore Sandbox')
        menu_item.set_behavior( {
            'sandbox_dir': my.sandbox_dir,
            'cbjs_action': '''
            var applet = spt.Applet.get();
            applet.makedirs(bvr.sandbox_dir);
            applet.open_explorer(bvr.sandbox_dir);
            '''
        })
        menu.add(menu_item)

        # client lib dir
        menu_item = MenuItem(type='action', label='Explore Repository')
        menu_item.set_behavior( {
            'client_lib_dir': my.client_lib_dir,
            'cbjs_action': '''
            var applet = spt.Applet.get();
            applet.open_explorer(bvr.client_lib_dir);
            '''
        })
        menu.add(menu_item)

        #menu_item = MenuItem(type='submenu', label='More ...')
        #menu_item.set_submenu_tag_suffix('MORE')
        #menu.add(menu_item)

        return menu


    def get_more_menu(my):
        menu = Menu(menu_tag_suffix='MORE', width=160)

        menu_item = MenuItem(type='title', label='... and more')
        menu.add(menu_item)
        return menu
        





class CheckinQueueData(object):

    def __init__(my):

        # should the stored checkin be a json data structure? Yes
        queue = []

        # checkin a single file to a single context
        checkin = {
            'search_key':   'prod/asset?project=cg&code=chr001',
            'mode':         'file',
            'process':      'model',
            'context':      'context',
            'file_paths':   ['C:/Temp/test.jpg'],
            'description':  'wow',
        }
        queue.append(checkin)


        # checkin a single file using "copy" mode
        checkin = {
            'search_key':   'prod/asset?project=cg&code=chr001',
            'mode':         'file',
            'process':      'model',
            'context':      'context',
            'file_paths':   ['C:/Temp/test.jpg'],
            'mode':         'copy',
            'description':  'wow again',
        }
        queue.append(checkin)


        # check in a two files to a single context
        checkin = {
            'search_key':   'prod/asset?project=cg&code=chr001',
            'mode':         'file',
            'process':      'model',
            'context':      'contextA',
            'file_paths':   ['C:/Temp/test.jpg', 'C:/Temp/test2.jpg'],
            'description':  'wow again again',
        }
        queue.append(checkin)



        # checkin a directory
        checkin = {
            'search_key':   'prod/asset?project=cg&code=chr001',
            'mode':         'directory',
            'process':      'model',
            'context':      'contextA',
            'file_paths':   ['C:/Temp'],
        }
        queue.append(checkin)

        my.queue = queue 




class CheckinQueueWdg(BaseRefreshWdg):
    def get_display(my):
        top = DivWdg()
        my.set_as_panel(top)

        link_wdg = DivWdg()
        link_wdg.add("<a href='http://192.168.153.129/tactic/cg/#//checkin' target='_blank'>Open in New Tab</a>")
        top.add(link_wdg)


        status_div = DivWdg()
        status_div.add_style("height: 100px")
        status_div.add_class("spt_queue_status")
        status_div.add("Uploading [C:/temp/test.jpg]<br/>")
        status_div.add("Checkin in ... [chr001]")
        top.add(status_div)


        queue = CheckinQueueData()
        queue = queue.queue

        inner = DivWdg()
        '''
            //var queue_key = 'sthpw/checkin_queue?code=123ABC';
            //var server = TacticServerStub.get();
            //var queue = server.get_by_search_key(queue_key);
            var search_key = queue.search_key;
            var context = queue.context;
            var file_paths = queue.file_paths;
        '''

        # onload, start checking in
        inner.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            var server = TacticServerStub.get();


            var search_key =   'prod/asset?project=cg&code=chr001';
            var mode =         'file';
            var process =      'model';
            var context =      'model';
            var file_paths =   ['C:/Temp/Handheld0001.png'];
            var description =  'wow';

            var protocol =     'http';
            var cmd = 'my_copy %s %s';

            if (protocol == 'http') {
                //server.upload()
            }
            elif (protocol == 'file') {
            }
 
            else if (protocol == 'torrent') {
            }
            else if (protocol == 'custom') {
                var applet = spt.Applet.get();
                applet.execute_cmd(cmd);
            }
     

            if (mode == "directory") {
                server.directory_checkin(search_key, context, file_paths[0], {})
            }
            else if (mode == "file") {
                server.simple_checkin(search_key, context, file_paths[0], {})
            }

            var top = bvr.src_el.getParent(".spt_checkin_top");
            spt.panel.refresh(top);
 

            '''
        } )
        top.add(inner)


        title = DivWdg()
        title.add("Checkin Queue")
        title.add_class("maq_search_bar")
        inner.add(title)


        queue_wdg = DivWdg()
        for job in queue:
            job_wdg = my.get_job_wdg(job)
            queue_wdg.add(job_wdg)
        inner.add(queue_wdg)


        return top


    def get_job_wdg(my, job):
        job_wdg = DivWdg()

        search_key = job.get("search_key")
        sobject = SearchKey.get_by_search_key(search_key)

        thumb = ThumbWdg()
        thumb.set_sobject(sobject)
        job_wdg.add(thumb)

        mode = job.get("mode")
        process = job.get("process")
        context = job.get("context")
        description = job.get("description")

        job_wdg.add("mode: %s<br/>" % mode)
        job_wdg.add("process: %s<br/>" % process)
        job_wdg.add("context: %s<br/>" % context)
        job_wdg.add("description: %s<br/>" % description)

        return job_wdg



class SObjectCheckinHistoryWdg(BaseRefreshWdg):

    def init(my):

        my.parent_key = my.kwargs.get("search_key")
        if not my.parent_key:
            my.parent_key = WebContainer.get_web().get_form_value('search_key')

        my.parent = Search.get_by_search_key(my.parent_key)
        my.search_type = my.parent.get_search_type()
        my.base_search_type = Project.extract_base_search_type(my.search_type)

        my.search_id = my.parent.get_id()

        my.context = my.kwargs.get("history_context")
    
        state = my.get_state()
        if not state:
            state = {}
        state['context'] = my.context
        my.set_state(state)


    def _get_value(my, sobject, snapshot):
        loader = AssetLoaderWdg(parent_key=my.parent_key)
        value = loader.get_input_value(sobject, snapshot)
        return value

    def get_default_versions_filter(my):
        return "latest"


    def get_snapshot_contexts(my, search_type, search_id):
        '''get the contexts for the snapshots'''
        return Snapshot.get_contexts(search_type, search_id)


    def get_display(my):
        
        web = WebContainer.get_web()
        args = web.get_form_args()

        if not my.search_type:
            my.search_type = args.get('search_type')
        if not my.search_id:
            my.search_id = args.get('search_id')
        # get from cgi
        if not my.search_type:
            my.search_type = web.get_form_value("search_type")
            my.search_id = web.get_form_value("search_id")



        context_filter = web.get_form_value("history_context")
        versions_filter = web.get_form_value("versions")

        if not context_filter:
            context_filter = my.context
        else:
            my.context = context_filter
        my.is_refresh = my.kwargs.get('is_refresh') == 'true'
        if my.is_refresh:
            div = Widget()
        else:
            div = my.top
            div.add_class("spt_checkin_history_top")
            my.set_as_panel(my.top)



        div.add( my.get_filter_wdg(my.search_type, my.search_id) )

        # get the sobject
        sobject = Search.get_by_id(my.search_type, my.search_id)

        # get the snapshots
        search = Search(Snapshot.SEARCH_TYPE)
        search.add_sobject_filter(sobject)


      

        if context_filter:
            # should listen to the user-chosen context
            my.context = context_filter
            search.add_op("begin")
            search.add_filter("context", context_filter)
            search.add_filter("context", "%s/%%" % context_filter, op='like')
            search.add_op("or")
            
        if not versions_filter:
            versions_filter = my.get_default_versions_filter()
            my.select.set_value(versions_filter)

        if versions_filter == 'current':
            search.add_filter("is_current", True)
        elif versions_filter == 'latest':
            search.add_filter("is_latest", True)
        elif versions_filter == 'last 10':
            search.add_limit(10)
        elif versions_filter == 'today':
            from pyasm.search import Select
            search.add_where(Select.get_interval_where(versions_filter))
        elif versions_filter == 'all':
            pass
        else:
            search.add_filter("is_latest", True)


        search.add_order_by("timestamp desc")
        snapshots = search.do_search()

        div.add(my.get_table(sobject,snapshots) )

        return div


    def get_filter_wdg(my, search_type, search_id):
        filter_wdg = DivWdg()

        color = filter_wdg.get_color("table_border", default="border")
        filter_wdg.add_style("border-color: %s" % color)
        filter_wdg.add_style("border-width: 1px 1px 0 1px")
        filter_wdg.add_style("border-style: solid")
        filter_wdg.add_style("height: 25px")
        filter_wdg.add_style("margin-top: -2px")

        filter_wdg.add_style("padding: 8px")
        filter_wdg.add_color("color", "color")
        filter_wdg.add_gradient("background", "background", -10)


        from tactic.ui.widget import SingleButtonWdg
        button = SingleButtonWdg(tip="Refresh", icon=IconWdg.REFRESH, long=False)
        filter_wdg.add(button)
        button.add_style("float: left")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.app_busy.show("Refreshing Check-in History")
            var top = bvr.src_el.getParent(".spt_checkin_history_top");
            spt.panel.refresh(top);
            spt.app_busy.hide();
            '''
        } )

        filter_wdg.add("&nbsp;"*5)




        # add a context selector
        select = SelectWdg("history_context")
        select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            spt.app_busy.show("Refreshing Check-in History")
            var top = bvr.src_el.getParent(".spt_checkin_history_top");
            spt.panel.refresh(top);
            spt.app_busy.hide();
            '''
        } )

        # find all of the contexts that have been checked in
        
        contexts = my.get_snapshot_contexts(search_type, search_id)
        select.set_option("values", contexts )

        # set the context if one has been passed in
        if my.context:

            if re.search('/', my.context):
                new_context = my.context.split("/")[0]
                select.set_value(new_context)
            else:
                select.set_value(my.context)

        #select.set_value("icon")

        select.add_empty_option("-- Select --")
        select.set_persist_on_submit()
        span = SpanWdg()
        span.add("Context: ")
        span.add(select)
        span.add("&nbsp;"*5)
        filter_wdg.add(span)

        # add a versions selector
        my.select = SelectWdg("versions")
        my.select.add_empty_option("-- Select --")
        my.select.add_behavior( {
            'type': 'change',
            'cbjs_action': '''
            spt.app_busy.show("Refreshing Check-in History")
            var top = bvr.src_el.getParent(".spt_checkin_history_top");
            spt.panel.refresh(top);
            spt.app_busy.hide();
            '''
        } )




        my.select.set_option("values", "latest|current|today|last 10|all")
        my.select.set_persist_on_submit()
        span = SpanWdg()
        span.add("Versions: ")
        span.add(my.select)
        span.add("&nbsp;"*5)
        filter_wdg.add(span)

        return filter_wdg


    def get_table(my, sobject, snapshots):
        parent_key = SearchKey.get_by_sobject(sobject)

        layout = 'default'
        #layout = 'tile'
        #layout = 'static_table'


        kwargs = {
            'table_id': 'snapshot_history_table',
            'search_type': 'sthpw/snapshot',
            'view': 'checkin_history',
            'show_search_limit': False,
            'show_gear': False,
            'show_insert': False,
            'show_shelf': False,
            'parent_key': parent_key,
            'mode': 'simple',
            '__hidden__': 'true',
            'state': my.get_state(),
        }
  
        from tactic.ui.panel import FastTableLayoutWdg, TileLayoutWdg, StaticTableLayoutWdg
        if layout == 'tile':
            table = TileLayoutWdg(**kwargs)
        if layout == 'static_table':
            table = StaticTableLayoutWdg(**kwargs)
        else:
            table = FastTableLayoutWdg(**kwargs)

        table.set_sobjects(snapshots)

        return table

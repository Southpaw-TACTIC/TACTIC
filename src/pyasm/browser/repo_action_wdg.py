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

__all__ = ['RepoActionWdg', 'PerforceActionWdg', 'PerforceWdg','TacticWdg',  'SnapshotCheckoutFilesWdg']

import re

from pyasm.biz import Snapshot, Project
from pyasm.web import *
from pyasm.widget import *

from pyasm.common import Common
from pyasm.checkin import Perforce, PerforceTransaction

from perforce_data import PerforceData
from repo_impl import PerforceRepoImpl, TacticRepoImpl      

class RepoActionWdg(BaseTableElementWdg):
    '''widget the performs actions to local perforce syncsitory'''

    BASE_DIR = "core_x/assets"
    POPUP_ID = "browser_popup" 

    def preprocess(my):
        pass
        
    def get_title(my):

        # FIXME: this should not be here!!!
        my.base_dir = '%s/core_x/assets/' %Project.get_project_name()

        # find all of the files in perforce that are in edit mode
        widget = Widget()
        widget.add( super( RepoActionWdg,my).get_title() )
        widget.add( PyPerforceInit() )
        widget.add( ProgressWdg())
        widget.add( GeneralAppletWdg() )
        widget.add( PerforceAppletWdg() )
 
        # this is the key css style
        from tactic.ui.container import PopupWdg
        popup = PopupWdg(id="%s_popup" % my.POPUP_ID, width='625px', allow_page_activity=True)
        div = DivWdg()
        #div = DivWdg(css="popup_wdg")
        div.set_id(my.POPUP_ID)
        div.add_style("display: block")
        div.add_style("top: 20px")
        div.add_style("left: 140px")
        div.add_style("width: 600px")

        popup.add("Repository Browser", "title")
        popup.add(div, "content")
        widget.add(popup)

        return widget


    def is_tactic_repo(cls, sobject):
        # if the sobject is a perforce sobject
        if sobject.has_value("perforce_path"):
            is_tactic_repo = False
        else:
            is_tactic_repo = True

        return is_tactic_repo
    is_tactic_repo = classmethod(is_tactic_repo)

    def get_base_path( sobject):
        base_path = Project.get_sandbox_base_dir(sobject, decrement=1)
        base_path = Common.process_unicode_string(base_path)
        return base_path
    get_base_path = staticmethod(get_base_path)

    def get_display(my):

        sobject = my.get_current_sobject()
        name = sobject.get_name()
        widget = Widget()
 
        # find the path to open explorer
      
        if my.is_tactic_repo(sobject):
            js = "tactic_repo"
        else:
            js = "pyp4"
            uploaded_wdg = HiddenWdg(SObjectUploadCmd.FILE_NAMES)
            widget.add(uploaded_wdg)

        # find the path to open explorer
      
        sobject_path = my.get_base_path(sobject)
        
        button = IconButtonWdg("Explore", IconWdg.LOAD, long=False)
        button.add_event("onclick", "%s.open_explorer('%s')" % \
            (js, sobject_path) )
        widget.add(button)

        
        file_list_wdg = my.get_file_list_wdg(sobject_path)
        widget.add(file_list_wdg)


        return widget

    def get_sobject_path(cls, sobject):
        if cls.is_tactic_repo(sobject):
            sobject_path = sobject.get_sandbox_dir()
            return sobject_path

        sobject_path = sobject.get_value("perforce_path")
        
        if sobject_path == "":
            name = sobject.get_value("name")
            asset_lib =  sobject.get_asset_library_obj()
            
            sobject_path = '%s/%s' %(asset_lib.get_value('repo_path'), name)
        sobject_path = "%s/%s/%s" %(Project.get_project_name(), cls.BASE_DIR, sobject_path)

        # make it lowercase (good for suppressing human errors in Windows)
        sobject_path = sobject_path.lower()
        return sobject_path
    get_sobject_path = classmethod(get_sobject_path)
    
    
        


    def get_file_list_wdg(my, path):

        sobject = my.get_current_sobject()
        code = sobject.get_code()
        name = sobject.get_name()
        name = Common.process_unicode_string(name)

        widget = Widget()

       
        search_key = sobject.get_search_key()
        ajax = AjaxLoader("%s" %my.POPUP_ID)
        if my.is_tactic_repo(sobject):
            ajax.set_load_class("pyasm.browser.TacticWdg")
            checkin_cbk = my.get_option("callback")
            ajax.set_option("callback", checkin_cbk)
        else:
            ajax.set_load_class("pyasm.browser.PerforceWdg")

        ajax.set_option("search_key", search_key)
        ajax.add_element_name("local_%s" % name)
        ajax.add_element_name("sync_%s" % name)
        ajax.add_element_name("repo_%s" % name)
        ajax.add_element_name("checkout_%s" % name)
        ajax.add_element_name("output_%s" % name)
        ajax.add_element_name("workspaces_%s" % name)
        # test
        ajax.add_element_name("have_%s" % name)
        ####
        off_script = ajax.get_off_script()
        ajax.set_option("off_script", off_script)
        my.add(ajax)

        for type in ('local', 'sync', 'repo', 'checkout', 'output','workspaces','have'):
            hidden = HiddenWdg("%s_%s" % (type, name),"")
            widget.add(hidden)


        # create the script that shows the interface
        script = []

        # first retrieve all of the information
        
        if my.is_tactic_repo(sobject):
            script.append("tactic_repo.set_info('%s','%s')" % (name, path) )
        else:
            script.append("pyp4.set_info('%s','%s')" % (name, path) )
        

        on_script = ajax.get_on_script()
        script.append(on_script)
        # move to where the mouse clicks vertically
        
        script.append("var popup =$('%s_popup'); var pos = spt.mouse.get_abs_cusor_position(evt);\
                spt.show(popup); popup.setStyle('top', pos.y - 15);\
                popup.setStyle('left', pos.x + 10); " % (my.POPUP_ID))


        button = IconButtonWdg("File Info", IconWdg.PUBLISH, long=False)

        """
        behavior = {
            'type': 'click_up',
            'mouse_btn': 'LMB',
            'cbfn_action': 'spt.Checkin.get()'
        }
        """
        button.add_behavior({'type': "click_up",\
                            'cbjs_action': ";".join(script)} )
        widget.add(button)

        return widget



class PerforceActionWdg(RepoActionWdg):
    pass



class SnapshotCheckoutFilesWdg(BaseTableElementWdg):
    ''' show the files that can be checked out using the Tactic Browser'''
   
    def preprocess(my):
        snapshot = my.get_current_sobject()
        if not snapshot:
            return
        asset = snapshot.get_sobject()
        repo_impl = my.get_option('repo_impl')
        my.repo_impl = Common.create_from_class_path('pyasm.browser.%s'\
            % repo_impl, [asset])

        
    
    def get_display(my):
        
        widget = Widget()
        main_div = DivWdg()
        
        snapshot = my.get_current_sobject()
        sandbox_dir = snapshot.get_sandbox_dir()
        remote_dir = snapshot.get_remote_web_dir()
        local_repo_dir = snapshot.get_local_repo_dir()

        for type in my.repo_impl.get_allowed_types():
            file_name = snapshot.get_file_name_by_type(type)

            if not file_name:
                continue
                #raise Exception("file type '%s' not in snapshot '%s'" % \
                #    (type, snapshot.get_code() ) )

            remote_path = "%s/%s" % (remote_dir,file_name)
            local_repo_path = "%s/%s" % (local_repo_dir,file_name)
            sandbox_path = "%s/%s" % (sandbox_dir,file_name)
            cb_value = "%s|%s|%s" % (remote_path, local_repo_path, sandbox_path)


            #version = snapshot.get_value("version")
            #context = snapshot.get_value("context")

            checkbox = CheckboxWdg(TacticWdg.FILE_CB_NAME)
            checkbox.set_attr('value', cb_value)
        
            item_div = DivWdg()
            
            item_div.add(checkbox)
            #item_div.add("%s ( %s v%0.2d - %s)" % (file_name, context, version, type) )
            item_div.add("%s (%s)" % (file_name, type) )
            
            # add item_div in main_div
            main_div.add(item_div)

        widget.add(main_div)
        return widget


class PerforceWdg(Widget):

    INDENT = "40px"
    FILE_CB_NAME = "files"
    FILE_CB_TYPE = "files_type"
    PUBLISH_DESC = "publish_desc"
    PUBLISH_CONTEXT = "publish_context"
    PUBLISH_SUBCONTEXT = "publish_sub_context"
    OUTPUT_WDG = "output_content"


    def is_tactic_repo(my):
        return False

    def get_repo_js_obj(my):
        return "pyp4"
            

    def add_tabs(my, tab_wdg):
        tab_wdg.add(my.get_local_files_wdg, 'Local')
        tab_wdg.add(my.get_repo_files_wdg, 'Repo')
        tab_wdg.add(my.get_checkout_files_wdg, 'Checkout')
        tab_wdg.add(my.get_output_wdg, 'Output')
       
        return ['Local', 'Repo', 'Checkout', 'Output']

    

    def init(my):

        web = WebContainer.get_web()

        #off_script = web.get_form_value("off_script")
        #span = SpanWdg("X", css="small hand")
        #span.add_event("onclick", off_script )
        #span.add_style("float: right")
        #my.add(span)
        

        from pyasm.search import Search
        search_key = web.get_form_value("search_key")
        my.sobject = Search.get_by_search_key(search_key)
        
        code = my.sobject.get_code()
        name = my.sobject.get_name()

        sobject_path = my.get_local_root_path()
        my.repo_impl = my.get_repo_impl()
        
        widget = Widget()
        title_wdg = DivWdg(name, css="maq_search_bar")
        widget.add(title_wdg)

        # define dyn tab wdg
        tab_wdg = DynTabWdg(css = DynTabWdg.SMALL)
        tab_wdg.set_option('search_key', search_key)
        div = tab_wdg.get_content_div()
        div.add_style('height: 30em')
       
        # add the ajax inputs
        for type in ('local', 'sync', 'repo', 'checkout','output','workspaces','have'):
            tab_wdg.add_ajax_input('%s_%s' %(type, name))
            
        #tab_wdg.add_preload_script("pyp4.set_info('%s')" %(name, sobject_path))
        tab_names = my.add_tabs(tab_wdg) 
        
        # add refresh script for each tab 
        for tab in tab_names:
            widget.add(HiddenWdg('%s_tab_script' %tab, \
                tab_wdg.get_tab_script(tab)))

        # list some actions
        widget.add( my.get_action_wdg(tab_wdg, sobject_path) )

       
        widget.add(HtmlElement.hr())

        div = DivWdg()
        div.add_style("height: 280px")
        div.add_style("overflow: auto")

        widget.add(tab_wdg)
       
        my.add(widget)

        
    def get_local_root_path(my):
        # perforce uses sobject path
        base_path =  RepoActionWdg.get_sobject_path(my.sobject)
        return base_path

    def get_local_files_wdg(my):
        no_status = False
       
        name = my.sobject.get_name()
       
        main_div = DivWdg()
        
        div = DivWdg(id='local_list')
        div.add(my.get_revert_button())
        div.add_style('overflow: auto') 
        div.add_style('height: 24em')
        div.add_style('width','585px')
        
        web = WebContainer.get_web()

        local_files = my.repo_impl.get_local_paths()
        sync_dict = my.repo_impl.get_sync_dict()
        repo_files = my.repo_impl.get_repo_paths()
        checkout_files = my.repo_impl.get_checkout_paths()
     
        unknown_list = []
      
        local_num = 0
        # we want the first entry == '' if the sandbox is empty
        if local_files[0] != '':
            local_num = len(local_files)

        base_path = my.get_local_root_path()
        div.add("<b>Local files</b> (%d)" %local_num)
       
        
        div.add(HtmlElement.br(2))
        
        icon_dict = my.get_icon_info(unknown_list, local_files, checkout_files, sync_dict, repo_files)
       
        # define pattern for file and directory
        pat = re.compile('.*%s/(.*)' %base_path )
        dir_pat = re.compile('(\w+/).*')
        
        last_dir = dir_div = None
       
        root_dir_div = my._add_folder_div(div, "./", display=True)
       
        for local_file in local_files: 
            checkbox = CheckboxWdg(my.FILE_CB_NAME)
            checkbox.set_attr('value', local_file)
            try:
                icon = icon_dict[local_file] 
            except KeyError, e:
                continue
            s = pat.search(local_file)
            if s:
                
                # strip the base_dir
                file = s.group(1)
                s = dir_pat.search(file)
                if s:
                    # get the first-level dir
                    dir = s.group(1)
                    if dir != last_dir:
                        last_dir = dir
                        dir_div = my._add_folder_div(div, dir)
                else:
                    # this is the root div
                    dir_div = root_dir_div

            # TODO: dir_div should probably not be none.  Parsing problem
            if not dir_div:
                continue
            
            item_div = DivWdg()
            item_div.add(icon)

            checkbox.set_attr( my.FILE_CB_TYPE, dir_div.get_id())
            item_div.add(checkbox)
            span = SpanWdg(file)
            if local_file in unknown_list:
                span.add_style("color: #777")
            item_div.add(span)

            # add item_div in dir_div
            dir_div.add(item_div)
            
        #if not dir_div:
        #    my._write_parsing_error(div)

        output = my._reformat_output_wdg()
        main_div.add(div)
        main_div.add(output)
        return main_div
       
    def get_icon_info(my, unknown_list, local_files, checkout_files, \
            sync_dict, repo_files):
        ''' get the icon dict for each file 
            It also insert files that could have been checked out. '''
            
        icon_dict = {}
        for file in local_files:
            for checkout in checkout_files:
                try:
                    if sync_dict:
                        checkout = sync_dict[checkout]
                    if file == checkout:
                        icon_dict[file] = IconWdg("checked out", IconWdg.CURRENT) 
                        break
                    
                    if checkout not in local_files:
                        # this has been removed, insert it 
                        local_files.insert(local_files.index(file), checkout)
                        icon_dict[checkout] = IconWdg("missing checked-out file", IconWdg.CROSS)
                        break   
                except KeyError:
                    # this should not happen
                    icon_dict[file] = IconWdg("Invalid data detected", IconWdg.INVALID)
                    break
                
            else:
                for sync, local in sync_dict.items():
                    if file in local:
                            
                        if sync in repo_files:
                            icon_dict[file] = IconWdg("in sync", IconWdg.GOOD) 
                            break
                        else:
                            icon_dict[file] = IconWdg("not in sync", IconWdg.ERROR) 
                            break
                    
                else:
                    # this file is not in repo
                   icon_dict[file] = IconWdg("not in repo", IconWdg.HELP) 
                   unknown_list.append(file)
        local_files.sort()
        return icon_dict
                   
    def _write_parsing_error(my, div):
        #div.add(MessageWdg("There was an error retrieving the file names. \
        #    Please double check the perforce path defined for this asset \
        #    (Summary tab) or \
        #    the repo path defined for the asset library [%s] (Asset Libraries tab)." \
        #    %(my.sobject.get_value('asset_library'))))
        div.add(MessageWdg("There was an error retrieving the file names."))
        
    def _reformat_output_wdg(my):
        output = my.get_output_wdg()
        output_div = output.get_widget(my.OUTPUT_WDG)
        output_div.set_style( 
            'overflow: auto; height: 5em; width: 585px; padding-top: 4px')
        return output
    
    def _add_folder_div(my, div, dir, display=False):
        ''' add a div for a new folder '''
        dir_div_id = '%s_%s' %(div.get_id(), dir)
        # add a checkbox
        checkbox_ctr = CheckboxWdg()
        checkbox_ctr.set_option("onclick", "a=get_elements('%s');"\
            "a.toggle_all(this,'%s','%s');" %(my.FILE_CB_NAME, my.FILE_CB_TYPE, dir_div_id))
        div.add(checkbox_ctr)

        # add a link
        
        dir_div = DivWdg(id=dir_div_id)
        if not display:
            dir_div.add_style('display: none')
        else:
            dir_div.add_style('display: block')
        
        script = "toggle_display('%s')" % dir_div_id
        div.add(HtmlElement.js_href(script, data=dir))
        div.add(HtmlElement.br())
        
        div.add(dir_div)
        
        return dir_div
   
    def get_checkout_button(my):
        # checkout button
        checkout_button = ProdIconButtonWdg("Checkout")
        checkout_script = [ProgressWdg.get_on_script()]
        checkout_script.append(my.get_checkout_script())
        checkout_script.append(ProgressWdg.get_off_script())

        checkout_script.append(my.get_tab_script('Local'))
        checkout_button.add_event("onclick", ";".join(checkout_script))
      
        div = FloatDivWdg(checkout_button, float='right')
        div.add_style("margin: 3px 4px 0px 0px")
        return div
    
    def get_revert_button(my):
        # revert button
        name = my.sobject.get_name()
        sobject_path = RepoActionWdg.get_sobject_path(my.sobject)
        revert_button = ProdIconButtonWdg('Revert')
        revert_script = [ProgressWdg.get_on_script()]
        revert_script.append("pyp4.file_action('%s','%s','revert', 'Revert')" \
            % (my.FILE_CB_NAME, name))
        
        revert_script.append("pyp4.set_info('%s','%s')" % (name, sobject_path))
        revert_script.append(ProgressWdg.get_off_script())
        revert_script.append(my.get_tab_script('Local'))
        revert_button.add_event("onclick", ";".join(revert_script))

        div = FloatDivWdg(revert_button, float='right')
        div.add_style("margin: 3px 4px 0px 0px")
        return div
        
    def get_repo_files_wdg(my):
        main_div = DivWdg()
        
        web = WebContainer.get_web()
        name = my.sobject.get_value("name")
        repo_files = my.repo_impl.get_repo_paths()
        local_files = my.repo_impl.get_local_paths()
        checkout_files = my.repo_impl.get_checkout_paths() 
        sync_dict = my.repo_impl.get_sync_dict()
       

        div = DivWdg(id='repo_files')
        div.add_style('overflow: auto') 
        div.add_style('height: 24em')
        div.add_style('width','585px')
        div.add(my.get_checkout_button())
        div.add("<b>Repo files</b> (%d)" %len(repo_files))
        div.add(HtmlElement.br(2))


        last_dir = dir_div = None
        pat = re.compile('.*%s/(.*)' %RepoActionWdg.get_sobject_path(my.sobject))
        dir_pat = re.compile('(\w+/).*')
        root_dir_div = my._add_folder_div(div, "./", display=True)
       
        for idx, repo_file in enumerate(repo_files):
            checkbox = CheckboxWdg(my.FILE_CB_NAME)
            
            if not sync_dict.has_key(repo_file):
                icon = IconWdg("not in sync", IconWdg.ERROR) 
            else:
                icon = IconWdg("in sync", IconWdg.GOOD) 
                
            cb_value = sync_dict.get(repo_file)
            checkbox.set_attr('value', cb_value)
            
            s = pat.search(repo_file)
            if s:
                # strip the base_dir
                file = s.group(1)
                s = dir_pat.search(file)
                if s:
                    # get the first-level dir
                    dir = s.group(1)
                    if dir != last_dir:
                        last_dir = dir
                        dir_div = my._add_folder_div(div, dir)
                else:
                    # this is the root div
                    dir_div = root_dir_div
 
            # TODO: dir_div should probably not be none.  Parsing problem
            if not dir_div:
                continue
            item_div = DivWdg()
            
            checkbox.set_attr( my.FILE_CB_TYPE, dir_div.get_id())
            item_div.add(icon)
            item_div.add(checkbox)
            item_div.add(file)
            
            # add item_div in dir_div
            dir_div.add(item_div)

        if not dir_div:
           my._write_parsing_error(div)

        output = my._reformat_output_wdg()
        main_div.add(div)
        main_div.add(output)
        
        return main_div

    def get_checkout_files_wdg(my):
        web = WebContainer.get_web()
        name = my.sobject.get_name()
        checkout = web.get_form_value("checkout_%s" % name)
        checkout_files = []
        if checkout:
            checkout_files = checkout.split("|")
        
        div = DivWdg()
        div.add_style('overflow','auto')
        div.add_style('height','30em')
        div.add_style('width','585px')
        div.add("<b>Open files</b> (%d)" %len(checkout_files))
        div.add(HtmlElement.br(2))
        for file in checkout_files:
            div.add(file)
            div.add("<br/>")

        return div
   
    def get_output_wdg(my):
        web = WebContainer.get_web()
        name = my.sobject.get_name()
        
        checkout = web.get_form_value("output_%s" % name)
        checkout_files = []
        if checkout:
            checkout_files = checkout.split("||")
        
        widget = Widget()
        title_div = DivWdg(HtmlElement.b(my.get_output_title()))
        div = DivWdg()
        div.add_style('overflow','auto')
        div.add_style('height','30em')
        div.add_style('width','585px')
        div.add(HtmlElement.br())
        for file in checkout_files:
            div.add(file)
            div.add(HtmlElement.br())

        widget.add(title_div)
        widget.add(div, my.OUTPUT_WDG)
        return widget

    def get_output_title(my):
        return "Perforce Output"
    
 

    def get_action_wdg(my, tab_wdg, sobject_path):
        ''' this is where the checkin widget is drawn'''
        search_key = WebContainer.get_web().get_form_value("search_key") 

        action_div = DivWdg()
      
        if my.is_tactic_repo():
            path = sobject_path
        else:
            path = "%s/%s" %(my._get_root(), sobject_path)
        
        
        base_div = DivWdg(HtmlElement.b("Root Path: ") )
        script = HtmlElement.js_href("pyp4.open_explorer2('%s')" %path, path)
        script.set_attr('title','If available, root path is 1 level below the folder for this search type')
        base_div.add(script)
        base_div.add_style('padding-left', '10px')
        base_div.add_style('margin-bottom','4px')
       
        action_div.add(base_div)

        label_div = DivWdg(HtmlElement.i("Publish Comments"))
        label_div.add_style('margin-left: %s' %my.INDENT)
        action_div.add(label_div)

        div = DivWdg()
        div.set_style('float: left; margin-left: %s' %my.INDENT)
        text_area = TextAreaWdg(my.PUBLISH_DESC)
        if WebContainer.get_web().is_IE():
            text_area.set_attr('rows','3')
        div.add(text_area)
        
        #context_sel = SelectWdg(my.PUBLISH_CONTEXT, label='Context: ')
        #context_sel.set_option('setting','asset_manual_publish_context')
        
        context_sel = ProcessContextWdg()
        context_sel.set_search_type(my.sobject.get_base_search_type())
        checkin_button = ProdIconButtonWdg("Publish")

        name = my.sobject.get_name()

        repo_js = my.get_repo_js_obj()


        # checkin button
        action_div.add( HiddenWdg("upload_files") )
        checkin_script =[]
        checkin_script.append(ProgressWdg.get_on_script())
        checkin_script.append("%s.checkin_file('%s','%s','%s')" % \
            (repo_js, my.FILE_CB_NAME, my.PUBLISH_DESC, name))
        checkin_script.append(my.get_checkin_script(search_key, action_div))
        checkin_script.append("%s.set_info('%s','%s')" % (repo_js, name, sobject_path))
        #checkin_script.append(tab_wdg.get_tab_script('Repo'))# add refresh script for each tab
       
        checkin_script.append(ProgressWdg.get_off_script())
        checkin_button.add_event("onclick", ";".join(checkin_script) )

        
        checkin_button_div = DivWdg(context_sel, css='small')
        
        checkin_button_div.add_style('margin: 40px 6px 5px 40px')
        action_div.add(div)
        action_div.add(HtmlElement.br())
        checkin_button_div.add(HtmlElement.br(2))
        button = SpanWdg(checkin_button)
        if my.is_tactic_repo():
            checkin_button_div.add(my.get_currency_wdg())
            button.add_style('padding-left','190px')
        else:
            button.add_style('padding-left','40px')
        checkin_button_div.add(button)

        action_div.add(checkin_button_div)

        action_div.add(HtmlElement.br())  

        
        
        divider = DivWdg()
        divider.add(HtmlElement.br())
        divider.set_style('border-top: 1px dotted #777; line-height: 6px;\
            width: 100%')
        div2 = DivWdg(divider)

        if not my.is_tactic_repo():
            
            # sync button
           
            sync_button = ProdIconButtonWdg('Sync')
            sync_script = [ProgressWdg.get_on_script()]
            sync_script.append("pyp4.file_action('%s','%s','sync', 'Sync')" \
                % (my.FILE_CB_NAME, name))
            sync_script.append("pyp4.set_info('%s','%s')" % (name, sobject_path))
            sync_script.append( tab_wdg.get_tab_script('Local'))
            sync_script.append(ProgressWdg.get_off_script())
            sync_button.add_event("onclick", ";".join(sync_script))

            div2.add(SpanWdg(sync_button, css='med'))
       


        explore_button = IconButtonWdg("Explore", IconWdg.LOAD, long=False)
        explore_span = SpanWdg(explore_button, css='med')
        div2.add(explore_span)

   
        button = ProdIconButtonWdg('Open WIP folder')
        button.set_attr('title', 'Put your work-in-progress files here')
        button.add_event('onclick', "pyp4.open_explorer2('%s/WIP')"%path)
        explore_span.add(button)

        refresh_button = IconWdg("Refresh", icon=IconWdg.REFRESH)
        refresh_button.add_class('hand')
        refresh_button.add_event('onclick',"%s.set_info('%s','%s'); %s" \
            %(repo_js, name, sobject_path, tab_wdg.get_tab_script('Local')))
        div2.add(refresh_button)
        action_div.add(div2) 

        explore_button.add_event("onclick", "pyp4.open_explorer2('%s')" %path)

        return action_div


    def _get_root(my):
        root = my.repo_impl.get_root_path()
        return root



    def get_currency_wdg(my):
        checkbox = CheckboxWdg(TacticWdg.CURRENCY)
        checkbox.set_default_checked()
        span = SpanWdg('Set as Current: ')
        span.add(checkbox)
        return span


    def get_checkin_script(my, search_key, action_div):
        ajax = AjaxCmd("snapshot_checkin")
        ajax.add_element_name(PerforceWdg.PUBLISH_DESC)
        marshaller = ajax.register_cmd('pyasm.browser.PerforceAssetCheckinCbk') 
        marshaller.add_arg(search_key)
        marshaller.add_arg('<snapshot/>')

        div = ajax.generate_div()
        event_container = WebContainer.get_event_container()
        caller = event_container.get_event_caller(SiteMenuWdg.EVENT_ID)

        post_script = [caller]
        post_script.append(my.get_tab_script('Repo'))

        div.set_post_ajax_script(';'.join(post_script))
        action_div.add(div)
        return ajax.get_on_script(False)



    def get_repo_impl(my):
        return PerforceRepoImpl(my.sobject)


    def get_set_info_script(my):
        name = my.sobject.get_name()
        sobject_path = RepoActionWdg.get_sobject_path(my.sobject)
        return "pyp4.set_info('%s','%s')" % (name, sobject_path)


    def get_checkout_script(my):
        script = [] 

        name = my.sobject.get_name()

        script.append( "pyp4.file_action('%s','%s','add_checkout_path','Check-out')" % (my.FILE_CB_NAME, name))
        script.append( my.get_set_info_script() )

        return ";".join(script)

    def get_tab_script(my, tab_name):
        ''' get the script to redirect to a dyn tab '''
        return "var a=get_elements('%s_tab_script').get_value(); eval(a)" %tab_name 

class TacticWdg(PerforceWdg):

    CURRENCY = 'currency'
    def is_tactic_repo(my):
        return True

    def get_output_title(my):
        return "Tactic Output"

    def get_repo_js_obj(my):
        return "tactic_repo"

    def add_tabs(my, tab_wdg):
        tab_wdg.add(my.get_local_files_wdg, 'Local')
        tab_wdg.add(my.get_repo_files_wdg, 'Repo')
        tab_wdg.add(my.get_output_wdg, 'Output')
       
        return ['Local', 'Repo', 'Output'] 

    def get_local_root_path(my):
        # perforce uses sobject path
        base_path =  RepoActionWdg.get_base_path(my.sobject)
        return base_path

    def get_icon_info(my, unknown_list, local_files, checkout_files,\
            sync_dict, repo_files):
        ''' get the icon dict for each file '''
        icon_dict = {}
        # IMPORTANT: if the sandbox is empty, local_files = [''], 
        # and this for loop will go thru this once
        for file in local_files:
            for checkout in checkout_files:
                try:
                    
                    if sync_dict:
                        checkout = sync_dict[checkout]
                    
                    if file == checkout:
                        icon_dict[file] = IconWdg("checked out", IconWdg.CURRENT) 
                        break
                    # this feature (adding the checkout candidates) is not really desired for Tactic Repo
                    """
                    if checkout not in local_files:
                        # this has been removed, insert it 
                        local_files.insert(local_files.index(file), checkout)
                        icon_dict[checkout] = IconWdg("non checked-out file", IconWdg.CROSS)
                        break   
                     
                    """
                except KeyError:
                    # this should not happen
                    icon_dict[file] = IconWdg("Invalid data detected", IconWdg.INVALID)
                    break
            else:
                # this file is not in repo
                icon_dict[file] = IconWdg("not in repo", IconWdg.HELP) 
                unknown_list.append(file)
        
        local_files.sort()
        return icon_dict
    
    def get_repo_files_wdg(my):

        # TODO: how to determine what snapshots to get
        snapshots = TacticRepoImpl.get_repo_snapshots(my.sobject)
       
        div = DivWdg(id='repo_files')
        div.add_style('width','585px')
        div.add(my.get_checkout_button())
        
        div.add(HtmlElement.br(2))
        
        table = TableWdg("sthpw/snapshot", "browser")
        table.set_sobjects(snapshots)

        table_div = DivWdg(table)
        table_div.set_style( 'overflow: auto; height: 28em;') 
        
        div.add(table_div)
        return div




    def get_checkin_script(my, search_key, action_div):
        ajax = AjaxCmd("snapshot_checkin")
        ajax.add_element_name(PerforceWdg.PUBLISH_DESC)
        ajax.add_element_name(PerforceWdg.PUBLISH_CONTEXT)
        ajax.add_element_name(PerforceWdg.PUBLISH_SUBCONTEXT)
        ajax.add_element_name(TacticWdg.CURRENCY)
        ajax.add_element_name("upload_files")
        
        checkin_cbk = WebContainer.get_web().get_form_value("callback")
        if not checkin_cbk:
            checkin_cbk = "pyasm.browser.TacticAssetCheckinCbk"
        marshaller = ajax.register_cmd(checkin_cbk) 
        #marshaller = ajax.register_cmd('pyasm.browser.MaxAssetCheckinCbk') 
        marshaller.add_arg(search_key)
        marshaller.add_arg(Project.get_project_code())
        div = ajax.generate_div()

        event_container = WebContainer.get_event_container()
        caller = event_container.get_event_caller(SiteMenuWdg.EVENT_ID)
        post_script = [caller]
        post_script.append(my.get_tab_script('Repo'))

        div.set_post_ajax_script(';'.join(post_script))
        action_div.add(div)
        return ajax.get_on_script(False)



    def get_repo_impl(my):
        return TacticRepoImpl(my.sobject)


    def get_set_info_script(my):
        name = my.sobject.get_name()
        sobject_path = RepoActionWdg.get_base_path(my.sobject)
        return "tactic_repo.set_info('%s','%s')" % (name, sobject_path)



    def get_checkout_script(my):
        script = []
        name = my.sobject.get_name()

        script.append( "tactic_repo.checkout_file('%s','%s')" % (my.FILE_CB_NAME, name))
        script.append( my.get_set_info_script() )
        return  ";".join(script)


    def get_revert_button(my):
        #TODO: to be implemented
        pass

   


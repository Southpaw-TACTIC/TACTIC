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
__all__ = ["SideBarPanelWdg", "SideBarBookmarkMenuWdg", "ViewPanelWdg", "ViewPanelSaveWdg"]

import os, types
import random
from pyasm.common import Xml, Common, Environment, Container, XmlException, jsonloads, jsondumps, Config, SetupException
from pyasm.biz import Project, Schema
from pyasm.search import Search, SearchType, SearchKey, SObject, WidgetDbConfig
from pyasm.web import Widget, DivWdg, HtmlElement, SpanWdg, Table, FloatDivWdg, WebContainer, WidgetSettings
from pyasm.widget import SelectWdg, FilterSelectWdg, WidgetConfig, WidgetConfigView, TextWdg, ButtonWdg, CheckboxWdg, ProdIconButtonWdg, HiddenWdg

from tactic.ui.common import BaseRefreshWdg, WidgetClassHandler
from tactic.ui.container import RoundedCornerDivWdg, LabeledHidableWdg, PopupWdg
from tactic.ui.container.smart_menu_wdg import SmartMenu
from tactic.ui.widget import ActionButtonWdg
from tactic.ui.input import TextInputWdg


class SideBarPanelWdg(BaseRefreshWdg):

    def get_views(my):

        views = []
        view = my.kwargs.get("view")
        if view:
            views.append(view)

        if not Project.get().is_admin():
            views.append('project_view')


        # detemine whether this use is allowed to see views other than the
        # main project_view
        security = Environment.get_security()
        if security.check_access("builtin", "view_save_my_view", "allow", default='allow'):
            # show my views section
            my_view = "my_view_%s" % Environment.get_user_name()
            my_view = my_view.replace("\\", "_")
            views.append(my_view)
                

        

        if security.get_version() == 1:
            if security.check_access("side_bar", "admin_views", "allow", default='allow'):
                if security.check_access("builtin", "view_site_admin", "allow"):
                    views.append('admin_views')
                else:
                    views.append('_my_admin')
            else:
                views.append('_my_admin')
                
        else:
            if security.check_access("link", "admin_views", "allow", default="deny"):
                if security.check_access("builtin", "view_site_admin", "allow"):
                    views.append('admin_views')
                else:
                    views.append('_my_admin')
            else:
                views.append('_my_admin')  

        return views


    def get_display(my):
        views = my.get_views()

        top = my.top

        # TEST: NEW LAYOUT
        if Config.get_value("install", "layout") == "fixed":
            top.add_style("position: fixed")
            top.add_style("top: 34px")
            top.add_style("z-index: -1")
            top.add_style("width: 185")

        top.add( my.get_subdisplay(views) )
        return top



    def get_subdisplay(my, views):

        div = DivWdg()
        div.set_attr('spt_class_name', Common.get_full_class_name(my))

        # remove the default round corners by making this div the same color
        div.add_color("background", "background3")

        div.add_behavior( {
            'type': 'load',
            'cbjs_action': my.get_onload_js()
        } )

        # add the down button
        down = DivWdg()
        down.set_id("side_bar_scroll_down")
        down.add_class("hand")

        # the button at the top of the nav menu to scroll it back to default
        # position
        down.add_looks("navmenu_scroll")

        down.add_style("display: none")
        down.add_style("height: 10px")
        #down.set_round_corners(5, corners=['TL','TR'])

        down.add("<div style='margin-bottom: 4px; text-align: center'>" \
                 "<img class='spt_order_icon' src='/context/icons/common/order_array_up_1.png'></div>")

        down.add_event("onclick", "new Fx.Tween('side_bar_scroll').start('margin-top', 0);" \
                       "$(this).setStyle('display', 'none');")
        div.add(down)



        outer_div = DivWdg()
        outer_div.add_style("overflow: hidden")
        div.add(outer_div)
        inner_div = DivWdg()
        inner_div.set_id("side_bar_scroll")
        inner_div.add_style("margin-top: 0px")
        outer_div.add(inner_div)


        behavior = {
            'type': 'wheel',
            'cbjs_action': 'spt.side_bar.scroll(evt,bvr)',
        }
        inner_div.add_behavior(behavior)



        # Project Views (main) side bar bookmark menu ...
        # (passing in an empty, "", title -- so that it is just the rounded div menu)
        #
        inner_div.add( my.get_bookmark_menu_wdg("", None, views) )
        inner_div.add(HtmlElement.br())


        return div



    def get_bookmark_menu_wdg(my, title, config, views):

        kwargs = {
            'title': title,
            'view': views,
            'config': config,
            'auto_size': my.kwargs.get('auto_size')
        }
        section_div = DivWdg()
        section_div.add_style("display: block")

        
        section_wdg = SideBarBookmarkMenuWdg(**kwargs)
        section_div.add(section_wdg)
        return section_div



    def get_onload_js(my):

        return r'''

spt.side_bar = {};

// Side bar panel functionality

//
//
spt.side_bar.load_section = function(evt, bvr)
{
    var dst_el = bvr.dst_el;
    var options = bvr.options;

    // get the class name from the destination element
    var top_el = dst_el.firstChild
    var class_name = top_el.getAttribute("spt_class_name")

    Effects.fade_out(dst_el, 150);

    var server = TacticServerStub.get();

    var kwargs = {'args': options};
    var widget_html = server.get_widget(class_name, kwargs);

    spt.behavior.replace_inner_html( dst_el, widget_html );

    Effects.fade_in(dst_el, 150);

}





// Displays a table to a target id
//
// behavior:
//  target_id: the target id element that the table will be put in
//  search_type: the search_type of the sobjects in the table
//  view: the view of the table
//
spt.side_bar.display_link_cbk = function(evt, bvr) {
    var target_id = bvr.target_id;
    var title = bvr.title;
    var options = bvr.options;
    var values = bvr.values;
    var is_popup = bvr.is_popup;

    spt.side_bar._display_link_action( target_id, title, options, values, is_popup );

}


spt.side_bar._display_link_action = function(target_id, title, options, values, is_popup)
{
    var busy_title = 'Load View';
    var busy_msg = 'View is now loading in a popup window ...';

    if( ! spt.is_TRUE(is_popup) ) {
        busy_msg = '"' + title + '" view is now loading ...';
    }

    //show busy message
    //spt.app_busy.show( busy_title, busy_msg );

    setTimeout( function() {
                        spt.side_bar._load_for_display_link_change(target_id, title, options, values, is_popup);
                        if( spt.is_TRUE(is_popup) )
                            spt.app_busy.hide();
                    }, 10 );
}


spt.side_bar._load_for_display_link_change = function(target_id, title, options, values, is_popup)
{
    // var link = spt.side_bar._link_display_info;
    var path = options['path'];

    // display a table
    var widget_class = options['class_name'];
    if (widget_class == null) {
        widget_class = "tactic.ui.panel.ViewPanelWdg";
    }
    options["title"] = title;
    if( spt.is_TRUE(is_popup) ) {
        options['target_id'] = target_id;
        spt.panel.load_popup(title, widget_class, options);
    }
    else {
        var target_element = $(target_id);

        var main_body = $('main_body');
        var tab_top = main_body.getElement(".spt_tab_top");
        spt.tab.top = tab_top;


        var class_name = options['class_name'];

        // Use path instead for the name
        //var element_name = options['element_name'];
        var element_name = options['path'];

        spt.tab.load_selected(element_name, title, class_name, options, values);

        // Set the state of the page
        var key = "top_layout";
        var panel_id = "main_body";
        var server = TacticServerStub.get();
        server.set_application_state(key, panel_id, widget_class, options, values);

        // set the url hash
        if (typeof(options.element_name) != "undefined") {
            var hash = "/link/"+options.element_name;
            if( ! spt.browser.is_Firefox() && ! spt.browser.is_Opera() ) {
                hash = encodeURI( hash );
            }
            var state = {
                mode: 'tab',
                hash: hash,
                element_name: options.element_name,
                title: title
            };
            var url = "link/"+options.element_name;
            spt.hash.set_hash( state, title, url );

        }
        else {
            alert("DEPRECATD: set hash in sidebar load_display");
            var kwargs = {'predefined': true};
            spt.panel.set_hash(panel_id, widget_class, options, kwargs)
        }
    }
}



// Command that occurs when a user clicks on a link
//
spt.side_bar.DisplayLinkCmd = function(target_id, title, options, values, is_popup) {
    
    this.target_id = target_id;
    this.title = title;
    this.options = options;
    this.values = values;
    this.is_popup = is_popup;

    this.prev_options = {};

    this.get_description = function () { return "DisplayLinkCmd"};
    this.execute = function() { 

        // get the target element
        var target_element = $(this.target_id);

        this.redo();
    }


    this.redo = function() {


        // display a table
        var widget_class = this.options['class_name'];
        if (widget_class == null) {
            widget_class = "tactic.ui.panel.ViewPanelWdg";
        }

        var path = this.options['path'];

        if (this.is_popup == 'true' || this.is_popup == true) {
            // set a default width of 600px
            //this.options['width'] = '600px';
            this.options['target_id'] = this.target_id;
            spt.panel.load_popup(path, widget_class, this.options);
        }
        else {
            var target_element = $(this.target_id);

            //$("breadcrumb").innerHTML = '<div><img src="/context/icons/common/indicator_snake.gif" border="0"> ' +
            //                            'Loading "' + this.title + '" ...</div>';

            spt.panel.load(target_element, widget_class, this.options, this.values)

            // Set the state of the page
            var key = "top_layout";
            var panel_id = "main_body";
            var server = TacticServerStub.get();

            // Make sure to send back the link title for the saved last link options
            this.options["title"] = this.title

            server.set_application_state(key, panel_id, widget_class, this.options, this.values);

            // also set the breadcrumb
            //$("breadcrumb").innerHTML = path
            //$("breadcrumb").innerHTML = this.title

            // set the url hash
            if (typeof(this.options.element_name) != "undefined") {
                var hash = "link="+this.options.element_name;
                if( ! spt.browser.is_Firefox && ! spt.browser.is_Opera ) {
                    hash = encodeURI( hash );
                }
                spt.last_hash = hash;
                window.location.hash = hash;
            }

        }

    }

    this.undo = function() {

        var target_element = $(this.target_id);

        Effects.fade_out(this.prev_target_id, 150);

        var server = TacticServerStub.get();

        // display a table
        widget_class = "tactic.ui.panel.ViewPanelWdg";
        args = {
            "search_type": this.prev_search_type,
            "view": this.prev_view,
            "search_view": this.prev_search_view
        };

        var kwargs = {'args': args};
        widget_html = server.get_widget(widget_class, kwargs);

        // Set the state of the page
        key = "top_layout";
        panel_name = "main_body";
        widget_class = "tactic.ui.panel.ViewPanelWdg";
        server.set_application_state(key, panel_name, widget_class, args);

        // replace the former element with the new element
        spt.behavior.replace_inner_html( target_element, widget_html );
        Effects.fade_in(this.prev_target_id, 150);


        // set the url
        var hash = "search_type=" + this.search_type + "&view=" + this.view;
        window.location.hash = hash;

    }

}


// This occurs when you use the mouse wheel on the side bar. It causes the
// whole side bar to scroll
//
spt.side_bar.scroll = function(evt, bvr) {
    var property = "margin-top";
    var margin = $("side_bar_scroll").getStyle(property);
    margin = parseInt(margin.replace("px", ""));
    if (evt.wheel < 0) {
        margin -= 30;
    }
    else {
        margin += 30;
    }

    if (margin > 0) {
        margin = 0;
        $("side_bar_scroll_down").setStyle('display', 'none');
        var pos = $(window).getScroll();
        $(window).scrollTo(pos.x, pos.y - 30);
    }
    else {
        $("side_bar_scroll_down").setStyle('display', 'block');
    }
    $("side_bar_scroll").setStyle(property, margin);
}




// This callback is called when clicking on a section link in the side bar.
// It toggles the display of a section and then sets the state
//
// bvr.dst_el: id of the section that is displayed

spt.side_bar.toggle_section_display_cbk = function(evt, bvr)
{
    var click_el = $(bvr.src_el);
    //hide el could be the section or div inside the section
    if (spt.has_class(click_el, 'spt_side_bar_element'))
        var hide_el = click_el.getElement(".spt_side_bar_section_content");
    else
        var hide_el = spt.get_cousin(click_el, ".spt_side_bar_element", ".spt_side_bar_section_content");

    bvr.slide_direction = "vertical";
    bvr.dst_el = hide_el;

    var arrow_img_el = click_el.getElement('img');
    var arrow_img_src = arrow_img_el.get('src');

    if( arrow_img_src.match( /_right_/ ) ) {
        arrow_img_el.set('src', arrow_img_src.replace(/_right_/,"_down_"));

        hide_el.setStyle("display", "block");
        hide_el.setStyle("margin-top", "-"+hide_el.getSize().y+"px")
        new Fx.Tween(hide_el, {duration:"short"}).start('margin-top', "0px");

    }
    else {
        arrow_img_el.set('src', arrow_img_src.replace(/_down_/,"_right_"));

        hide_el.setStyle("margin-top", "0px")
        new Fx.Tween(hide_el, {duration:"short"}).start('margin-top', "-"+hide_el.getSize().y+"px");
        //hide_el.setStyle("display", "none");



    }

    spt.side_bar.store_state();
}




//
// Side bar state methods
//
// Stores the state of the sidebar in a cookie.
spt.side_bar.cookie = null;
spt.side_bar.get_state = function()
{
    if (spt.side_bar_cookie == null) {
        spt.side_bar.cookie = new Cookie('sidebar_status');
    }
    return spt.side_bar.cookie;
}


spt.side_bar.store_state = function()
{
    var elements = $("side_bar").getElements(".spt_side_bar_section_content");

    var open_folders = {};

    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        if ( element.getStyle("display") == "block" ) {
            var path = element.getAttribute("spt_path");
            open_folders[path] = true;
        }
    }

    var state = spt.side_bar.get_state();
    state.write(JSON.stringify(open_folders))
}



spt.side_bar.restore_state = function()
{
    var side_bar_el = $("side_bar");
    if( ! side_bar_el ) {
        spt.js_log.warning( "WARNING: in spt.side_bar.restore_state(), element with ID 'side_bar' not found." );
        return;
    }

    var elements = side_bar_el.getElements(".spt_side_bar_section_content");

    var state = spt.side_bar.get_state();
    var open_folders = {};
    if( state.read() ) {
        open_folders = JSON.parse( state.read() );
    }
    else {
        return;
    }

    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        var path = element.getAttribute("spt_path");

        // Find the element with the arrow indicator for open or closed state of section ...
        var prev = $(element).getPrevious();
        if (!prev) continue;
        var arrow_img_el = prev.getElement("img");
        var img_src = arrow_img_el.get('src');

        if (open_folders[path] == true) {
            element.setStyle("display", "block");
            arrow_img_el.set('src', img_src.replace(/_right_/,"_down_"));
        }
        else {
            element.setStyle("display", "none");
            arrow_img_el.set('src', img_src.replace(/_down_/,"_right_"));
        }
    }
}



// action widget callback
//
spt.side_bar.manage_section_action_cbk = function(element, view, is_personal) {

    // get the value of the element
    var value = element.value;
    if (value == "save") {
        // it could be saving other sub-views involved as well like reordering 
        // within the predefined views
        if (confirm("Save ordering of this view [" + view + "] ?") ) {
            var server = TacticServerStub.get();
            server.start({"title": "Updating views"});

            for (changed_view in spt.side_bar.changed_views) {
                var search_type = "SideBarWdg";
                spt.side_bar.save_view(search_type, changed_view, is_personal);
            }
            spt.side_bar.changed_views = {};
            server.finish();
            spt.panel.refresh("side_bar");
            spt.panel.refresh("ManageSideBarBookmark_" + view);
        }
    }
    else if (value == "predefined") {
        spt.popup.open('predefined_side_bar');
    }

    else if ( ["new_link",'new_folder','new_separator'].contains(value) ) {
        spt.side_bar.context_menu_cbk(value, view, is_personal);
    }

    else if (value == "save_folder") {
        var popup_id = "New Item Panel";
        var values = spt.api.Utility.get_input_values(popup_id , null, false);
        // Convert the user input new folder name all in lower case and replace all spaces with underscores.
        //var new_title = values['new_name'].toLowerCase().replace(/ /g,"_");;
        var new_title = values['new_title'];
        var new_name = values['new_name']
     
        if (spt.input.has_special_chars(new_name)) {
            alert("The view name cannot contain special characters.  Please try again.");  
            return;
        }
        if (spt.input.start_with_num(new_name)) {
            alert("A view starting with a number is not allowed.");
            return;
        }

        // folder view cannot be one of the predefined views
        var predefined_views = ['_my_tactic', '_preproduction','_asset_pipeline', '_shot_pipeline', '_site_admin', '_project_admin', '_overview', '_application', '_editorial', '_template', 'definition', 'search', 'publish'];
        if (predefined_views.contains(new_title)) {
            alert('This view name [' + new_name + '] is reserved');
            return;
        }
        
        
        // don't assign login for "project_view", but personal and project view 
        // share the same definition
        var kwargs = {};
        var kwargs2 = {};
        if (is_personal) {
            var user = spt.Environment.get().get_user();
            kwargs['login'] = user;
            kwargs2['login'] = user;
            new_name = user + '.' +  new_name;
        } 
      
        // save this user-defined view
        var server = TacticServerStub.get();
        server.start({"title": "Adding folder", 
            "description": "Adding folder [" + new_title + "]"});
        kwargs['class_name'] ='SideBarSectionLinkWdg';
        kwargs['element_attrs'] = {'title': new_title};
        kwargs['display_options'] = {'view': new_name};
        kwargs['auto_unique_name'] = false;
        kwargs['auto_unique_view'] = false;
        kwargs['unique'] = true;
        
        try{       
            // add it to the project_view
            search_type = 'SideBarWdg';

            // Order matters here
            // set an option to auto adjust the element_name to be unique
            var info = server.add_config_element(search_type, 'definition', new_name, kwargs);
            var unique_el_name = info['element_name'];
            // now add to project_view or my_view_...
            server.add_config_element(search_type, view, unique_el_name, kwargs2);
            
            // only extract elements inside the folder view "new_folder"
            var folder_elements = spt.side_bar.get_elements('new_folder', popup_id);
            var folder_element_names = [];
            folder_elements.each( function(x) 
                    {folder_element_names.push(x.getAttribute("spt_element_name"))});
            if (folder_element_names.length > 0)
                server.update_config(search_type, unique_el_name, folder_element_names, kwargs2);

            server.finish();
        }
        catch(err) {
            var error_str = spt.exception.handler(err);
            alert(error_str);
            server.abort();
            return;
        }
        //refresh 
        spt.popup.destroy(popup_id);
        spt.panel.refresh("ManageSideBarBookmark_" + view);
        spt.panel.refresh("side_bar");
    }
    else if (value == "save_link") {
        var popup_id = "New Item Panel";
        var values = spt.api.Utility.get_input_values(popup_id , null, false);
        // Convert the user input link title all in lower case and replace all spaces with underscores.
        var link_name = values['new_link_title'].toLowerCase().replace(/ /g,"_");
        var include_search_view = values["include_search_view"] == 'on'; 

        if (spt.input.has_special_chars(link_name)) {
            alert("The view name cannot contain special characters.  Please try again.");  
            return;
        }
      
        // link name cannot be one of the predefined views
        var predefined_views = ['_my_tactic', '_preproduction','_asset_pipeline', '_shot_pipeline', '_site_admin', '_project_admin', '_overview', '_application', '_editorial', '_template', 'definition', 'search', 'publish','edit','insert','edit_definition'];
        if (predefined_views.contains(link_name)) {
            alert('This view name [' + link_name + '] is reserved');
            return;
        }
            
        var new_title = link_name;
        var search_type = values['new_search_type'];
        if (!link_name || !search_type) {
            alert('A title and a search type are required.');
            return;
        }
     
        
        var kwargs = {};
        var kwargs2 = {};
        var new_view = values['new_link_view'];
        if (is_personal) {
            var user = spt.Environment.get().get_user();
            kwargs['login'] = user;
            kwargs2['login'] = user;
            link_name = user + '.' +  link_name;
            //new_view = user + '.' + new_view;
        }

        if (confirm("Save this link [" + new_title + "] ?") ) {
            try {
                var server = TacticServerStub.get();
                server.start({"title": "Adding link",
                    "description": "Adding link [" + new_title + "]"});
                //hard-code table view for now
                
                kwargs['class_name'] = 'LinkWdg';
                kwargs['element_attrs'] = {'title': new_title};
                
                var display_options =  {'search_type': search_type, 'view': new_view};
                if (include_search_view) {
                    display_options['search_view'] = 'link_search:' + new_view;
                }
                // special case for CustomLayoutWdg
                if (search_type == 'CustomLayoutWdg') {
                    delete display_options['search_view'];
                    delete display_options['search_type'];
                    display_options['class_name'] = 'tactic.ui.panel.CustomLayoutWdg';
                }
                kwargs['display_options'] = display_options;
                
                //kwargs['auto_unique_name'] = true;
                kwargs['unique'] = true;
                
                // add it to the view, if view is my personal view, add login
                search_type = 'SideBarWdg';
                var info = server.add_config_element(search_type, 'definition', link_name, kwargs);
                var unique_el_name = info['element_name'];
                
                // now add to project_view
                server.add_config_element(search_type, view, unique_el_name, kwargs2);
                server.finish();
                //refresh 
                spt.popup.destroy(popup_id);
                spt.panel.refresh("ManageSideBarBookmark_" + view);
                spt.panel.refresh("side_bar");
            }
            catch(e) {
                alert(spt.exception.handler(e));
            }
            
        }
    }
    else if (value == "save_separator") {
        var popup_id = "New Item Panel";
        var name = 'separator';
        
        var server = TacticServerStub.get();
        server.start({"title": "Adding separator"});
        var kwargs = {'class_name' : 'SeparatorWdg',
                      'element_attrs' : {'title': 'Separator'},
                      'unique': false,
                      'auto_unique_name': true,
                       'auto_unique_view': true}; 
        // add it to the project_view
        search_type = 'SideBarWdg';
        var kwargs2 = {};

        //have login for the view, and definition
        if (is_personal){
            var user = spt.Environment.get().get_user();
            kwargs['login'] = user;
            kwargs2['login'] = user;
            name = user + '.' +  name;
        }

        var info = server.add_config_element(search_type, 'definition', name, kwargs);
        var unique_el_name = info['element_name'];
        
        // now add to project_view
        server.add_config_element(search_type, view, unique_el_name, kwargs2);
        server.finish();
        //refresh 
        spt.popup.destroy(popup_id);
        spt.panel.refresh("ManageSideBarBookmark_" + view);
        spt.panel.refresh("side_bar");
        
    }
    else {
        alert("Unimplemented option: " + value);
    }

    element.value = "";
}


// save the changed views
spt.side_bar.save_view = function(search_type, view, is_personal, list_top) {

    // backwards compatibility (this is an id)
    if (typeof(list_top) == 'undefined') {

        var elements;
        if (view == "definition") {
            elements = spt.side_bar.get_elements(view, "menu_item_definition_list");
        }
        else {
            elements = spt.side_bar.get_elements(view);
        }
    }
    else {
        elements = spt.side_bar.get_elements(view, list_top);
    }


    if (spt.side_bar.found_view == false) {
        return;
    }

    var element_names = [];
    for (var i = 0; i < elements.length; i++) {
        var element_name = elements[i].getAttribute("spt_element_name");
        element_names.push(element_name);
    }
    var server = TacticServerStub.get();
    // will get unexpected results if multiple folders share the same view
    //
    var kwargs = {};
    if (is_personal){
        kwargs['login'] = spt.Environment.get().get_user();
    }
    //add the trashed items
    kwargs['deleted_element_names'] = spt.side_bar.trashed_items;
    
    server.update_config(search_type, view, element_names, kwargs);
    spt.side_bar.trashed_items = [];
}



// get all the elements of a specific view
spt.side_bar.found_view = false;
spt.side_bar.get_elements = function(view, list_id) {
    if (typeof(list_id) == 'undefined' || list_id == null) {
        list_id = "menu_item_list";
    }

    var elements = $(list_id).getElements(".spt_side_bar_element");
    if (typeof(view) == 'undefined') {
        return elements;
    }

    spt.side_bar.found_view = false;

    var data = {};
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];

        var element_view = element.getAttribute("spt_view");
        if (element_view == view) {
            spt.side_bar.found_view = true;
        }
        // ignore the dummy created when there are no elements
        if (element.hasClass("spt_side_bar_dummy")) {
            continue;
        }

        // dynamically create the list
        var element_list = data[element_view];
        if (element_list == null) {
            element_list = [];
            data[element_view] = element_list;
        }

        //var element_name = elements[i].getAttribute("spt_element_name");
        element_list.push(element);
    }
    if (spt.side_bar.found_view) {
        var element_list = data[view];
        if (element_list)
            return element_list;
        else
            return [];
    }
    else {
        // to prevent undefined from being returned
        return [];
    }
}





//
// Drag and drop actions for the elements
//

spt.side_bar.changed_views = {};
spt.side_bar.trashed_items = [];
spt.side_bar.active_elems = {};
spt.side_bar.pp_setup = function(evt, bvr, mouse_411)
{   
    var clonable = bvr.src_el;
    if (! clonable.hasClass("spt_side_bar_element")) {
        clonable = bvr.src_el.getParent('.spt_side_bar_element');
    }
    // make sure that the src element is actually a side bar element.
    //if (! bvr.src_el.hasClass("spt_side_bar_element")) {
    //    bvr.src_el = bvr.src_el.parentNode;
    //}

    var ghost_el = $(bvr.drag_el);
    if (!ghost_el) {
        var ghost_el = spt.mouse._create_drag_copy( bvr.src_el );
        bvr.drag_el = ghost_el;
    }

    if( ghost_el )
    {
        // Make a clone of the source div that we clicked on to drag ...
        var src_copy = spt.behavior.clone(clonable);
        var w = clonable.clientWidth;
        var h = clonable.clientHeight;


        // Use this if you want the initial ghost div position to be offset from mouse same as on mouse momve ...
        ghost_el.setStyle( "left", (mouse_411.curr_x + 10) );
        ghost_el.setStyle( "top", (mouse_411.curr_y + 10) );

        ghost_el.setStyle( "width", w );
        ghost_el.setStyle( "height", h );

        // Then plug the clone div into the Utility ghost_el div to be the contents of the drop ...
        ghost_el.innerHTML = "";
        ghost_el.appendChild( $(src_copy) );

        ghost_el.setStyle( "display", "block" );
        ghost_el.setStyle( "text-align", "left" );
        //ghost_el.setStyle( "background", "#4F4FC4");
        ghost_el.setStyle( "box-shadow", "0px 0px 5px rgba(0,0,0,0.5)");
    }
    else {
        spt.js_log.debug("WARNING: NO ghost el found in spt.side_bar.pp_setup() callback!");
    }
}


spt.side_bar.pp_motion = function(evt, bvr, mouse_411)
{
    var ghost_el = $(bvr.drag_el);
    if( ghost_el )
    {
        ghost_el.setStyle( "left", (mouse_411.curr_x + 10) );
        ghost_el.setStyle( "top", (mouse_411.curr_y + 10) );
        var elem = spt.side_bar.pp_find_drop_elem(evt, bvr, mouse_411);
        //make the Trash can having a hard border
        if (spt.side_bar.pp_is_trash(elem))
            spt.add_class(elem, 'look_menu_hover');
        else
        {
            elem = spt.side_bar.active_elems['trash'];
            if (elem)
                spt.remove_class(elem, 'look_menu_hover');
        }
    }
}
// Find valid droppable element
spt.side_bar.pp_find_drop_elem = function(evt, bvr)
{
    // find drop element inside out
    var found = false;
    var drop_on_el = spt.get_event_target(evt);
    while( drop_on_el ) {
        if( ('getAttribute' in drop_on_el) && drop_on_el.getAttribute("SPT_ACCEPT_DROP") == "manageSideBar" ) {
            found = true;
            break;
        }
        drop_on_el = drop_on_el.parentNode;
    }
    if ( found )
        return drop_on_el;
    else
        return null;
    
}

spt.side_bar.pp_is_trash = function(drop_on_el)
{
    if (drop_on_el && drop_on_el.hasClass("spt_side_bar_trash") == true)
    {
        spt.side_bar.active_elems['trash'] = drop_on_el;
        return true;
    }
    return false;
}
spt.side_bar.pp_action = function(evt, bvr)
{
    var ghost_el = bvr.drag_el;
    if( ! ghost_el ) {
        return;
    }


    // Grab the cloned div that we had plugged in as the contents (firstChild) of the ghost_el Utility div ...
    var ghost_content = ghost_el.removeChild( ghost_el.firstChild );
    ghost_el.innerHTML = "";
    ghost_el.style.display = "none";

    // find valid drop element
    var drop_on_el = spt.side_bar.pp_find_drop_elem(evt, bvr);
    if (!drop_on_el)
        return;

    var mode = bvr.mode;
    if (!mode) {
        // look for parent
        var start_content = bvr.src_el.getParent(".spt_side_bar_content");
        var end_content = drop_on_el.getParent(".spt_side_bar_content");
        if (end_content == null) {
            mode = "move";
        }
        else {

            var start_view = start_content.getAttribute("spt_view");
            var end_view = end_content.getAttribute("spt_view");

            if (start_view != end_view) {
                mode = "copy";
            }
            else {
                mode = "move";
            }
        }
    }

    var contents;

    if (mode == "copy") {
        contents = ghost_content;
    }
    else {
        // make sure that the contents is actually a side bar element.
        var contents = bvr.src_el;
        if (! contents.hasClass("spt_side_bar_element")) {
            contents = contents.getParent('.spt_side_bar_element');
        }

    }


    var view;
  
    // Record that the old view has changed if not in copy mode
    var old_view = contents.getAttribute("spt_view")
    if (mode != 'copy') {
        spt.side_bar.changed_views[old_view] = true;
    }

    // up one level if dropped on a section link
    if  (drop_on_el.hasClass("spt_side_bar_section_link"))
        drop_on_el = drop_on_el.getParent(".spt_side_bar_section");
    // if dropped on trash
    if (spt.side_bar.pp_is_trash(drop_on_el) ) {
        var name = contents.getAttribute('spt_element_name');
        spt.side_bar.trashed_items.push(name);
        contents.destroy();
        elem = spt.side_bar.active_elems['trash'];
        if (elem)
            spt.remove_class(elem, 'look_menu_hover');
        return;
    }
    // if dropped on a section or a section link
    
    else if( drop_on_el.hasClass("spt_side_bar_section") ) {
        var children = drop_on_el.getElements(".spt_side_bar_element");
        if (children[0] != null && !children[0].hasClass("spt_side_bar_dummy")) {
            contents.inject(children[0], 'before');
            view = children[0].getAttribute("spt_view");
        }
        else {
            var container = drop_on_el.getElement(".spt_side_bar_section_content");
            container.appendChild(contents);
            // get the view
            // FIXME: assume view == element_name
            //view = drop_on_el.getAttribute("spt_view");
            view = drop_on_el.getAttribute("spt_element_name");
        }

    }
    // if dropped on a link
    else if ( drop_on_el.hasClass("spt_side_bar_link") == true ) {
        contents.inject(drop_on_el, 'before');
        view = drop_on_el.getAttribute("spt_view");
    }
    else if( drop_on_el.hasClass("spt_section_top") ) {
        var children = drop_on_el.getElements(".spt_side_bar_element");
        var last = children[children.length-1];
        contents.inject(last, 'after');
        view = last.getAttribute("spt_view");
    }
    // if dropped on any other element
    else {
        var parent = drop_on_el.getParent(".spt_side_bar_element");
        contents.inject(parent, 'before');
        view = parent.getAttribute("spt_view");
    }

    // switch view
    if (view == null) {
        alert("view is NULL!!!!");
    }


    //
    if (mode == 'copy') {

        var element_name = contents.getAttribute("spt_element_name");
        var element_title = contents.getAttribute("spt_title");

        //var content_view = base + "_" + element_name;
        var content_view = element_name;
        if (content_view.substr(0,1) == "_") {
            content_view = content_view.substr(1, content_view.length);
        }



        // check to see what that there are no duplicate view titles
        var menu_item_list = contents.getParent(".spt_menu_item_list");
        elements = spt.side_bar.get_elements(view, menu_item_list);

        element_list = new Array();
        for (var i = 0; i < elements.length; i++) {
            var cur_element_name = elements[i].getAttribute("spt_element_name");
            pat = new RegExp( '^' + element_name+ '\d*');
            if (cur_element_name.match(pat)) {
                element_list.push(cur_element_name);
            }
        }
        if (element_list.length > 0) {
            content_view = content_view + element_list.length;
            element_title = element_title + element_list.length;
        }
        contents.setAttribute("spt_element_name", content_view);
        contents.setAttribute("spt_title", element_title);
        // set the new view of the element
        contents.setAttribute("spt_view", view);
        // go through the elements names and change them to the new view
        var elements = contents.getElements(".spt_side_bar_element");
        for (var i = 0; i < elements.length; i++) {
            var element = elements[i];
            element.setAttribute("spt_view", content_view);
        }


        // change the title
        var title = contents.getElement(".spt_side_bar_title");
        if (title){
            var title_icon = title.getFirst();
            if (!title_icon) {
                title.innerHTML = element_title;
            } else {
                title.innerHTML = '';
                title.appendChild(title_icon);
                title.appendText(element_title);
            }
        }

        spt.side_bar.changed_views[view] = true;
    }
    else {
        // set the new view of the element
        contents.setAttribute("spt_view", view);
        spt.side_bar.changed_views[view] = true;
    }

    if( bvr.class_name ) {
        spt.side_bar.display_element_info_cbk(evt,bvr);
    }
}



spt.side_bar.context_menu_cbk = function(action, view, is_personal) {

    var element_name = null;
    /*
    config = document.createElement('config')
    element = document.createElement('element')
    display =  document.createElement('display')
    config.appendChild(element);
    element.appendChild(display);
    */
    if (action == "new_link") {
        element_name = "new_link";
    }
    else if (action == "new_folder") {
        element_name = "new_folder";
    }
    else if (action == "new_separator") {
       element_name = "new_separator";
    }
    
    if (element_name) {
        var clone = spt.side_bar.add_new_item(view, element_name);
        //clone.setStyle('background', '#6CB87B');
        if (element_name =='new_separator') {
            
            spt.side_bar.manage_section_action_cbk({'value':'save_separator'},view, is_personal);
        }
       
    }
}



spt.side_bar.add_new_item = function(view, element_name, template_top) {

    var list_id = "menu_item_list";
    var options = {'type': element_name, 'view': view};
    var popup_id = "New Item Panel";

    new_item_class = 'tactic.ui.panel.ManageViewNewItemWdg';
    spt.panel.load_popup(popup_id, 'tactic.ui.panel.ManageViewNewItemWdg', options, {});
    // get the template menu items
    // index is prone to error, use element_name instead

    if ( typeof(template_top) == 'undefined' ) {
        template_top = $("menu_item_template");
    }
    var menu_item = template_top.getElement("div[spt_element_name=" + element_name +"]");
  
    if (!menu_item)
        return;

    var clone = spt.behavior.clone(menu_item);

    // get the element and inject after
    var div = $(popup_id).getElement('.spt_new_item');
    div.appendChild(clone);

    // now add some properties to the new element
    if (element_name ='new_folder')
        clone.addClass("spt_side_bar_section");
    else
        clone.addClass("spt_side_bar_element");

    clone.setAttribute("spt_view", view);
    // get the current name of the cloned element
    var clone_name = clone.getAttribute("spt_element_name");
    
    bvr = {};
    bvr.src_el = clone;
  
    
    return clone;

}





//
// Element info setting and saving
//
spt.side_bar.display_element_info_cbk = function(evt, bvr)
{
    var top = bvr.src_el.getParent(".spt_view_manager_top");
    if (!top)
        return;

    var detail_panel = top.getElement(".spt_view_manager_detail");

    var src_el = bvr.src_el;

    var element_name = src_el.getAttribute("spt_element_name");
    if (element_name == null) {
        src_el = src_el.getParent(".spt_side_bar_element");
        element_name = src_el.getAttribute("spt_element_name");
    }

    var search_type = detail_panel.getAttribute("spt_search_type");
    var personal = detail_panel.getAttribute("spt_personal");
    var view = src_el.getAttribute("spt_view");
    var path = src_el.getAttribute("spt_path");
    var login = detail_panel.getAttribute("spt_login");
    var is_default = src_el.getAttribute("spt_default");
    var config_xml = bvr["config_xml"];
    // rename
    if (config_xml) {
        //it could be double or single quotes
        var pat = new RegExp('(.*element .*name=(?:\"|\'))([^\\s\\t]*)((?:\"|\').*)')
        var m = config_xml.match(pat);
        if (m) {
            config_xml = config_xml.replace(pat, '$1' + element_name +'$3');
        }
    }
    else {
        config_xml = '';
    }
    var server = TacticServerStub.get();
    var class_name = bvr.class_name;
    var options = {
        'search_type': search_type,
        'view': view,
        'element_name': element_name,
        'config_xml': config_xml,
        'config_mode': bvr.config_mode,
        'path': path,
        'login': login,
        'default': is_default,
        'personal': personal
    };
    var fade = false;
    var values = {};
    spt.panel.load(detail_panel, class_name, options, values, fade);

 
}





spt.side_bar.save_definition_cbk = function( bvr )
{
    var view_manager_top = null;
    if( bvr ) {
        view_manager_top = bvr.src_el.getParent(".SPT_VIEW_MANAGER_TOP");
    }

    var panel = view_manager_top.getElement(".spt_view_manager_detail");
    
    var values = spt.api.Utility.get_input_values( panel );

    if (values.config_element_name == "") {
        alert("Please provide a name for this element");
        return;
    }

    values['update'] = "true";

    // execute the command with the widget
    var fade = false;
    spt.panel.refresh(panel, values, fade);

    spt.panel.refresh("side_bar");

    var elements = view_manager_top.getElements(".spt_view_manager_section");
    for (var i = 0; i < elements.length; i++) {
        var element = elements[i];
        if (element != null) {
            spt.panel.refresh(element);
        }
    }
}






        '''







class SideBarBookmarkMenuWdg(BaseRefreshWdg):
   
    ERR_MSG = 'SideBar_Error'
    def get_args_keys(cls):
        '''external settings which populate the widget'''
        return {
        'parent_view': 'Parent View of the search type to be displayed',
        'config_search_type': 'Search type parent of the view to be displayed',
        'view': 'Current View of the search type to be displayed',
        'title': 'The title that appears at the top of the section',
        'config': 'Explicit config xml',
        'width': 'The width of the sidebar',
        'prefix': 'A unique identifier for this widget',

        'recurse': 'Determines whether to recurse down sections',
        'mode': 'edit|view determines the mode of the widget',
        'default': "Determine whether to look just in default file",
        'sortable' : "Determine whether it is sortable"
        }
    get_args_keys = classmethod(get_args_keys)

    def get_target_id(my):
        '''get the target to which this side bar loads to'''
        return "main_body"


    def get_display(my):
        my.config_search_type = my.kwargs.get("config_search_type")
        if not my.config_search_type:
            my.config_search_type = "SideBarWdg"
        my.default = my.kwargs.get('default') == 'True'

        web = WebContainer.get_web()
        my.palette = web.get_palette()
        my.project = Project.get()

        title = my.kwargs.get('title')
        config = my.kwargs.get('config')
        view = my.kwargs.get('view')
        parent_view = my.kwargs.get('parent_view')
        sortable = my.kwargs.get('sortable')

        my.prefix = my.kwargs.get("prefix")
        if not my.prefix:
            my.prefix = "side_bar"


        width = my.kwargs.get('width')
        if not width:
            #width = "175"
            width = "100%"

        my.mode = my.kwargs.get("mode")
        if not my.mode:
            my.mode = 'view'



        div = DivWdg()
        if web.is_IE():
            div.add_style("text-align: left")
        background = my.palette.color("background3")
        if width == "100%":
            div.add_style("min-width: 175px")


        # create the top widgets
        label = SpanWdg()
        label.add(title)
        label.add_style("font-size: 13px")
        section_div = LabeledHidableWdg(label=label)
        div.add(section_div)

        section_div.set_attr('spt_class_name', Common.get_full_class_name(my))
        for name, value in my.kwargs.items():
            if name == "config":
                continue
            section_div.set_attr("spt_%s" % name, value)


        # get the content div
        project_div = RoundedCornerDivWdg(hex_color_code=background,corner_size="5")
        project_div.set_dimensions( width_str='%s' % width, content_height_str='100%' )
        section_div.add( project_div )

        content_div = project_div.get_content_wdg()
        content_div.add_class("spt_side_bar_content")
        content_div.add_attr("spt_view", view)
        content_div.add_style("text-align: left")

        auto_size = my.kwargs.get("auto_size")
        #if auto_size in ['true', True]:
        if True:
            content_div.add_behavior( {
                'type': 'load',
                'cbjs_action': '''
                var size = $(window).getSize();
                //bvr.src_el.setStyle("min-height", size.y - 60);
                bvr.src_el.setStyle("min-height", size.y);
                //bvr.src_el.setStyle("overflow-y", "auto");
                //bvr.src_el.setStyle("overflow-x", "hidden");
                '''
            } )
        #content_div.add_style("margin-right: -4px")
        content_div.add_style("height: 100%")

        # add in a context smart menu for all links
        my.add_link_context_menu(content_div)



        if type(view) in types.StringTypes:
            view = [view]

        # draw each view
        for view_item in view:
            is_personal = False
            if view_item.startswith('my_view_'):
                is_personal = True

            config = my.get_config(my.config_search_type, view_item, default=my.default, personal=is_personal)
            if not config:
                continue


            # make up a title
            title = DivWdg()
            title.add_gradient( "background", "side_bar_title", 0, -15, default="background" )
            title.add_color( "color", "side_bar_title_color", default="color" )
            view_margin_top = '4px'
            title.add_styles( "margin-top: %s; margin-bottom: 3px; vertical-align: middle" % view_margin_top )
            if not web.is_IE():
                title.add_styles( "margin-left: -5px; margin-right: -5px;")
            title.add_looks( "navmenu_header" )
            title.add_style( "height: 18px" )
            title.add_style( "padding-top: 2px" )


            view_attrs = config.get_view_attributes()
            tt = view_attrs.get("title")
            if not tt:
                if view_item.startswith("my_view_"):
                    tt = "My Views"
                else:
                    tt = view_item.replace("_", " ");
                tt = tt.capitalize()


            title_label = SpanWdg()
            title_label.add_styles( "margin-left: 6px; padding-bottom: 2px;" )
            title_label.add_looks( "fnt_title_5 fnt_bold" )
            title_label.add( tt )
            title.add( title_label )

            content_div.add( title )
            if sortable:
                title.add_behavior({'type': 'click_up',
                    'cbjs_action': "spt.panel.refresh('ManageSideBarBookmark_%s')" % view_item});
            info = { 'counter' : 10, 'view': view_item, 'level': 1 }

            ret_val = my.generate_section( config, content_div, info, personal=is_personal )
            if ret_val == 'empty':
                title.add_style("display: none")

            error_list = Container.get_seq(my.ERR_MSG)
            if error_list: 
                span = SpanWdg()
                span.add_style('background', 'red')
                span.add('<br/>'.join(error_list))
                content_div.add(span)
                Container.clear_seq(my.ERR_MSG)
            my.add_dummy(config, content_div) 




        # display the schema links on the bottom of the the admin views
        if view_item == "admin_views":        
            config_xml = my.get_schema_xml()
            config = WidgetConfig.get(xml=config_xml, view='schema')
            my.generate_section( config, content_div, info, personal=False, use_same_config=True )

        return div




    def get_schema_xml(my):

        config_xml = []
       
        config_xml.append( '''
        <config>
        <schema>
        <element name='schema_view' title='Schema Views' icon="dependency">
          <display class='FolderWdg'>
              <view>schema_view</view>
          </display>
        </element>
        </schema>
        ''')

        # get project type schema
        project = my.project
        project_code = project.get_code()
        project_type = project.get_type()
        schema = Schema.get_by_code(project_code)

        if project_code in ['sthpw', 'admin']:
            my.is_admin = True
        else:
            my.is_admin = False



        config_xml.append( '''
        <schema_view>
        ''')

        if not my.is_admin:
            config_xml.append( '''
            <element name='_current_schema' title='%s Schema'>
              <display class='FolderWdg'>
                <view>_current_schema</view>
              </display>
            </element>
            ''' % project_code.capitalize() )

            if project_type != "simple":
                config_xml.append( '''
                <element name='_prod_schema' title='%s Schema'>
                  <display class='FolderWdg'>
                    <view>_prod_schema</view>
                  </display>
                </element>
                ''' % project_type.capitalize() )

            config_xml.append( '''
            <element name='_config_schema' title='Config Schema'>
              <display class='FolderWdg'>
                <view>_config_schema</view>
              </display>
            </element>
            ''')

        config_xml.append( '''
        <element name='_admin_schema' title='Global Config/Data'>
          <display class='FolderWdg'>
            <view>_admin_schema</view>
          </display>
        </element>
        ''')

        config_xml.append( '''
        </schema_view>

        ''')


        if schema:
            my.get_schema_snippet("_current_schema", schema, config_xml)
        if project_type:
            schema = Schema.get_predefined_schema(project_type)
            my.get_schema_snippet("_prod_schema", schema, config_xml)


        config_schema = Schema.get_predefined_schema('config')
        my.get_schema_snippet("_config_schema", config_schema, config_xml)
        schema = Schema.get_admin_schema()
        my.get_schema_snippet("_admin_schema", schema, config_xml)


        config_xml.append( '''
        </config>
        ''')

        xml = "".join(config_xml)
        return xml


    def get_schema_snippet(cls, view, schema, config_xml):
        schema_xml = schema.get_xml_value("schema")
        search_types = schema_xml.get_values("schema/search_type/@name")
        if not search_types:
            return

        search_types.sort()

        config_xml.append( '''
        <%s>
        ''' % view)
        for search_type in search_types:
            try:
                search_type_obj = SearchType.get(search_type)
            except:
                print "WARNING: search type [%s] does not exist" % search_type
                continue
            if not search_type_obj:
                continue

            title = search_type_obj.get_value("title")
            if not title:
                title = search_type
            config_xml.append( '''
            <element name='%s' title='%s'>
              <display class='LinkWdg'>
                  <search_type>%s</search_type>
                  <view>table</view>
                  <schema_default_view>true</schema_default_view>
              </display>
            </element>
            ''' % (search_type, title, search_type) )
        config_xml.append( '''
        </%s>
        ''' % view)
    get_schema_snippet = classmethod(get_schema_snippet)



    def add_link_context_menu(my, widget):

        from tactic.ui.container import  Menu, MenuItem
        menu = Menu(width=180)
        menu.set_allow_icons(False)
        #menu.set_setup_cbfn( 'spt.dg_table.smenu_ctx.setup_cbk' )

        menu_item = MenuItem(type='title', label='Navigate')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Open Link In New Tab')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var link = spt.smenu.get_activator(bvr);
            var main_body = $('main_body');
            var tab_top = main_body.getElement(".spt_tab_top");
            spt.tab.top = tab_top;
            var class_name = link.getAttribute("spt_class_name");

            var kwargs_str = link.getAttribute("spt_kwargs");
            kwargs_str = kwargs_str.replace(/&quote;/g, '"');
            var kwargs = JSON.parse(kwargs_str);

            var element_name = link.getAttribute("spt_element_name");
            var title = link.getAttribute("spt_title");
            spt.tab.add_new(element_name, title, class_name, kwargs);

            '''
        } )
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Open Link In New Window')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var link = spt.smenu.get_activator(bvr);
            var main_body = $('main_body');
            var class_name = link.getAttribute("spt_class_name");

            var kwargs_str = link.getAttribute("spt_kwargs");
            kwargs_str = kwargs_str.replace(/&quote;/g, '"');
            var kwargs = JSON.parse(kwargs_str);

            var element_name = link.getAttribute("spt_element_name");
            var title = link.getAttribute("spt_title");
            kwargs['title'] = title;
            spt.panel.load_popup(title, class_name, kwargs);

            '''
        } )
        menu.add(menu_item)


        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            menu_item = MenuItem(type='title', label='Actions')
            menu.add(menu_item)

            #menu_item = MenuItem(type='action', label='Edit Link')
            #menu.add(menu_item)
            menu_item = MenuItem(type='action', label='Remove Link')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'cbjs_action': '''
                var link = spt.smenu.get_activator(bvr);
                var element_name = link.getAttribute("spt_element_name");

                spt.app_busy.show("Removing link ["+element_name+"]");
                var server = TacticServerStub.get();
                var search_type = "SideBarWdg";


                var section = link.getParent(".spt_side_bar_section");
                var view;
                if (section == null) {
                    view = "project_view";
                }
                else {
                    view = section.getAttribute("spt_element_name");
                }    
                server.update_config(search_type, view, [], {deleted_element_names:[element_name]});
                spt.panel.refresh("side_bar");
                spt.app_busy.hide();
                '''
            } )

            menu_item = MenuItem(type='action', label='Edit Side Bar')
            menu.add(menu_item)
            menu_item.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.tab.set_main_body_tab();
                var class_name = 'tactic.ui.panel.ManageViewPanelWdg';
                var kwargs = {
                    help_alias: 'managing-sidebar'
                };
                spt.tab.add_new("manage_project_views", "Manage Side Bar", class_name, kwargs);
            '''
            } )

        menus = [menu.get_data()]
        menus_in = {
            'LINK_CTX': menus,
        }
        SmartMenu.attach_smart_context_menu( widget, menus_in, False )








    def add_internal_config(configs, views):
        '''add an internal config based on project base type'''
        project = Project.get()
        project_type = project.get_base_type()
        # catch potential invalid xpath error
        try:
            if project_type:
                tmp_path = __file__
                dir_name = os.path.dirname(tmp_path)
                file_path="%s/../config/%s-conf.xml" % (dir_name, project_type)
                if os.path.exists(file_path):
                    for view in views:
                        config = WidgetConfig.get(file_path=file_path, view=view)
                    
                        view_node = config.get_view_node()
                        if view_node is not None:
                            configs.append(config)

            # finally, just look at the DEFAULT config
            tmp_path = __file__
            dir_name = os.path.dirname(tmp_path)
            file_path="%s/../config/%s-conf.xml" % (dir_name, "DEFAULT")
                
            if os.path.exists(file_path):
                for view in views:
                    config = WidgetConfig.get(file_path=file_path, view=view)
                 
                    view_node = config.get_view_node()

                    if view_node is not None:
                        configs.append(config)

        except XmlException, e:
            msg = "Error with view [%s]"% ' '.join(views)
            print "Error: ", str(e)
            
            error_list = Container.get_seq(SideBarBookmarkMenuWdg.ERR_MSG)
            if msg not in error_list:
                Container.append_seq(SideBarBookmarkMenuWdg.ERR_MSG, msg)
                print e.__str__()


    add_internal_config = staticmethod(add_internal_config)

   

    def get_config(cls, config_search_type, view,  default=False, personal=False):

        config = None
        configs = []
        login = None
        defined_view = view
        '''
        if '.' in view:
            parts  = view.split('.')
            login = parts[0]
            defined_view = parts[1]
        '''
        # this is really for the predefined view that shouldn't go to the db
        # otherwise, it is a never ending cycle.
        if default:
            views = [defined_view, 'definition']
            SideBarBookmarkMenuWdg.add_internal_config(configs, views)
            
        # special condition for children
        elif view in ['children']:
            tmp_path = __file__
            dir_name = os.path.dirname(tmp_path)
            file_path="%s/../config/children-conf.xml" % (dir_name)
            config = WidgetConfig.get(file_path=file_path, view=defined_view)
            configs.append(config)

          
        elif view == "definition":
            # look for a definition in the database
            search = Search("config/widget_config")
            search.add_filter("search_type", config_search_type)
            search.add_filter("view", "definition")
            # lower the chance of getting some other definition files
            if personal:
                login = Environment.get_user_name()
            
            search.add_filter("login", login)

            config = search.get_sobject()
            if config:
                configs.append(config)
            # We should not allow redefinition of a predefined item
            # so it is fine to add internal config for definition
            # then look for a definition in the definition file
            SideBarBookmarkMenuWdg.add_internal_config(configs, ['definition'])
        
       

        else:
            # first look in the database
            search = Search("config/widget_config")
            search.add_filter("search_type", config_search_type)
            search.add_filter("view", view)
            #search.add_filter("login", login)
            
            config = search.get_sobject()
            if config:
                configs.append(config)
            # then look for a file
           
            SideBarBookmarkMenuWdg.add_internal_config(configs, [defined_view])
            
            logins = []
            if personal:
                logins.append(Environment.get_user_name())

            logins.append(None)
            for login in logins:
                # look for a definition in the database
                search = Search("config/widget_config")
                search.add_filter("search_type", config_search_type)
                search.add_filter("view", "definition")
                # lower the chance of getting some other definition files
                search.add_filter("login", login)
                
                key = '%s|definition|%s'%(config_search_type, login)
                config = WidgetDbConfig.get_by_search(search, key)
                #config = search.get_sobject()
                if config:
                    configs.append(config)


            # then look for a definition in the definition file
            SideBarBookmarkMenuWdg.add_internal_config(configs, ['definition'])

        widget_config_view = WidgetConfigView(config_search_type, view, configs)

        return widget_config_view

    get_config = classmethod(get_config)

    def add_dummy(my, config, subsection_div):
        div = DivWdg()
        div.add_attr("spt_view", config.get_view() )
        div.add_class("spt_side_bar_element")
        div.add_class("spt_side_bar_dummy")
        div.add( my.get_drop_wdg() )
        subsection_div.add(div)

    def generate_section( my, config, subsection_div, info, base_path="", personal=False, use_same_config=False ):

        title = my.kwargs.get('title')
        view = my.kwargs.get('view')
        parent_view = my.kwargs.get('parent_view')
        sortable = my.kwargs.get('sortable')

        base_path_flag = True
        if not base_path:
            base_path = "/%s" % info.get('view').capitalize()
            base_path_flag = False
        current_path = base_path

        # add in the elements
        if config.get_view() == "definition":
            element_names = config.get_element_names()
            sort = False
            # not sorting for now
            if sort == True:
                element_names.sort()
        else:
            element_names = config.get_element_names()


        if not element_names:
            return "empty"
        
        # if there are no elements, then just add a drop widget
        if not element_names:
            if my.mode == 'view':
                item_div = DivWdg()
                item_div.add_style("margin: 3px")
                item_div.add_color("color", "color")
                item_div.add_style("opacity: 0.5")
                item_div.add("<i>-- No items --</i>")
                subsection_div.add(item_div)
            else:
                my.add_dummy(config, subsection_div)
            return

        user = Environment.get_user_name()

        for element_name in element_names:
            if not element_name:
                print "WARNING: element name is None in Sidebar config"
                continue

            display_class = config.get_display_handler(element_name)

            # project specific key
            security = Environment.get_security()
            if security.get_version() == 1:
                default_access = "view"
                key = element_name
                if not security.check_access("side_bar", key, "view", default=default_access):
                    continue
            else:
                key = {'project': my.project.get_code(), 'element': element_name}
                key2 = {'element': element_name}
                key3 = {'project': my.project.get_code(), 'element': '*'}
                key4 = {'element': '*'}
                keys = [key, key2, key3, key4]
                if element_name.startswith('%s.'%user):
                    # personal view is default to be viewable
                    if not security.check_access("link", keys, "view", default="view"):
                        continue
                elif not security.check_access("link", keys, "view", default="deny"):
                    continue
                # backwards compatibility
                #if not security.check_access("side_bar", keys, "view", default="deny"):
                #    continue



            # TESTING: backwards compatibility
            """
            access = security.get_access("link", keys)
            # if an access is not defined, then check
            if access != None:
                allowed = security.compare_access(access, "view")
            else:
                # otherwise check for "side_bar" rule for backwards
                # compatibility
                access = security.get_access("side_bar", keys)
                allowed = security.compare_access(access, "view")
                if allowed == None:
                    allowed = False

            if not allowed:
                return
            """





            if display_class == "SeparatorWdg":
                options = config.get_display_options(element_name)
                div = my.get_separator_wdg(element_name, config, options)
                subsection_div.add(div)
                continue

            elif display_class == "TitleWdg":
                options = config.get_display_options(element_name)
                div = my.get_title_wdg(element_name, config, options)
                subsection_div.add(div)
                continue

            elif display_class in ["SideBarSectionLinkWdg","FolderWdg"]:
               options = config.get_display_options(element_name)
               div = my.get_folder_wdg(element_name, config, options, base_path, current_path, info, personal, use_same_config)
               subsection_div.add( div )

            else:
                # assume LinkWdg, it's too loosely defined now
                options = config.get_display_options(element_name)
                options['path'] = '%s/%s' % (current_path, element_name)

                # If is not link widget then remap dynamically
                if display_class != 'LinkWdg':
                    options['class_name'] = display_class

                link_wdg = my._get_link_wdg(element_name, config, options, current_path, info)
                if link_wdg:
                    subsection_div.add(link_wdg)

        # ------------------------------------------
        # end of 'for element_name in element_names'
        # ------------------------------------------

        # @@@
        # if base_path_flag:
        #     subsection_div.add( "<div style='height: 8px;'><HR/></div>" )



    def get_drop_wdg(my):
        if my.mode == 'view':
            return SpanWdg()
        hr = DivWdg()
        hr.set_attr("SPT_ACCEPT_DROP", "manageSideBar")
        hr.add_style("height: 5px")
        hr.add_style("width: 150px")
        #hr.add_style("border: solid 1px black")
        hr.add_style("position: absolute")
        hr.add_event("onmouseover", "this.getChildren()[0].style.display=''")
        hr.add_event("onmouseout", "this.getChildren()[0].style.display='none'")
        hr.add("<hr style='margin-top: 2px; size: 1px; color: #222; display: none'/>")
        return hr



    def get_title_wdg(my, element_name, config, options):
            div = DivWdg()
            div.add_attr("spt_view", config.get_view() )
            div.add_class("spt_side_bar_element")
            div.add_class("spt_side_bar_title")
            div.add_attr("spt_element_name", element_name)

            div.add_styles( "margin-top: 4px; margin-bottom: 3px; vertical-align: middle")
            div.add_styles( "margin-left: -5px; margin-right: -5px;")
            div.add_color( "background", "background3", -8, default="background3" )
            div.add_color( "color", "color3", default="color3" )
            div.add_style( "height: 18px" )
            div.add_style( "padding-top: 2px" )
            div.add_style( "padding-left: 5px" )
            div.add_style( "font-weight: bold" )

            #options = config.get_display_options(element_name)
            my.add_title_behavior(div, element_name, config, options)

            title = my._get_title(config, element_name)
            if not title:
                title = Common.get_display_title(element_name)

            div.add(title)

            return div


    def get_separator_wdg(my, element_name, config, options):
            div = DivWdg()
            div.add_attr("spt_view", config.get_view() )
            div.add_class("spt_side_bar_element")
            div.add_class("spt_side_bar_separator")
            div.add_attr("spt_element_name", element_name)

            hr =  HtmlElement.hr()
            hr.add_style("size: 1px")
            div.add(hr)
            div.add_style("height", "5")
            div.add_style("padding-left: 3px")

            options = config.get_display_options(element_name)
            my.add_separator_behavior(div, element_name, config, options)

            return div



    def _get_link_wdg(my, element_name, config, options, current_path, info):
        # put in a default class name
        class_name = options.get("class_name")
        widget_key = options.get("widget_key")
        if widget_key:
            class_name = WidgetClassHandler().get_display_handler(widget_key)
            options['class_name'] = class_name

        if not class_name:
            options['class_name'] = "tactic.ui.panel.ViewPanelWdg"

        link_wdg = my.get_link_wdg(element_name, config, options, info)

        return link_wdg





    def get_link_wdg(my, element_name, config, options, info):
        attributes = config.get_element_attributes(element_name)

        if my.mode != 'edit' and attributes.get("is_visible") == "false":
            return

        title = my._get_title(config, element_name)

        default_access = "view"
        path = options.get('path')



        link_wdg = DivWdg(css="hand")
        if my.mode == 'edit' and attributes.get("is_visible") == "false":
            link_wdg.add_style("opacity: 0.5")
            link_wdg.add_style("font-style: italic")

        link_wdg.add_style("cursor: pointer")
        link_wdg.add_style("padding: 2px 5px 2px 6px" )
        link_wdg.add_style("margin: 0px -3px 0px -3px" )
        link_wdg.set_round_corners(5)


        link_wdg.add_attr("spt_title", title)
        link_wdg.add_attr("spt_icon", attributes.get("icon"))
        link_wdg.add_attr("spt_view", config.get_view() )
        link_wdg.add_attr("spt_element_name", element_name)
        link_wdg.add_attr("spt_path", options['path'])
        link_wdg.add_attr("spt_view", config.get_view() )

        link_wdg.add_class("spt_side_bar_element")
        link_wdg.add_class("spt_side_bar_link")
       

        # add the mouseover color change
        bg_color = my.palette.color("background3")
        bg_color2 = my.palette.color("background3", 20)
        color = my.palette.color("color3")
        link_wdg.add_style("color: %s" % color)
        link_wdg.add_class("SPT_DTS")
        link_wdg.add_event("onmouseover", "this.style.background='%s'" % bg_color2)
        link_wdg.add_event("onmouseout", "this.style.background='%s'" % bg_color)
        link_wdg.add_looks("fnt_text")
        link_wdg.add_style("font-size: 12px")


        # add an invisible drop widget
        drop_wdg = my.get_drop_wdg()
        drop_wdg.add_style("margin-top: -3px")
        link_wdg.add(drop_wdg)

        span = SpanWdg()
        span.add_class("spt_side_bar_title")

        # add an icon
        icon = attributes.get("icon")
        if not icon:
            icon = "VIEW"

        if icon:
            icon = icon.upper()
            from pyasm.widget import IconWdg
            try:
                span.add( IconWdg(title, eval("IconWdg.%s" % icon) ) )
            except:
                pass


        span.add(title)
        link_wdg.add(span)


        my.add_link_behavior(link_wdg, element_name, config, options)


        return link_wdg



    def get_folder_wdg(my, element_name, config, options, base_path, current_path, info, personal, use_same_config):
        security = Environment.get_security()
        default_access = "view"

        title = my._get_title(config, element_name)

        attributes = config.get_element_attributes(element_name)

        if my.mode != 'edit' and attributes.get("is_visible") == "false":
            return

        options = config.get_display_options(element_name)

        state = attributes.get("state")

        paths = []
        if current_path in paths:
            is_open = True
        elif state == 'open':
            is_open = True
        else:
            is_open = False


        config_view = config.get_view()

        current_path = "%s/%s" % (base_path, element_name)
        
        # create HTML elements for Section Link ...
        outer_div = DivWdg()

        if my.mode == 'edit' and attributes.get("is_visible") == "false":
            outer_div.add_style("opacity: 0.5")
            outer_div.add_style("font-style: italic")


        outer_div.add_attr("spt_view", config_view )
        outer_div.add_class("spt_side_bar_element")
        outer_div.add_class("spt_side_bar_section")
        outer_div.set_attr("SPT_ACCEPT_DROP", "manageSideBar")
        outer_div.add_attr("spt_element_name", element_name)
        outer_div.add_attr("spt_title", title)
        outer_div.add_style("padding-left: 5px")

        
        #if info.get('login') : 
        #    outer_div.add_attr("spt_login", info.get('login')) 

        # add an invisible drop widget
        outer_div.add(my.get_drop_wdg())


        # Create the link
        s_link_div = DivWdg()
        s_link_div.add_class("SPT_DTS")
        s_link_div.add_class("spt_side_bar_section_link")
        s_link_div.add_style("font-size: 12px")
        s_link_div.add_style("font-weight: bold")

        s_link_div.add_style("cursor: pointer")
        s_link_div.add_style("padding: 2px 3px 2px 3px" )
        s_link_div.add_style("margin: 0px -3px 0px -3px" )
        s_link_div.set_round_corners(5)


        #s_link_div.add_looks("navmenu_section fnt_text fnt_bold")
        s_link_div.add_looks("fnt_text fnt_bold")
        bg_color = my.palette.color("background3")
        bg_color2 = my.palette.color("background3", 20)
        color = my.palette.color("color3")
        s_link_div.add_style("color: %s" % color)
        s_link_div.add_event("onmouseover", "this.style.background='%s'" % bg_color2)
        s_link_div.add_event("onmouseout", "this.style.background='%s'" % bg_color)

        if is_open:
            s_link_div.add( "<img src='/context/icons/silk/_spt_bullet_arrow_down_dark.png' " \
                    "style='float: top left; margin-left: -5px; margin-top: -4px;' />" )
        else:
            s_link_div.add( "<img src='/context/icons/silk/_spt_bullet_arrow_right_dark.png' " \
                    "style='float: top left; margin-left: -5px; margin-top: -4px;' />" )

        # add an icon if applicable
        icon = attributes.get("icon")
        if icon:
            icon = icon.upper()
            from pyasm.widget import IconWdg
            try:
                icon_wdg =  IconWdg(title, eval("IconWdg.%s" % icon) ) 
                s_link_div.add(icon_wdg)
            except:
                pass
        s_link_div.add(SpanWdg(title))

        # create the content of the link div
        s_content_div = DivWdg()
        info['counter'] = info['counter'] + 1
        s_content_div.add_class("SPT_DTS")

        s_content_div.add_attr("spt_path", current_path)
        
        s_content_div.add_class("spt_side_bar_section_content")

        s_content_div.add_style( "padding-left: 11px" )

        if is_open:
            s_content_div.add_style( "display: block" )
        else:
            s_content_div.add_style( "display: none" )


        # add the behaviors
        my.add_folder_behavior(s_link_div, element_name, config, options)

        # then get view name from options in order to read a new
        # config and recurse ...
        options_view_name = options.get('view')
        if options_view_name:
            if use_same_config:
                xml = config.get_xml()
                sub_config = WidgetConfig.get(xml=xml)
                sub_config.set_view(options_view_name)
            else:
                sub_config = my.get_config( my.config_search_type, options_view_name, default=my.default, personal=personal)

            info['level'] += 1
            my.generate_section( sub_config, s_content_div, info, base_path=current_path, personal=personal, use_same_config=use_same_config )
            info['level'] -= 1


        outer_div.add(s_link_div)

        inner_div = DivWdg()
        outer_div.add(inner_div)
        inner_div.add(s_content_div)
        inner_div.add_style("overflow: hidden")

        return outer_div


    #
    # behavior functions
    #
    def add_separator_behavior(my, separator_wdg, element_name, config, options):
        pass

    def add_title_behavior(my, title_wdg, element_name, config, options):
        pass


    def add_folder_behavior(my, folder_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a folder'''

        # determines whether the folder opens on click
        behavior = {
            'type':         'click_up',
            'cbjs_action':  'spt.side_bar.toggle_section_display_cbk(evt,bvr)',
        }
        folder_wdg.add_behavior( behavior )


    def add_link_behavior(my, link_wdg, element_name, config, options):
        '''this method provides the changed to add behaviors to a link'''

        target_id = my.get_target_id()

        # if a parent key filter is specified, use it
        parent_key = my.kwargs.get("parent_key")
        if parent_key:
            options['parent_key'] = parent_key

        state = my.kwargs.get("state")
        if state:
            options['state'] = state


        options['element_name'] = element_name

        attributes = config.get_element_attributes(element_name)
        if attributes.get("help"):
            options['help_alias'] = attributes.get("help")

        # send the title through
        title = my._get_title(config, element_name)

        header_title = options.get('header_title')
        if not header_title:
            header_title = title

        popup = False
        if options.get('popup') == 'true':
            popup = True
           
        values = config.get_web_options(element_name)
        behavior = {
            'type':         'click_up',
            'bvr_repeat_interval': 3,
            'cbjs_action':  '''spt.side_bar.display_link_cbk(evt, bvr)''',
            'target_id':    target_id,
            'title':        header_title,
            'options':      options,
            'values':       values
        }
        if popup:
            behavior['is_popup'] = 'true'
        
        if options.get('popup') != None:
            del options['popup']


        link_wdg.add_behavior( behavior )

        options2 = options.copy()
        options2['inline_search'] = "true"


        behavior = {
            'type':         'click_up',
            'modkeys':      'SHIFT',
            'cbjs_action':  '''spt.side_bar.display_link_cbk(evt, bvr)''',
            'target_id':    element_name,
            'is_popup':     'true',
            'title':        title,
            'options':      options2,
            'values':       values
        }
        link_wdg.add_behavior( behavior )


        # assign the link context menu
        from pyasm.common import jsondumps
        SmartMenu.assign_as_local_activator( link_wdg, 'LINK_CTX' )
        link_wdg.add_attr("spt_element_name", element_name)
        link_wdg.add_attr("spt_title", header_title)

        json_options = jsondumps(options)
        json_options = json_options.replace('"', '&quote;')
        link_wdg.add_attr("spt_kwargs", json_options )

        link_wdg.add_attr("spt_class_name", options.get("class_name") )
        link_wdg.add_attr("spt_search_type", options.get("search_type") )
        link_wdg.add_attr("spt_view", options.get("view") )




    def _get_title(my, config, element_name):
        attributes = config.get_element_attributes(element_name)
        title = attributes.get("title")
        if not title:
            title = element_name
            if '.' in title:
                parts  = title.split('.', 1)
                title = parts[1]
            title = " ".join( [x.capitalize() for x in title.split("_")] )

        title = _(title)
        return title








class ViewPanelWdg(BaseRefreshWdg):
    '''Panel which displays a complete view, including filters, search
    and results'''

    ARGS_KEYS = {
        "search_type": {
            'description': "Search type that this panels works with",
            'type': 'TextWdg',
            'order': 0,
            'category': 'Search'
        },
        "view": {
            'description': "Config View to be displayed",
            'type': 'TextWdg',
            'order': 1,
            'category': 'Search'
        },
        "do_initial_search": {
            'description': "Flag to determine whether to do an initial search",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': 3,
            'category': 'Search'
        },


        "custom_filter_view": {
            'description': "view for custom filters",
            'category': 'Search'
        },
        'simple_search_view': {
            'description': 'View for defining a simple search',
            'type': 'TextWdg',
            'order': 5,
            'category': 'Search'
        },
        'simple_search_visible_rows': {
            'description': 'Number of visible rows in the simple search bar',
            'type': 'TextWdg',
            'order': 6,
            'category': 'Search'
        },
        'simple_search_mode': {
            'description': 'Display mode of simple search bar',
            'type': 'SelectWdg',
            'category': 'Search',
            'order': 4,
            'values': 'inline|hidden',
        },
        'simple_search_columns': {
            'description': 'Number of columns in the simple search bar',
            'type': 'SelectWdg',
            'order': 7,
            'values': '2|3|4',
            'category': 'Search'
        },

        "search_view": "search view to be displayed",
        "order_by": "order by a particular column",
        "search_limit": "The number of items to show on each page",
        "expression": "use an expression for the search",
        
        "parent_key":  {
            'description': '(Advanced) filter for a parent specified by this parent_key. Can accept "self" which takes the search_key',
            'type': 'TextWdg',
            'order': 8
        },
     
        "search_key": {
            'description': 'filter for a search_key usually used for an accompnaying expression',
            'type': 'TextWdg',
            'order': 9
        },
        


        "filter": "filter structure",
        "width": "the default width of the table",
        "target_id": {
            'description': "The target id that this panel will be put in",
            'category': "deprecated"
        },

        "element_names": "Show only these elements",

        #"show_view_select": "determines whether the view selector is visible",
        "schema_default_view": "true if it is generated from a schema",


        "layout": {
            'description': 'Determine the layout to use',
            'type': 'SelectWdg',
            'values': 'default|tile|static_table|raw_table|fast_table|tool|browser|card|old_table|custom|custom_item',
            'category': 'Layout',
            'order': '00',
        },




        'show_select': {
            'description': 'Flag to determine whether or not to show row_selection',
            'type': 'SelectWdg',
            'values': 'true|false',
            'category': 'Display',
            'order': '01',
        },
        'show_refresh': {
            'description': 'Flag to determine whether or not to show the refresh icon',
            'type': 'SelectWdg',
            'values': 'true|false',
            'category': 'Display',
            'order': '02'
        },

        "show_shelf": {
            'description': "Determines whether or not to show the action shelf",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '03',
            'category': 'Display'
        },
        "show_gear": {
            'description': "determines whether or not to show the gear",
            'type': 'SelectWdg',
            'values': 'true|false',
            "order": '04',
            'category': 'Display'
        },
        "show_search": {
            'description': "determines whether to show the Advanced Search button in the shelf",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '05',
            'category': 'Display'
        },
        "show_keyword_search": {
            'description': "determines whether or not to show keyword search bar",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '06',
            'category': 'Display'
        },
 

        "show_search_limit": {
            'description': "determines whether or not to show the search limit",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '07',
            'category': 'Display'
        },
         "search_limit_mode": {
            'description': "determine if it displays top, bottom or both search limit",
            'type': 'SelectWdg',
            'values': 'bottom|top|both',
            'order': '07a',
            'category': 'Display'
        },


        'show_insert': {
            'description': 'Flag to determine whether or not to show the insert button',
            'category': '2.Display',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '08',
            'category': 'Display'
        },
        "show_layout_switcher": {
            'description': "determines whether or not to show the layout switcher",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '09',
            'category': 'Display'
        },
        "show_column_manager": {
            'description': "determines whether or not to show the column manager",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '10',
            'category': 'Display'
        },
        "show_context_menu": {
            'description': "determines whether or not to show the context menu",
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '11',
            'category': 'Display'
        },
        "show_expand": {
            'description': "determines whether or not to expand the table",
            'type': 'SelectWdg',
            'values': 'true|false',
            "order": '11a',
            'category': 'Display'
        },
        "show_border": {
            'description': "determines whether or not to show borders on the table",
            'type': 'SelectWdg',
            'values': 'true|false',
            "order": '11b',
            'category': 'Display'
        },
        'checkin_context': {
            'description': 'override the checkin context for Check-in New File',
            'category': 'Check-in',
            'type': 'TextWdg',
            'order': '12'
        },
        'checkin_type': {
            'description': 'override the checkin type for Check-in New File',
            'category': 'Check-in',
            'type': 'SelectWdg',
            'empty': 'true',
            'values': 'auto|strict',
            'order': '13'
        },


        'insert_view': {
            'description': 'Specify a custom insert view other than [insert]',
            'category': 'Display',
            'type': 'TextWdg',
            'order': '14'
        },
        'edit_view': {
            'description': 'Specify a custom edit view other than [edit]',
            'category': 'Display',
            'type': 'TextWdg',
            'order': '15'
        },
     
        'ingest_data_view': {
            'description': 'a view similar to edit view that defines any data to be saved with each ingested sobject.',
            'type': 'TextWdg',
            'category': 'Display',
            'order': '16'
        },


        'popup': {
            'description': 'Flag to determine whether or not to open as a popup by default',
            'category': '2.Display',
            'type': 'SelectWdg',
            'values': 'true|false',
            'order': '17',
            'category': 'Display'
        },

        'init_load_num': {
            'description': 'set the number of rows to load initially. If set to -1, it will not load in chunks',
            'type': 'TextWdg',
            'category': 'Display',
            'order': '18'
        },    

        "no_results_msg" : {
            'description': 'the message displayed when the search returns no item',
            'type': 'TextWdg',
            'category': 'Display',
            'Order': '19'
        },

        "no_results_mode" : {
            'description': 'the display modes for no results',
            'type': 'SelectWdg',
            'values': 'default|compact',
            'category': 'Display',
            'order': '20'
        }, 

        "show_collection_tool" : {
            'description': 'determines whether to show the collection button or not',
            'type': 'SelectWdg',
            'values': 'true|false',
            'category': 'Display',
            'order': '21'
        }, 


        "link": {
            'description': "Definition from a link",
            'category': 'internal',
        },
        "title": {
            'description': "Title of the link",
            'category': 'internal'
        },

        "inline_search": {
            'description': "true|false determines whether the search_wdg is inline",
            'category': 'internal'
        },
        "use_last_search": {
            'description': "true|false determines whether the last search is used",
            'category': 'internal'
        },
        "state": {
            'description': "dictionary: global state of the widget",
            'category': 'internal'
        },

        "process" : {
            'description': 'the process which is applicable when load view is used',
            'type': 'TextWdg',
            'order': 10
        },
        "mode" : {
            'description': 'mode to pass onto layout engine',
            'type': 'SelectWdg',
            'empty': 'true',
            'values': 'simple|insert',
            'order': 11
        },
        "group_elements" : {
            'description': 'a preset one or more columns for grouping e.g. sort_order,category',
            'type': 'TextWdg',
            'order': 12
        },
        "height" : {
            'description': 'a specified height for the table, tile, or card layout',
            'category': 'Display',
            'type': 'TextWdg',
            'order': 13
        },
        "gallery_align" : {
            'description': 'top or bottom gallery vertical alignment',
            'type': 'SelectWdg',
            'values': 'top|bottom',
            'order' : 20,
            'category': 'Display'

        }

    }

    def get_display(my):
        target_id = my.kwargs.get("target_id")
        if not target_id:
            target_id = 'main_body'

        link_view = my.kwargs.get("link")
        my.default = my.kwargs.get('default') == 'True'
        parent_key = my.kwargs.get('parent_key')
        search_key = my.kwargs.get('search_key')
        order_by = my.kwargs.get('order_by')
        element_name = my.kwargs.get('element_name')

        mode = my.kwargs.get('mode')



        if link_view:   
            config = SideBarBookmarkMenuWdg.get_config("SideBarWdg", "definition", default=my.default)
            display_options = config.get_display_options(link_view)

            search_type = display_options.get("search_type")
            view = display_options.get("view")

            search_view = display_options.get("search_view")
            custom_filter_view = display_options.get("custom_filter_view")
            custom_search_view = display_options.get("custom_search_view")
            filter = {}


        else:
            search_type = my.kwargs.get("search_type")
            view = my.kwargs.get("view")
            search_view = my.kwargs.get('search_view')
            custom_filter_view = my.kwargs.get('custom_filter_view')
            custom_search_view = my.kwargs.get("custom_search_view")
            filter = my.kwargs.get("filter")

            # take the search filter structure from search_view
            # if filter is a non-xml string, then it is in JSON format
            
            if type(filter) in types.StringTypes and filter != '':
                try:
                    filter = jsonloads(filter)
                except Exception:
                    filter = None

        has_view = True
        if not view:
            view = "table"
            has_view = False



        from pyasm.search import SearchException
        my.element_names = my.kwargs.get('element_names')
        if not my.element_names:
            if not search_type:
                # this could be the old default layout, just return
                if not search_view and not has_view:
                    return
                else:
                    raise SetupException('Empty search_type is passed in')
            try:
                impl = SearchType.get_database_impl_by_search_type(search_type)
                if impl.get_database_type() == "MongoDb":
                    my.element_names = impl.get_default_columns()
            except SearchException:
                raise


           
         
        # this is needed so that each custom made view can have its own last-search settings
        if not search_view:
            search_view = 'auto_search:%s'%view


        # set the state
        my.state = my.kwargs.get('state')
        if not my.state:
            my.state = {}
        if type(my.state) in types.StringTypes:
            try:
                my.state = eval(my.state)
            except Exception, e:
                print "WARNING: eval(state) error", e.__str__()
                my.state = {}
        Container.put("global_state", my.state)


        if not custom_search_view:
            custom_search_view = ''



        # define the top widget
        top = my.top
        top.add_class("spt_view_panel_top");

        inner = DivWdg()
        top.add(inner)
        inner.add_style("position: relative")


        if not Container.get_dict("JSLibraries", "spt_view_panel"):
            inner.add_behavior({
                'type': 'load',
                'cbjs_action': my.get_onload_js()
            });



        # add refresh information
        top.set_attr("spt_node", "true")
        my.set_as_panel(top, class_name='spt_view_panel')

            
        if not search_type or not view:
            return top



        title_wdg = my.get_title_wdg()
        if title_wdg:
            inner.add(title_wdg)


        # set up a search
        try:
            search_type_obj = SearchType.get(search_type)
        except SearchException, e:
            print "Warning: can't find search type [%s]" % search_type
            return top


        title = my.kwargs.get("title")
        if not title:
            title = "%s : %s view" % (search_type_obj.get_title(), view)

        #breadcrumb_wdg = Container.get("breadcrumb")
        #if breadcrumb_wdg:
        #    breadcrumb_wdg.add( title )


        # add in the action options widgets
        # This widget will depend on the view.  Some specialized views require
        # actions options in order to function properly
        option_container = DivWdg()
        option_container.set_id( "%s_action_options" % target_id)
        option_container.add_style("display", "block")
        option_container.set_attr("spt_search_type", search_type)
        option_container.set_attr("spt_search_view", search_view)




        # add in the search filter
        search_container = DivWdg()
        search_container.set_id( "%s_search" % target_id)
        search_container.add_style("display", "block")
        search_container.set_attr("spt_search_type", search_type)
        search_container.set_attr("spt_search_view", search_view)




        

        # Search box
        inline_search = "true"
        search = None
        use_last_search = my.kwargs.get('use_last_search')
        
        show_search = my.kwargs.get('show_search')
        if show_search in [False,'false']:
            show_search = 'false'
        else:
            show_search = 'true'

        search_limit = my.kwargs.get("search_limit")
        run_search_bvr = my.kwargs.get('run_search_bvr') 


        search_dialog_id = 0
        search_wdg = None
        can_search = True

        show_shelf = my.kwargs.get("show_shelf")


        # make some checks to see if search will actually work
        try:
            search = Search(search_type)
            search.set_null_filter()
            sobjects = search.get_sobjects()
        except Exception, e:
            impl = SearchType.get_database_impl_by_search_type(search_type)
            if impl.get_database_type() == "MongoDb":
                can_search = False


        # FIXME: this doesn't work yet because the filter information
        # is not passed through
        #if show_shelf not in [False, 'false']:
        #if True:
        if can_search:
            search = my.kwargs.get("search")
            try:
                from tactic.ui.app import SearchWdg
                search_wdg = SearchWdg(search=search,search_type=search_type, view=search_view, parent_key=None, filter=filter, use_last_search=use_last_search, display=True, custom_filter_view=custom_filter_view, custom_search_view=custom_search_view, state=my.state, run_search_bvr=run_search_bvr, limit=search_limit)
            except SearchException, e:
                # reset the top_layout and must raise again
                WidgetSettings.set_value_by_key('top_layout','')
                raise


            from tactic.ui.container import DialogWdg
            search_dialog = DialogWdg(width=770, offset={'x':-250,'y':0})
            search_dialog_id = search_dialog.get_id()
            #if show_search == 'true':
            # Comment out the above. 
            # Needs to draw the search_dialog for pre-saved parameters to go thru
            # Fast(Base) Table Layout will take care of hiding it
            inner.add(search_dialog)
            search_dialog.add_title("Advanced Search")
            search_dialog.add(search_wdg)

        # FIXME: this should be a configured option.
        from tactic.ui.cgapp import CGAppLoaderWdg
        cg_wdg = CGAppLoaderWdg(view=view, search_type=search_type)
        option_container.add(cg_wdg)
        inner.add(option_container)


        # add an exposed search
        simple_search_view = my.kwargs.get('simple_search_view')
        simple_search_mode = my.kwargs.get("mode")
        if not simple_search_mode:
            simple_search_mode = my.kwargs.get("simple_search_mode")

        if simple_search_view:
            search_class = "tactic.ui.app.simple_search_wdg.SimpleSearchWdg"
            custom_simple_search_view = simple_search_view
        else:
            # add a custom search class
            search_class = my.kwargs.get('search_class')
            custom_simple_search_view = my.kwargs.get("search_view")

        if search_class:
            kwargs = {
                "search_type": search_type,
                "search_view": custom_simple_search_view
            }
            if run_search_bvr:
                kwargs['run_search_bvr'] = run_search_bvr

            if my.kwargs.get("keywords"):
                kwargs['keywords'] = my.kwargs.get("keywords")

            kwargs['visible_rows'] = my.kwargs.get("simple_search_visible_rows")
            kwargs['columns'] = my.kwargs.get("simple_search_columns")
 


            show_shelf = my.kwargs.get("show_shelf")
            """
            if simple_search_mode == "inline" and show_shelf in [True, 'true', '']:
                show_search = "false"
            elif show_shelf in [False, 'false']:
                show_search = "true"
            
            else:
                show_search = True
            """
            kwargs['show_search'] = show_search

            simple_search_wdg = Common.create_from_class_path(search_class, kwargs=kwargs)
            inner.add(simple_search_wdg)

            if simple_search_mode != "inline":
                simple_search_wdg.add_style("display: none")
                simple_search_wdg.add_style("position: absolute")
                simple_search_wdg.add_style("z-index: 200")
                simple_search_wdg.add_style("top: 40px")
                #simple_search_wdg.add_style("top: 10px")
                simple_search_wdg.add_style("left: 10px")
                simple_search_wdg.add_style("box-shadow: 0px 0px 15px rgba(0,0,0,0.5)")




        # create a parent div to contain the table.  This is the refreshable
        # widget
        target_node = DivWdg()
        target_node.add_style("display: block")
        inner.add(target_node)


        #show_view_select = my.kwargs.get("show_view_select")
        schema_default_view = my.kwargs.get("schema_default_view")
        show_keyword_search = my.kwargs.get("show_keyword_search")
        show_search_limit = my.kwargs.get("show_search_limit")
        search_limit_mode = my.kwargs.get("search_limit_mode")
        show_layout_switcher = my.kwargs.get("show_layout_switcher")
        show_column_manager = my.kwargs.get("show_column_manager")
        show_context_menu = my.kwargs.get("show_context_menu")
        show_insert = my.kwargs.get("show_insert")
        insert_view = my.kwargs.get("insert_view")
        edit_view = my.kwargs.get("edit_view")
        show_border = my.kwargs.get("show_border")
        show_select = my.kwargs.get("show_select")
        show_refresh = my.kwargs.get("show_refresh")
        show_gear = my.kwargs.get("show_gear")
        show_expand = my.kwargs.get("show_expand")
        show_shelf = my.kwargs.get("show_shelf")
        width = my.kwargs.get("width")
        height = my.kwargs.get("height")
        expression = my.kwargs.get("expression")
        do_initial_search = my.kwargs.get("do_initial_search")
        keywords = my.kwargs.get("keywords")
        init_load_num = my.kwargs.get("init_load_num")
        checkin_context = my.kwargs.get("checkin_context")
        checkin_type = my.kwargs.get("checkin_type")
        ingest_data_view = my.kwargs.get("ingest_data_view")
        group_elements = my.kwargs.get("group_elements")
        expand_mode = my.kwargs.get("expand_mode")
        show_name_hover = my.kwargs.get("show_name_hover")
        op_filters = my.kwargs.get("op_filters")
        show_collection_tool = my.kwargs.get("show_collection_tool")
       

        save_inputs = my.kwargs.get("save_inputs")
        no_results_mode = my.kwargs.get("no_results_mode")
        no_results_msg = my.kwargs.get("no_results_msg")

        # create a table widget and set the sobjects to it
        table_id = "%s_table_%s" % (target_id, random.randint(0,10000))

        # this can be used to relate a View Panel to a table in order to 
        # tell if a table is embedded or not in js
        top.set_attr('table_id', table_id)
        layout = my.kwargs.get("layout")
        if not layout or layout == "default":
            layout = search_type_obj.get_value("default_layout", no_exception=True)
        if not layout:
            layout = 'default'

        search = my.kwargs.get("search")

        kwargs = {
            "table_id": table_id,
            "search": search,
            "search_type": search_type,
            "order_by": order_by,
            "view": view,
            "width": width,
            "target_id": target_id,
            "schema_default_view": schema_default_view,
            "show_search": show_search,
            "show_keyword_search": show_keyword_search,
            "show_search_limit": show_search_limit,
            "search_limit_mode": search_limit_mode,
            "show_layout_switcher": show_layout_switcher,
            "show_column_manager": show_column_manager,
            "show_context_menu": show_context_menu,
            "show_select": show_select,
            "show_refresh": show_refresh,
            "show_insert": show_insert,
            "insert_view": insert_view,
            "edit_view": edit_view,
            "show_gear": show_gear,
            "show_expand": show_expand,
            "show_shelf": show_shelf,
            "search_key": search_key,
            "parent_key": parent_key,
            "state": my.state,
            "show_border": show_border,
            "search_class": search_class,
            "search_view": search_view,
            "search_limit": search_limit,
            "custom_search_view": custom_search_view,
            "expression": expression,
            "do_search": 'false',
            "element_names":  my.element_names,
            "save_inputs": save_inputs,
            "simple_search_view": simple_search_view,
            "simple_search_mode": simple_search_mode,
            "search_dialog_id": search_dialog_id,
            "do_initial_search": do_initial_search,
            "no_results_mode": no_results_mode,
            "no_results_msg": no_results_msg,
            "init_load_num": init_load_num, 
            "checkin_context": checkin_context,
            "checkin_type" : checkin_type,
            "ingest_data_view" : ingest_data_view,
            "group_elements" : group_elements,
            "mode": mode,
            "height": height,
            "keywords": keywords,
            "filter": filter,
            "expand_mode": expand_mode,
            "show_name_hover": show_name_hover,
            "op_filters": op_filters,
            "show_collection_tool": show_collection_tool
            #"search_wdg": search_wdg
            
        }
        if run_search_bvr:
            kwargs['run_search_bvr'] = run_search_bvr

      
        if layout == 'tile':
            from tile_layout_wdg import TileLayoutWdg
            kwargs['top_view'] = my.kwargs.get("top_view")
            kwargs['bottom_view'] = my.kwargs.get("bottom_view")
            kwargs['sticky_scale'] = my.kwargs.get("sticky_scale")
            kwargs['scale'] = my.kwargs.get("scale")
            kwargs['show_scale'] = my.kwargs.get("show_scale")
            kwargs['styles'] = my.kwargs.get("styles")
            kwargs['show_drop_shadow'] = my.kwargs.get("show_drop_shadow")
            kwargs['show_name_hover'] = my.kwargs.get("show_name_hover")
            kwargs['detail_element_names'] = my.kwargs.get("detail_element_names")
            kwargs['title_expr'] = my.kwargs.get("title_expr")
            kwargs['overlay_expr'] = my.kwargs.get("overlay_expr")
            kwargs['overlay_color'] = my.kwargs.get("overlay_color")
            kwargs['allow_drag'] = my.kwargs.get("allow_drag")
            kwargs['upload_mode'] = my.kwargs.get("upload_mode")
            kwargs['process'] = my.kwargs.get("process")
            kwargs['gallery_align'] = my.kwargs.get("gallery_align")
            layout_table = TileLayoutWdg(**kwargs)

        elif layout == 'static_table':
            from static_table_layout_wdg import StaticTableLayoutWdg
            kwargs['mode'] = 'widget'
            layout_table = StaticTableLayoutWdg(**kwargs)
        elif layout == 'raw_table':
            from static_table_layout_wdg import StaticTableLayoutWdg
            kwargs['mode'] = 'raw'
            layout_table = StaticTableLayoutWdg(**kwargs)
        elif layout == 'fast_table':
            kwargs['expand_on_load'] = my.kwargs.get("expand_on_load")
            kwargs['edit'] = my.kwargs.get("edit")
            from table_layout_wdg import FastTableLayoutWdg
            layout_table = FastTableLayoutWdg(**kwargs)


        elif layout == 'tool':
            from tool_layout_wdg import ToolLayoutWdg
            kwargs['tool_icon'] = my.kwargs.get('tool_icon')
            kwargs['tool_msg'] = my.kwargs.get('tool_msg')
            layout_table = ToolLayoutWdg(**kwargs)

        elif layout == 'browser':
            from tool_layout_wdg import RepoBrowserLayoutWdg
            layout_table = RepoBrowserLayoutWdg(**kwargs)

        elif layout == 'card':
            kwargs['preview_width'] = my.kwargs.get("preview_width")
            kwargs['process'] = my.kwargs.get("process")
            from tool_layout_wdg import CardLayoutWdg
            layout_table = CardLayoutWdg(**kwargs)

        elif layout == 'collection':
            kwargs['detail_element_names'] = my.kwargs.get("detail_element_names")
            from collection_wdg import CollectionLayoutWdg
            layout_table = CollectionLayoutWdg(**kwargs)

        elif layout == 'custom':
            from tool_layout_wdg import CustomLayoutWithSearchWdg
            layout_table = CustomLayoutWithSearchWdg(**kwargs)

        elif layout == 'aggregate':
            from tool_layout_wdg import CustomAggregateWdg
            layout_table = CustomAggregateWdg(**kwargs)

        elif layout == 'custom_item':
            from tool_layout_wdg import CustomItemLayoutWithSearchWdg
            layout_table = CustomItemLayoutWithSearchWdg(**kwargs)

        elif layout == 'old_table':
            from layout_wdg import OldTableLayoutWdg
            layout_table = OldTableLayoutWdg(**kwargs)
        else:
            kwargs['expand_on_load'] = my.kwargs.get("expand_on_load")
            kwargs['show_border'] = my.kwargs.get("show_border")
            kwargs['edit'] = my.kwargs.get("edit")
            from table_layout_wdg import FastTableLayoutWdg
            layout_table = FastTableLayoutWdg(**kwargs)

        layout_table.set_search_wdg(search_wdg)

        # add the search in the table
        #search_container = layout_table.search_container_wdg
        #if not show_search:
        #    search_div.add_style("display: none")
        #layout_table.search_container_wdg.add(search_wdg)

        search_keys = my.kwargs.get("search_keys")
        if search_keys:
            my.sobjects = Search.get_by_search_keys(search_keys)


        if my.sobjects:
            layout_table.set_sobjects(my.sobjects)
            layout_table.set_items_found(len(my.sobjects))

        else:
            # perform the search.  It is possible that the search is badly formed
            # due to some parameters that are incorrect in the search.  This should
            # not be fatal, so we catch the exception here
            from pyasm.search import SqlException
            try:
                if can_search:
                    layout_table.handle_search()
            except SqlException, e:
                from pyasm.widget import ExceptionWdg
                exception_wdg = ExceptionWdg(e)

                from tactic.ui.container import PopupWdg
                popup = PopupWdg(destroy_on_close="true", display="true", width='700px')
                popup.add_title("SQL Error")
                popup.add(exception_wdg)
                inner.add(popup)


        
        target_node.add(layout_table) 

        if my.kwargs.get('is_refresh') in ['true', True]:
            return inner
        else:
            return top



    def get_title_wdg(my):

        # FIXME: just a test

        title = my.kwargs.get("title")
        title = ""
        description = my.kwargs.get("description")
        title_view = my.kwargs.get("title_view")
        if not title and not description and not title_view:
            return


        title_box_wdg = DivWdg()
        title_box_wdg.add_border()
        title_box_wdg.add_style("padding: 10px")
        title_box_wdg.add_color("background", "background", -5)
        title_box_wdg.add_style("margin-bottom: -1px")


        if title_view:
            from custom_layout_wdg import CustomLayoutWdg
            title_wdg = CustomLayoutWdg(view=title_view)
            title_box_wdg.add(title_wdg)


        if title:
            title_wdg = DivWdg()
            title_box_wdg.add(title_wdg)
            title_wdg.add(title)
            title_wdg.add_style("font-size: 16px")
            title_wdg.add_style("font-weight: bold")

        if description:
            title_box_wdg.add("<br/>")
            title_box_wdg.add(description)
            title_box_wdg.add("<br/>"*2)

        return title_box_wdg



    def get_onload_js(my):

        return r'''

spt.Environment.get().add_library("spt_view_panel");

spt.view_panel = {}

spt.view_panel.top = null;

spt.view_panel.set_top = function(top_el) {
    spt.view_panel.top = top_el;
}

spt.view_panel.get_current_layout = function() {
    var top = spt.view_panel.top;
    var layout_el = top.getElement(".spt_layout");
    var layout = layout_el.getAttribute("spt_layout");
    return layout;
}


spt.view_panel.switch_layout = function(layout) {
          
    var top = spt.view_panel.top;
    if (!top) {
        alert("Error: spt_view_panel_top not found");
        return;
    }

    var search_type = top.getAttribute("spt_search_type");

    var kwargs = {
        search_type: search_type,
        layout: layout,
    }
    var server = TacticServerStub.get();
    var data = server.execute_class_method("tactic.ui.panel.LayoutUtil", "get_layout_data", kwargs);

    var class_name = data.class_name;
    var element_names = data.element_names;
    var view = data.view;

    var table_top = top.getElement(".spt_table_top");
    var table = top.getElement(".spt_table_table");
    var layout_el = top.getElement(".spt_layout");

    var last_view = top.getAttribute("spt_view");

    layout_el.setAttribute("spt_layout", layout);
    layout_el.setAttribute("spt_last_view", last_view);
    layout_el.setAttribute("spt_view", view);

    table_top.setAttribute("spt_class_name", class_name);
    table_top.setAttribute("spt_view", view);
    table.setAttribute("spt_view", view);

    spt.dg_table.search_cbk( {}, {src_el: table, element_names: element_names, widths:[]} );

}

        '''





class ViewPanelSaveWdg(BaseRefreshWdg):
    '''Simple dialog widget which popups and allows you to save the
    current view'''

    def get_args_keys(my):
        return {
        'table_id': 'id of the table to be operated on',
        'dialog_id': 'id of the dialog',
        #'is_aux_title': 'True if it is in title mode'
        }

    def init(my):
        my.table_id = my.kwargs.get("table_id")
        assert my.table_id

    def get_display(my):
       
        js_action = "spt.dg_table.save_view_cbk('%s','%s')" % (my.table_id, Environment.get_user_name())

        # create the buttons
        save_button = ActionButtonWdg(title='Save')
        behavior = {
        'type': 'click_up',
        'dialog_id': my.kwargs.get("dialog_id"),
        'cbjs_action':  '''
            var ret_val = %s;
            if (ret_val) {
                spt.hide($(bvr.dialog_id));
                var top = bvr.src_el.getParent(".spt_new_view_top");
                spt.api.Utility.clear_inputs(top);
            }

        '''%js_action

        }
        save_button.add_behavior(behavior)


        cancel_button = ActionButtonWdg(title='Cancel')
        behavior = {
        'type': 'click_up',
        'dialog_id': my.kwargs.get("dialog_id"),
        #'cbjs_action': "var el=bvr.src_el.getParent('.spt_table_aux');spt.hide(el)"
        'cbjs_action': 'spt.hide($(bvr.dialog_id))'
        }
        cancel_button.add_behavior(behavior)

        # add the name entry input
        div = DivWdg(id='save_view_wdg')
        div.add_class("spt_new_view_top")
        div.add_class("spt_save_top")
        div.add_style("width: 280px")
        div.add_style("padding: 15px")
        div.add_color("color", "color")

        title_div = DivWdg("View Title: ")
        title_div.add_style('width: 100px')
        div.add(title_div)
        text = TextInputWdg(name="save_view_title")
        div.add(text)
        text.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var title = bvr.src_el.value;
        var code = spt.convert_to_alpha_numeric(title);
        var top = bvr.src_el.getParent(".spt_new_view_top");
        var code_el = top.getElement(".spt_new_view_name");
        code_el.value = code;
        var radios = top.getElements("input[name='save_mode']");
        
        var is_checked = false;
        for (var k = 0 ; k < radios.length; k++) {
            if (radios[k].checked) {
                is_checked = true;
                break
            }
        }
        if (!is_checked) {
            
            radios[0].checked = true;

        }
        '''
        } )


        div.add(HtmlElement.br(2))

        
        title_div = FloatDivWdg("View Name: ")
        title_div.add_style('width: 80px')
        div.add(title_div)

        div.add(HtmlElement.br())
        text = TextInputWdg(name="save_view_name")
        text.add_class("spt_new_view_name")
        #text.add_style('display: none')
        text.add_class('spt_save_view_name')
        div.add(text)
        div.add(HtmlElement.br(2))
     
        #cb = CheckboxWdg('save_a_link', label='Add View To Side Bar')
        #cb.set_default_checked()
        #div.add(cb)
        #div.add(HtmlElement.br())

        checkbox_div = DivWdg()
        div.add(checkbox_div)
        checkbox_div.add_style("padding: 5px")
        checkbox_div.add_class("spt_checkbox_top")

        checkbox_div.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_input',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_checkbox_top");
            var checkboxes = top.getElements(".spt_input");
            for (var i = 0; i < checkboxes.length; i++) {
                checkboxes[i].checked = false;
            }
            '''
        } )
        names = []
        labels = []
       
        is_reg_user = False 
        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            is_admin = True
            names = ['save_project_views', 'save_my_views', 'save_view_only']
            labels = [
                'Add Link to "Project Views"',
                'Add Link to "My Views"',
                'No Links'
            ]
        else:
            is_admin = False

        if security.check_access("builtin", "view_save_my_view", "allow", default='allow') and not is_admin:
             names = ['save_my_views']
             labels = ['Add Link to "My Views"']
             is_reg_user = True

        from pyasm.widget import RadioWdg
        for name, label in zip(names, labels):
            cb_div = DivWdg()
            cb_div.add_style("padding: 3px")
            #cb = CheckboxWdg(name, label=label)
            #cb_div.add(cb)
            cb = RadioWdg("save_mode", label=label)
            cb.set_option("value", name)
            cb_div.add(cb)
            if name == 'save_project_views':
                #cb.set_default_checked()
                cb.set_checked()
            if is_reg_user:
                if name == 'save_my_views':
                    cb.set_checked()

            checkbox_div.add(cb_div)



        div.add(HtmlElement.br() )

        # need to use a table for now
        button_table = Table()
        button_table.add_style("margin: 0px auto")
        button_table.add_style("text-align: center")
        button_table.add_row()
        button_table.add_cell(save_button)
        button_table.add_cell(cancel_button)
        div.add(button_table)

        
        return div

    def get_existing_views(is_personal):
        search = Search('config/widget_config')
        # could be any search type
        #search.add_filter('search_type','SideBarWdg')
        search.add_regex_filter('view', '(link_search|saved_search)', 'NEQ')
        login = None
        if is_personal:
            login = Environment.get_user_name()
            
        search.add_filter('login', login)
        db_configs = search.get_sobjects()
        views = SObject.get_values(db_configs, 'view', unique=True)
        # strip the user_name if there is
        new_views = []
        for view in views:
            if '.' in view:
                parts = view.split('.')
                new_view = parts[1]
            else:
                new_view = view
            new_views.append(new_view)
        return new_views

    get_existing_views = staticmethod(get_existing_views)




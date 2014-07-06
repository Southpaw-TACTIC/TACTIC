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

__all__ = ['TabWdg', 'TabSaveStateCmd']

from pyasm.common import TacticException, Xml, Common, Environment, Container
from pyasm.web import DivWdg, SpanWdg, WebState, WebContainer
from pyasm.search import Search
from pyasm.widget import WidgetConfigView, WidgetConfig, IconWdg
from tactic.ui.common import BaseRefreshWdg

import types, sys, re, os

class TabWdg(BaseRefreshWdg):

    ARGS_KEYS = {
        'show_add': {
            'description': 'show the + button',
             'values': 'true|false',
            'category': 'Display'
        },
        'show_context_menu': {
            'description': 'show the context menu',
             'values': 'true|false',
            'category': 'Display'
        },
        'show_remove': {
            'description': 'show the close button',
             'values': 'true|false',
            'category': 'Display'
        },
    }

    def get_onload_js(my):

        return r'''

if (spt.tab) {
    return;
}

spt.Environment.get().add_library("spt_tab");


spt.tab = {};

spt.tab.top = null;

spt.tab.set_main_body_tab = function() {
    spt.tab.top = $(document.body).getElement(".spt_tab_top");
    return spt.tab.top;
}

// this is to be deprecated
spt.tab.set_main_body_top = function() {
    spt.tab.top = $('main_body').getElement(".spt_tab_top");
}


spt.tab.set_tab_top = function( tab_top ) {
    // if this is not really a tab top, then find a child
    if (! tab_top.hasClass("spt_tab_top") ) {
        tab_top = tab_top.getElement(".spt_tab_top");
    }
    spt.tab.top = tab_top;
    return spt.tab.top;
}


spt.tab.set_tab_top_from_child = function( el ) {
    // if this is not really a tab top, then find a parent
    if (! el.hasClass("spt_tab_top") ) {
        el = el.getParent(".spt_tab_top");
    }
    spt.tab.top = el;
    return spt.tab.top;
}


spt.tab.get_headers = function() {
    var top = spt.tab.top;
    var tab_id = top.getAttribute("id");

    var header_top = top.getElement(".spt_tab_header_top");
    var all_headers = header_top.getElements(".spt_tab_header");
    //return all_headers;

    var headers = [];
    for (var i = 0; i < all_headers.length; i++ ) {
        var header_tab_id = all_headers[i].getAttribute("spt_tab_id");
        if (header_tab_id != tab_id) {
            continue;
        }

        headers.push(all_headers[i]);
    }

    return headers;
}


spt.tab.get_header = function(name) {
    var top = spt.tab.top;
    var header_top = top.getElement(".spt_tab_header_top");
    var headers = header_top.getElements(".spt_tab_header");
    for (var i = 0; i < headers.length; i++) {
        if (name == headers[i].getAttribute("spt_element_name") ) {
            return headers[i];
        }
    }
    return null;
}



spt.tab.get_content = function(name) {
    var top = spt.tab.top;
    var tab_id = top.getAttribute("spt_tab_id");

    var content_top = top.getElement(".spt_tab_content_top");
    var all_contents = content_top.getElements(".spt_tab_content");

    // FIXME: this breaks when opening new tabs for some reason
    //return all_contents;

    for (var i = 0; i < all_contents.length; i++ ) {
        var content_tab_id = all_contents[i].getAttribute("spt_tab_id");
        var content_name = all_contents[i].getAttribute("spt_element_name");
        if (content_name == name) {
            return all_contents[i];
        }
    }


    return null;
}





spt.tab.get_contents = function() {
    var top = spt.tab.top;
    var tab_id = top.getAttribute("spt_tab_id");

    var content_top = top.getElement(".spt_tab_content_top");
    var all_contents = content_top.getElements(".spt_tab_content");

    // FIXME: this breaks when opening new tabs for some reason
    //return all_contents;

    var contents = [];
    for (var i = 0; i < all_contents.length; i++ ) {
        var content_tab_id = all_contents[i].getAttribute("spt_tab_id");
        if (content_tab_id == null) {
            alert(all_contents[i].getAttribute("spt_element_name"));
        }
        if (content_tab_id != tab_id) {
            continue;
        }

        contents.push(all_contents[i]);
    }


    return contents;
}




spt.tab.set_attribute = function(element_name, name, value) {
    var header = spt.tab.get_header(element_name);
    var kwargs_str = header.getAttribute("spt_kwargs");
    var kwargs;
    if (kwargs_str != '') {
        kwargs_str = kwargs_str.replace(/&quote;/g, '"');
        kwargs = JSON.parse(kwargs_str);
    }
    else {
        kwargs = {};
    }

    kwargs[name] = value;
    header.setAttribute("spt_"+name, value);

    kwargs_str = JSON.stringify(kwargs);
    kwargs_str = kwargs_str.replace(/"/g,"&quote;");
    header.setAttribute("spt_kwargs", kwargs_str);

}





spt.tab.add_new = function(element_name, title, class_name, kwargs,
        values, hash) {

    if (typeof(title) == 'undefined') {
        title = '(Untitled)';
    }
    if (typeof(element_name) == 'undefined') {
        //alert("No element name provided");
        //return;
        element_name = "__default__";
    }
    if (typeof(class_name) == 'undefined') {
        class_name = '';
    }
    if (typeof(kwargs) == 'undefined') {
        kwargs = {};
    }
    if (typeof(values) == 'undefined') {
        values = {};
    }

    var top = spt.tab.top;

    if (!hash && hash != false && kwargs.hash) {
        hash = kwargs.hash;
    }
    if (hash == "__link__") {
        hash = "link/" + element_name;
    }


    var orig_element_name = element_name;

    var mode = top.getAttribute("spt_tab_mode");
    if (mode == "hidden") {
        element_name = "__default__";
    }

    var unique = false;
    if (unique) {
        var header = spt.tab.get_header(element_name);
        if (header) {
            var num = Math.floor((Math.random()*10000)+1); 
            element_name = element_name + num;
            //title = title + num;
        }
    }


    var top_id = top.getAttribute("spt_tab_id");

   
    //var headers = header_top.getElements(".spt_tab_header");
    var headers = spt.tab.get_headers();
    var header;
    var found = false;
    var force = false;
    for (var k=0; k < headers.length; k++){
        var existing_header = headers[k];
        if (existing_header.getAttribute('spt_element_name')==element_name){
            header = existing_header;
            found = true;
            force = true;
            break;
        }
    }
    
    if (!found) {


        var template_top = top.getElement(".spt_tab_template_top");
        //var header_top = top.getElement(".spt_tab_header_top");
        var header_template = template_top.getElement(".spt_tab_header");
        var header = spt.behavior.clone(header_template);
        
        var last_header = headers[headers.length -1];

        // set the new label
        var label = header.getElement(".spt_tab_header_label");
        var display_title = title;
        if (display_title.length > 20) {
            display_title = title.substr(0,18) + "...";
        }

        label.setAttribute("title", title);
        label.innerHTML = display_title;

        header.setAttribute("spt_class_name", class_name);
        var kwargs_str = JSON.stringify(kwargs);
        kwargs_str = kwargs_str.replace(/\"/,"&quote;");
        header.setAttribute("spt_kwargs", kwargs_str);
        header.setAttribute("spt_element_name", element_name);
        header.setAttribute("spt_title", title);
        header.setAttribute("spt_tab_id", top_id);
        header.removeClass("spt_content_loaded");
        header.inject(last_header, "after");


        var selected_header = spt.tab.get_selected_header();
        if (selected_header) {
            var opener = selected_header.getAttribute("spt_element_name");
            header.setAttribute("spt_tab_opener", opener);
        }

        // copy the content from template
        var content_top = top.getElement(".spt_tab_content_top");
        var content_template = template_top.getElement(".spt_tab_content");
        var content_box = spt.behavior.clone(content_template);

        content_box.setAttribute("spt_element_name", element_name);
        content_box.setAttribute("spt_title", title);
        content_box.setAttribute("spt_tab_id", top_id);

        var content_boxes = spt.tab.get_contents();
        var last_content = content_boxes[content_boxes.length -1];
        content_box.inject(last_content, "after");
        var content_boxes = spt.tab.get_contents();

    }
    else {
        var content_top = top.getElement(".spt_tab_content_top");
        var content_boxes = content_top.getElements(".spt_tab_content");
        for (var i=0; i < content_boxes.length; i++) {
            var content_box = content_boxes[i];
            var box_name = content_box.getAttribute("spt_element_name")
            if (box_name == element_name) {
                content_box.setAttribute("spt_element_name", element_name)
                break;
            }
        }
    }
    if (typeof(class_name) == 'undefined') {
        spt.tab.select(element_name);
    }
    else {
        spt.tab.load_class(header, class_name, kwargs, values, force);
    }

    // FIXME: this should only move on the main table
    //var top_pos = spt.tab.getY(header_top);
    //scroll(0,top_pos-20);


    // register the hash
    if (hash) {
        var state = {
            element_name: orig_element_name,
            title: title,
            class_name: class_name,
            kwargs: kwargs,
            hash: hash
        }
        spt.hash.set_hash(state, title, hash);
    }

    return header;
}

// TEST
spt.tab.getY = function(oElement)
{
    var iReturnValue = 0;
        while( oElement != null ) {
        iReturnValue += oElement.offsetTop;
        oElement = oElement.offsetParent;
    }
    return iReturnValue;
}



spt.tab.load_selected = function(element_name, title, class_name, kwargs, values) {
    var top = spt.tab.top;
    //var content_top = top.getElement(".spt_tab_content_top");
    //var content_boxes = content_top.getElements(".spt_tab_content");

    var header = spt.tab.get_selected_header();
    // if none are selected, use the last one
    if (header == null) {
        var headers = spt.tab.get_headers();
        header = headers[headers.length - 1];
    }

    var old_element_name = header.getAttribute("spt_element_name");

    header.setAttribute("spt_element_name", element_name);
    header.setAttribute("spt_title", title);
    header.setAttribute("spt_class_name", class_name);

    if (typeof(kwargs) == 'undefined') {
        kwargs = {};
    }
    var kwargs_str = JSON.stringify(kwargs)
    header.setAttribute("spt_kwargs", kwargs_str);

    var label = header.getElement(".spt_tab_header_label");
    label.innerHTML = title;

    var content_top = top.getElement(".spt_tab_content_top");
    var content_boxes = content_top.getElements(".spt_tab_content");
    for (var i=0; i < content_boxes.length; i++) {
        var content_box = content_boxes[i];
        var box_name = content_box.getAttribute("spt_element_name")
        if (box_name == old_element_name) {
            content_box.setAttribute("spt_element_name", element_name)
            break;
        }
    }
    
 
    var force = true; 
    spt.tab.load_class(header, class_name, kwargs, values, force);
}



// add a DOM node to the named content
spt.tab.load_node = function(element_name, node) {
    var top = spt.tab.top;
    var content_top = top.getElement(".spt_tab_content_top");
    var content_boxes = spt.tab.get_contents();
    for (var i=0; i < content_boxes.length; i++) {
        var content_box = content_boxes[i];
        var box_name = content_box.getAttribute("spt_element_name")
        if (box_name == element_name) {

            if(content_box.hasChildNodes()) {
                while(content_box.childNodes.length >= 1 ) {
                    content_box.removeChild(content_box.firstChild);
                }
            }

            content_box.appendChild(node);


            break;
        }
    }

}    

// add raw HTML to the named content
spt.tab.load_html = function(element_name, html) {
    var top = spt.tab.top;
    var content_top = top.getElement(".spt_tab_content_top");
    var content_boxes = spt.tab.get_contents();
    for (var i=0; i < content_boxes.length; i++) {
        var content_box = content_boxes[i];
        var box_name = content_box.getAttribute("spt_element_name")
        if (box_name == element_name) {
           spt.behavior.replace_inner_html(content_box, html);
        }
    }

}    
 



spt.tab.select = function(element_name) {

    var header = spt.tab.get_header(element_name);
    var top = spt.tab.top;

    var header_top = top.getElement(".spt_tab_header_top");
    var headers = spt.tab.get_headers();
    for (var i=0; i < headers.length; i++) {
        headers[i].setStyle("opacity", "0.4");
        headers[i].setStyle("font-weight", "normal");
        headers[i].removeClass("spt_is_selected");
    }

    header.setStyle("opacity", "1.0");
    header.addClass("spt_is_selected");
    header.setStyle("font-weight", "bold");
    header.setStyle("z-index", "200");


    var content_top = top.getElement(".spt_tab_content_top");
    var content_boxes = spt.tab.get_contents();

    for (var i=0; i < content_boxes.length; i++) {
        var content_box = content_boxes[i];
        content_box.setStyle("display", "none");
    }

    for (var i=0; i < content_boxes.length; i++) {
        var content_box = content_boxes[i];
        var box_name = content_box.getAttribute("spt_element_name")
        if (box_name == element_name) {
            content_box.setStyle("display", "");
            if (!content_box.hasClass("spt_content_loaded")) {
                spt.tab.load_class(header);
            }
            break;
        }
    }


    var kwargs_str = header.getAttribute("spt_kwargs");
    if (kwargs_str == '') {
        kwargs = {};
    }
    else {
        kwargs_str = kwargs_str.replace(/&quote;/g, '"');
        kwargs = JSON.parse(kwargs_str);
    }

    bvr.options = {
      element_name: element_name,
      alias: kwargs.help_alias
    }
    spt.named_events.fire_event("tab|select", bvr);
    
    // usually a tab contains a table and layout. it's better to set to that.
    var tab_content = top.getElement('.spt_tab_content[spt_element_name=' + element_name + ']');
    if (tab_content) {
        var table = tab_content.getElement('.spt_table_table');
        if (table) {
            var layout = table.getParent(".spt_layout");
            spt.table.set_layout(layout);
        }
    }


    var last_element_name = spt.tab.get_selected_element_name();
    if (last_element_name) {
        top.setAttribute("spt_last_element_name", last_element_name);
    }


}



spt.tab.load_class = function(header, class_name, kwargs, values, force) {
    var title = header.getAttribute("spt_title");
    var tab_element_name = header.getAttribute("spt_element_name");

    if (typeof(force) == 'undefined') {
         force = false;
    }

    if (typeof(class_name) == 'undefined') {
        class_name = header.getAttribute("spt_class_name");
    }

    if (typeof(kwargs) == 'undefined') {
        var kwargs_str = header.getAttribute("spt_kwargs");
        if (kwargs_str == '') {
            kwargs = {};
        }
        else {
            kwargs_str = kwargs_str.replace(/&quote;/g, '"');
            kwargs = JSON.parse(kwargs_str);
        }
    }


    var top = spt.tab.top;
    var header_top = top.getElement(".spt_tab_header_top");
    var top_id = top.getAttribute("id");

    //spt.api.app_busy_show("Loading " + title, '');

    setTimeout( function() {

        var header_top = header.getParent(".spt_tab_header_top");
        var headers = spt.tab.get_headers();
        for (var i=0; i < headers.length; i++) {
            headers[i].setStyle("opacity", "0.4");
            headers[i].setStyle("font-weight", "normal");
            headers[i].removeClass("spt_is_selected");
        }


        header.setStyle("opacity", "1.0");
        header.addClass("spt_is_selected");
        header.setStyle("font-weight", "bold");
        header.setStyle("z-index", "200");

        var content_top = top.getElement(".spt_tab_content_top");
        var content_boxes = spt.tab.get_contents();

        // make all of the content boxes disappear
        for (var i=0; i < content_boxes.length; i++) {
            var content_box = content_boxes[i];
            content_box.setStyle("display", "none");
        }

        for (var i=0; i < content_boxes.length; i++) {

            var content_box = content_boxes[i];
            var box_name = content_box.getAttribute("spt_element_name")
            if (box_name == tab_element_name) {
                content_box.setStyle("display", "");

                // if no class name is defined, then break out
                if (typeof(class_name) == 'undefined' || class_name == '') {
                    break;
                }

                if (force || ! content_box.hasClass("spt_content_loaded")) {
                    spt.panel.load(content_box, class_name, kwargs, values);

                    // update info on header
                    header.setAttribute("spt_class_name", class_name);
                    var kwargs_str = JSON.stringify(kwargs);
                    kwargs_str = kwargs_str.replace(/\"/,"&quote;");
                    header.setAttribute("spt_kwargs", kwargs_str);
                    header.setAttribute("spt_element_name", tab_element_name);
                    header.setAttribute("spt_title", title);

                    content_box.addClass("spt_content_loaded");
                    // have to set this again because load removes it
                    content_box.setAttribute("spt_element_name", tab_element_name);
                    content_box.setAttribute("spt_tab_id", top_id);
                    content_box.setAttribute("spt_title", title);
                }
                break;
            }
        }

        var bvr = {};
        var parts = tab_element_name.split("/");
        var element_name = parts[parts.length-1];

        var alias = kwargs.help_alias;
        bvr.options = {
          element_name: element_name,
          alias: alias
        }
        spt.named_events.fire_event("tab|select", bvr);
        spt.api.app_busy_hide();

      }, 10 );

    
}


spt.tab.reload_selected = function() {
    var header = spt.tab.get_selected_header();
    var class_name = header.getAttribute("spt_class_name");
    var kwargs = header.getAttribute("spt_kwargs");

    var kwargs_str = header.getAttribute("spt_kwargs");
    var kwargs;
    if (kwargs_str != '') {
        kwargs_str = kwargs_str.replace(/&quote;/g, '"');
        kwargs = JSON.parse(kwargs_str);
    }
    else {
        kwargs = {};
    }

    var values = null;
    var force = true;
    spt.tab.load_class(header, class_name, kwargs, values, force);
}



spt.tab.get_selected_header = function() {
    var top = spt.tab.top;
    var header_top = top.getElement(".spt_tab_header_top");
    var headers = header_top.getElements(".spt_tab_header");
    for (var i = 0; i < headers.length; i++) {
        var header = headers[i];
        if ( header.hasClass("spt_is_selected") ) {
            return header;
        }
        
    }
    return null;
}


spt.tab.get_selected_element_name = function() {
    var header = spt.tab.get_selected_header();
    if (header) {
        var element_name = header.getAttribute("spt_element_name");
        return element_name;
    }
    return "";
}


spt.tab.get_last_selected_element_name = function() {
    var top = spt.tab.top;
    return top.getAttribute("spt_last_element_name");
}


spt.tab.save_state = function() {
    var top = spt.tab.top;
    var header_top = top.getElement(".spt_tab_header_top");
    var headers = header_top.getElements(".spt_tab_header");

    var class_names = [];
    var attrs_list = [];
    var kwargs_list = [];
    for (var i = 0; i < headers.length; i++) {
        var header = headers[i];

        var element_name = header.getAttribute("spt_element_name")
        var title = header.getAttribute("spt_title")
        var attrs = {
            name: element_name,
            title: title
        };
        attrs_list.push(attrs)

        var class_name = header.getAttribute("spt_class_name");
        class_names.push(class_name);
        var kwargs_str = header.getAttribute("spt_kwargs");

        var kwargs;
        if (kwargs_str != '') {
            kwargs_str = kwargs_str.replace(/&quote;/g, '"');
            kwargs = JSON.parse(kwargs_str);
        }
        else {
            kwargs = {};
        }
        kwargs_list.push(kwargs);
    }

    var server = TacticServerStub.get();
    var command = 'tactic.ui.container.TabSaveStateCmd';
    var kwargs = {
        class_names: class_names,
        attrs_list: attrs_list,
        kwargs_list: kwargs_list
    };
    server.execute_cmd(command, kwargs);

}




spt.tab.header_pos = null;
spt.tab.mouse_pos = null;
spt.tab.header_drag_setup = function( evt, bvr, mouse_411) {
    spt.tab.top = bvr.src_el.getParent(".spt_tab_top");
    spt.tab.header_pos = bvr.src_el.getPosition();
    spt.tab.mouse_pos = {x: mouse_411.curr_x, y: mouse_411.curr_y};
    var header = bvr.src_el;
    var element_name = header.getAttribute("spt_element_name");
    spt.tab.select(element_name);
}

spt.tab.header_drag_motion = function( evt, bvr, mouse_411) {
    //var header = bvr.drag_el;
    var header = bvr.src_el;
    var dx = mouse_411.curr_x - spt.tab.mouse_pos.x;
    var dy = mouse_411.curr_y - spt.tab.mouse_pos.y;
    if (Math.abs(dx) < 20) {
        return;
    }

    header.setStyle("position", "absolute");
    header.setStyle("z-index", "100");
    header.setStyle("opacity", "1.0");

    header.setStyle("left", spt.tab.header_pos.x + dx - 10 );
    //header.setStyle("top", spt.tab.header_pos.y + dy );
}

spt.tab.header_drag_action = function( evt, bvr, mouse_411) {
    var header = bvr.src_el;
    var drag_pos = header.getPosition();


    var headers = spt.tab.get_headers();
    for ( var i = headers.length-1; i >= 0; i-- ) {
        if (headers[i] == header) {
            continue;
        }
        var pos = headers[i].getPosition();
        var size = headers[i].getSize();
        if (drag_pos.x > pos.x + size.x/2) {
            header.inject(headers[i], "after");
            break;
        }
        if (drag_pos.x > pos.x) {
            header.inject(headers[i], "before");
            break;
        }



    }

    bvr.drag_el.setStyle("position", "static");
    bvr.drag_el.setStyle("z-index", "");
    bvr.drag_el.setStyle("top", "");
    bvr.drag_el.setStyle("left", "");

    bvr.drag_el.setStyle("background", bvr.gradient);

}

spt.tab.close = function(src_el) {
    // src_el should be a child of spt_tab_content or spt_tab_header
    if (!src_el) {
        spt.error('src_el passed in to spt.tab.close() does not exist.');
        return;
    }
    spt.tab.top = src_el.getParent(".spt_tab_top");
    var top = spt.tab.top;
    var headers = spt.tab.get_headers();
    if (headers.length == 1) {
        return;
    }


    var content = src_el.getParent(".spt_tab_content");
    var header;
    var element_name;
    // check if it's a header child
    if (content) {
        element_name = content.getAttribute("spt_element_name");
        header = spt.tab.get_selected_header(element_name);
    } else {

        header = src_el.getParent(".spt_tab_header");
        if (header) {
            element_name = header.getAttribute("spt_element_name");
            content = spt.tab.get_content(element_name);
        }

    }
    if (!header || !content) {
        spt.error('Tab close cannot find the header or content. Abort');
        return;
    }

    
    var opener = header.getAttribute("spt_tab_opener");
    var element_name = header.getAttribute("spt_element_name");
    header.destroy();

    content.destroy();

    var last_element_name = spt.tab.get_last_selected_element_name();
    last_element_name = null;

    // make the opener active
    if (opener) {
        spt.tab.select(opener);
    }
    else if (last_element_name) {
        spt.tab.select(last_element_name);
    }
    else {
        var last = headers[headers.length - 1].getAttribute("spt_element_name");
        spt.tab.select(last);
    }
}

        '''



    def get_config_xml(my):
        return '''
        <config>
        <tab>
        <element name="untitled" title="(Untitled)"/>
        </tab>
        </config>
        '''




    def get_display(my):

        my.search_type = None

        my.view = my.kwargs.get("view")
        config_xml = my.kwargs.get("config_xml")
        config = my.kwargs.get("config")


        my.mode = my.kwargs.get('mode')
        if not my.mode:
            my.mode = "default"


        if my.view and my.view != 'tab' and not config_xml:
            config = None

            # if it is not defined in the database, look at a config file
            includes = my.kwargs.get("include")
            if includes:
                includes = includes.split("|")
                for include in includes:
                    tmp_path = __file__
                    dir_name = os.path.dirname(tmp_path)
                    file_path="%s/../config/%s" % (dir_name, include)
                    config = WidgetConfig.get(file_path=file_path, view=my.view)
                    if config and config.has_view(my.view):
                        pass
                    else:
                        config = None

            if not config:

                search = Search("config/widget_config")
                search.add_filter("category", "TabWdg")
                search.add_filter("view", my.view)
                config_sobj = search.get_sobject()
                if not config_sobj:
                    config_xml = "<config><%s></%s></config>" % (my.view, my.view)
                else:
                    config_xml = config_sobj.get_value("config")
                config = WidgetConfig.get(view=my.view, xml=config_xml)
        else:
            

            if config:
                pass
            elif config_xml:
                # this is for custom config_xml with a matching custom view
                if not my.view:
                    my.view = 'tab'
                config = WidgetConfig.get(view=my.view, xml=config_xml)
            elif my.widgets:
                config_xml = '''
                <config>
                <tab></tab>
                </config>
                '''

            else:
                config_xml = '''
                <config>
                <tab>
                  <element name="untitled" title="(Untitled)"/>
                </tab>
                </config>
                '''
                my.view = 'tab'
                config = WidgetConfig.get(view=my.view, xml=config_xml)

        if config:
            element_names = config.get_element_names()
        else:
            element_names = []


        top = my.top
        top.add_class("spt_tab_top")
        #top.add_style("padding: 10px")
        my.unique_id = top.set_unique_id()
        top.set_attr("spt_tab_id", my.unique_id)

        top.set_attr("spt_tab_mode", my.mode)

        gradient = top.get_gradient("background", -5, 5)

        inner = DivWdg();
        top.add(inner);

        if not Container.get_dict("JSLibraries", "spt_tab"):
            inner.add_behavior( {
            'type': 'load',
            'gradient': gradient,
            'cbjs_action': my.get_onload_js()
            } )

        #outer_header = DivWdg()
        #inner.add(outer_header)
        #outer_header.add_style("overflow-x: hidden")
        #outer_header.add_style("height: 30px")
        #outer_header.add_style("float: left")

        header_div = DivWdg()
        inner.add(header_div)
        #outer_header.add(header_div)
        header_div.add_style("height: 30px")
        header_div.add_class("spt_tab_header_top")
        #header_div.add_style("width: 5000")
        header_div.add_style("float: left")

        #state = WebState.get().get_current()
        # if a search_key has been passed in, add it to the state.
        state = my.kwargs.get("state")
        if not state:
            state = my.kwargs

        search_key = my.kwargs.get("search_key")
        if search_key:
            state['search_key'] = search_key

        selected = my.kwargs.get("selected")
        if not selected:
            if element_names:
                selected = element_names[0]
            else:
                selected = ''

        offset = my.kwargs.get("tab_offset")
        if offset:
            header_div.add_style("padding-left: %s" % offset)


        if my.mode == "hidden":
            header_div.add_style("display: none")


        header_defs = {}

        title_dict = {}
        my.add_context_menu( header_div )
        loaded_dict = {}
        for element_name in element_names:
            attrs = config.get_element_attributes(element_name)
            title = attrs.get("title")
            if not title:
                title = Common.get_display_title(element_name)

            load_now = attrs.get('load')
            is_loaded = load_now =='true'
            loaded_dict[element_name] = is_loaded

            display_class = config.get_display_handler(element_name)
            display_options = config.get_display_options(element_name)

            header_defs[element_name] = {
                'display_class': display_class,
                'display_options': display_options
            }

            # FIXME: this is already defined in get_display_options
            # process the display options
            for name, value in display_options.items():
                # so it allows JSON string to pass thru without eval as expression
                if re.search("^{[@$]", value) and  re.search("}$", value):
                    value = Search.eval(value, state=state)
                    display_options[name] = value


            # DEPRECATED: this should not really be used.  It is likely
            # better to use expressions set above to explicitly set
            # the values
            if display_options.get("use_state") in [True, 'true']:
                # add the state items to the display options
                for state_name, state_value in state.items():
                    display_options[state_name] = state_value


            if element_name == selected:
                is_selected = True
            else:
                is_selected = False

            header = my.get_tab_header(element_name, title, display_class, display_options, is_selected=is_selected, is_loaded=is_loaded, is_template=False)
            header_div.add(header)




        for i, widget in enumerate(my.widgets):
            name = widget.get_name()
            if not name:
                import random
                num = random.randint(0, 10000)
                name = "noname%s" % num
                widget.set_name(name)
                title = "(Untitled)"
            else:
                title = Common.get_display_title(name)
            if not title:
                title = "(Untitled)"

            title_dict[name] = title

            if name == selected:
                is_selected = True
            else:
                is_selected = False


            class_name = Common.get_full_class_name(widget)
            if isinstance(widget, BaseRefreshWdg):
                kwargs = widget.get_kwargs()
            else:
                kwargs = {}
                

            header = my.get_tab_header(name, title, class_name, kwargs, is_selected=is_selected, is_loaded=True, is_template=False)
            header_div.add(header)


        show_add = my.kwargs.get("show_add") not in [False, "false"]
        if show_add:
            inner.add( my.get_add_wdg() )

        # should only be seen by admin
        #security = Environment.get_security()
        #if security.check_access("builtin", "view_site_admin", "allow"):
        #    inner.add( my.get_edit_wdg() )


        inner.add("<br clear='all'>")


        content_top = DivWdg()

        # add a div so that it breaks correctly
        if my.mode == 'default':
            content_top.add("<div style='height:5px'></div>")
            content_top.set_round_corners(5, corners=['TR','BR','BL'])
            palette = content_top.get_palette()
            border = palette.color("border")
            content_top.add_style("border: 1px solid %s" % border)
            content_top.add_style("margin-top: -5px")

        inner.add(content_top)
        content_top.add_class("spt_tab_content_top")
        content_top.add_style("min-height: 500px")

        width = my.kwargs.get("width")
        if not width:
            content_top.add_style("min-width: 500px")
        else:
            content_top.add_style("min-width: %s" % width)

        content_top.add_class("tab_content_top")
        content_top.add_color("color", "color")
        content_top.add_color("background", "background")


        """
        content_top.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            new Scrollable(bvr.src_el);
            '''
        } )
        content_top.add_style("overflow: hidden")
        content_top.add_style("height: 300px")
        content_top.add_style("padding-right: 15px" )
        """




        # put in a content box for each element
        for element_name in element_names:
            content_div = DivWdg()
            content_div.add_class("spt_tab_content")
            content_div.add_attr("spt_tab_id", my.unique_id)
            content_div.add_attr("spt_element_name", element_name)

            
            content_div.add_style("width: 100%")
            #content_div.add_style("height: 100%")
            content_div.add_style("text-align: left")
            content_top.add(content_div)
            
            is_loaded = loaded_dict.get(element_name)
            if element_name == selected or is_loaded:
                
                header_def = header_defs[element_name]
                display_class = header_def.get("display_class")
                if not display_class:
                    widget = DivWdg()
                    widget.add_color("background", "background")
                    widget.add_style("height: 300px")
                    widget.add_style("padding-top: 50px")

                    inner = DivWdg()
                    widget.add(inner)
                    inner.add_style("margin-left: auto")
                    inner.add_style("margin-right: auto")
                    inner.add_style("width: 500px")
                    inner.add_style("height: 100px")
                    inner.add_border()
                    inner.add_style("text-align: center")
                    inner.add_style("padding-top: 50px")
                    inner.add_color("color", "color3")
                    inner.add_color("background", "background3")

                    inner.add( IconWdg("WARNING", IconWdg.WARNING) )
                    inner.add(" <b>Nothing to display</b>")


                else:
                    display_options = header_def.get("display_options")
                    widget = Common.create_from_class_path(display_class, kwargs=display_options)
                content_div.add(widget)
                content_div.add_class("spt_content_loaded")


                if is_loaded and  element_name != selected:
					# hide preloaded tabs or non-selected tabs
                    content_div.add_style("display: none")

            else:
                content_div.add("&nbsp;")
                content_div.add_style("display: none")



        for widget in my.widgets:
            name = widget.get_name()
            content_div = DivWdg()
            content_div.add_class("spt_tab_content")
            content_div.add_attr("spt_tab_id", my.unique_id)
            content_div.add_class("spt_content_loaded")
            content_div.add_attr("spt_element_name", name)

            title = title_dict.get(name)
            content_div.add_attr("spt_title", title)
            if name != selected:
                content_div.add_style("display: none")
            content_div.add(widget)
            content_div.add_style("width: 100%")
            #content_div.add_style("height: 100%")
            content_div.add_style("text-align: left")
            content_top.add(content_div)



        # Add in a template
        template_div = DivWdg()
        template_div.add_class("spt_tab_template_top")
        template_div.add_style("display: none")

        name = ""
        title = ""
        is_selected = False
        header = my.get_tab_header(name, title, None, None, is_selected=is_selected, is_template=True)
        template_div.add(header)

        top.add(template_div)
        content_div = DivWdg()
        content_div.add_class("spt_tab_content")
        content_div.add_attr("spt_element_name", "NEW")
        content_div.add_attr("spt_tab_id", my.unique_id)
        content_div.add("")
        content_div.add_style("width: 100%")
        #content_div.add_style("height: 100%")
        content_div.add_style("text-align: left")
        template_div.add(content_div)

        return top


    def get_add_wdg(my):

        div = DivWdg()
        div.add_style("margin-left: -2px")

        icon_div = DivWdg()
        icon_div.add_style("padding: 0 2px 0 2px")
        icon_div.set_round_corners(3, corners=['TR','TL'])
        from tactic.ui.widget import IconButtonWdg
        icon = IconButtonWdg(title="New Tab", icon=IconWdg.PLUS)
        icon = IconWdg("New Tab", IconWdg.PLUS)
        #icon.add_style("top: -1px")
        #icon.add_style("left: 0px")
        #icon.add_style("position: absolute")
        icon.add_style("margin-top: -1px")
        icon.add_style("margin-left: 3px")
        icon_div.add_class("hand")

        icon_div.add(icon)
        icon.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tab.top = bvr.src_el.getParent(".spt_tab_top");
        spt.tab.add_new();
        '''
        } )
        icon_div.add_style("padding-top: 4px")

        icon_div.add_style("float: left")
        icon_div.add_style("height: 20px")
        icon_div.add_style("width: 18px")
        icon_div.add_style("margin-left: 2px")
        icon_div.add_gradient("background", "background")
        #icon_div.add_gradient("background", "tab_background", default="background")
        icon_div.add_border()
        icon_div.add_style("text-align: center")
        div.add(icon_div);

        my.extra_menu = my.kwargs.get("extra_menu")
        if my.extra_menu:
            icon_div = DivWdg()
            icon_div.set_round_corners(3, corners=['TR'])
            from tactic.ui.widget import IconButtonWdg
            icon = IconWdg("More Options", IconWdg.ARROWHEAD_DARK_DOWN)
            icon.add_style("margin-left: -2px")

            icon_div.add(icon)
            from smart_menu_wdg import SmartMenu
            smenu_set = SmartMenu.add_smart_menu_set( icon_div, { 'BUTTON_MENU': my.extra_menu } )
            SmartMenu.assign_as_local_activator( icon_div, "BUTTON_MENU", True )

            icon_div.add_style("padding-top: 4px")

            icon_div.add_style("float: left")
            icon_div.add_style("height: 20px")
            icon_div.add_style("width: 10px")
            icon_div.add_style("margin-left: -1px")
            icon_div.add_gradient("background", "background")
            icon_div.add_border()
            icon_div.add_style("text-align: center")
            div.add(icon_div);


        return div



    def get_edit_wdg(my):

        div = DivWdg()
        div.add_style("margin-left: -2px")

        icon_div = DivWdg()
        icon_div.add_style("padding: 0 2px 0 2px")
        icon_div.set_round_corners(3, corners=['TR','TL'])
        from tactic.ui.widget import IconButtonWdg
        icon = IconButtonWdg(title="New Tab", icon=IconWdg.EDIT)
        icon = IconWdg("Edit Tab Definition", IconWdg.EDIT)
        icon.add_style("margin-top: -1px")
        icon.add_style("margin-left: 1px")
        icon_div.add_class("hand")

        icon_div.add(icon)
        icon.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var class_name = 'tactic.ui.tools.tab_edit_wdg.TabEditWdg';
        var kwargs = {}
        spt.panel.load_popup("Tab Edit", class_name, kwargs)
        '''
        } )
        icon_div.add_style("padding-top: 4px")

        icon_div.add_style("float: left")
        icon_div.add_style("height: 20px")
        icon_div.add_style("width: 18px")
        icon_div.add_style("margin-left: 2px")
        icon_div.add_gradient("background", "background")
        icon_div.add_border()
        icon_div.add_style("text-align: center")
        div.add(icon_div);

        return div




    def add_context_menu(my, header_div):

        from menu_wdg import Menu, MenuItem
        menu = Menu(width=180)
        #menu.set_allow_icons(False)
        #menu.set_setup_cbfn( 'spt.tab.smenu_ctx.setup_cbk' )



        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Reload Tab')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_tab_top");
            spt.tab.top = top;


            var header = activator;
            var class_name = header.getAttribute("spt_class_name");
            var kwargs_str = header.getAttribute("spt_kwargs");
            var kwargs;
            if (kwargs_str != '') {
                kwargs_str = kwargs_str.replace(/&quote;/g, '"');
                kwargs = JSON.parse(kwargs_str);
            }
            else {
                kwargs = {};
            }


            var values = null;
            var force = true;
            spt.tab.load_class(header, class_name, kwargs, values, force);

            
            '''
        } )
        menu.add(menu_item)


        menu_item = MenuItem(type='separator')
        menu.add(menu_item)



        menu_item = MenuItem(type='action', label='New Tab')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_tab_top");
            spt.tab.top = top;
            spt.tab.add_new();
            '''
        } )
        menu.add(menu_item)




        menu_item = MenuItem(type='action', label='Tear Off')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_tab_top");

            // add new if this is the last oni
            var headers = spt.tab.get_headers();
            if (headers.length == 1) {
                spt.tab.add_new();
            }
            
            spt.tab.top = top;

            var header = activator;
            var element_name = header.getAttribute("spt_element_name");
            spt.behavior.destroy_element(header);

            var contents = spt.tab.get_contents();
            for (var i=0; i<contents.length; i++) {
                var content = contents[i];
                if (content.getAttribute("spt_element_name") == element_name) {
                    spt.panel.load_popup_with_html( element_name, content.innerHTML );
                    spt.behavior.destroy_element(content);
                }
            } 

            '''
        } )
        menu.add(menu_item)




        menu_item = MenuItem(type='action', label='Copy To Main Tab')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_tab_top");
            spt.tab.top = top;


            var html;
            var header = activator;
            var element_name = header.getAttribute("spt_element_name");
            var title = header.getAttribute("spt_title");

            var class_name = header.getAttribute("spt_class_name");
            var kwargs_str = header.getAttribute("spt_kwargs");
            var kwargs = {};
            if (kwargs_str) {
                kwargs_str = kwargs_str.replace(/&quote;/g, '"');
                kwargs = JSON.parse(kwargs_str);
            }
            var contents = spt.tab.get_contents();
            for (var i=0; i<contents.length; i++) {
                var content = contents[i];
                if (content.getAttribute("spt_element_name") == element_name) {
                    html = content.innerHTML;
                    break;
                }
            }
            spt.tab.set_main_body_tab();
            spt.tab.add_new(element_name, title, class_name, kwargs);
            '''
        } )
        menu.add(menu_item)





        if my.kwargs.get("show_remove") not in ['false', False]: 
            menu_item = MenuItem(type='separator')
            menu.add(menu_item)
            menu_item = MenuItem(type='action', label='Close Tab')
            menu_item.add_behavior( {
                'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);
                var top = activator.getParent(".spt_tab_top");
                spt.tab.top = top;

                var header = activator;
                var element_name = header.getAttribute("spt_element_name");
                spt.behavior.destroy_element(header);

                var contents = top.getElements(".spt_tab_content");
                for (var i=0; i<contents.length; i++) {
                    var content = contents[i];
                    if (content.getAttribute("element_name") == element_name) {
                        spt.behavior.destroy_element(content);
                    }
                }
                '''
            } )
            menu.add(menu_item)



        security = Environment.get_security()
        if security.check_access("builtin", "view_site_admin", "allow"):
            menu_item = MenuItem(type='separator')
            menu.add(menu_item)


            menu_item = MenuItem(type='action', label='View Definition')
            menu_item.add_behavior( {
                'cbjs_action': r'''
                var activator = spt.smenu.get_activator(bvr);
                var header = activator;
                var class_name = header.getAttribute("spt_class_name");
                var kwargs_str = header.getAttribute("spt_kwargs");
                var kwargs;
                if (kwargs_str != '') {
                    kwargs_str = kwargs_str.replace(/&quote;/g, '"');
                    kwargs = JSON.parse(kwargs_str);
                }
                else {
                    kwargs = {};
                }


                /* TEST: show widget editor
                var class_name2 = 'tactic.ui.tools.WidgetEditorWdg';
                var kwargs2 = {
                    'editor_id': bvr.editor_id,
                    'display_handler': class_name,
                    'display_options': kwargs,
                }
                spt.panel.load_popup("Widget Editor", class_name2, kwargs2);
                */
         

                var br = '\n';
                var xml = '';
                xml += '<element>' + br;
                xml += '  <display class="'+class_name+'">'  + br;
                for (var name in kwargs) {
                  if (name == 'class_name') {
                    continue;
                  }
                  xml += '    <'+name+'>'+kwargs[name]+'</'+name+'>' + br;
                }
                xml += '  </display>' + br;
                xml += '</element>';

                var html = spt.convert_to_html_display(xml);
                spt.alert(html, {type:'html'});
                '''
            } )
            menu.add(menu_item)




            menu_item = MenuItem(type='action', label='Add to Side Bar')
            menu_item.add_behavior( {
                'cbjs_action': '''
                var activator = spt.smenu.get_activator(bvr);
                var top = activator.getParent(".spt_tab_top");
                spt.tab.top = top;

                var header = activator;
                var element_name = header.getAttribute("spt_element_name");
                var title = header.getAttribute("spt_title");

                var kwargs = header.getAttribute("spt_kwargs");
                kwargs = kwargs.replace(/&quote;/g, '"');
                kwargs = JSON.parse(kwargs);

                var view = element_name;
                var element_name = element_name.replace(/ /g, "_");
                element_name = element_name.replace(/\//g, "_");

                var kwargs = {
                    class_name: 'LinkWdg',
                    display_options: kwargs,
                    element_attrs: {
                        title: title
                    }
                }

                try {
                    var server = TacticServerStub.get();
                    var info = server.add_config_element("SideBarWdg", "definition", element_name, kwargs);
                    var info = server.add_config_element("SideBarWdg", "project_view", element_name, kwargs);

                    spt.panel.refresh("side_bar");
                }
                catch(e) {
                    alert(e);
                    throw(e);
                }

                '''
            } )
            menu.add(menu_item)





        if my.kwargs.get("show_context_menu") not in ['false', False]:
            menus = [menu.get_data()]
            menus_in = {
                'DG_HEADER_CTX': menus,
            }
            from smart_menu_wdg import SmartMenu
            SmartMenu.attach_smart_context_menu( header_div, menus_in, False )






    def get_tab_header(my, element_name, title, class_name=None, kwargs=None, is_selected=False, is_loaded=False, is_template=False):


        web = WebContainer.get_web()
        is_IE = web.is_IE()

        header = DivWdg()
        header.set_round_corners(5, corners=['TL','TR'])
        #header = SpanWdg()
        header.add_class("spt_tab_header")
        header.add_attr("spt_tab_id", my.unique_id)
        palette = header.get_palette()
        border = palette.color("border")
        header.add_style("border-style: solid")
        header.add_style("border-color: %s" % border)
        header.add_style("border-width: 1px 1px 0px 1px")

        header.add_style("float: left")
        header.add_style("padding: 5px")
        header.add_style("margin-right: 1px")
        #header.add_style("margin-left: 1px")
        if is_IE:
            header.add_style("width: 150px")
        header.add_class("hand")

        #line = DivWdg()
        #header.add(line)
        #line.add_style("height: 1px")
        #line.add_style("width: 100%")
        #line.add_style("background: red")
        #line.add("&nbsp;")
        #line.add_style("margin-top: -5px")

        if is_selected:
            header.add_color("color", "color")
            header.add_gradient("background", "background", -5, 5)
            header.add_style("opacity", "1.0");
            header.add_class("spt_is_selected")
        else:
            header.add_color("color", "color")
            header.add_style("opacity", "0.4");
            header.add_gradient("background", "background", -5, 5)


        palette = header.get_palette()
        hover_color = palette.color("background3")
        header.add_behavior( {
        'type': 'hover',
        'mod_styles': 'background: %s' % hover_color
        } )


        header.add_attr("spt_element_name", element_name)
        header.add_attr("spt_title", title)

        if not is_template:
            header.add_attr("spt_class_name", class_name)
            if kwargs:
                # FIXME: this kwargs processing is a big HACK ...
                # need to extract what add_behavior does.
                kwargs_str = Common.convert_to_json(kwargs)
                header.add_attr("spt_kwargs", kwargs_str)
            else:
                header.add_attr("spt_kwargs", '')
        else:
            header.add_attr("spt_kwargs", '')

           
        header.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var header = bvr.src_el;
        spt.tab.top = header.getParent(".spt_tab_top");
        var this_name = header.getAttribute('spt_element_name');
        spt.tab.select(this_name);
        '''
        } )

        from smart_menu_wdg import SmartMenu
        SmartMenu.assign_as_local_activator( header, 'DG_HEADER_CTX' )


 
        #header.add_behavior( {
        #'type': 'click_up',
        #'mouse_btn': 'RMB',
        #'modkeys': '',
        #'cbjs_action': '''
        #alert("RMB");
        #'''
        #} )

        title_div = DivWdg()
        title_div.add_style("min-width: 100px")
        title_div.add_style("text-align: left")
        title_div.add_style("overflow: hidden")
        title_div.add_attr("nowrap", "nowrap")
        title_div.add_style("float: left")
        title_div.add_class("spt_tab_header_label");
        if len(title) > 20:
            display_title = "%s..." % title[:18]
        else:
            display_title = title
        title_div.add(display_title)
        header.add(title_div)

        title_div.add_attr("title", "%s (%s)" % (title, element_name))

        remove_wdg = DivWdg()

        show_remove = my.kwargs.get("show_remove")
        if is_template or show_remove not in [False, 'false']:
            header.add(remove_wdg)
        #header.add(remove_wdg)


        remove_wdg.add_styles("float: right; position: relative; padding-right: 14px")
        from pyasm.widget import IconButtonWdg
        icon = IconButtonWdg("Remove Tab", IconWdg.CLOSE_INACTIVE)
        icon.add_class("spt_icon_inactive")
        icon.add_styles("margin: auto;position: absolute;top: 0;bottom: 0; max-height: 100%")
        remove_wdg.add(icon)
        icon = IconButtonWdg("Remove Tab", IconWdg.CLOSE_ACTIVE)
        icon.add_class("spt_icon_active")
        icon.add_style("display: none")
        icon.add_styles("margin: auto;position: absolute;top: 0;bottom: 0; max-height: 100%")
        remove_wdg.add(icon)
        

        remove_wdg.add_behavior( {
        'type': 'hover',
        'cbjs_action_over': '''
        var inactive = bvr.src_el.getElement(".spt_icon_inactive");
        var active = bvr.src_el.getElement(".spt_icon_active");
        spt.show(active);
        spt.hide(inactive);
        ''',
        'cbjs_action_out': '''
        var inactive = bvr.src_el.getElement(".spt_icon_inactive");
        var active = bvr.src_el.getElement(".spt_icon_active");
        spt.show(inactive);
        spt.hide(active);
        '''
        })

        remove_wdg.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
            spt.tab.close(bvr.src_el); 
        '''
        } )




        # add a drag behavior
        allow_drag = my.kwargs.get("allow_drag")
        if allow_drag not in [False, 'false']:
            header.add_style("position", "relative");
            header.add_behavior( {
            'type': 'drag',
            "mouse_btn": 'LMB',
            "drag_el": '@',
            "cb_set_prefix": 'spt.tab.header_drag'
            } )

        header.add("&nbsp;")


        return header


from pyasm.command import Command
class TabSaveStateCmd(Command):
    def execute(my):

        class_names = my.kwargs.get("class_names")
        attrs_list = my.kwargs.get("attrs_list")
        kwargs_list = my.kwargs.get("kwargs_list")

        xml = Xml()
        xml.create_doc("config")
        root = xml.get_root_node()

        view = xml.create_element("tab")
        xml.append_child(root, view)

        for class_name, attrs, kwargs in zip(class_names, attrs_list, kwargs_list):
            element = xml.create_element("element")
            xml.append_child(view, element)

            for key, value in attrs.items():
                xml.set_attribute(element, key, value)

            display = xml.create_element("display")
            xml.append_child(element, display)

            xml.set_attribute(display, "class", class_name)

            for key, value in kwargs.items():
                attr = xml.create_text_element(key, value)
                xml.append_child(display, attr)

        xml_string = xml.to_string()

        from pyasm.web import WidgetSettings
        WidgetSettings.set_value_by_key("main_body_tab", xml_string)



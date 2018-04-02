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
from pyasm.web import DivWdg, SpanWdg, WebState, WebContainer, WidgetSettings
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
        'save_state': {
            'description': 'key which is used to save state [ie: "save_state|main_tab" is the default]',
            'category': 'Display'
        },
 
    }

    def get_onload_js(self):

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
    if (!top) {
        spt.tab.set_main_body_tab();
        top = spt.tab.top;
    }

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

    var unique = kwargs.unique;
    if (unique == true || unique == "true") {
        var header = spt.tab.get_header(element_name);
        if (header) {
            var num = Math.floor((Math.random()*10000)+1); 
            element_name = element_name + num;
        }
    }


    var top_id = top.getAttribute("spt_tab_id");

    // disable sub tabs for now
    full_element_name = element_name;
    subelement_name = "";
    /*
    if (element_name.indexOf("/") != -1) {
        var full_element_name = element_name;
        var parts = element_name.split("/");
        element_name = parts[0];
        var subelement_name = parts[1];
    }
    else {
        var full_element_name = element_name;
        var subelement_name = "";
    }
    */


    var subelement_title;
    var full_title;
    if (title.indexOf("/") != -1) {
        full_title = title;
        var parts = title.split("/");
        title = parts[0];
        subelement_title = parts[1];
    }
    else {
        full_title = title;
        subelement_title = title;
    }

   
    //var headers = header_top.getElements(".spt_tab_header");
    var headers = spt.tab.get_headers();
    var header;
    var found = false;
    for (var k=0; k < headers.length; k++){
        var existing_header = headers[k];
        if (existing_header.getAttribute('spt_element_name')==element_name){
            header = existing_header;
            found = true;
            break;
        }
    }

    // add a new tab
    if (!found) {
        var template_top = top.getElement(".spt_tab_template_top");
        var header_template = template_top.getElement(".spt_tab_header");

        // clone the header template
        var header = spt.behavior.clone(header_template);
        var header_id = Math.floor(Math.random()*10000000+1);
        header.setAttribute("id", header_id);

        if (kwargs.hidden == "true") {
            header.setStyle("display", "none");
        }


        // add a subheader template for each header
        var subheader_template = template_top.getElement(".spt_tab_subheader");
        if (subheader_template) {
            var subheader = spt.behavior.clone(subheader_template);

            var subheader_id = Math.floor(Math.random()*10000000+1);
            header.setAttribute("spt_subheader_id", subheader_id);

            subheader.setAttribute("id", subheader_id);
            subheader.setStyle("display", "none");

            subheader.setAttribute("spt_header_id", header_id);

            subheader_top = top.getElement(".spt_tab_subheader_top")
            subheader.inject(subheader_top);
        }
       

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

    }


    // if a subtab is needed, create that
    if (subelement_name) {
        // find out if the subheader exists
        var subheader_id = header.getAttribute("spt_subheader_id");
        var subheader_top = $(subheader_id);
        var subheaders = subheader_top.getElements(".spt_tab_subheader_item");

        var subheader_exists = false;
        var subheader = null;
        for (var i = 0; i < subheaders.length; i++) {
            var box_name = subheaders[i].getAttribute("spt_element_name");
            if (full_element_name == box_name) {
                subheader_exists = true;
                subheader = subheaders[i];
                break;
            }
        }

        if (subheader_exists == false) {

            // create a new one
            var subheader = $(document.createElement("div"));
            subheader.innerHTML = "<div style='padding: 5px 5px'><div class='spt_tab_header_label'>"+subelement_name+"</div></div>";
            subheader_top.appendChild(subheader);
            subheader.addClass("spt_tab_subheader_item");


            // set the new label
            var label = subheader.getElement(".spt_tab_header_label");
            var display_title = subelement_title;
            if (display_title.length > 20) {
                display_title = subelement_title.substr(0,18) + "...";
            }
            title = subelement_name;

            label.setAttribute("title", subelement_title);
            label.innerHTML = display_title;

            subheader.setAttribute("spt_class_name", class_name);
            var kwargs_str = JSON.stringify(kwargs);
            kwargs_str = kwargs_str.replace(/\"/,"&quote;");
            subheader.setAttribute("spt_kwargs", kwargs_str);
            subheader.setAttribute("spt_element_name", full_element_name);
            subheader.setAttribute("spt_title", full_title);
            subheader.setAttribute("spt_tab_id", top_id);
            subheader.removeClass("spt_content_loaded");


            // copy the content from template
            var template_top = top.getElement(".spt_tab_template_top");
            var content_top = top.getElement(".spt_tab_content_top");
            var content_template = template_top.getElement(".spt_tab_content");
            var content_box = spt.behavior.clone(content_template);

            content_box.setAttribute("spt_element_name", full_element_name);
            content_box.setAttribute("spt_title", full_title);
            content_box.setAttribute("spt_tab_id", top_id);

            var content_boxes = spt.tab.get_contents();
            var last_content = content_boxes[content_boxes.length -1];
            content_box.inject(last_content, "after");


        }

    }


    // This does nothing?
    //else {
    /*
    if (true) {
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
    */


    if (! class_name) {
        spt.tab.select(element_name);
    }
    else if (subelement_name) {
        var force = true;
        spt.tab.load_class(subheader, class_name, kwargs, values, force);
    }
    else {
        var force = true;
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
            hash: hash,
            mode: 'tab',
        }
        spt.hash.set_hash(state, title, hash);
    }

    if (top.hasClass("spt_tab_save_state") ) {
        spt.tab.save_state();
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
    var display_title = title;
    if (display_title.length > 20) {
        display_title = title.substr(0,18) + "...";
    }
    label.innerHTML = display_title;

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
        headers[i].removeClass("spt_tab_selected");
        headers[i].addClass("spt_tab_unselected");
    }
    if (header) {
        header.setStyle("opacity", "1.0");
        header.addClass("spt_is_selected");
        header.addClass("spt_tab_selected");
        header.removeClass("spt_tab_unselected");
        header.setStyle("z-index", "200");
    }

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


    var kwargs_str = header ? header.getAttribute("spt_kwargs") : '';
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
            headers[i].removeClass("spt_tab_selected");
            headers[i].addClass("spt_tab_unselected");
        }


        // select the header
        if (header.hasClass("spt_tab_subheader_item")) {
            var subheader_top = header.getParent(".spt_tab_subheader");
            header_id = subheader_top.getAttribute("spt_header_id");
            select_header = $(header_id);
        }
        else {
            select_header = header;
        }

        // select the header
        select_header.setStyle("opacity", "1.0");
        select_header.addClass("spt_is_selected");
        select_header.addClass("spt_tab_selected");
        select_header.removeClass("spt_tab_unselected");
        select_header.setStyle("z-index", "200");




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
    var save_state = top.getAttribute("spt_tab_save_state");

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
        kwargs_list: kwargs_list,
        save_state: save_state
    };
    server.execute_cmd(command, kwargs, {}, { on_complete: function() {} });

}




spt.tab.header_pos = null;
spt.tab.mouse_pos = null;
spt.tab.dragging = false;

spt.tab.header_drag_setup = function( evt, bvr, mouse_411) {
    spt.tab.top = bvr.src_el.getParent(".spt_tab_top");
    spt.tab.header_pos = bvr.src_el.getPosition(spt.tab.top);
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
        spt.tab.dragging = false;
        return;
    }
    spt.tab.dragging = true;
    header.setStyle("position", "absolute");
    header.setStyle("z-index", "100");
    header.setStyle("opacity", "1.0");

    header.setStyle("left", spt.tab.header_pos.x + dx - 10 );
    //header.setStyle("top", spt.tab.header_pos.y + dy );
}

spt.tab.header_drag_action = function( evt, bvr, mouse_411) {
    var header = bvr.src_el;
    var drag_pos = header.getPosition();
    if (spt.tab.dragging == false)
        return;
    
    var headers = spt.tab.get_headers();
    for ( var i = headers.length-1; i >= 0; i-- ) {
        if (headers[i] == header) {
            continue;
        }
        var pos = headers[i].getPosition();

        var size = headers[i].getSize();
        // the y ensures 2nd row tabs don't jump to first row on click
        if (drag_pos.x > pos.x + size.x/2 && drag_pos.y >= pos.y) {
            header.inject(headers[i], "after");
            break;
        }
        if (drag_pos.x > pos.x && drag_pos.y >= pos.y ) {
            header.inject(headers[i], "before");
            break;
        }



    }

    bvr.drag_el.setStyle("position", "static");
    bvr.drag_el.setStyle("z-index", "");
    bvr.drag_el.setStyle("top", "");
    bvr.drag_el.setStyle("left", "");

    bvr.drag_el.setStyle("background", bvr.gradient);

    var top = spt.tab.top;
    if (top.hasClass("spt_tab_save_state") ) {
        spt.tab.save_state();
    }

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
    var element_name;
    // check if it's a header child
    if (src_el.hasClass("spt_tab_header")) {
        var header = src_el;
    }
    else {
        var header = src_el.getParent(".spt_tab_header");
    }
    var subheader = src_el.getParent(".spt_tab_subheader");
    if (header) {
        element_name = header.getAttribute("spt_element_name");
        content = spt.tab.get_content(element_name);
    } else if (subheader) {
        element_name = header.getAttribute("spt_element_name");
        content = spt.tab.get_content(element_name);
    } else if (content) {
        element_name = content.getAttribute("spt_element_name");
        header = spt.tab.get_selected_header(element_name);
    } 

    if (!header || !content) {
        spt.error('Tab close cannot find the header or content. Abort');
        return;
    }

    
    /* If there are changed elements in the current tab, changedParameters
     * is a list with index 0 containing changed element, and index 1 containing
     * change type class. Otherwise, changedParameters is false. 
     */
    function ok(changedParameters) {
        //Remove unsaved changes flags
        if (changedParameters) {
            var changed_element = changedParameters[0];
            var changed_type = changedParameters[1];
            changed_element.removeClass(changed_type);
        }
        var opener = header.getAttribute("spt_tab_opener");
        var element_name = header.getAttribute("spt_element_name");

        if (header) {
            var subheader = $(header.getAttribute("spt_subheader_id"));
            if (subheader) {
                var items = subheader.getElements(".spt_tab_subheader_item");
                for (var i = 0; i < items.length; i++) {
                    var subheader_element_name = items[i].getAttribute("spt_element_name");
                    var subheader_content = spt.tab.get_content(subheader_element_name);
                    spt.behavior.destroy_element(subheader_content);

                }
                spt.behavior.destroy_element(subheader);
            }
        }

        //header.destroy();
        //content.destroy();
        spt.behavior.destroy_element(header);
        spt.behavior.destroy_element(content);



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
            // select last one from the remaining
            headers = spt.tab.get_headers();
            var last = headers[headers.length - 1].getAttribute("spt_element_name");
            spt.tab.select(last);
        }

        if (top.hasClass("spt_tab_save_state") ) {
            spt.tab.save_state();
        }
    }
   
    var changed_el = content.getElement(".spt_has_changes");
    var changed_row = content.getElement(".spt_row_changed");
    
    if (changed_el) {
        spt.confirm("There are unsaved changes in the current tab. Continue without saving?", ok, null, {ok_args : [changed_el, "spt_has_changed"]});
    }
    else if (changed_row) {
        spt.confirm("There are unsaved changes in the current tab. Continue without saving?", ok, null, {ok_args: [changed_row, "spt_row_changed"]});
    }
    else {
       ok(false);
    } 
}

        '''



    def get_config_xml(self):
        return '''
        <config>
        <tab>
        <element name="untitled" title="(Untitled)"/>
        </tab>
        </config>
        '''


    def add_styles(self):

        self.use_default_style = self.kwargs.get("use_default_style")
        if self.use_default_style not in [False, 'false']:
            self.use_default_style = True
        else:
            self.use_default_style = False

        if self.use_default_style:

            palette = self.top.get_palette()
            border = palette.color("border")
            color = palette.color("color")
            background = palette.color("background")

            data = {
                'border': border,
                'color': color,
                'background': background,
                'header_id': self.header_id,
            }



            from pyasm.web import HtmlElement

            style = HtmlElement.style()
            self.top.add(style)
            style.add('''
            #%(header_id)s .spt_tab_header {
                border-style: solid;
                border-color: %(border)s;
                border-width: 1px 1px 0px 1px;
                padding: 7px 5px;
                color: %(color)s;
                background: %(background)s;
            }

            #%(header_id)s .spt_tab_selected {
                opacity: 1.0;
                #border-bottom: none;
            }

            #%(header_id)s .spt_tab_unselected {
                opacity: 0.4 ;
                #border-bottom: solid 1px %(border)s;
            }

            #%(header_id)s .spt_tab_hover {
            }


            .spt_tab_content_body {
            }
            ''' % data)

 

    def get_display(self):

        top = self.top
        top.add_class("spt_tab_top")

        self.search_type = None

        self.view = self.kwargs.get("view")
        config_xml = self.kwargs.get("config_xml")
        config = self.kwargs.get("config")

        self.save_state = self.kwargs.get("save_state")
        if self.save_state in [True, 'true']:
            self.save_state = "save_state|main_tab"

        if self.save_state:
            saved_config_xml = WidgetSettings.get_value_by_key(self.save_state)
            if saved_config_xml:
                config_xml = saved_config_xml

            top.add_class("spt_tab_save_state")
            top.add_attr("spt_tab_save_state", self.save_state)


        self.mode = self.kwargs.get('mode')
        if not self.mode:
            self.mode = "default"


        if self.view and self.view != 'tab' and not config_xml:
            config = None

            # if it is not defined in the database, look at a config file
            includes = self.kwargs.get("include")
            if includes:
                includes = includes.split("|")
                for include in includes:
                    tmp_path = __file__
                    dir_name = os.path.dirname(tmp_path)
                    file_path="%s/../config/%s" % (dir_name, include)
                    config = WidgetConfig.get(file_path=file_path, view=self.view)
                    if config and config.has_view(self.view):
                        pass
                    else:
                        config = None

            if not config:

                search = Search("config/widget_config")
                search.add_filter("category", "TabWdg")
                search.add_filter("view", self.view)
                config_sobj = search.get_sobject()
                if not config_sobj:
                    config_xml = "<config><%s></%s></config>" % (self.view, self.view)
                else:
                    config_xml = config_sobj.get_value("config")
                config = WidgetConfig.get(view=self.view, xml=config_xml)
        else:

            if config:
                pass
            elif config_xml:
                # this is for custom config_xml with a matching custom view
                if not self.view:
                    self.view = 'tab'
                config = WidgetConfig.get(view=self.view, xml=config_xml)
            elif self.widgets:
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
                self.view = 'tab'
                config = WidgetConfig.get(view=self.view, xml=config_xml)


        element_names = self.kwargs.get("element_names")
        if element_names and isinstance(element_names, basestring):
            element_names = element_names.split(",")

        if not element_names:
            if config:
                element_names = config.get_element_names()
        
        if not element_names:
            element_names = []


        #top.add_style("padding: 10px")
        self.unique_id = top.set_unique_id()
        top.set_attr("spt_tab_id", self.unique_id)

        top.set_attr("spt_tab_mode", self.mode)

        gradient = top.get_gradient("background", -5, 5)

        inner = DivWdg();
        top.add(inner);
        inner.add_style("position: relative")
        inner.add_style("width: auto")


        if not Container.get_dict("JSLibraries", "spt_tab"):
            inner.add_behavior( {
            'type': 'load',
            'gradient': gradient,
            'cbjs_action': self.get_onload_js()
            } )


        header_div = DivWdg()
        header_div.add_class("spt_tab_header_top")
        self.header_id = header_div.set_unique_id()
        inner.add(header_div)
        header_div.add_style("height: auto")
        #header_div.add_style("overflow-y: hidden")
        #header_div.add_style("overflow-x: hidden")
        header_div.add_style("float: left")
        header_div.add_style("position: relative")
        header_div.add_style("z-index: 2")

        #header_div.add_style("width: 100%")
        header_div.add_style("margin-bottom: -1px")


        subheader_div = DivWdg()
        subheader_div.add_class("spt_tab_subheader_top")
        inner.add(subheader_div)
        self.add_subheader_behaviors(subheader_div)
        #subheader_div.add_style("display: none")
 


        self.add_styles()


        # if a search_key has been passed in, add it to the state.
        state = self.kwargs.get("state")
        if not state:
            state = self.kwargs

        search_key = self.kwargs.get("search_key")
        if search_key:
            state['search_key'] = search_key

        selected = self.kwargs.get("selected")
        if not selected:
            if element_names:
                selected = element_names[0]
            else:
                selected = ''

        offset = self.kwargs.get("tab_offset")
        if offset:
            header_div.add_style("padding-left: %s" % offset)


        if self.mode == "hidden":
            header_div.add_style("display: none")


        header_defs = {}

        title_dict = {}

        self.add_context_menu( header_div )


        loaded_dict = {}
        for element_name in element_names:
            attrs = config.get_element_attributes(element_name)
            title = attrs.get("title")
            if not title:
                title = Common.get_display_title(element_name)


            title = _(title)

            if attrs.get("display") == "false":
                continue

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

            header = self.get_tab_header(element_name, title, display_class, display_options, is_selected=is_selected, is_loaded=is_loaded, is_template=False, attrs=attrs)
            header_div.add(header)



        # add widgets that have been manually added
        for i, widget in enumerate(self.widgets):
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
                

            header = self.get_tab_header(name, title, class_name, kwargs, is_selected=is_selected, is_loaded=True, is_template=False)
            header_div.add(header)


        show_add = self.kwargs.get("show_add") not in [False, "false"]
        if show_add:
            inner.add( self.get_add_wdg() )

        # should only be seen by admin
        #security = Environment.get_security()
        #if security.check_access("builtin", "view_site_admin", "allow"):
        #    inner.add( self.get_edit_wdg() )


        inner.add("<br clear='all'>")


        content_top = DivWdg()
        content_top.add_class("spt_tab_content_top")
        content_top.add_style("z-index: 1")
        #content_top.add_style("margin-top: -1px")

        # add a div so that it breaks correctly
        if self.mode == 'default':
            content_top.add("<div style='height:5px'></div>")
            content_top.set_round_corners(5, corners=['TR','BR','BL'])
            border = self.kwargs.get("border_color")
            if not border:
                palette = content_top.get_palette()
                border = palette.color("border")
            content_top.add_style("border: 1px solid %s" % border)

        inner.add(content_top)

        height = self.kwargs.get("height")
        if height:
            content_top.add_style("height: %s" % height)
            content_top.add_style("overflow-y: auto")

            content_top.add_style("min-height: %s" % height)
        else:
            # TODO: make this configurable
            content_top.add_style("min-height: 500px")



        width = self.kwargs.get("width")
        if not width:
            content_top.add_style("min-width: 500px")
        else:
            content_top.add_style("min-width: %s" % width)

        content_top.add_class("tab_content_top")

        color_mode = self.kwargs.get("color_mode")
        if color_mode == "transparent":
            pass
        else:
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
            content_div.add_attr("spt_tab_id", self.unique_id)
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



        for widget in self.widgets:
            name = widget.get_name()
            content_div = DivWdg()
            content_div.add_class("spt_tab_content")
            content_div.add_attr("spt_tab_id", self.unique_id)
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
        header = self.get_tab_header(name, title, None, None, is_selected=is_selected, is_template=True)
        template_div.add(header)


        # subheader test
        subheader = self.get_tab_subheader(name, title, None, None, is_selected=is_selected, is_template=True, config=config)
        template_div.add(subheader)
        subheader.add_style("z-index: 3")

        header.add_behavior( {
            'type': 'click',
            'cbjs_action': '''

            var header_top = bvr.src_el.getParent(".spt_tab_header_top");
            var top = bvr.src_el.getParent(".spt_tab_top");
        

            var subheader_id = bvr.src_el.getAttribute("spt_subheader_id")

            var subheaders = top.getElements(".spt_tab_subheader");
            for ( var i = 0; i < subheaders.length; i++) {
                subheaders[i].setStyle("display", "none");
            }

            var el = $(subheader_id);
            var items = el.getElements(".spt_tab_subheader_item");
            if (items.length == 0) {
                return;
            }

            var size = bvr.src_el.getSize();
            var pos = bvr.src_el.getPosition(header_top);

            if (el) {
                el.setStyle("display", "");
                spt.body.add_focus_element(el);

                el.position({x: pos.x, y: pos.y+size.y-1}, el);
            }

            '''
        } )



        top.add(template_div)
        content_div = DivWdg()
        content_div.add_class("spt_tab_content")
        content_div.add_attr("spt_element_name", "NEW")
        content_div.add_attr("spt_tab_id", self.unique_id)
        content_div.add("")
        content_div.add_style("width: 100%")
        #content_div.add_style("height: 100%")
        content_div.add_style("text-align: left")
        template_div.add(content_div)

        return top


    def get_add_wdg(self):

        div = DivWdg()
        div.add_style("margin-left: -2px")

        icon_div = DivWdg()
        icon_div.add_style("padding: 0 2px 0 2px")
        icon_div.set_round_corners(12, corners=['TR'])
        from tactic.ui.widget import IconButtonWdg
        icon = IconButtonWdg(title="New Tab", icon=IconWdg.PLUS)
        icon = IconWdg("New Tab", IconWdg.PLUS)
        #icon.add_style("top: -1px")
        #icon.add_style("left: 0px")
        #icon.add_style("position: absolute")
        icon.add_style("margin-left: 3px")
        icon_div.add_class("hand")
        icon_div.add_style("opacity: 0.5")

        icon_div.add(icon)
        icon.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tab.top = bvr.src_el.getParent(".spt_tab_top");
        spt.tab.add_new();
        '''
        } )

        icon_div.add_style("float: left")
        icon_div.add_style("margin-top: 2px")
        icon_div.add_style("padding-top: 4px")
        icon_div.add_style("height: 21px")
        icon_div.add_style("width: 22px")
        icon_div.add_style("margin-left: 4px")
        icon_div.add_gradient("background", "background", -5, 5)
        icon_div.add_style("border-style: solid")
        icon_div.add_style("border-width: 1px 1px 0px 1px")
        icon_div.add_color("border-color", "border")
        icon_div.add_style("text-align: center")
        div.add(icon_div);

        self.extra_menu = self.kwargs.get("extra_menu")
        if self.extra_menu:
            icon_div = DivWdg()
            icon_div.set_round_corners(3, corners=['TR'])
            from tactic.ui.widget import IconButtonWdg
            icon = IconWdg("More Options", IconWdg.ARROWHEAD_DARK_DOWN)
            icon.add_style("margin-left: -2px")

            icon_div.add(icon)
            from smart_menu_wdg import SmartMenu
            smenu_set = SmartMenu.add_smart_menu_set( icon_div, { 'BUTTON_MENU': self.extra_menu } )
            SmartMenu.assign_as_local_activator( icon_div, "BUTTON_MENU", True )

            icon_div.add_style("padding-top: 4px")
            icon_div.add_style("margin-top: 10px")

            icon_div.add_style("float: left")
            icon_div.add_style("height: 16px")
            icon_div.add_style("width: 10px")
            icon_div.add_style("margin-left: -1px")
            icon_div.add_gradient("background", "background", -5, 5)
            icon_div.add_border()
            icon_div.add_style("text-align: center")
            icon_div.add_style("opacity: 0.5")
            div.add(icon_div);


        return div



    def get_edit_wdg(self):

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
        icon_div.add_gradient("background", "background", -5, 5)
        icon_div.add_border()
        icon_div.add_style("text-align: center")
        div.add(icon_div);

        return div




    def add_context_menu(self, header_div):

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


        menu_item = MenuItem(type='action', label='Rename Tab')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var class_name = 'tactic.ui.container.TabRenameWdg';
            var kwargs = {};

            var activator = spt.smenu.get_activator(bvr);
            var label = activator.getElement(".spt_tab_header_label");
            name = label.innerHTML;

            title = "Raname Tab ["+name+"]";
            var popup = spt.panel.load_popup(title, class_name, kwargs);
            popup.activator = activator;


            '''
        } )
        menu.add(menu_item)


        """
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
        """




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





        if self.kwargs.get("show_remove") not in ['false', False]: 
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


            menu_item = MenuItem(type='action', label='Close All Except This Tab')
            menu_item.add_behavior( {
            'cbjs_action': '''
            var activator = spt.smenu.get_activator(bvr);
            var top = activator.getParent(".spt_tab_top");
            spt.tab.top = top;

            var headers = spt.tab.get_headers();
            for (var i=0; i < headers.length; i++) {
                var element_name = headers[i].getAttribute("spt_element_name");
                if (activator.getAttribute('spt_element_name') != element_name) {
                    spt.tab.close(headers[i]);
                }

            }

            var element_name = activator.getAttribute("spt_element_name");
            spt.tab.select(element_name);

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


        has_my_views = True
        if has_my_views:
            menu_item = MenuItem(type='action', label='Add to My Views')
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


                var login = 'admin';

                var class_name = kwargs.class_name;
                if (!class_name) {
                    class_name = "tactic.ui.panel.CustomLayoutWdg";
                }


                var view = element_name;
                var element_name = element_name.replace(/ /g, "_");
                element_name = element_name.replace(/\//g, "_");

                element_name = login + "." + element_name;


                var kwargs = {
                    class_name: class_name,
                    display_options: kwargs,
                    element_attrs: {
                        title: title
                    },
                    login: login,
                    unique: false,
                }



                var view = "self_view_" + login;

                try {

                    var server = TacticServerStub.get();
                    var info = server.add_config_element("SideBarWdg", "definition", element_name, kwargs);
                    var info = server.add_config_element("SideBarWdg", view, element_name, kwargs);

                    spt.panel.refresh("side_bar");
                }
                catch(e) {
                    alert(e);
                    throw(e);
                }

                '''
            } )
            menu.add(menu_item)



        if self.kwargs.get("show_context_menu") not in ['false', False]:
            menus = [menu.get_data()]
            menus_in = {
                'DG_HEADER_CTX': menus,
            }
            from smart_menu_wdg import SmartMenu
            SmartMenu.attach_smart_context_menu( header_div, menus_in, False )






    def get_tab_header(self, element_name, title, class_name=None, kwargs=None, is_selected=False, is_loaded=False, is_template=False, attrs={}):


        web = WebContainer.get_web()

        header = DivWdg()
        header.add_class("spt_tab_header")
        header.add_attr("spt_tab_id", self.unique_id)
        header.add_class("hand")

        header.add_style("overflow: hidden")

        if self.use_default_style:
            header.set_round_corners(5, corners=['TL','TR'])


        #header.add_style("border-style: solid")
        #header.add_style("border-color: %s" % border)
        #header.add_style("border-width: 1px 1px 0px 1px")
        #header.add_style("padding: 7px 5px")
        #header.add_color("color", "color")

        #header.add_style("float: left")
        header.add_style("display: inline-block")
        header.add_style("vertical-align: top")
        header.add_style("margin-right: 1px")


        if is_selected:
            header.add_class("spt_tab_selected")
            header.add_class("spt_is_selected")
        else:
            header.add_class("spt_tab_unselected")


        palette = header.get_palette()
        hover_color = palette.color("background3")

        header.add_behavior( {
            'type': 'mouseenter',
            'color': hover_color,
            'cbjs_action': '''
            bvr.src_el.setStyle("background", bvr.color);
            '''
        } )
        header.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "");
            '''
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


 
        title_div = DivWdg()

        icon = None
        count = attrs.get("count")
        if icon:
            icon = IconWdg(name="whatever", icon=icon)
            title_div.add(icon)
        if count:
            count_color = attrs.get("count_color")

            state = self.kwargs.get("state") or {}
            search_key = state.get("search_key")

            if not search_key:
                search_key = self.kwargs.get("search_key")

            if search_key:
                sobject = Search.get_by_search_key(search_key)
            else:
                sobject = None

            if sobject:
                value = Search.eval(count, sobject)
                count_wdg = SpanWdg(value)
                count_wdg.add_class("badge")
                title_div.add(count_wdg)
                count_wdg.add_style("float: right")
                count_wdg.add_style("font-size: 0.7em")
                if count_color:
                    count_wdg.add_style("background", count_color)

                count_wdg.add_update( {
                    'expression': count,
                    'search_key': search_key,
                    'interval': 10,
                } )




        #if self.use_default_style:
        if True:
            title_div.add_style("min-width: 100px")
            title_div.add_style("text-align: left")
            title_div.add_style("overflow: hidden")
            title_div.add_attr("nowrap", "nowrap")
            title_div.add_style("float: left")


        title_div.add_class("spt_tab_header_label");
        #title_div.add_style("text-overflow: ellipsis")
        if len(title) > 20:
            display_title = "%s..." % title[:18]
        else:
            display_title = title
        title_div.add(display_title)
        header.add(title_div)



        title_div.add_attr("title", "%s (%s)" % (title, element_name))

        remove_wdg = DivWdg()
        remove_wdg.add_class("spt_tab_remove")

        show_remove = self.kwargs.get("show_remove")
        if is_template or show_remove not in [False, 'false']:
            header.add(remove_wdg)
        #header.add(remove_wdg)

        if show_remove == "hover":
            remove_wdg.add_style("opacity: 0.0")

            header.add_behavior( {
                'type': 'mouseenter',
                'cbjs_action': '''
                var el = bvr.src_el.getElement(".spt_tab_remove");
                el.setStyle("opacity", 1);
                '''

            } )

            header.add_behavior( {
                'type': 'mouseleave',
                'cbjs_action': '''
                var el = bvr.src_el.getElement(".spt_tab_remove");
                el.setStyle("opacity", 0);
                '''

            } )






        remove_wdg.add_styles("float: right; position: relative; padding-right: 14px")
        from pyasm.widget import IconButtonWdg
        #icon = IconButtonWdg("Remove Tab", IconWdg.CLOSE_INACTIVE)
        icon = IconWdg("Remove Tab", "FA_REMOVE", opacity=0.3)
        icon.add_class("spt_icon_inactive")
        icon.add_styles("margin: auto;position: absolute;top: 0;bottom: 0; max-height: 100%")
        remove_wdg.add(icon)
        #icon = IconButtonWdg("Remove Tab", IconWdg.CLOSE_ACTIVE)
        icon = IconWdg("Remove Tab", "FA_REMOVE")
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
        'type': 'click',
        'cbjs_action': '''
            spt.tab.close(bvr.src_el); 
        '''
        } )


        

        # add a drag behavior
        allow_drag = self.kwargs.get("allow_drag")
        if allow_drag not in [False, 'false']:
            header.add_style("position", "relative");
            header.add_behavior( {
            'type': 'drag',
            #"mouse_btn": 'LMB',
            "drag_el": '@',
            "cb_set_prefix": 'spt.tab.header_drag'
            } )

        header.add("&nbsp;")


        return header



    def get_tab_subheader(self, element_name, title, class_name=None, kwargs=None, is_selected=False, is_loaded=False, is_template=False, config=None):

        subheader_div = DivWdg()
        subheader_div.add_class("spt_tab_subheader")
        subheader_div.add_style("width: 200px")
        subheader_div.add_style("height: auto")
        subheader_div.add_border()
        subheader_div.add_style("position: absolute")
        subheader_div.add_style("left: 5px")
        subheader_div.add_color("background", "background")
        subheader_div.add_style("top: 28px")
        subheader_div.add_style("padding: 10px 5px")

        #element_names = ['my_tasks','all_orders','all_deliverables']
        element_names = []
        for element_name in element_names:
            attrs = config.get_element_attributes(element_name)
            title = attrs.get("title")
            if not title:
                title = Common.get_display_title(element_name)

            subheader = DivWdg()
            subheader.add_style("position: relative")
            subheader.add_attr("spt_element_name", element_name)

            subheader.add_class("spt_tab_subheader_item")

            icon = IconWdg("Remove Tab", "BS_REMOVE", opacity=0.3)
            subheader.add(icon)
            icon.add_class("spt_icon_inactive")
            icon.add_styles("position: absolute; right: 0; top: 3px;")


            subheader_div.add( subheader )
            subheader.add_style("padding: 5px")
            subheader.add(title)
     
            display_class = config.get_display_handler(element_name)
            display_options = config.get_display_options(element_name)

            """
            subheader.add_behavior( {
                'type': 'click',
                'title': title,
                'display_class': display_class,
                'display_options': display_options,
                'cbjs_action': '''
                spt.panel.load_popup(bvr.title, bvr.display_class, bvr.display_options);
                '''
            } )
            subheader.add_behavior( {
                'type': 'mouseenter',
                'cbjs_action': '''
                bvr.src_el.setStyle("background", "#DDD");
                '''
            } )
            subheader.add_behavior( {
                'type': 'mouseleave',
                'cbjs_action': '''
                bvr.src_el.setStyle("background", "");
                '''
            } )
            """


        return subheader_div



    def add_subheader_behaviors(self, subheader_top):

        subheader_top.set_unique_id()
        subheader_top.add_smart_style("spt_tab_subheader_item", "pointer", "cursor")

        subheader_top.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_tab_subheader_item',
            'cbjs_action': '''
            var element_name = bvr.src_el.getAttribute("spt_element_name");
            var title = bvr.src_el.getAttribute("spt_title");
            var display_class = bvr.src_el.getAttribute("spt_class_name");
            var kwargs_str = bvr.src_el.getAttribute("spt_kwargs");

            if (!kwargs_str) {
                kwargs = {}
            }
            else {
                kwargs_str = kwargs_str.replace(/&quote;/g, '"');
                kwargs = JSON.parse(kwargs_str);
            }

            spt.tab.load_selected(element_name, title, display_class, kwargs);

            '''
        } )
        subheader_top.add_relay_behavior( {
            'type': 'mouseenter',
            'bvr_match_class': 'spt_tab_subheader_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "#DDD");
            '''
        } )
        subheader_top.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': 'spt_tab_subheader_item',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "");
            '''
        } )


        subheader_top.add_relay_behavior( {
            'type': 'mouseleave',
            'bvr_match_class': 'spt_tab_subheader',
            'cbjs_action': '''
            bvr.src_el.setStyle("display", "none");
            '''
        } )



__all__.append("TabRenameWdg")
class TabRenameWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top
        top.add_style("margin: 20px")

        top.add_class("spt_tab_rename_top")

        top.add("<div>New Name:</div>")

        from tactic.ui.input import TextInputWdg
        from tactic.ui.widget import ActionButtonWdg

        text = TextInputWdg(name="new_name")
        text.add_class("spt_tab_new_name")
        top.add(text)

        text.add_behavior( {
            'type': 'load',
            'cbjs_action': 'bvr.src_el.focus()'
        } )



        top.add("<br/>")

        button = ActionButtonWdg(title="Rename", color="basic")
        top.add(button)
        button.add_style("float: right")



        button.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var popup = bvr.src_el.getParent(".spt_popup");
            var activator = popup.activator

            var rename_top = bvr.src_el.getParent(".spt_tab_rename_top");
            var input = rename_top.getElement(".spt_tab_new_name");
            new_name = input.value

            spt.popup.close(popup);

            var label = activator.getElement(".spt_tab_header_label");
            label.innerHTML = new_name;

            label.setAttribute("title", new_name);
            activator.setAttribute("spt_title", new_name);

            var top = spt.tab.top;
            if (!top) {
                spt.tab.set_main_body_tab();
                top = spt.tab.top;
            }

            if (top.hasClass("spt_tab_save_state") ) {
                spt.tab.save_state();
            }

            
            '''
        } )


        top.add("<br clear='all'/>")


        return top



from pyasm.command import Command
class TabSaveStateCmd(Command):
    def execute(self):

        class_names = self.kwargs.get("class_names")
        attrs_list = self.kwargs.get("attrs_list")
        kwargs_list = self.kwargs.get("kwargs_list")
        save_state = self.kwargs.get("save_state")

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

        WidgetSettings.set_value_by_key(save_state, xml_string)



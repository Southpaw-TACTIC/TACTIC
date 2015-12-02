/* *********************************************************
 *
 * Copyright (c) 2005-2010, Southpaw Technology
 *                     All Rights Reserved
 * 
 * PROPRIETARY INFORMATION.  This software is proprietary to
 * Southpaw Technolog, and is not to be reproduced, transmitted,
 * or disclosed in any way without written permission.
 * 
 * 
 */ 


// initialize api namspace.
//spt.api = {}


// method to retrieve project code
spt.api.get_project = function() {
    var server = TacticServerStub.get();
    return server.get_project();
}


// method to return the server url
spt.api.get_server_url = function() {
    return app.base_url; 
}


// Methods to retrieve input information
spt.api.get_input_values = function(element, filter, return_array, return_labels) {
    return spt.api.Utility.get_input_values(element, filter, return_array, return_labels);

}



// DOM navigation methods.  Uses the mootools frameworks DOM navigation
// method
spt.api.get_parent = function(el, tag) {
    return spt.get_parent(el, tag);
}

spt.api.get_elements = function(el, tag) {
    return spt.get_elements(el, tag);
}

spt.api.get_element = function(el, tag) {
    return spt.get_element(el, tag);
}

spt.api.add_class = function(el, class_name) {
    return $(el).addClass(class_name);
}

spt.api.remove_class = function(el, class_name) {
    return $(el).removeClass(class_name);
}

spt.api.set_style = function(el, name, value) {
    return $(el).setStyle(name, value);
}

spt.api.set_attribute = function(el, name, value) {
    return $(el).setAttribute(name, value);
}





// Loading methods
//

// Method to load a widget into a popup
//
// @param:
//  title - The title of the window.  This uniquely identifies the window and
//      any new content will always be reloaded into this same window.
//  class_name - the fully qualified Python class name for the widget
//      to be displayed
//  kwargs - (dict) the kwargs data structure that is to be passed into the
//      constructor of "class_name"
//
// @return:
//  null
//
// @examples:
//
//  The following will load a custom layout view "example01" into the window
//  titled "Example 01"
//
//      var class_name = 'tctic.ui.panel.CustomLayoutWdg';
//      var kwargs = {
//          view: 'example01'
//      };
//      spt.api.load_popup('Example01', class_name, kwargs);
//      
//      var web_values = {'json': search_data_dict}
//      spt.api.load_popup('Example01', class_name, kwargs, {'values': web_values});
//
spt.api.load_popup = function(title, class_name, kwargs, web_values) {
    
    return spt.panel.load_popup(title, class_name, kwargs, web_values);
}


// Method to close a popup
//
// @param:
//  el: the top popup element of any element in the popup.
//
// @return
//  null
//
//
// @examples:
//
//   The following will close a popup in a behavior of an element in a popup
//
//       var el = bvr.src_el;
//       spt.api.close_popup(el);
//
//
spt.api.close_popup = function(el) {
    spt.popup.close_popup(el);
}


// Method to load a widget into an existing panel
//
// @param:
//  title - the panel name or dom element to load the widget into
//  class_name - the fully qualified Python class name for the widget
//      to be displayed
//  cls_kwargs - (dict) the kwargs data structure that is to be passed into the
//      constructor of "class_name"
//  values - (dict) extra user chosen info to pass in  
//  kwargs - (dict) to set the async and fade option to true or false
//
// @return:
//  null
//
// @examples:
//
//  The following will load a custom layout view "example01" into panel with an id  'my_panel'
//
//      var class_name = 'tctic.ui.panel.CustomLayoutWdg';
//      var cls_kwargs = {
//          view: 'example01'
//      };
//      var panel = $('my_panel');
//      var kwargs = {async : true};
//      var values = {};
//      spt.api.load_panel(panel, class_name, cls_kwargs, values, kwargs);
//
spt.api.load_panel = function(panel, class_name, cls_kwargs, values, kwargs) {
    return spt.panel.load(panel, class_name, cls_kwargs, values, kwargs);
}



// Method to refresh a widget into an existing panel
//
// @param:
//  panel - the panel id or dom element to load the widget into
//  values - (dict) extra user chosen info to pass in  
//  kwargs - (dict) {fade : false, async: false, auto_find: false} to control the fade, asynchronous, and auto_find property
//
// @return:
//  null
//
// @examples:
//
//  The following will refresh a panel with a class "custom_panel" 
//
//      var kwargs = {fade : true, async: false, auto_find: false};
//      // when auto_find is true, it will refresh the nearest parent containing the spt_panel class
//      // this is usually extra user-chosen values to override what is already defined in the 
//      // cls_kwargs when the panel was first loaded
//      var values {};
//      var panel = spt.api.get_element(bvr.src_el, '.custom_panel');
//      spt.api.refresh_panel(panel, values, kwargs);
//
spt.api.refresh_panel = function(panel, values, kwargs) {
    if (kwargs && kwargs.auto_find)
        spt.panel.refresh_element(panel, values, kwargs);
    else
        spt.panel.refresh(panel, values, kwargs);
}

// Method to load a widget into the selected main tab
//
// @param:
//  title - the panel name or dom element to load the widget into
//  class_name - the fully qualified Python class name for the widget
//      to be displayed
//  kwargs - (dict) the kwargs data structure that is to be passed into the
//      constructor of "class_name"
//
// @return:
//  null
//
spt.api.load_tab = function(title, class_name, kwargs) {
    spt.tab.set_main_body_tab();
    spt.tab.load_selected(title, title, class_name, kwargs);
}




// Method fire a named event
//
// @param
//  name - name of the event
//
// @return
//  null
//  
spt.api.fire_event = function(name)
{
    return spt.named_events.fire_event(name)
}




// Method to show that the application is busy
//
spt.api.app_busy_show = function(title, description) {
    spt.app_busy.show(title, description);
}
spt.api.app_busy_hide = function(func) {
    spt.app_busy.hide(func);
}

// JSON methods
//
//
// Method to load in a JSON string and return a datastructure
//
// @params:
//     data_string: a stringified json data structure
//
// @return:
//     the data structure converted from the input data string
//
// @examples:
//     var data_string = '{"a": 1, "b": 2, "c": 3}';
//     var data = spt.api.jsonloads(data_string);
//     
spt.api.jsonloads = function(data_string) {
    return JSON.parse(data_string);
}

// Method to dump out a JSON data string from a given data structure
//
// @params:
//     data: the data structure to be converted to a string
//
// @return:
//     string: the returned JSON string
//
// @examples:
//     var data_string = {"a": 1, "b": 2, "c": 3};
//     var data_string = spt.api.jsondumps(data);
// 
spt.api.jsondumps = function(data) {
    return JSON.stringify(data);
}


// Method to a dynamic update to the element
//
// @params:
//     el: The element that will dynamically updated
//     update: Update data structure giving instructions how to update
//
// @return:
//     None
//
// @examples:
//     var data_string = {"a": 1, "b": 2, "c": 3};
//     var data_string = spt.api.jsondumps(data);
// 

spt.api.add_update = function(el, update) {
    var el_id = el.getAttribute("id");
    if (!el_id) {
        el_id = "SPT_" + Math.random(1000000);
        el.setAttribute("id", el_id);
    }
    el.addClass("spt_update");
    el.spt_update = {};
    el.spt_update[el_id] = update;
}


spt.api.remove_update = function(el) {
    el.removeClass("spt_update");
    el.spt_update = null;
}


/* Some others that need to be implmeneted

spt.load_link(el, link);
spt.load_custom_layout(el, view);

// libraries
tactic.table.xyz();
tactic.popup.xyz();
tactic.tab.xyz();


*/





// new API using tactic namespace
tactic = {}


tactic.validate_form = function(top_el)
{
    alert("validate form");

}











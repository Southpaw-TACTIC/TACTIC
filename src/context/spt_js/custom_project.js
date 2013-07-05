// *********************************************************
//
// Copyright (c) 2005-2008, Southpaw Technology
//                     All Rights Reserved
//
// PROPRIETARY INFORMATION.  This software is proprietary to
// Southpaw Technolog, and is not to be reproduced, transmitted,
// or disclosed in any way without written permission.
//
//


spt.CustomProject = new Class( {
    initialize: function() {}

} );

spt.custom_project = {};
//
// Callbacks
//

// Called when a type selection is made when creating a new property type
spt.CustomProject.property_type_select_cbk = function(el) {
    var panel = el.getParent(".spt_panel");
    var kwargs = { top_el: panel };

    spt.simple_display_hide('.foreign_key_options', kwargs);
    spt.simple_display_hide('.list_options', kwargs);
    spt.simple_display_hide('.button_options', kwargs);


    if (el.value == "foreign_key") {
        spt.simple_display_show('.foreign_key_options', kwargs);
    }
    else if (el.value == "list") {
        spt.simple_display_show('.list_options', kwargs);
    }
    else if (el.value == "button") {
        spt.simple_display_show('.button_options', kwargs);
    }
}




// called when the mode of "add property" is switched"
spt.CustomProject.switch_property_mode = function(evt, bvr) {
    var src_el = bvr.src_el;
    var value = src_el.value;

    var panel = src_el.getParent(".spt_panel")

    var element = panel.getElement(".spt_custom_simple")
    spt.simple_display_hide(element);
    //var element = panel.getElement(".spt_custom_widget")
    //spt.simple_display_hide(element);
    var element = panel.getElement(".spt_custom_xml")
    spt.simple_display_hide(element);

    var element = panel.getElement(".spt_custom_" + value)
    spt.simple_display_show(element);
}



spt.CustomProject.add_property_cbk = function(evt, bvr) {

    var search_type = bvr['search_type'];
    var view = bvr['view'];
    var exit = bvr['exit'];
    
    var panel = bvr.src_el.getParent(".spt_panel");
    var popup = bvr.src_el.getParent(".spt_popup");

    var mode = panel.getElement(".spt_custom_mode").value;
    var input_top = panel.getElement(".spt_custom_"+mode);
    var values = spt.api.Utility.get_input_values(input_top);
    
    // add the mode value
    values['custom_mode'] = mode;

    var class_name = "tactic.ui.app.CustomPropertyAdderCbk";
    var options = {
        'search_type': search_type,
        'view': view
    };


    var server = TacticServerStub.get();
    try {
        server.start({title:"Add new property"});
        var response = server.execute_cmd(class_name, options, values);
        if (exit == "true") {

            $('add_property_wdg').setStyle("display", "none");
            // this may or may not exist
            if (popup)
                spt.popup.close(popup);
        }
        else {
            // erase all of the inputs
            for (var i = 0; i < input_list.length; i++) {
                var filter = input_list[i];
                filter.value = "";
            }
        }
        var st_view = "definition";
        spt.panel.refresh("ManageSearchTypeMenuWdg_" + st_view);
    }
    catch (e) {
        server.abort();
        alert(spt.exception.handler(e));
    }

}




// FIXME: badly named.  Used in view manager

spt.CustomProject.pp_startx = 0;
spt.CustomProject.pp_starty = 0;

spt.CustomProject.pp_setup = function(evt, bvr) {
    spt.CustomProject.pp_startx = evt.clientX;
    spt.CustomProject.pp_starty = evt.clientY;
}


spt.CustomProject.pp_motion = function(evt, bvr) {
    var src_el = bvr.src_el;
    src_el.style.left = evt.clientX - spt.CustomProject.pp_startx;
    src_el.style.top = evt.clientY - spt.CustomProject.pp_starty;
}


spt.CustomProject.pp_action = function(evt, bvr) {
    var src_el = bvr.src_el;
    var drop_on_el = spt.get_event_target(evt);
    var drop_id = drop_on_el.getAttribute("id")

    spt.js_log.debug("drop_id: " + drop_id);
    spt.js_log.debug("src_id: " + src_el.getAttribute('id'));
    spt.js_log.debug("left: " + src_el.style.left);
    spt.js_log.debug("top: " + src_el.style.top);

    if (drop_id == null) {
        src_el.style.left = 0
        src_el.style.top = 0
        return;
    }

    var src_row = src_el.getParent("tr");
    var drop_row = drop_on_el.getParent("tr");

    drop_row.parentNode.insertBefore(src_row, drop_row);

    src_el.style.left = 0;
    src_el.style.top = 0;
    spt.CustomProject.pp_startx = src_el.style.left;
    spt.CustomProject.pp_starty = src_el.style.top;
}


//
// Execution of custom script
//
spt.CustomProject.get_script = function(script_code) {

    var server = TacticServerStub.get();
    var search_type = "config/custom_script";

    var filters = [['code', script_code]];
    var results = server.query(search_type, {filters:filters});
    if (results.length == 0) {
        alert("Custom script ["+script_code+"] does not exist");
        return;
    }

    var script = results[0]["script"]
    if (script == "") {
        alert("Custom script ["+script_code+"] is empty");
        return;
    }

    return script;

}


spt.CustomProject.get_script_by_path = function(script_path) {

    var server = TacticServerStub.get();
    var search_type = "config/custom_script";
    if (!script_path)
        return;
    var parts = script_path.split('/');
    var title = parts[parts.length-1];
    parts.pop();
    var folder = parts.join("/");

    var filters = [['folder', folder], ['title', title]];
    var results = server.query(search_type, {filters:filters});
    if (results.length == 0) {
        alert("Custom script ["+script_path+"] does not exist");
        return;
    }

    var script = results[0]["script"]
    if (script == "") {
        alert("Custom script ["+script_path+"] is empty");
        return;
    }

    return script;

}


spt.CustomProject.run_script_by_path = function( script_path, input )
{
    var script = spt.CustomProject.get_script_by_path( script_path );
    if( ! script ) {
        return;
    }
    try {
        if (!input) input = {};
        eval(script, input);
    } catch(e) {
        spt.alert("[ERROR in custom script '" + script_path + "']: " + e);
    }
}
spt.CustomProject.run_script_by_code = function( script_code, input )
{
    var script = spt.CustomProject.get_script( script_code );
    if( ! script ) {
        return;
    }
    try {
        if (!input) input = {};
        eval(script, input);
    } catch(e) {
        spt.alert("[ERROR in custom script '" + script_code + "']: " + e);
    }
}


spt.CustomProject.custom_script = function(evt, bvr) {

    var script_code = bvr.script_code

    var server = TacticServerStub.get();
    var search_type = "config/custom_script";

    var filters = [['code', script_code]];
    var results = server.query(search_type, {filters:filters});
    if (results.length == 0) {
        alert("Custom script ["+script_code+"] does not exist");
        return;
    }

    var script = results[0]["script"]
    if (script == "") {
        alert("Custom script ["+script_code+"] is empty");
        return;
    }

    bvr.script = script

    // wrap the script up in a function
    spt.CustomProject.exec_custom_script(evt, bvr);
}


spt.CustomProject.exec_custom_script = function(evt, bvr) {
    // FIXME: should be able to catch errors here.
    eval(bvr.script);
}



spt.CustomProject.exec_script = function(script) {
    // FIXME: should be able to catch errors here.
    eval(script);
}




spt.custom_project.manage_action_cbk = function(element, view, bvr) {

    // get the value of the element
    var value = element.value;
    if (value == "save") {
        // it could be saving other sub-views involved as well like reordering 
        // within the predefined views
        if (confirm("Are you sure you want to update the database schema of this search type [" + view + "] ?") ) {
            var server = TacticServerStub.get();
            server.start({"title": "Updating views"});

            spt.side_bar.save_view(view);
            
            spt.side_bar.changed_views = {};
            server.finish();
            //spt.panel.refresh("side_bar");
            // definition view is actually called custom_definition in the panel
            spt.panel.refresh("ManageSearchTypeMenuWdg_" + view);
        }
    }
    else if (value == "predefined") {
        spt.popup.open('predefined_db_columns');
    }

    else if ( value == "new_column" ) {
        spt.custom_project.context_menu_cbk(value, view);
    }
    
    else if ( value == "new_widget_column" ) {
        var widget_class = "tactic.ui.app.CustomPropertyAdderWdg";
        var options = {'search_type': bvr.search_type};
        spt.panel.load_popup('New Table Column', widget_class, options)
    }
    else {
        alert("Unimplemented option: " + value);
    }

    element.value = "";
}

spt.custom_project.context_menu_cbk = function(action, view) {

    var element_name = null;
  
    if (action == "new_column") {
        element_name = "new_column";
    }
    
    if (element_name) {
        var clone = spt.side_bar.add_new_item(view, element_name);
        clone.setStyle('background', '#6CB87B');
    }
}

spt.custom_project.save_definition_cbk = function() {

    var panel_id = "manage_side_bar_detail";

    var values = spt.api.Utility.get_input_values( panel_id );
    values['update'] = "true";
    spt.js_log.debug(values)

    // execute the command with the widget
    var fade = false;
    spt.panel.refresh(panel_id, values, fade);


    var view = values['view'];
    // Very likely, it is a name/title rename, we need to refresh these panels
    spt.panel.refresh("ManageSearchTypeMenuWdg_" + view);

}



// DEPRECATED: moved inline
spt.custom_project.change_column_cbk = function(bvr) {
    alert( "DEPRECATED: [spt.custom_project.change_column_cbk]");

    var class_name = 'tactic.ui.panel.AlterSearchTypeCbk';
    var options ={'alter_mode': bvr.alter_mode};

    try {
        rtn = TacticServerCmd.execute_cmd(class_name, 'search_type_detail', options);
        if (bvr.alter_mode == 'Remove Column')
            alert('Column Deleted')
    }
    catch (e) {
        alert(spt.exception.handler(e));
    }
    var view = 'db_column';
    spt.panel.refresh("ManageSearchTypeMenuWdg_" + view);
    var view = 'definition';
    spt.panel.refresh("ManageSearchTypeMenuWdg_" + view);
}




//
// This is used in the custom layout engine for resizing containers
//
spt.custom_project.drag_start = null;
spt.custom_project.prev_start = null;

spt.custom_project.divider_setup = function(mouse_411, evt, bvr) {
    var drag_el = bvr.drag_el;

    var prev = drag_el.getParent(".spt_container").getElement(".spt_content");

    if (bvr.mode == "height") {
        spt.custom_project.drag_start = mouse_411.curr_y;
        spt.custom_project.prev_start = prev.getSize().y;
    }
    else {
        spt.custom_project.drag_start = mouse_411.curr_x;
        spt.custom_project.prev_start = prev.getSize().x;
    }

}


spt.custom_project.divider_motion = function(mouse_411, evt, bvr) {

    var drag_el = bvr.drag_el;

    if (bvr.mode == "height") {
        var prev = drag_el.getParent(".spt_container").getElements(".spt_content");
        var diff = parseFloat(mouse_411.curr_y - spt.custom_project.drag_start);
        for (var i=0; i < prev.length; i ++) {
            prev[i].setStyle("height", spt.custom_project.prev_start + diff);
        }
    }
    else {
        //var prev = drag_el.getParent(".spt_panel").getElements(".spt_content");
        var prev = drag_el.getParent(".spt_container").getElements(".spt_content");
        var diff = parseFloat(mouse_411.curr_x - spt.custom_project.drag_start);
        for (var i=0; i < prev.length; i ++) {
            prev[i].setStyle("width", spt.custom_project.prev_start + diff);
        }

    }

}



//
// Method that splits the cells in two
spt.custom_project.split_horizontal = function(evt, bvr) {

    var activator = spt.smenu.get_activator(bvr);
    var parent = activator.getParent(".spt_container");

    var clone = spt.behavior.clone(parent);

    clone.inject(parent, 'after');

    var size = parent.getSize();

    var new_height = size.y / 2;
    if (new_height < 50) {
        new_height = 50;
    }
    parent.getElement('.spt_content').setStyle("height", new_height);
    clone.getElement('.spt_content').setStyle("height", new_height);
}


spt.custom_project.split_vertical = function(evt, bvr) {
}

//
// Method to remove a panel
//
spt.custom_project.remove_panel = function(evt, bvr) {

    var activator = spt.smenu.get_activator(bvr);
    var parent = activator.getParent(".spt_container");
    parent.destroy();
}


//
// Save the layout
//
spt.custom_project.save_layout = function(evt, bvr) {
    var activator = spt.smenu.get_activator(bvr);

    var top = activator.getParent(".spt_custom_content")
    //top.setStyle("border", "solid 1px blue");

    var new_top = top.clone();

    var config = '';
    var elements = top.getElements(".spt_container");
    var new_elements = new_top.getElements(".spt_container");


    for (var i = 0; i < elements.length; i++) {
        spt.js_log.warning("<div class='spt_panel'>");
        var element = elements[i];

        // Get information from the element
        var size = element.getSize();
        var position = element.getPosition(top);

        var new_element = document.createElement("element");
        new_element.setAttribute("width", size.x);
        new_element.setAttribute("height", size.y);
        new_element.setAttribute("top", position.x);
        new_element.setAttribute("left", position.y);

        new_element.replaces(new_elements[i]);
    }

    var config = new_top.innerHTML;


    var server = TacticServerStub.get();
    var view = 'whatever2';

    var data = {
        'search_type': 'CustomLayoutWdg',
        'view': view
    }
    var sobject = server.get_unique_sobject("config/widget_config", data);

    server.update(sobject['__search_key__'], {config: config} );

}

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



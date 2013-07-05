// ------------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to
//   Southpaw Technology Inc., and is not to be reproduced, transmitted,
//   or disclosed in any way without written permission.
// 
// ------------------------------------------------------------------------------



// DEPRECATED


spt.pipeline_editor = {}

function thisMovie(movieName) {
    if (navigator.appName.indexOf("Microsoft") != -1) {
        return window[movieName]
    }
    else {
        return document[movieName]
    }
}


var current_process = ""
var current_title = ""
var current_node_type = ""


spt.pipeline = {};

spt.pipeline.get_current_process = function()
{
    return current_process;
}


function get_properties(process_name, node_type) {

    var movie = thisMovie("pipeline_creator");
    // This is a popup
    var properties = $("spt_pipeline_properties");
    var node = properties.getElement(".spt_pipeline_node");
    var process_properties = properties.getElement(".spt_pipeline_process_properties");

    if (process_name == undefined) {
        process_name = movie.get_selected();
    }
    if (process_name == undefined) {
        node.innerHTML = "< None Selected >";
        return
    }

    // store these
    current_process = process_name;
    current_node_type = node_type;


    // refresh the dynamic part
    var top = $(movie).getParent(".spt_pipeline_top");
    var pipeline_code = top.getAttribute("spt_pipeline_code");


    if (node_type != "connector") {
        var kwargs = {
            pipeline_code: pipeline_code,
            process: process_name
        };
        spt.panel.load(process_properties, "pyasm.admin.creator.ProcessPropertiesWdg", kwargs);
    }

    

    node.innerHTML = '<b>' + node_type + ": " + process_name + '</b>';

    var properties = []
    if (node_type == "connector") {
        properties = ['context']
    }
    else {
        properties = ['group', 'completion', 'task_pipeline', 'assigned_login_group', 'supervisor_login_group','duration','color', 'label']
    }

    for (var i=0; i<properties.length; i++) {
        var property = properties[i]
        var element_id = 'property_'+properties[i]

        var value = ""
        if (node_type == "connector") 
            value = movie.get_connector_attr(process_name, property)
        else
            value = movie.get_node_attr(process_name, property)
            //console.log('value from action script: '+value)

        if (value == undefined || value == null || value == "null") {
            value = ""
        }
        $(element_id).value = value
    }
}

function set_properties() {
    var process_name = current_process
    var node_type = current_node_type

    // Not sure if we need this
    var movie = thisMovie("pipeline_creator")
    if (process_name == undefined) {
        process_name = movie.get_selected()
    }


    var properties = []
    if (node_type == "connector") {
        properties = ['context']
    }
    else {
        properties = ['group', 'completion', 'task_pipeline', 'assigned_login_group', 'supervisor_login_group', 'duration', 'color', 'label']
    }

    for (var i=0; i<properties.length; i++) {
        var property = properties[i]
        var element_id = 'property_'+properties[i]
        var value = $(element_id).value
        if (value == undefined || value == null || value == "null") {
            value = ""
        }

        if (node_type == "connector") {
            //alert("connect: " + process_name + " " + property + " " + value) 
            movie.set_connector_attr(process_name, property, value)
        }
        else {
            //alert("process: " + process_name + " " + property + " " + value) 
            movie.set_node_attr(process_name, property, value)
        }
    }

}



function toggle_properties() {
    toggle_display('properties_editor')
}
function toggle_context_properties() {
    toggle_display('context_editor')
}

function set_properties_on() {
    set_display_on('properties_editor')
}
function set_properties_off() {
    set_display_off('properties_editor')
}
function set_context_properties_on() {
    set_display_on('context_editor')
}
function set_context_properties_off() {
    set_display_off('context_editor')
}





function create_node(node_type) {
    var movie = thisMovie("pipeline_creator")
    movie.create_node(node_type)
}
function clear_nodes() {
    var movie = thisMovie("pipeline_creator")
    movie.clear_nodes()
}
function do_commit() {
    var movie = thisMovie("pipeline_creator")
    movie.do_commit()
}

spt.pipeline_editor.save = function(params) {
   var server = TacticServerStub.get();
   var class_name = params.class_name;
   delete(params.class_name);
   spt.app_busy.show( 'Pipeline Editor', 'Save' );
   setTimeout(function() {
        try {
            server.execute_cmd(class_name, params, {});
        }
        catch (e){
            alert(spt.exception.handler(e));
        } 
        spt.app_busy.hide();
   }, 50);

}

/*********************************************************
 *
 * Copyright (c) 2008, Southpaw Technology
 *                     All Rights Reserved
 * 
 * PROPRIETARY INFORMATION.  This software is proprietary to
 * Southpaw Technology, and is not to be reproduced, transmitted,
 * or disclosed in any way without written permission.
 * 
 * 
 */ 


import mx.controls.*
import tactic.PipelineContainer
import tactic.Node



/*
var showItem = true; // Change this to false to remove
var my_cm:ContextMenu = new ContextMenu(menuHandler);

my_cm.hideBuiltInItems();
my_cm.builtInItems.print = true;
my_cm.customItems.push(new ContextMenuItem("Create Search Type", itemHandler));
function menuHandler(obj, menuObj) {
    if (showItem == false) {
    menuObj.customItems[0].enabled = false;
    } else {
    menuObj.customItems[0].enabled = true;
    }
}
function itemHandler(obj, item) {
    //...put code here...
    trace("Create Search Type");
    _root.createEmptyMovieClip("loader_mc", this.getNextHighestDepth());
    var link = 'http://saba/tactic/racoon?sthpw%2Fsearch_object_search_ids=424%7C492&customize_project_tab=SObject+Creation&main_tab=Admin&admin_tab=Customize+Project&Refresh=Refresh&sobject_parent=bar%2Fasddf&form_key=9b812d08da09d8e0b92ae42727264021&is_form_submitted=yes'
    loader_mc.getURL(link, "tactic");
}
_root.menu = my_cm;
*/

/* Define external interface for html components */

import flash.external.*;


set_node_attr = function(node_name, attr, value) {
    var pipeline = PipelineContainer.get().get_current()
    node = pipeline.get_node(node_name)
    node.set_attr(attr, value)
}
ExternalInterface.addCallback("set_node_attr", this, this.set_node_attr);

get_node_attr = function(node_name, attr) {
    var pipeline = PipelineContainer.get().get_current()
    node = pipeline.get_node(node_name)
    return node.get_attr(attr)
}
ExternalInterface.addCallback("get_node_attr", this, this.get_node_attr);

// get all of the nodes in the session
get_nodes = function() {
    var pipeline = PipelineContainer.get().get_current()
    return pipeline.get_nodes()
}
ExternalInterface.addCallback("get_nodes", this, this.get_nodes);


// get the last selected item
get_selected = function() {
    var selected = get_selected()
    var selection = selected[selected.length - 1]
    return selection.get_name()
}
ExternalInterface.addCallback("get_selected", this, this.get_selected);


// get the attribute of a connector
get_connector_attr = function(connect_name, attr) {
    var pipeline = PipelineContainer.get().get_current()
    var connector = pipeline.get_connector(connect_name)

    //connector.get_attr(attr, value)
    if (connector.attrs == undefined) {
        connector.attrs = {}
    }
    return connector.attrs[attr]
}
ExternalInterface.addCallback("get_connector_attr", this, this.get_connector_attr);


// set the attribute of a connector
set_connector_attr = function(connect_name, attr, value) {
    var pipeline = PipelineContainer.get().get_current()
    var connector = pipeline.get_connector(connect_name)

    //return connector.set_attr(attr)
    if (connector.attrs == undefined) {
        connector.attrs = {}
    }
    connector.attrs[attr] = value
}
ExternalInterface.addCallback("set_connector_attr", this, this.set_connector_attr);










// NOT IMPLEMENTED
var undo = new Array()


/* Environment retrieval functions */
get_login_ticket = function() {
    return _root.login_ticket
}
get_url = function() {
    return _root.url
}
// determines the url to get the xml to load
get_load_xml = function() {
    return _root.load_xml
}
// get the pipeline code that this session uses
get_pipeline_code = function() {
    return _root.pipeline_code
}
// determines whether the title should be hidden
get_hide_title = function() {
    return _root.hide_title
}
// determines the type of connector that will be displayed
get_connector_type = function() {
    return _root.connector_type
}




/* Context functions */

var default_context = "none"
var _context = default_context

get_context = function() {
    return _context
}


set_context = function(ctx) {
    _context = ctx
}

set_default_context = function() {
    set_context(default_context)
}



/* Selection list functions */

var selected = new Array()

get_selected = function() {
    return selected
}

select = function(object) {
    clear_selected()
    add_to_selected(object)
}

add_to_selected = function(object) {
    //trace("adding: " + object)
    selected.push(object)
    object._alpha = "50"

    var selected_name = ""
    var node_type = object.node_type
    if (node_type == 'connector') {
        selected_name = object.input_node.get_name() + " -> " + object.output_node.get_name()
        selected_name = object._name
        ExternalInterface.call("set_context_properties_on")
        ExternalInterface.call("set_properties_off")
    }
    else {
        selected_name =  object.get_name()
        ExternalInterface.call("set_properties_on")
        ExternalInterface.call("set_context_properties_off")
    }
    ExternalInterface.call("get_properties", selected_name, node_type)
    //ExternalInterface.call("alert('"+object.node_type +"')")
}

clear_selected = function() {
    for (var i = 0; i < selected.length; i++) {
        var select = selected[i]
        select._alpha = "100"
    }
    selected = new Array()
    ExternalInterface.call("set_properties_off")
    ExternalInterface.call("set_context_properties_off")
}

get_selection_box = function() {
    return _root.selection
}





/* connector functions */

var connector_count = 0
var connectors = new Array()


function create_connector(conn_type) {
    if (conn_type == undefined)
        conn_type = 'dependency'

    connector_count += 1
    var depth = connector_count + 1000

    var pipeline = PipelineContainer.get().get_current()
    var pipeline_mc = pipeline.get_mc()

    var conn_name = "connector"+connector_count
    connector = pipeline_mc.attachMovie("connector_"+conn_type, conn_name, depth)


    connector.conn_type = conn_type
    connector.node_type = "connector"
    connector._mode = "mouse"
    connector.name = conn_name

    connectors.push(connector)

    pipeline.add_connector(connector)

    select(connector)
    return connector
}


function position_connector( connector ) {

  var node1 = connector.input_node
  var node2 = connector.output_node

  var node_xscale = node1.get_xscale()
  var node_yscale = node1.get_yscale()

  connector._x = node1._x + node_xscale
  connector._y = node1._y + (node_yscale/2)

  var geo = connector.geo
  if (connector.conn_type == 'hierarchy') {
    connector._x = node1._x + (node_xscale/2)
    connector._y = node1._y + (node_yscale)
    geo._xscale = (node2._x - node1._x )
    geo._yscale = (node2._y - (node1._y + node_yscale) )
  }
  else {
    connector._x = node1._x + node_xscale
    connector._y = node1._y + (node_yscale/2)
    geo._xscale = (node2._x - (node1._x + node_xscale) )
    geo._yscale = (node2._y - node1._y)
  }


  var label = connector.label
  label._x = geo._x + geo._xscale/2 + 5
  label._y = geo._y + geo._yscale - 20
}



function position_connector_to_mouse( connector, node ) {

  var node_xscale = node.get_xscale()
  var node_yscale = node.get_yscale()

  var node_xoffset = node_xscale

  connector._x = node._x + node_xoffset
  connector._y = node._y + (node_yscale/2)

  var mouse_xoffset = 2 
  var mouse_yoffset = 22 
  var node_container = PipelineContainer.get().get_current_mc()
  var xscale = (node_container._xmouse - (node._x + node_xoffset + mouse_xoffset) )
  var yscale = (node_container._ymouse - node._y - mouse_yoffset)
  if (xscale < 1 and xscale > -1) xscale = 1 
  if (yscale < 1 and yscale > -1) yscale = 1

  var geo = connector.geo
  var label = connector.label
  geo._xscale = xscale
  geo._yscale = yscale
  label._x = geo._x + geo._xscale/2 + 5
  label._y = geo._y + geo._yscale - 20
}


function delete_connector(delete_connector) {
    for (var i = 0; i < connectors.length; i++) {
        connector = connectors[i]
        if (connector == delete_connector) {
            connector.unloadMovie()
            connectors.splice(i,1)
            break
        }
    }
}

/* node functions */

var node_count = 0

var node_xscale = 120
var node_yscale = 40
var all_scale = 100



function set_scale(scale) {
    all_scale = scale
    node_container = PipelineContainer.get().get_current_mc()
    node_container._xscale = all_scale;
    node_container._yscale = all_scale;
}


create_node = function(node_type:String) {
    node_count += 1
    var depth = node_count + 2000
    var pipeline = PipelineContainer.get().get_current()
    var pipeline_mc = pipeline.get_mc()

    var node_name = "node"+node_count
    var node = pipeline_mc.attachMovie("node", node_name, depth)
    node._x = node_count * 5
    node._y = node_count * 5

    if (node_type == undefined)
        node_type = "process"

    node.set_node_type(node_type)
    node.set_name(node_name)

    pipeline.add_node(node)

    return node
}
ExternalInterface.addCallback("create_node", this, this.create_node);



function clear_nodes() {
    var pipeline = PipelineContainer.get().get_current()
    pipeline.clear_all()
}
ExternalInterface.addCallback("clear_nodes", this, this.clear_nodes);


function get_node(node_name) {
    var pipeline = PipelineContainer.get().get_current()
    return pipeline.get_node(node_name)
}


function delete_node(delete_node) {
    var pipeline = PipelineContainer.get().get_current()
    return pipeline.delete_node(delete_node)
}



/* functions to handle mouse events when nothing is hit...
   TODO: should probably have listeners here */

hit_test = function() {
    hit = false
    var pipeline = PipelineContainer.get().get_current()
    var pipeline_mc = pipeline.get_mc()
    var nodes = pipeline.get_nodes()
    for (var i = 0; i < nodes.length; i++) {
        var node = nodes[i]
        hit = node.hitTest(this._xmouse, this._ymouse)
        if (hit == true)
            break
    }

    return hit
}
 
handleMouseDown = function() {
    if ( hit_test() == true )
        return

    var context = get_context()
    if (context == "select") {
        clear_selected()
        box = get_selection_box()
	box._x = _root._xmouse
	box._y = _root._ymouse
        box.xstart = _root._xmouse
	box.ystart = _root._ymouse
	box._xscale = 1
	box._yscale = 1
	box._alpha = 100
        
    }
    else if (context == "panhold") {
        set_context("pan")
        var pipeline = PipelineContainer.get().get_current()
        var pipeline_mc = pipeline.get_mc()
        var nodes = pipeline.get_nodes()
        for (var i = 0; i < nodes.length; i++) {
            var node = nodes[i]
            node.xpan_mouse_start = pipeline_mc._xmouse
            node.ypan_mouse_start = pipeline_mc._ymouse
            node.xpan_start = node._x
            node.ypan_start = node._y
        }
    }
    else if (context == "drag") {
        trace("drag!!")
        for (var i = 0; i < selected.length; i++) {
            var select = selected[i]
            select.startDrag()
        }
    }
    else if (context == "none") {
        set_context("select")
        handleMouseDown()
    }

}


handleMouseMove = function() {

    var pipeline = PipelineContainer.get().get_current()
    var connectors = pipeline.get_connectors()

    for (var i = 0; i < connectors.length; i++) {
        var connector = connectors[i];
	if (connector._mode == "mouse")
	    _root.position_connector_to_mouse(connector, connector.input_node)
	else {
            _root.position_connector(connector)
        }
    }


}



handleEnterFrame = function() {

    var context = get_context()
    if (context == "select") {
        box = get_selection_box()
        box._xscale = _root._xmouse - box.xstart
        box._yscale = _root._ymouse - box.ystart
    }
    else if (context == "pan") {
        var pipeline = PipelineContainer.get().get_current()
        var pipeline_mc = pipeline.get_mc()
        var nodes = pipeline.get_nodes()
        for (var i = 0; i < nodes.length; i++) {
            var node = nodes[i]
            node._x = (pipeline_mc._xmouse - node.xpan_mouse_start + node.xpan_start)
            node._y = (pipeline_mc._ymouse - node.ypan_mouse_start + node.ypan_start)
        }
    }
}

handleMouseUp = function() {

    //if ( hit_test() == true )
    //    return

    var context = get_context()
    if (context == "select") {
        box = get_selection_box()
        var node_count = 0
        clear_selected()

        var pipeline = PipelineContainer.get().get_current()
        var nodes = pipeline.get_nodes()
        var connectors = pipeline.get_connectors()

        for (var i = 0; i < nodes.length; i++) {
            var node = nodes[i];
            if (box.hitTest(node)) {
                //trace("hit: " + node)
                add_to_selected(node)
                node_count += 1
            }
        }

        // do not select connectors is a single node is selected
        if (node_count == 0) {

            for (var i = 0; i < connectors.length; i++) {
                var connector = connectors[i];
                if (box.hitTest(connector)) {
                    trace("hit: " + connector)
                    add_to_selected(connector)
                }
            }

        }
        box._alpha = 0
    }
    else if (context == "pan") {
        set_context("panhold")
    }
    else if (context == "connect") {
        //clear_selected()
        /*
        selected = get_selected()
        var select = selected[0]
        delete_connector(select)

        */
    }
    else if (context == "text") {
        clear_selected()
        set_default_context()
    }
}




handleKeyDown = function() {
    //trace("DOWN -> Code: " + Key.getCode() + "\tACSII: " + Key.getAscii() + "\tKey: " + chr(Key.getAscii()))

    // text entry is most important
    if (get_context() == "text") {
        return
    }

    // certain keys override
    key_pressed = chr( Key.getAscii() )

    //if ( hit_test() == true )
    //    return

    if (key_pressed == 'f') {
        set_scale(100)
    }
    else if (key_pressed == 'q') {
        trace("q")
        var selection = selected[0]
        if (selection != undefined) {
            input = selection.node_geo.node_name
            input.visible = true
            input.setFocus()
            input.text = ""
            set_context("text")
        }

    }
    else if (key_pressed == '+' or key_pressed == '=') {
        var scale = all_scale + 3
        set_scale(scale)
    }
    else if (key_pressed == '-' or key_pressed == '_') {
        var scale = all_scale - 3
        set_scale(scale)
    }

    else if (Key.isDown(Key.ENTER) || key_pressed == 'e') {
        // first get the selected one
        var selection = selected[0]
        if (selection != undefined) {
            var name = selection.get_name()
            selection.expand()


            clear_selected()
            container = PipelineContainer.get()
            container.create(name)
            container.set_current(name)
        }
    }
    else if (key_pressed == 'u') {
        container = PipelineContainer.get()
        container.set_current("Main")
    }

    // open the properties widgets
    else if (key_pressed == 'p') {
        ExternalInterface.call("toggle_properties")
    }



    else if (Key.isDown(Key.CONTROL) || Key.isDown(Key.SPACE) ) {
        var context = get_context()
        if (context != "pan")
            set_context("panhold")

    }

    else if (Key.isDown(Key.DELETEKEY) || Key.isDown(Key.BACKSPACE) || key_pressed == 'd') {
        for (var i = 0; i < selected.length; i++) {
            var selection = selected[i]
            delete_node(selection)
            delete_connector(selection)
            set_default_context()
        }
    }

}


handleKeyUp = function() {
    //trace("UP -> Code: " + Key.getCode() + "\tACSII: " + Key.getAscii() + "\tKey: " + chr(Key.getAscii()))
    
    if ( hit_test() == true )
        return

    key_code = Key.getCode()
    if (key_code == Key.CONTROL || key_code == Key.SPACE) {
        set_default_context()
    }
}




var mouseListener:Object = new Object();
mouseListener.onMouseWheel = function(delta) {
    var scale = all_scale + delta
    set_scale(scale)
}
Mouse.addListener(mouseListener);



/* Import - Export functions */

dump_xml = function() {
    xml = new XML()
    root = xml.createElement("pipeline")
    root.attributes.scale = all_scale

    var pipeline = PipelineContainer.get().get_main()
    var nodes = pipeline.get_nodes()
    var connectors = pipeline.get_connectors()

    // reorder the nodes from left to right x positions
    function order(a,b):Number {
        var ax = a._x
        var bx = b._x
        if (ax<bx) {
            return -1
        } else if (ax>bx) {
            return 1
        } else {
            return 0
        }
    }
    nodes.sort(order)


    xml.appendChild(root)
    for (var i = 0; i < nodes.length; i++) {
        var node = nodes[i]
        var name = node.get_name()
        var node_type = node.get_node_type()
        if (node_type == undefined)
            node_type = "process"

        // create the node
        xml_node = xml.createElement(node_type)
        xml_node.attributes.name = name
        xml_node.attributes.xpos = node._x
        xml_node.attributes.ypos = node._y

        // get the attributes and set them
        for (key in node.attrs) {
            value = node.attrs[key]
            if (value == undefined || value == null || value == 'null') {
                continue
            }
            xml_node.attributes[key] = node.attrs[key]
        }

        root.appendChild(xml_node)

        // add action elements
        var action_data = node.get_data()
        for (var j = 0; j < action_data.length; j++) {
            var item = action_data[j] 
            var event = item['event']
            var scope = item['scope']
            var handler = item['handler']
            action_node = xml.createElement("action")
            var has_attrs = false

            if (event != undefined) {
                action_node.attributes.event = event
                has_attrs = true
            }
            if (scope != undefined) {
                action_node.attributes.scope = scope
                has_attrs = true
            }
            if (handler != undefined) {
                action_node.attributes.handler = handler
                has_attrs = true
            }

            if (has_attrs == true) {
                xml_node.appendChild(action_node)
            }
        }

    }

    for (var i = 0; i < connectors.length; i++) {
       var connector = connectors[i]
       var input_node = connector.input_node
       input_name = input_node.get_name()
       var output_node = connector.output_node
       if (output_node)
           output_name = output_node.get_name();
       else
           output_name = connector.cross_output;

       xml_node = xml.createElement("connect")
       xml_node.attributes.from = input_name
       xml_node.attributes.to = output_name
      
       //we want no output_name for cross-pipeline action
       if (!input_name || !output_name)
          continue;

       root.appendChild(xml_node)

       // get the attributes and set them
       for (key in connector.attrs) {
           xml_node.attributes[key] = connector.attrs[key]
       }

    }

    trace(xml)
    return xml
}



import_xml = function(xml_string) {
    xml = new XML()
    xml.ignoreWhite = true
    xml.parseXML(xml_string)

    root_node = xml.firstChild
    attributes = root_node.attributes
    scale = attributes.scale
    if (scale)
        set_scale(int(scale))



    xml_nodes = root_node.childNodes

    var num_connectors = 0
    var nodes = new Array()

    for (var i = 0; i < xml_nodes.length; i++) {
        var xml_node = xml_nodes[i]
        var attributes = xml_node.attributes

        node_name = xml_node.nodeName
        if (node_name == "process" || node_name == "pipeline" ||
                node_name == "search_type" )
        {
            xml_node_name = attributes.name

            // position the node
            xpos = attributes.xpos
            ypos = attributes.ypos

            if (!xpos) {
                xpos = 150 * i - 350 
                ypos = 50 * i - 150
            }
            node = create_node(node_name)
            nodes.push(node)
            // FIXME: this is not yet defined???
            node.set_name(xml_node_name)
            node.name = xml_node_name

            node._x = xpos
            node._y = ypos

            // import all of the other attributes
            if (attributes.completion != undefined)
                node.set_attr("completion", attributes.completion)
            if (attributes.task_pipeline != undefined)
                node.set_attr("task_pipeline", attributes.task_pipeline)
            if (attributes.group != undefined)
                node.set_attr("group", attributes.group)
            if (attributes.supervisor_login_group != undefined)
                node.set_attr("supervisor_login_group", attributes.supervisor_login_group)
            if (attributes.assigned_login_group != undefined)
                node.set_attr("assigned_login_group", attributes.assigned_login_group)
            if (attributes.duration != undefined)
                node.set_attr("duration", attributes.duration)
            if (attributes.color != undefined)
                node.set_attr("color", attributes.color)
            if (attributes.label != undefined)
                node.set_attr("label", attributes.label)
        }

        else if (node_name == "connect") {
            to_node = get_node( attributes.to )
            from_node = get_node( attributes.from )

            // skip if any of the nodes are null
            if ( from_node == undefined) {
                trace("skipping: " + attributes.from + " -> " + attributes.to)
                continue
            }

            var conn_type = get_connector_type()
            connector = create_connector(conn_type)
            connector.input_node = from_node
            connector.output_node = to_node;
            if (!to_node && attributes.to)
                connector.cross_output = attributes.to;

            if (attributes.context != undefined) {
                var conn_name = connector.name
                set_connector_attr(conn_name,"context", attributes.context)
            }

            connector._mode = "none"
            position_connector(connector)
            num_connectors += 1
        }
    }

    // if there are no connectors in the xml, then create some defaults
    if (num_connectors == 0 && nodes.length > 1) {
        for (var i = 0; i < nodes.length-1; i++) {
            var conn_type = get_connector_type()
            connector = create_connector(conn_type)
            connector.input_node = nodes[i]
            connector.output_node = nodes[i+1]
            connector._mode = "none"
            position_connector(connector)
            num_connectors += 1
        }
    }


}


do_commit = function() {

    var xml = dump_xml()

    var login_ticket = get_login_ticket()
    var url = get_url()
    var pipeline_code = get_pipeline_code()

    if (login_ticket == undefined) {
        ExternalInterface.call("alert", "Error: Could not find ticket")
        return
    }

    /*
    if (url == undefined) {
        ExternalInterface.call("alert", "Error: Could not find server")
        return
    }
    url = "http://" + url


    var result_vars:LoadVars = new LoadVars();

    var load_vars:LoadVars = new LoadVars()
    load_vars.xml = xml.toString()
    load_vars.dynamic_file = "true"
    load_vars.widget = "pyasm.admin.creator.CommitPipelineXml"
    load_vars.login_ticket = login_ticket
    load_vars.pipeline_code = pipeline_code
    load_vars.sendAndLoad(url, result_vars, "POST")
    */
    var param = {};
    param.xml =xml.toString();
    param.class_name = "pyasm.admin.creator.CommitPipelineXmlCmd";
    param.login_ticket = login_ticket;
    param.pipeline_code = pipeline_code;
    
    ExternalInterface.call("spt.pipeline_editor.save", param)

}

ExternalInterface.addCallback("do_commit", this, this.do_commit)



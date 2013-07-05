/* *********************************************************
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


class tactic.Pipeline {

private var name:String;
private var nodes:Array;
private var connectors:Array;

private var pipeline_mc = null

public function Pipeline(name:String, pipeline_mc) {
    this.name = name
    this.nodes = new Array()
    this.connectors = new Array()

    this.pipeline_mc = pipeline_mc
}

public function get_name() {
    return this.name
}

public function get_mc() {
    return this.pipeline_mc
}


public function add_node(node) {
    this.nodes.push(node)
}


public function get_node(node_name) {
    for (var i = 0; i < this.nodes.length; i++) {
        var node = this.nodes[i]
        
        //if (node.get_name() == node_name) {
        //if (node.node_geo.node_name.text == node_name) {
        if (node.name == node_name) {
            return node
        }
    }
    return null
}

public function get_nodes() {
    return this.nodes
}




public function add_connector(connector) {
    this.connectors.push(connector)
}

public function get_connectors() {
    return this.connectors
}

public function get_connector(connector_name) {
    for (var i = 0; i < this.connectors.length; i++) {
        var connector = this.connectors[i]
        
        if (connector.name == connector_name) {
            return connector
        }
    }
}


public function clear_all() {
    for (var i = 0; i < this.nodes.length; i++) {
        var node = this.nodes[i]
        node.unloadMovie()
    }
    this.nodes = new Array()

    for (var i = 0; i < this.connectors.length; i++) {
        var connector = this.connectors[i]
        connector.unloadMovie()
    }

    this.connectors = new Array()
}



public function delete_node(delete_node) {
    for (var i = 0; i < this.connectors.length; i++) {
        var connector = this.connectors[i]
        if (connector.output_node == delete_node || connector.input_node == delete_node) {
            connector.unloadMovie()
            this.connectors.splice(i,1)
            i -= 1
        }
    }
    for (var i = 0; i < this.nodes.length; i++) {
        var node = this.nodes[i]
        if (node == delete_node) {
            node.unloadMovie()
            this.nodes.splice(i,1)
            break
        }
    }
   
}



}







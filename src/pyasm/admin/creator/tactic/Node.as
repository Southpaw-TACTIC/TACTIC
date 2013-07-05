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
import flash.external.*;


class tactic.Node extends MovieClip {

private var name:String
private var node_geo:MovieClip
private var node_type:String
private var node_expand:MovieClip
private var data
private var attrs

public function Node() {
    this.attrs = {}
}

// function that gets executed when everything is loaded.  These variables
// can only be set when the whole movie is loaded
public function onLoad() {
    // set the name of the labels
    this.node_geo.node_name.text = this.name
    this.node_geo.node_label.text = this.name
} 


public function get_name() {
    //var text = this.node_geo.node_label
    //return text.text
    return this.name
}

public function set_name(node_name) {
    this.name = node_name
    this.node_geo.node_name.text = node_name
    this.node_geo.node_label.text = node_name
} 

public function set_node_type(node_type) {
    this.node_type = node_type
}

public function get_node_type() {
    return this.node_type
}

public function expand() {
    this.node_expand.gotoAndPlay(2)
}

/*
Accessor methods for attributes of the node itself
*/

public function set_attr(name, value) {
    this.attrs[name] = value
}

public function get_attr(name) {
    return this.attrs[name]
}


/*
Methods for the getting and retrieving from the data of a node.  The data
houses a bunch of data that is used to create the xml

data
 |-actions
 |-inputs (not implemented)
 |-outputs (not implemented)
 */

public function set_data(data) {
    this.data = data
}

public function get_data():Array {
    if (this.data == undefined) {
        this.data = new Array({})
    }
    return this.data
}


public function get_xscale() {
    if (this.node_type == "process" or this.node_type == 'search_type') {
        return 120
    } else {
        return 40
    }
}

public function get_yscale() {
    //return this.node_geo._yscale
    if (this.node_type == "process")
        return 40
    else
        return 40
}



}

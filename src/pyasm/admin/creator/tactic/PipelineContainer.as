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


import tactic.Pipeline


class tactic.PipelineContainer {

private var count = 1
private var pipelines = new Array()
private var current = 'Main'
private var top = null
private var main = null

public function PipelineContainer() {
    this.top = _root.node_container
    this.main = this.create("Main")
    this.pipelines[this.current] = this.main

}


public function create(pipeline_name) {

    // make sure it doesn't already exist
    if (this.pipelines[pipeline_name] != undefined)
        return this.pipelines[pipeline_name]

    this.count += 1
    var depth = this.count + 4000

    var pipeline_mc = this.top.attachMovie("node_container", pipeline_name, depth)


    pipeline_mc._x = 0
    pipeline_mc._y = 0

    var pipeline = new Pipeline()
    pipeline = new Pipeline(pipeline_name, pipeline_mc)

    this.pipelines[pipeline_name] = pipeline
    this.set_current(pipeline_name)

    return pipeline
}


public function get_current() {
    return this.pipelines[this.current]
}

public function get_current_mc() {
    return this.pipelines[this.current].get_mc()
}




public function get_main() {
    return this.pipelines['Main']
}

public function set_current(pipeline_name) {
    var current_mc = this.get_current_mc()
    if (pipeline_name != 'Main')
        current_mc._alpha = 5 
    else
        current_mc._alpha = 0

    this.current = pipeline_name
    var new_current_mc =  this.get_current_mc()
    new_current_mc._alpha = 100
}


/* get function */
private static var instance:PipelineContainer = null

public static function get():PipelineContainer {
    if (PipelineContainer.instance == null) {
        PipelineContainer.instance = new PipelineContainer()
    }
    return PipelineContainer.instance
}


}







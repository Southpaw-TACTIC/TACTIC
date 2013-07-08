/* *********************************************************
 *
 * Copyright (c) 2005, Southpaw Technology
 *                     All Rights Reserved
 * 
 * PROPRIETARY INFORMATION.  This software is proprietary to
 * Southpaw Technolog, and is not to be reproduced, transmitted,
 * or disclosed in any way without written permission.
 * 
 */ 

function include(file, base_dir)
{
    try {
        var contents = FLfile.read("file:///" +  base_dir + "/" + file )
        eval( contents )
    } catch (err) {
        fl.trace(err)
    }
}


/*
 * Initialize the session
 */
function init_session(load_mode, prefix_mode, log_path, sandbox_path)
{
    // completely create a new set of documents
    fl.trace(load_mode)
    if (load_mode == "new")
    {
        fl.closeAll()
        fl.createDocument()
    }
    // create a new document
    else if (load_mode == "simple")
    {
        // create the folder for sandbox
        FLfile.createFolder("file:///" +  sandbox_path)
    }
    // if load mode is merge, then don't create a new document
    else
    {
        // do nothing
    }
    my_load_info.load_mode = load_mode
    my_load_info.prefix_mode = prefix_mode
    my_load_info.log_path = log_path 
    my_load_info.sandbox_path = sandbox_path

    

}

function setup_doc(tmpl_path)
{
    var dst_doc = fl.getDocumentDOM()
    if (dst_doc == null)
    {
        if (tmpl_path == null)
            dst_doc = fl.createDocument()
        else
        {
            
            var new_tmpl_path = tmpl_path.replace('.fla', '_tactic.fla')
            names = new_tmpl_path.split("/")
            var new_tmpl_name = names[names.length - 1]
            // copy the tmpl file as something else first since
            // it will always get written over on next load

            // create the folder for sandbox
            FLfile.createFolder("file:///" +  my_load_info.sandbox_path)
            // TODO: copy to somewhere in the sandbox
            new_tmpl_path = my_load_info.sandbox_path + '/' +  new_tmpl_name
            var dst_URI = "file:///" +  new_tmpl_path

            if (FLfile.exists(dst_URI))
                FLfile.remove(dst_URI)
            FLfile.copy("file:///" + tmpl_path, dst_URI)

            //fl.trace("opening  " + new_tmpl_path )
            dst_doc = fl.openDocument(dst_URI)
        }
    }

    return dst_doc
}


/*
 *  Load an asset into a session
 */
function load_asset(src_path, tmpl_path, layer_name)
{
    var common = new Common()

    if (my_load_info.load_mode == 'simple')
    {
        var dst_URI = "file:///" + my_load_info.sandbox_path + '/' + layer_name + '_tactic.fla'
        // remove the old one before copying
        if (FLfile.exists(dst_URI))
            FLfile.remove(dst_URI)
        FLfile.copy("file:///" + src_path, dst_URI)
        fl.openDocument(dst_URI)
        common.exit("Loaded [" + layer_name + "]", my_load_info.log_path)
        return
    }

    // else handle merge mode

    
    // if a template is given open the template, otherwise create a new doc
    var dst_doc = setup_doc(tmpl_path)
    
    var src_uri = "file:///" + src_path
    if ( FLfile.exists(src_uri) == false)
    {
        common.exit("File '" + src_path + "' does not exist", my_load_info.log_path)
        return
    }
    // open the src_path
    src_doc = fl.openDocument(src_uri)

    // get the timelines
    src_timeline = src_doc.getTimeline()

    // copy the asset over
    // TO BE REMOVED: use source's first layer name if load_mode is not merge
    // if (my_load_info.load_mode != 'merge')
    //    layer_name = src_timeline.layers[0].name
    common.copy_layers( src_doc, dst_doc, layer_name)
    common.match_symbol_folders( src_doc.library, dst_doc.library)

    src_doc.close(false)

    fl.setActiveWindow(dst_doc)

    common.exit("Loaded [" + layer_name + "]", my_load_info.log_path)
}



/* import an asset, expects an image or supported video file */ 
    
function import_asset(src_path, tmpl_path, layer_name)
{
   
    var cur_doc = setup_doc(tmpl_path)

    timeline = cur_doc.getTimeline()

    var common = new Common()
    idx = common.create_layer(layer_name, timeline, true)

    //if (timeline.frameCount < 1)
    //   timeline.insertFrames()
    timeline.setSelectedFrames(0,1)

    // it doesn't really return a value, so we can't check for success
    document.importFile("file:///" + src_path)
    common.exit("Imported [" + layer_name + "]", my_load_info.log_path)

}


/*
 *  Import a bunch of frames in a selected directory into the session
 */

function import_leica( src_path, layer_name, start_frame, end_frame )
{
    var padding = 4

    //TODO: hard code start_frame to 1
    var by_frame = 2
    start_frame = 1
    end_frame = end_frame

    var cur_doc = fl.getDocumentDOM()
    if (cur_doc == null)
    {
        cur_doc = fl.createDocument()
    }

    var timeline = cur_doc.getTimeline()
    var library = cur_doc.library
    var layers = timeline.layers


    // add the appropriate frames in the timeline
    for (var i = 0; i < layers.length; i++) {
        timeline.setSelectedLayers(i)
        timeline.setSelectedFrames(end_frame-2, end_frame-2)
        timeline.insertFrames()
    }


    // add a new Leica layer
    timeline.addNewLayer(layer_name)
    library.newFolder(layer_name)
    leica_index = timeline.findLayerIndex(layer_name)[0]
    leica_layer = timeline.layers[leica_index]


    // import the leica
    for (var i=start_frame; i < end_frame; i += by_frame) {

        var idx = i - 1
        if (idx < 0) idx = 0
        timeline.setSelectedFrames(idx, idx)

        
        frame = new String(i)    
        digits = frame.length
        padded_frame = ""
        for (var j = 0; j < padding - digits; j++) {
            padded_frame += 0
        }
        padded_frame += frame


        var place_holder = ""
        for (var j = 0; j < padding; j++) {
            place_holder += "#"
        }

        path = src_path.replace(place_holder, padded_frame)
        path_uri = "file:///" + path
        if ( FLfile.exists(path_uri) == false)
        {
            fl.trace("WARNING: path '" + path + "' does not exist")
            continue
        }

        document.importFile(path_uri) 

        // scale the element
        var scale = 6.4 

        var element = leica_layer.frames[idx].elements[0]
        var matrix = element.matrix
        matrix.a = matrix.a * scale
        matrix.d = matrix.d * scale
        matrix.tx = 0
        matrix.ty = 0
        element.matrix = matrix

        // move the symbols to a Leica folder
        last_item = library.items[library.items.length-1]
        library.moveToFolder(layer_name, last_item.name)
    }
    fl.trace("loaded frames: " + start_frame + " to " + end_frame)

}



function import_audio(audio_path, layer_name)
{
    // extract the audio file
    audio_path_parts = audio_path.split("/")
    var audio_file = audio_path_parts[audio_path_parts.length-1]

    var cur_doc = fl.getDocumentDOM()
    if (cur_doc == null)
    {
        fl.trace("cur_doc is null")
        cur_doc = fl.createDocument()
    }


    // import audio
    timeline = cur_doc.getTimeline()
    library = cur_doc.library

    // find the layer: if it does not exist, then create it
    layer_idx = timeline.findLayerIndex(layer_name)
    if (layer_idx == null)
        timeline.addNewLayer(layer_name)
    
    library.newFolder(layer_name)

    timeline.setSelectedFrames(1,1)
    document.importFile("file:///" + audio_path) 
    library.selectItem(audio_file)
    library.addItemToDocument({x:0,y:0},audio_file)

    library.newFolder(layer_name)
    last_item = library.items[library.items.length-1]
    library.moveToFolder(layer_name, last_item.name)
    fl.trace("imported " + audio_file)
}


// TODO: this should be a custom post_stage script
function post_stage()
{
    // FIXME: BIG HACK
    // this is harmelss if there is no "Audio" layer
    var cur_doc = fl.getDocumentDOM()
    var timeline = cur_doc.getTimeline()
    var layers = timeline.layers

    // move layers below the guide layer
    var guide_idx = 0
    for (var i = 0; i < layers.length; i++ ) {
        layer = layers[i]
        if (layer.layerType == "guide") {
            guide_idx = i
            break
        }
    }


    // move all the new layers below the guide layer
    for (var i = 0; i < guide_idx; i++ ) {
        layer = layers[i]

        timeline.setSelectedLayers(i, true)
        timeline.setSelectedFrames(timeline.frameCount-1, timeline.frameCount-1)
        timeline.insertFrames()

        timeline.reorderLayer(i, guide_idx+1)
    }

    // set some default parameters
    fl.getDocumentDOM().height = 720;
    fl.getDocumentDOM().width= 1280;
    fl.getDocumentDOM().frameRate = 24;
}



function reset_document()
{
    fl.closeAll()
    fl.createDocument()
}

function close_docs()
{
    fl.closeAll()
}


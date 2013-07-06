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

/* a singleton for data storage */
my_load_info = new function()
{
    this.load_mode = null
    this.prefix_mode = null
    this.log_path = null 
    this.sandbox_path = null
}

Common = function()
{

this.exit = function(value, log_path)
{
    var out_URI = "file:///" + log_path
    var out_backup_URI = "file:///" +  log_path + ".bak"
    if (!FLfile.write(out_URI, value))
    {
        var msg = "Your browser has locked the log file and should be restarted"
        alert(msg)
        fl.trace("<Tactic>: " + msg)
    }
    else
    {
        fl.trace("<Tactic>: " + value)
    }
    FLfile.write(out_backup_URI, value)
    // the log_path on exit will be removed for proper functioning of Download Progress 
    // this step must be and will be handled by applet
}    

/*
 * Detects whether the source path is valid
 */
this.is_source_valid = function(src_path)
{
    if (src_path.indexOf('.fla') < 0 )
    {
        var msg = "<Tactic>: Source for [" +  layer_name
            + "] is invalid or does not exist. Skipped!"
        fl.trace(msg)
        return false
    }
    return true
}



/*
 *  Copies all of the layers on a timeline to another timeline
 */
this.copy_layers = function(src_doc, dst_doc, layer_name)
{
    src_timeline = src_doc.getTimeline()
    dst_timeline = dst_doc.getTimeline()
    
    src_timeline.selectAllFrames()
    src_timeline.copyFrames()

    // HACK: Bug in Flash 8: to select a layer, the document has to be active
    fl.setActiveWindow(dst_doc)

    // create the layer if it does not exist
    var create_above = true
    var idx = this.create_layer(layer_name, dst_timeline, create_above)


    dst_timeline.currentLayer = idx
    dst_timeline.pasteFrames(0)

}



this.match_symbol_folders = function(src_library, dst_library)
{
    src_library_items = src_library.items
    dst_library_items = dst_library.items

    // to fix a bug in flash, reproduce the symbol folders
    // re-establish the symbol folders
    for (var i = 0; i < src_library_items.length; i++)
    {
        src_name = src_library_items[i].name
        src_parts = src_name.split("/")

        if (src_parts.length == 1)
            continue

        for ( var j = 0; j < dst_library_items.length; j++)
        {
            dst_name = dst_library_items[j].name

            if (src_name == dst_name)
                continue

            dst_parts = dst_name.split("/")

            // if the destination symbol is already in a folder, continue
            if (dst_parts.length > 1)
                continue

            // match the last name
            if (dst_parts[dst_parts.length-1] == src_parts[src_parts.length-1])
            {
                src_parts.pop()
                new_folder_name = src_parts.join("/")
                dst_library.newFolder(new_folder_name)
                dst_library.selectItem(dst_name)
                dst_library.moveToFolder(new_folder_name)
                break
            }
        }
    }
}


/*
 * create the layer if it does not exist.  Ensures that Layer 1 is removed
 */
this.create_layer = function(layer_name, timeline, create_above)
{
   
    var default_idx = timeline.findLayerIndex("Layer 1")
    
    var new_idx = 0

    // this if statement has to be right before the addNewLayer call   
    // select the top layer or bottom layer depending on 'create_above'
    if (create_above)
        timeline.setSelectedLayers(0)
    else
        timeline.setSelectedLayers(timeline.layerCount-1)
    if (default_idx != 0)
        new_idx = timeline.addNewLayer(layer_name, 'normal', create_above)
    else
        // rename the layer [Layer 1]
        timeline.layers[0].name = layer_name
    
    // select the newly-created layer to prepare for frames removal
    timeline.setSelectedLayers(new_idx)
    timeline.removeFrames(0, timeline.frameCount)
   
    // move the layer to root level if created below
    if (!create_above) 
        timeline.layers[new_idx].parentLayer = null

    // clean out "Layer 1"
    /*
    useless_idx = timeline.findLayerIndex("Layer 1")
    if (useless_idx != undefined)
    {
        timeline.deleteLayer(useless_idx[0])
    }
    */
    
    return new_idx

}


/* Introspect the session and produce a file of information */
this.introspect = function(doc, out_path)
{
    // get all of the layers
    timeline = doc.getTimeline()
    layers = timeline.layers

    out_URI = "file:///" + out_path
    FLfile.remove(out_URI)

    FLfile.write(out_URI, "<introspect>\n", "apppend")
    FLfile.write(out_URI, "<layers>\n", "apppend")

    for (var i = 0; i < layers.length; i++)
    {
        layer = layers[i]
        node = '  <layer name="'+layer.name+'"/>\n'
        FLfile.write(out_URI, node, "apppend")
    }

    FLfile.write(out_URI, "</layers>\n", "apppend")
    FLfile.write(out_URI, "</introspect>\n", "apppend")

}



// end class
}






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


function publish_asset(asset_code, publish_path, log_path)
{
     // Remove the log file first
    FLfile.remove("file:///" + log_path)
    
    var cur_doc = fl.getDocumentDOM()
    if (cur_doc == null)
    {
         __exit("false", log_path)
        return
    }

    //rename_lib(cur_doc, asset_code)

    // FIXME: BIG HACK
    // this is harmelss if there is no "Audio" layer
    cur_doc = fl.getDocumentDOM()
    timeline = cur_doc.getTimeline()
    layers = timeline.layers
    move_flag = false
    asset_idx = 0
    for (var i = 0; i < layers.length; i++ ) {
        layer = layers[i]
        if (layer.name == "Assets") {
            asset_idx = i
            continue
        }

        if (layer.name == "Audio") {
            move_flag = true
            continue
        }

        if (!move_flag) {
            continue
        }
    
        timeline.setSelectedLayers(i, true)
        timeline.setSelectedFrames(timeline.frameCount-1, timeline.frameCount-1)
        timeline.insertFrames()

        timeline.reorderLayer(i, asset_idx+1)
    }


    fl.getDocumentDOM().height = 720;
    fl.getDocumentDOM().width= 1280;
    fl.getDocumentDOM().frameRate = 24;

    cur_doc.save()

  
    var cur_doc_URI = "file:///" + cur_doc.path.replace(/\\/g, "/") 
    var new_URI= "file:///" + publish_path + '/' + asset_code + ".fla"

    if (FLfile.exists("file:///" + publish_path ) == false)
        FLfile.createFolder("file:///" + publish_path )
    
    FLfile.remove(new_URI)
    var copied = FLfile.copy(cur_doc_URI, new_URI)

    if (move_flag) {
        cur_doc.close()
    }
    
    if (copied)
    {
        var new_doc = fl.openDocument(new_URI)
        new_doc.publish()
        new_doc.save()
        new_doc.close()
        __exit(asset_code, log_path)
    }
    else
    {
        alert("copied failed")
        __exit("false", log_path)
    }
    

}

/* rename a layer by adding layer_name as the prefix */ 
function rename_layer(layer_name)
{
    var cur_doc = fl.getDocumentDOM()
    var cur_timeline = cur_doc.getTimeline()
    var layers = cur_timeline.layers
    for (var k=0; k < layers.length; k++)
    {
        layers[k].name = layer_name + ":" + layers[k].name
    }
}
    
function close_doc()
{
    fl.getDocumentDOM().close(false)
}

/* publish a layer defined in tactic. 
   All Tactic layers are to be put into a Flash folder */
        
function publish_layer(shot_code, layer_name, tmpl, publish_path, log_path, is_prefix)
{
    // Remove the log file first
    FLfile.remove("file:///" + log_path)
 
    var cur_doc = fl.getDocumentDOM()
    var cur_doc_path = cur_doc.path
    if (cur_doc_path == null)
    {
        alert("The current document has to be saved first.")
        var saved = fl.saveDocumentAs(cur_doc)
        if (!saved)
        {
            __exit("false", log_path)
            return
        }
        cur_doc = fl.getDocumentDOM()
        cur_doc_path = cur_doc.path
    }
    
    if (FLfile.exists("file:///" + publish_path ) == false)
        FLfile.createFolder("file:///" + publish_path )

   

    // validate and get all the sub-layers in this folder
    var info = __find_layers_idx(cur_doc, layer_name, is_prefix)
    var layers_idx = info[0]
    var cur_timeline = info[1]
    
    if (layers_idx.length != 1 && layers_idx == false)
    {
        __exit("false", log_path)
        return
    }

   
    layers_idx.sort(__sort_num)

    var parent_layers = new Array(layers_idx.length)
   
    // store parent names 
    for (i=0; i < layers_idx.length; i++) 
    {
        var idx = layers_idx[i]
        parent = cur_timeline.layers[idx].parentLayer
        var parent_name = ''
        if (parent != null)
             parent_name = parent.name
           
        parent_layers[i] = parent_name
       
    }

    // create a temp file from a template
    var originalFileURI="file:///" + tmpl
    var newFileURI="file:///" + publish_path + '/' + shot_code 
        + "_" + layer_name + ".fla"
    // remove if the temp file exists
    FLfile.remove(newFileURI)
    FLfile.copy(originalFileURI, newFileURI)

    var tmp_doc = fl.openDocument(newFileURI)

    /// expand folder
    // cur_doc.getTimeline().expandFolder(true, true, layers_idx[0])

    var tmp_timeline = tmp_doc.getTimeline() 
    var layer_count = tmp_timeline.layerCount
    var boundary = new Array(2)
    boundary[0] = (layer_count == 1) ? layer_count - 1 : layer_count
    boundary[1] = layer_count + layers_idx.length - 1 
    
    for (i=0; i < layers_idx.length; i++) 
    {
        //add new layer
        if (i > 0 || layer_count > 1)
        {
            tmp_timeline.addNewLayer('','normal', false)
            layer_count = layer_count + 1
        }
        
        // bring the current doc back in focus
        cur_doc = fl.openDocument("file:///" + cur_doc_path.replace(/\\/g, "/") )
        var idx = parseInt(layers_idx[i])
        cur_timeline.setSelectedLayers(idx)
                         
        cur_timeline.copyFrames()
        
        // switch to tmp doc
        tmp_doc = fl.openDocument(newFileURI)

        var tmp_active_layer = tmp_timeline.layers[layer_count - 1] 

        // rename layer
        tmp_active_layer.name = cur_timeline.layers[idx].name
        
        // parent layers to parent
            
        var parent_layer =  __get_parent_layer(tmp_timeline, 
            boundary, parent_layers[i])

        if (parent_layer == false)
        {
            // Close and remove the tmp doc if there is an error
            tmp_doc.close(false)
            FLfile.remove(newFileURI)
            __exit("false", log_path)
 
            return
        }
        tmp_active_layer.parentLayer = parent_layer
        
        tmp_timeline.setSelectedLayers(layer_count-1)
        //alert("about to paste frame in layer " + (layer_count-1))
        tmp_timeline.pasteFrames() 	
    }  
    /// collapse folder
    //cur_doc.getTimeline().expandFolder(false, true, layers_idx[0])
    
    // the save command does not seem to block, so I save it again
    tmp_doc.save()
    tmp_doc.publish()
    var saved = tmp_doc.save()
  
    // bring the current doc back in focus
    cur_doc = fl.openDocument("file:///" + cur_doc_path.replace(/\\/g, "/") )
    
    __exit( layer_name, log_path)
    tmp_doc.close(false)
}

function __exit(value, log_path)
{
    var out_URI = "file:///" + log_path
    if (!FLfile.write(out_URI, value))
    {
        var msg = "Your browser has locked the log file and should be restarted"
        alert(msg)
        fl.trace("<Tactic>: " + msg)
    }
}    

/* get the timeline from a movie symbol with a name starting with "Camera" */
function __get_movie_timeline(cur_doc)
{
    var main_timeline = cur_doc.timelines[0]
    var layers = main_timeline.layers

    for (var i=0; i < layers.length; i++)
    {
        var layer = layers[i]
        if (__is_cam(layer.name))
        {
            var frames = layer.frames
            for (var j=0; j < frames.length; j++)
            {
                var element = frames[j].elements[0]
                // check the keyframe symbols, assuming single element
                // per frame
                if (element.elementType == "instance" && 
                    j == frames[j].startFrame)
                {
                    if (__is_cam(element.libraryItem.name))
                        return element.libraryItem.timeline
                }
            }
        }  
    }

    return null 
}


/* find the layers in 2 locations 
    1. in current timeline
    2. in main time line in Scene 1
    returns a idx and timeline in an array
*/
function __find_layers_idx(cur_doc, layer_name, is_prefix)
{
    var timeline = cur_doc.getTimeline()
    var idx = __get_layers_idx(timeline, layer_name, is_prefix) 
    if (!idx)
    {   
        timeline = __get_movie_timeline(cur_doc)
        if (timeline != null)
            idx = __get_layers_idx(timeline, layer_name, is_prefix)
    }
    var info = new Array(2)
    info[0] = idx
    info[1] = timeline
    return info
}

/* get the layer indices for the layer defined by this layer_name */
function __get_layers_idx(timeline, layer_name, is_prefix)
{
    if (is_prefix)
    {
        var layers_idx = new Array()
        var layers = timeline.layers
        var counter = 0
        for (var i=0; i< layers.length; i++)
        {
            if (__like(layers[i].name, layer_name + ":"))
            {
                idx_array =  timeline.findLayerIndex(layers[i].name)
                if (idx_array.length > 1)
                {
                    alert("duplicated layer names found")
                    return false
                }
                layers_idx[counter++] =  idx_array
            }
                
        }
       
        if (layers_idx.length > 0) 
            return layers_idx
        else
            return false
    } 

    var matched_parent_idx = timeline.findLayerIndex(layer_name)
    if (matched_parent_idx == null)
    {
        //alert("Layer [" + layer_name + "] cannot be found in the session!")
        return false
    }
    if (matched_parent_idx.length > 1)
    {
        alert("There should only be 1 layer named [" +  layer_name + "]"
            + " in the session. Please delete or rename the duplicated one.")
        return false
    }
    
    var idx = matched_parent_idx[0] + 1
    while (timeline.layers[idx].layerType != 'folder' &&
            timeline.layers[idx].parentLayer !=null)
    {
        idx++
        if (timeline.layers[idx] == null)
            break

    }
    var layers_idx = new Array(idx-matched_parent_idx[0])
    for (k=0; k < (idx-matched_parent_idx[0]); k++)
        layers_idx[k] = matched_parent_idx[0] + k 
    
    return layers_idx
}

/* get the parent layer in the given timeline */
function __get_parent_layer(timeline, boundary, name)
{
    if (name == '')
        return null
    var matched_layer_idx = timeline.findLayerIndex(name)
    var layer = null 
    var match_count = 0
    //alert ("boundary " + boundary[0] + " "  + boundary[1])    
    if (matched_layer_idx == null )
    {
        alert("layer name [" + name + "] is invalid!")
        return false
    }
    
    for ( var i=0 ; i<matched_layer_idx.length; i++)
    {
        var idx = matched_layer_idx[i] 
        //alert("matched idx  " + idx + " " + name)
        if (idx >= boundary[0] && idx < boundary[1])
        {
            layer = timeline.layers[idx]
            match_count++
        }
    }
    
    if (match_count != 1)
    {
        alert("layer name [" + name + "] has to be unique! " + match_count
            + " found.")
        return false
    }
    return layer
}

// add unique prefix to the library items
function rename_lib(cur_doc, prefix)
{
    var lib_items = cur_doc.library.items
    for (var i=0; i<lib_items.length; i++)
    {
        // select the item
        var item = lib_items[i]
        cur_doc.library.selectItem(item.name, true, true)
        
        // rename only if the prefix does not exist
        if (item.name.indexOf(prefix) != 0 )
            cur_doc.library.renameItem(prefix + "_" + item.name)
       
    }
}

/* create a library folder if it does not exist */
function create_lib(cur_doc, folder_name)
{
    if (cur_doc.library.itemExists(folder_name) == false)
        cur_doc.library.newFolder(folder_name)
}

/* move a top-level item to a library folder  */
function edit_lib(cur_doc, folder_name)
{
    var lib_items = cur_doc.library.items
    for (var i=0; i<lib_items.length; i++)
    {
        // select the item
        var item = lib_items[i]
        cur_doc.library.selectItem(item.name, true, true)

        // check if it is in a folder
        if (item.name.indexOf('/') < 0 && item.itemType != 'folder' )
        {
            // ask for move confirmation
            var answer = confirm("Move [" + item.name + "] to folder [" 
                + folder_name + "]?")
            if (answer == true)
                cur_doc.library.moveToFolder(folder_name)
        }
    }
}

function __sort_num(a,b)
{
    return a-b
}

/* check if the name starts with 'Camera' */
function __is_cam(name)
{
    return __like(name, "Camera")
}

function __like(name, str)
{      
    if (name.indexOf(str) > -1)
        return true
    else
        return false
}

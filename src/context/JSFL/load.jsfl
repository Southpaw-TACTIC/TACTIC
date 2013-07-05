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


/* import an asset, expects an image or supported video file */ 
    
function import_asset(src_path, tmpl_path, asset_code, log_path)
{
    
    var cur_doc = null
    cur_doc = fl.getDocumentDOM()

    if (cur_doc == null || cur_doc.path == null)
    {
        fl.openDocument("file:///" + tmpl_path )
        cur_doc = fl.getDocumentDOM()
    }
    
    document.importFile("file:///" + src_path) 
    FLfile.remove("file:///" + src_path)
    
    return cur_doc
}


/* import a series of images */

function import_leica(src_path, tmpl_path, asset_code, log_path)
{
    var cur_doc = fl.getDocumentDOM()


    if (cur_doc == null || cur_doc.path == null)
    {
        fl.openDocument("file:///" + tmpl_path )
        cur_doc = fl.getDocumentDOM()
    }
    
    var timeline = cur_doc.getTimeline()

    var frames = 10
    for (i=0; i < frames; i++) {
        // skip the first one
        if (i!=0)
            timeline.insertKeyframe(i);
        document.importFile("file:///" + src_path) 
    }
}



/*
    load a flash asset defined in Tactic in 
    simple mode (loaded as a separate file) or 
    merge mode (loaded into the current file)

Args:
    src_path:        path of the flash file to be loaded
    tmpl_path:       path of the template file
    asset_code:      the code of the sobject being loaded
    load_mode:       either simple or merge
    log_path:
    is_prefix:       determines whether to load with a prefix or not
    post_load_path:  location of the post loading script
 */ 
function load_asset(src_path, tmpl_path, asset_code, load_mode, log_path, 
                    is_prefix, post_load_path)
{
    if (is_source_valid(src_path, asset_code) == false)
        return
    
    var cur_doc = null

    if (load_mode == 'simple')
    {
        cur_doc = fl.openDocument("file:///" + src_path )
        // run the post_load script
        if (post_load_path != null)
        {
            if (FLfile.exists("file:///" + post_load_path))
                fl.runScript("file:///"  + post_load_path, 'post_load_asset', asset_code)
            else
                fl.trace("<Tactic>: Postloading asset script not found!")
        }
    }
    else if (load_mode == 'merge')
    {
        cur_doc = fl.getDocumentDOM()
        src_doc = fl.openDocument("file:///" + src_path )
        // run the post_load script
        if (post_load_path != null)
        {
            if (FLfile.exists("file:///" + post_load_path))
                fl.runScript("file:///" + post_load_path, 'post_load_asset', asset_code)
            else
                fl.trace("<Tactic>: Postloading asset script not found!")
        }
        if (cur_doc == null || cur_doc.path == null)
        {
            fl.openDocument("file:///" + tmpl_path )
            cur_doc = fl.getDocumentDOM()
        }
        
        var src_timeline = src_doc.getTimeline()
        if (is_prefix)
        {
            // trash the need to verify source's asset_code
            is_asset = true
            load_layer(src_path, '', asset_code, cur_doc, log_path, true, is_asset, null)
        }
        else
        {
            var idx = __get_parent_folder(src_timeline)
            if (idx == -1)
            {
                var msg = "Merge loading requires the source [" + asset_code 
                    + "] to contain only "
                    + "1 parent folder. Loaded as a seperate file instead."
                alert(msg)
                fl.trace("<Tactic>: "+msg)
                __exit("false", log_path)
                return
            }
            var layer_name = src_timeline.layers[idx].name
            is_asset = false // this is only applicable in prefix mode
            load_layer(src_path, '', layer_name, cur_doc, log_path, false, is_asset, null)
        }
        FLfile.remove("file:///" + src_path)
    }
    
    return cur_doc

}
    
/*
    load a layer defined in Tactic. 
    All Tactic layers are put into their corresponding Flash folders
*/     
function load_layer(src_path, tmpl_path, layer_name, cur_doc, log_path,
         is_prefix, is_asset, post_load_path) 
{

    if (is_source_valid(src_path, layer_name) == false)
        return

    if (cur_doc == null)
        cur_doc = fl.getDocumentDOM()
   
    // open a template file if no document is active
    if (cur_doc == null || cur_doc.path == null)
    {
        alert(temp_path)
        fl.openDocument("file:///" + tmpl_path )
        cur_doc = fl.getDocumentDOM()
    }
    var cur_doc_path = cur_doc.path
    var cur_timeline = cur_doc.getTimeline()

    // open the layer source   
    fl.openDocument("file:///" + src_path )
    
    // run the post_load script
    if (post_load_path != null)
    {
        if (FLfile.exists("file:///" + post_load_path))
            fl.runScript("file:///"  + post_load_path, 'post_load_layer', layer_name)
        else
            fl.trace("<Tactic>: Postloading layer script not found!")
    }
    var src_doc = fl.getDocumentDOM()
    var src_timeline = fl.getDocumentDOM().getTimeline()
    var src_library_items = fl.getDocumentDOM().library.items
   
    // validate and get all the sub-layers in this folder
   
    // find all the layer with this layer_name prefix or by folder name
    
    var layers_idx = __get_layers_idx(cur_doc, src_timeline, layer_name, is_prefix, is_asset) 
    //alert("layers_idx " + typeof(layers_idx))

    if (layers_idx.length != 1 && layers_idx == false)
    {
        var msg = "<Tactic> : Error loading layer [" + layer_name 
            + "]."
        fl.trace(msg)
        src_doc.close(false)
        return
    }
    layers_idx.sort(__sort_num)
    
    var parent_layers = new Array(layers_idx.length)

    // store parent names 
    
    for (i=0; i < layers_idx.length; i++) 
    {
        var idx = layers_idx[i]
        parent = src_timeline.layers[idx].parentLayer
        var parent_name = ''
        if (parent != null)
             parent_name = parent.name
           
        parent_layers[i] = parent_name
 
    }
    // expand folder
    // src_doc.getTimeline().expandFolder(true, true, layers_idx[0])
   
    // make last layer active
    var last_layer_idx = cur_timeline.layerCount - 1
   
    // bring the current doc back in focus
    fl.openDocument("file:///" + cur_doc_path.replace(/\\/g, "/") )
        
    cur_timeline.currentLayer = last_layer_idx
    
    var layer_count = cur_timeline.layerCount
    var boundary = new Array(2)
    boundary[0] = (layer_count == 1) ? layer_count - 1 : layer_count
    boundary[1] = layer_count + layers_idx.length - 1 
    
    for (i=0; i < layers_idx.length; i++) 
    {
        // add new layer
        if (i > 0 || layer_count >= 1)
        {
            // only skips if the layer is the default 'Layer 1'
            if (!(layer_count == 1 && cur_timeline.layers[0].name == 'Layer 1'))
            {
                cur_timeline.addNewLayer('','normal', false)
                layer_count = layer_count + 1
            }
        }
       
        // switch to src doc 
        fl.openDocument("file:///" + src_path )
        var idx = layers_idx[i]

        src_timeline.setSelectedLayers(idx)
                 
        src_timeline.copyFrames()
        var cur_idx = layer_count - 1
        var cur_active_layer = cur_timeline.layers[cur_idx] 

        // back to cur doc
        fl.openDocument("file:///" + cur_doc_path.replace(/\\/g, "/") )

        // rename layer
        //alert("renaming layer " + cur_idx + " to [" + src_timeline.layers[idx].name + "]")
        cur_active_layer.name = src_timeline.layers[idx].name
        
        // parent layers to parent
        var parent_layer =  __get_parent_layer(cur_timeline, 
            boundary, parent_layers[i])

        if (parent_layer == false)
        {
            src_doc.close(false)
             __exit("false", log_path)
 
            return
        }
        cur_active_layer.parentLayer = parent_layer

        cur_timeline.setSelectedLayers(cur_idx)
        cur_timeline.pasteFrames() 
           	
    } 
   
    /// collapse folder
    //src_doc.getTimeline().expandFolder(false, true, layers_idx[0])

    // re-establish the symbol folders
    cur_library_items = cur_doc.library.items
    for (var i = 0; i < cur_library_items.length; i++) {
        cur_name = cur_library_items[i].name
        cur_parts = cur_name.split("/")

        for ( var j = 0; j < src_library_items.length; j++) {
            src_name = src_library_items[j].name
            src_parts = src_name.split("/")

            if (cur_parts[cur_parts.length-1] == src_parts[src_parts.length-1])
            {
                //fl.trace("match")
                //fl.trace("... "+ src_name)
                //fl.trace("... "+ cur_name)
                //fl.trace("")
                src_parts.pop()
                cur_doc.library.newFolder(src_parts.join("/"))
                cur_doc.library.selectItem(cur_name)
                cur_doc.library.moveToFolder(src_parts.join("/"))
                break
            }
        }

    }



    // close src
    src_doc.close(false)   
    var removed = FLfile.remove("file:///" + src_path)
    
    if (removed)
         fl.trace("<Tactic>: Loading and clean-up finished for [" + layer_name + "]")
    
    return cur_doc

}

function is_source_valid(src_path, layer_name)
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

/* exit and write a value to the log */
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


/* get the layer indices for the layer defined by this layer_name */

function __get_layers_idx(cur_doc, timeline, layer_name, is_prefix, is_asset)
{
    if (is_prefix)
    {
        var layers_idx = new Array()
        var layers = timeline.layers
        var counter = 0
        for (var i=0; i< layers.length; i++)
        {
            
            if (is_asset || __like(layers[i].name, layer_name + ":"))
                layers_idx[counter++] =  parseInt(timeline.findLayerIndex(
                    layers[i].name))
        }
        if (layers_idx.length > 0) 
            return layers_idx
        else
            return false
    } 
   
    // if is_prefix is false, try the original detection by folder    


    var matched_parent_idx = timeline.findLayerIndex(layer_name)
    var layers_idx = true
    if (matched_parent_idx == null)
    {
        //alert("Layer [" + layer_name + "] cannot be found in the session!")
        layers_idx = false
    }
    else if (matched_parent_idx.length > 1)
    {
        alert("There should only be 1 layer named [" +  layer_name + "]"
            + " in the session. Please delete or rename the duplicated one.")
        layers_idx = false
    }
    if (layers_idx == false)
    { 
        var answer = confirm("If [" + layer_name 
            + "] is a new empty layer, please click 'OK'.   ")
        if (answer == true)
        {
            // initialize a layer
            timeline.addNewLayer(layer_name, 'folder')
            matched_parent_idx = timeline.findLayerIndex(layer_name)
            timeline.layers[1].parentLayer = timeline.layers[matched_parent_idx[0]]
            
            // initialize library (commented out for now)
            //create_lib(cur_doc, layer_name)
        }
        else
            return false
    }
    
    var idx = matched_parent_idx[0] + 1
    var layer = timeline.layers[idx] 
    while (timeline.layers[idx].layerType != 'folder' ||
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
    
    if (matched_layer_idx == null )
    {
        alert("layer name [" + name + "] is invalid!")
        return false
    }
    
    for ( var i=0 ; i<matched_layer_idx.length; i++)
    {
        var idx = matched_layer_idx[i] 
        //alert("matched idx  " + idx + " parent_layer name " + name)
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

/* get the parent folder index in the timeline */

function __get_parent_folder(timeline)
{
    var layers = timeline.layers
    var index = -1
    var count = 0
    for (var i=layers.length-1; i>=0; i--)
    {
        if (layers[i].layerType == 'folder' &&
            layers[i].parentLayer ==null)
        {
             index = i
             count++
        }
    }
    if (count == 1)
        return index
    else
        return -1

}

/* create a library folder if it does not exist */
function create_lib(cur_doc, folder_name)
{
    if (cur_doc.library.itemExists(folder_name) == false)
    {
        cur_doc.library.newFolder(folder_name)
    }
}

/* get the timeline from a graphic symbol with a name starting with "Camera" */
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

/* Numeric comparator */
function __sort_num(a,b)
{
    return a-b
}

/* Render function starts here */

function render_layer( preprocess_path, src_path, layer_name, cam_path,
    cam_layer_name, render_dir, file_format)
{
    // create folder for the render path
    FLfile.createFolder('file:///' + render_dir)
    var cur_doc = fl.openDocument( 'file:///' +src_path )

    // load the camera
    var log_path = render_dir + "/actionLog.txt"
    load_layer(cam_path, '', cam_layer_name, cur_doc, log_path)         

    if (file_format != 'swf')
    {
        // preprocessing
        fl.runScript( preprocess_path, 'preprocess_layer', layer_name
                , cam_layer_name , log_path ) 
      
        fl.getDocumentDOM().exportPublishProfile('file:///'  + render_dir + '/' 
            + 'profile.xml')
    }

    // render swf or png
    if (file_format =='swf')
    {
        fl.getDocumentDOM().exportSWF('file:///' + render_dir + '/' 
        + layer_name + '.swf', true)
        fl.getDocumentDOM().exportPNG('file:///' + render_dir + '/' 
        + layer_name + '.png' , true, true)
    }
    else if (file_format =='png')
        fl.getDocumentDOM().exportPNG('file:///' + render_dir + '/' 
        + layer_name + '.' , true, false)
    else
        alert("Unknown render file format [" + file_format  + "]")
    

    // clean up 
    cur_doc.close(false)
    FLfile.remove("file:///" + src_path)
    
}

function write_render_log(render_dir, render_log)
{
    // create a file to signal render finished
    var out_URI = 'file:///' + render_dir + '/' + render_log;
    if (!FLfile.write(out_URI, 'Render finished'))
        alert("writing render log failed")
}




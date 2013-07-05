/*
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
*/

/* preprocess a layer defined in tactic. 
   according to the transformation of the camera layer */

        
function preprocess_layer(layer_name, cam_layer_name, log_path)
{
    //alert(layer_name + " "  + cam_layer_name + " " +  log_path)
    if (cam_layer_name == '' || cam_layer_name == null)
        return

    // Remove the log file first
    FLfile.remove("file:///" + log_path)
 
    var cur_doc = fl.getDocumentDOM()
    var cur_doc_path = cur_doc.path
    
    if (cur_doc_path == null) // should not be null in general
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
    

    // validate and get all the sub-layers in this folder
    var info = __find_layers_idx(cur_doc, layer_name)
    var layers_idx = info[0]
    var cur_timeline = info[1]
    
    if (layers_idx == false)
    {
        __exit("false", log_path)
        return
    }

    var parent_layers = new Array(layers_idx.length)
   
    layers_idx.sort(__sort_num)

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

   
    
    // expand folder
    cur_doc.getTimeline().expandFolder(true, true, layers_idx[0])

    cur_doc.library.addNewItem("graphic", "render_target")

    // find the render target's timeline in the library
    var tmp_timeline = null
    var items = cur_doc.library.items
    for (var k=0; k<items.length; k++)
    {
        if (items[k].name == "render_target")
            tmp_timeline = items[k].timeline
    }

    var layer_count = tmp_timeline.layerCount
    var boundary = new Array(2)
    boundary[0] = (layer_count == 1) ? layer_count - 1 : layer_count
    boundary[1] = layer_count + layers_idx.length - 1 
   
    var max_frame_count = 0
  
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
        var idx = layers_idx[i]
        cur_timeline.setSelectedLayers(idx)
        var cur_frame_count = cur_timeline.layers[idx].frameCount
        if (cur_frame_count > max_frame_count)
            max_frame_count = cur_frame_count
                         
        cur_timeline.cutFrames()
        
      
        var tmp_active_layer = tmp_timeline.layers[layer_count - 1] 

        // rename layer
        tmp_active_layer.name = cur_timeline.layers[idx].name
        
        // parent layers to parent
        var parent_layer =  __get_parent_layer(tmp_timeline, 
            boundary, parent_layers[i])

        if (parent_layer == false)
        {
            __exit("false", log_path)
            return
        }
        tmp_active_layer.parentLayer = parent_layer
            
        tmp_timeline.setSelectedLayers(layer_count-1)
        tmp_timeline.pasteFrames() 	
    }  
    // collapse folder
    cur_doc.getTimeline().expandFolder(false, true, layers_idx[0])
    
    
    // Add render_target to stage
    
    var render_layer_name = 'render'
    cur_timeline.addNewLayer(render_layer_name, 'normal', false)
    var cx = cur_doc.width / 2
    var cy = cur_doc.height / 2
    cur_doc.library.addItemToDocument({x:cx, y:cy}, 'render_target')
    cur_timeline.convertToKeyframes(0, max_frame_count)

    var layers_idx = __get_layers_idx(cur_timeline, cam_layer_name)
    if (layers_idx == false)
        __exit('false', log_path)
    
    //assuming 1 layer for camera 
    var cam_idx = layers_idx[1]

    cur_timeline.setSelectedLayers(cam_idx)

    // bake all the frames within the range of max_frame_count 
    cur_timeline.convertToKeyframes(0, max_frame_count)

    __transform(cur_timeline, render_layer_name, cam_layer_name, log_path)

    __exit("true\n" + layer_name, log_path)

}

/* apply transformation */
function __transform(timeline, render_layer_name, cam_layer_name, log_path)
{
    var doc = fl.getDocumentDOM()
    var layers_idx = __get_layers_idx(timeline, cam_layer_name)
    if (layers_idx == false)
        __exit('false', log_path)
    
    //assuming 1 layer for camera 
    var idx = layers_idx[1]
    var frames = timeline.layers[idx].frames
    timeline.layers[idx].layerType = 'guide'
    
    for (var j=0; j < frames.length; j++)
    {
        var element = frames[j].elements[0]
        // check the keyframe symbols, assuming single element
        // per frame
        if (element.elementType == "instance" /*&& 
            j == frames[j].startFrame*/)
        {
            if (__is_cam(element.libraryItem.name))   
            {
                
                var m = element.matrix
                var m_w = element.width
                var m_h = element.height
                
                //fl.trace("Frame " + (j + 1) + " m_w " + m_w + " m_h " + m_h)
                var render_idx = timeline.findLayerIndex(render_layer_name)[0]    
                var render_frames = timeline.layers[render_idx].frames
               
                var render_element = render_frames[j].elements[0]
                var rm = render_element.matrix
                var rm_w = render_element.width
                var rm_h = render_element.height
                
                var scaleX = doc.width / m_w
                var scaleY = doc.height / m_h
               
                // displacement from origin 
                dx = -1 * rm.tx
                dy = -1 * rm.ty
                
                timeline.setSelectedFrames([render_idx, j, j+1])
                
                // adjust the transformation pivot
                doc.setTransformationPoint({x:dx, y:dy})
                
                // transform
                render_element.width *= scaleX
                render_element.height *= scaleY 
            
                rm = render_element.matrix
                rm.tx -= element.left * scaleX
                rm.ty -= element.top * scaleY 
                render_element.matrix = rm
                
            }            
        }
    }
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

/* get the timeline from a symbol with a name starting with "Camera" */
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
function __find_layers_idx(cur_doc, layer_name)
{
    var timeline = cur_doc.getTimeline()
    var idx = __get_layers_idx(timeline, layer_name) 
    if (!idx)
    {   
        timeline = __get_movie_timeline(cur_doc)
        if (timeline != null)
            idx = __get_layers_idx(timeline, layer_name)
    }
    var info = new Array(2)
    info[0] = idx
    info[1] = timeline
    return info
}

/* get the layer indices for the layer defined by this layer_name */
function __get_layers_idx(timeline, layer_name)
{
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



function __sort_num(a,b)
{
    return a-b
}

/* check if the name starts with 'Camera' */
function __is_cam(name)
{
    if (name.indexOf("Camera") > -1)
        return true
    else
        return false
}
    


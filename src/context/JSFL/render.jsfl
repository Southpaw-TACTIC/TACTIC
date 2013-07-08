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

function include (file, base_dir)
{
    try {
        var contents = FLfile.read("file:///" +  base_dir + "/" + file )
        eval( contents )
    } catch (err) {
        fl.trace(err)
    }
}


common = new Common()


/* convert all the layers of a shot into guide layers */
function convert_to_guide(doc, prefix)
{
    timeline = doc.getTimeline()

    // get all of the layers
    layers = timeline.layers

    for (var i = 0; i < layers.length; i++ )
    {
        var layer = layers[i]
        fl.trace(layer.name)
        var reg = "^" + prefix + ":"

        if ( ! layer.name.match(reg) && layer.name != prefix)
        {
            // set to a guide layer
            layer.layerType = "guide"
        }
    } 
}



function render_layer(prefix, file_format, render_dir, log_path)
{
    // Remove the log file first
    var succeed = FLfile.remove("file:///" + log_path)
    
    // if there is no document then just exit
    var cur_doc = fl.getDocumentDOM()
    if (cur_doc == null)
    {
        common.exit("false", log_path)
        return
    }

    common.introspect(cur_doc, render_dir + '/introspect.xml')

    // if there is no preifx, then render the whole file
    if (prefix != null) {
        convert_to_guide(cur_doc, prefix)
    }
    else {
        prefix = "render"
    }

    // create folder for the render path
    FLfile.createFolder('file:///' + render_dir)

    if (file_format != 'swf')
    {
        // preprocessing
/* handle this later 
        fl.runScript( preprocess_path, 'preprocess_layer', layer_name
                , cam_layer_name , log_path ) 
      
*/
        fl.getDocumentDOM().exportPublishProfile('file:///'  + render_dir + '/' 
            + 'profile.xml')
    }

    // render swf or png
    if (file_format =='swf')
    {
        fl.getDocumentDOM().exportSWF('file:///' + render_dir + '/' 
        + prefix + '.swf', true)
        fl.getDocumentDOM().exportPNG('file:///' + render_dir + '/' 
        + prefix + '.png' , true, true)
    }
    else if (file_format =='png')
        fl.getDocumentDOM().exportPNG('file:///' + render_dir + '/' 
        + prefix + '.' , true, false)
    else
        alert("Unknown render file format [" + file_format  + "]")
   

    // clean up 
    //cur_doc.close(false)


    common.exit("true", log_path)
}



function write_render_log(render_dir, render_log)
{
    // create a file to signal render finished
    var out_URI = 'file:///' + render_dir + '/' + render_log;
    if (!FLfile.write(out_URI, 'Render finished'))
        alert("writing render log failed")
}




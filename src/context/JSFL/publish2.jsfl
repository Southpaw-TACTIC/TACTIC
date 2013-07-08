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

/* simple publish an entire asset */ 
function publish_asset(asset_code, publish_path, log_path)
{
    // Remove the log file first
    var succeed = FLfile.remove("file:///" + log_path)
    
    // if there is no document then just exist
    var cur_doc = fl.getDocumentDOM()
    if (cur_doc == null)
    {
        common.exit("false", log_path)
        return
    }

    // check if this file is untitled
    var cur_doc_URI = null
    if (cur_doc.path == null)
        cur_doc_URI = "file:///C:/sthpw/temp/"+asset_code+".fla" 
    else
        cur_doc_URI = "file:///" + cur_doc.path.replace(/\\/g, "/") 

    // Reject layer named 'Layer 1'
    useless_idx = cur_doc.getTimeline().findLayerIndex("Layer 1")
    if (useless_idx != null)
    {
        common.exit("[Layer 1] is not allowed to be published. Please rename it.", log_path)
        return
    }    

    // build the published file name 
    var new_URI= "file:///" + publish_path + '/' + asset_code + ".fla"


    // create the directory if it does not exist yet
    if (FLfile.exists("file:///" + publish_path ) == false)
        FLfile.createFolder("file:///" + publish_path )

    // if published file already exists, remove it
    FLfile.remove(new_URI)

    // save the document
    fl.trace(cur_doc_URI)
    fl.saveDocument( cur_doc, cur_doc_URI )


    //cur_doc.save(false)

    // pre-publish check
    if (cur_doc_URI == new_URI)
    {
        common.exit("It appears you are working in the publish area of Tactic. Please save your file in other folders (e.g. Sandbox area) before publishing.",
            log_path)
        return
    }

    // introspect
    var introspect_path = publish_path + '/' + asset_code + ".xml"
    common.introspect(cur_doc, introspect_path)


    var copied = FLfile.copy(cur_doc_URI, new_URI)
    if (copied)
    {
        // close current doc to save memory
        cur_doc.close()

        var new_doc = fl.openDocument(new_URI)
        new_doc.publish()
        new_doc.save()
        new_doc.close()

        // reopen current doc
        fl.openDocument(cur_doc_URI)
    }
    else
    {
        var msg = "Copying during publish failed '" + asset_code 
            + "'. Please Try Again."
        common.exit(msg, log_path)
        return
    }

    common.exit("Published [" + asset_code + "]", log_path)
}



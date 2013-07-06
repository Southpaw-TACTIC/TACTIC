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

function include (file)
{
    try {
        var base_dir = "file:///C:/Program Files/Southpaw/Tactic/src/context/JSFL"
        var contents = FLfile.read( base_dir + "/" + file )
        eval( contents )
    } catch (err) {
        fl.trace(err)
    }
}

include( "common.jsfl" );


var common = new Common()
fl.trace( common.pig() )

documents = fl.documents
src_document = documents[1]
dst_document = documents[0]
src_timeline = src_document.getTimeline()
dst_timeline = dst_document.getTimeline()

layer_name = 'pickle'

common.copy_layers( src_timeline, dst_timeline, layer_name)
common.copy_layers( src_timeline, dst_timeline, "cow")
common.match_symbol_folders( src_document.library, dst_document.library)


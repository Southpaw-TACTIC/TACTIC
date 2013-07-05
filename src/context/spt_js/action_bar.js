// ------------------------------------------------------------------------------------------------------
//
//   Copyright (c) 2009, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// ------------------------------------------------------------------------------------------------------


// DEPRECATED


spt.action_bar = {};


spt.action_bar.close_aux = function()
{
    alert("spt.action_bar is deprecated");
    var aux_div = $("ActionBar_Aux");
    var aux_content = $("ActionBar_Aux_Content");
    var aux_title = $("ActionBar_Aux_Title");

    // @@@
    // replace the Action Bar auxiliary content area ...
    spt.behavior.replace_inner_html( aux_content, "" );
    spt.behavior.replace_inner_html( aux_title, "" );

    aux_div.setStyle("display", "none");
}



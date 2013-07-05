// -----------------------------------------------------------------------------
//
//   Copyright (c) 2008, Southpaw Technology Inc., All Rights Reserved
//   
//   PROPRIETARY INFORMATION.  This software is proprietary to Southpaw Technology Inc., and is not to be
//   reproduced, transmitted, or disclosed in any way without written permission.
//   
// 
// -----------------------------------------------------------------------------



// DEPRECATED


spt.sobject_planner = {};


// Side bar panel functionality

//
//
spt.sobject_planner.action = function(evt, bvr)
{
    var search_type = bvr.search_type;
    var action = bvr.action;

    var left_search_keys = spt.dg_table.get_selected_search_keys('table_left');
    var right_search_keys = spt.dg_table.get_selected_search_keys('table_right');



    var server = TacticServerStub.get();

    if (action == "add") {
        var values = {
            'search_type': search_type,
            'left_search_key': left_search_keys,
            'right_search_key': right_search_keys
        }

        var cmd_class = "pyasm.prod.web.SObjectInstanceAdderCbk";
        server.execute_cmd(cmd_class, {}, values);
    }
    else if (action == "retire") {
        alert("Unimplented option");
        return;
    }
    else if (action == "delete") {
        alert("Unimplented option");
        return;
    }

    // for now, refresh the whole panel
    spt.panel.refresh('main_body');
}



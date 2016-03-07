###########################################################
#
# Copyright (c) 2015, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['DynamicUpdateWdg', 'DynamicUpdateCmd']

import tacticenv
from pyasm.common import jsonloads, Common
from pyasm.search import Search
from pyasm.command import Command
import time

from datetime import datetime, timedelta
from dateutil import parser


from tactic.ui.common import BaseRefreshWdg


class DynamicUpdateWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        interval = 5000

        top.add_behavior( {
            'type': 'load',
            'interval': interval,
            'cbjs_action': my.get_onload_js()
        } )

        top.add_behavior( {
            'type': 'unload',
            'cbjs_action': '''
            var top = $(document.body);
            clearInterval( top.spt_update_interval_id );
            top.spt_update_interval_id = 0;
            top.spt_update_src_el = null;
            '''
        } )

        return top


    def get_onload_js(my):
        return r'''

spt.update = {};


spt.update.add = function(el, update) {
    // update is an dict object
    if (!update) {
        var expression = el.getAttribute("expression");
        var handler = el.getAttribute("handler");

        var update = {}
        if (expression) {
            update["expression"] = expression;
        }
        if (handler) {
            update['handler'] = handler;
        }
    }

   
    var el_id = el.getAttribute("id");
    if (!el_id) {
        el_id = "SPT__" + Math.random(1000000);
        el.setAttribute("id", el_id);

    }

    updates = {};
    updates[el_id] = update;
    el.spt_update = updates;
    el.addClass("spt_update");
}



spt.update.display = function(el, column, value) {
    var div = $(document.createElement("div"));
    $(document.body).appendChild(div);
    div.addClass("glyphicon glyphicon-refresh");
    //div.innerHTML = "Update...";

    var pos = el.getPosition();
    var size = el.getSize();

    div.setStyle("position", "absolute");
    div.setStyle("top", pos.y);
    div.setStyle("left", pos.x);
    div.setStyle("z-index", 1000);
    div.setStyle("background", "rgba(128,128,128,0.8");
    div.setStyle("color", "#FFF");
    div.setStyle("padding", "3px 5px");
    //div.setStyle("border", "solid 1px rgba(128,128,128,1)");
    div.setStyle("box-shadow", "0px 0px 5px rgba(128,128,128,0.5)");

    // check for parent spt_cell_edit
    if (column) {
        var cell_edit = el.getParent('.spt_cell_edit');
        cell_edit.setAttribute('spt_input_value', value);
    }
    setTimeout( function() {
        div.destroy();
    }, 500 );

}


var top = $(document.body);

if (top.spt_update_interval_id) {
    clearInterval( top.spt_update_interval_id );
}

top.spt_update_src_el = bvr.src_el;

//setTimeout( function() {
top.spt_update_interval_id = setInterval( function() {

    var top = $(document.body);
    if (spt.body.is_active() == false) {
        return;
    }


    if ( $(top.spt_update_src_el).isVisible() == false) {
        clearInterval( top.spt_update_interval_id );
        top.spt_update_interval_id = 0;
        top.spt_update_src_el = null;
        return;
    }


    var server = TacticServerStub.get();

    // find out if there are any changes in the last interval
    //var expr = "@COUNT(sthpw/change_timestamp['timestamp','>','$PREV_HOUR'])";
    //count = server.eval(expr);


    cmd = "tactic.ui.app.DynamicUpdateCmd"
    

    var update = top.spt_update;
    if (!update) {
        update = {};
    }

    var oldest_timestamp = top.spt_update_timestamp;

    // get all of the updates below as well
    var update_els = top.getElements(".spt_update");
    var pass_els = [];

    out_loop:
    for (var i = 0; i < update_els.length; i++) {
        var update_el = update_els[i];
        if (! update_el.isVisible()) {
            continue;
        }


        sub_update = update_el.spt_update;
        
        if (!sub_update) {
            continue;
        }

        var last_check = update_el.spt_last_check;
        // initial time set-up
        if (last_check && last_check < oldest_timestamp) {
            oldest_timestamp = last_check;
        }

        // merge with update
        in_loop:
        for (var key in sub_update) {
            
            // on elements that have intervals, set the counter
            var update_interval = sub_update[key].interval;
            if (update_interval) {
                var counter = update_el.spt_update_count;
                if (!counter) {
                    counter = 0;
                }
                counter += 1;
                if (counter < update_interval) {
                    update_el.spt_update_count = counter;
                    continue out_loop;

                }

                update_el.spt_update_count = 0;
            }


            update[key] = sub_update[key];
        }
        pass_els.push(update_el);
    }


    if (Object.keys(update).length > 0) {

        var on_complete = function(ret_val) {
            var timestamp = ret_val.info ? ret_val.info.timestamp : null;
            if (!timestamp) 
                return;
            
            top.spt_update_timestamp = timestamp;

            for (var i = 0; i < pass_els.length; i++) {
                pass_els[i].spt_last_check = timestamp;
            }
            var server_data = ret_val.info.updates;

            for (var el_id in server_data) {

                var el = $(el_id);
                if (!el) {
                    continue;
                }
                var value = server_data[el_id];

                var node_name = el.nodeName;

                var x = update[el_id];
                var preaction = x.cbjs_preaction;
                var action = x.cbjs_action;
                var postaction = x.cbjs_postaction;
                var column = x.column;

                var preaction_cbk = null;
                var action_cbk = null;
                var postaction_cbk = null;

                var cbk_bvr = {
                    src_el: el,
                    value: value
                }

                if (preaction) {
                    preaction_cbk = function(bvr) {
                        eval(preaction);
                    }
                    preaction_cbk(cbk_bvr);
                }

               
                if (action) {
                    action_cbk = function(bvr) {
                        eval(action);
                    }
                    action_cbk(cbk_bvr);
                }

                else if (value == "__REFRESH__") {
                    spt.panel.refresh(el)
                    spt.update.display(el);
                }
                else if ( node_name == "SELECT" || node_name == "INPUT") {
                    var old_value = el.value;
                    if (old_value != value) {
                        el.value = value;

                        spt.update.display(el, column, value);
                    }
                }
                else if (typeof(value) == "boolean") {
                    if (value) {
                        value = 'true';
                    }
                    else {
                        value = 'false';
                    }

                    var old_value = el.innerHTML;
                    if (old_value != value) {
                        el.innerHTML = value;

                        spt.update.display(el, column, value);
                    }
                }
                else {
                    var old_value = el.innerHTML;
                    if (old_value != value) {
                        el.innerHTML = value;

                        spt.update.display(el, column, value);
                    }
                }


                if (postaction) {
                    postaction_cbk = function(bvr) {
                        eval(postaction);
                    }
                    postaction_cbk(cbk_bvr);
                }


            }

        }


        var kwargs = {
            updates: JSON.stringify(update),
            last_timestamp: oldest_timestamp,
            _debug: false,
        };


        server.execute_cmd(cmd, kwargs, {}, {on_complete: on_complete} );

    }


}, bvr.interval);

        '''





class DynamicUpdateCmd(Command):


    def execute(my):

        start = time.time()

        from pyasm.common import SPTDate
        timestamp = SPTDate.now()
        timestamp = SPTDate.add_gmt_timezone(timestamp)
        timestamp = SPTDate.convert_to_local(timestamp)
        format = '%Y-%m-%d %H:%M:%S'
        timestamp = timestamp.strftime(format)
        
        updates = my.kwargs.get("updates")
        if isinstance(updates, basestring):
            updates = jsonloads(updates)
        last_timestamp = my.kwargs.get("last_timestamp")
        #assert last_timestamp
        if not last_timestamp:
            my.info = {
                "updates": {},
                "timestamp": timestamp
            }
            return

        last_timestamp = parser.parse(last_timestamp)
        last_timestamp = SPTDate.add_gmt_timezone(last_timestamp)
        
        # give 2 seconds of extra room 
        last_timestamp = last_timestamp - timedelta(seconds=2)


        # get out all of the search_keys
        client_keys = set()
        client_stypes = set()
        for id, values_list in updates.items():
            if isinstance(values_list, dict):
                values_list = [values_list]

            for values in values_list:
                handler = values.get("handler")
                if handler:
                    handler = Common.create_from_class_path(handler)
                    # it could be a list
                    search_key = handler.get_search_key()
                else:
                    search_key = values.get("search_key")

                if search_key:
                    if isinstance(search_key, list):
                        search_key_set = set(search_key)
                    else:
                        search_key_set = set()
                        search_key_set.add(search_key)
                    client_keys.update(search_key_set)

                stype = values.get("search_type")
                if stype:
                    client_stypes.add(stype)

        # find all of the search that have changed
        changed_keys = set()
        changed_types = set()
        for check_type in ['sthpw/change_timestamp', 'sthpw/sobject_log']:
            search = Search(check_type)
            search.add_filter("timestamp", last_timestamp, op=">")
            search.add_filters("search_type", ["sthpw/sobject_log", "sthpw/status_log"], op="not in")
            changed_sobjects = search.get_sobjects()
            for sobject in changed_sobjects:
                search_type = sobject.get_value("search_type")
                search_code = sobject.get_value("search_code")
                if search_type.startswith("sthpw/"):
                    search_key = "%s?code=%s" % (search_type, search_code)
                else:
                    search_key = "%s&code=%s" % (search_type, search_code)
                changed_keys.add(u'%s'%search_key)
                changed_types.add(search_type)

        intersect_keys = client_keys.intersection(changed_keys)
        intersect_types = client_stypes.intersection(changed_types)

        from pyasm.web import HtmlElement

        results = {}
        for id, values_list in updates.items():
            if isinstance(values_list, dict):
                values_list = [values_list]

            for values in values_list:

                handler = values.get("handler")
                if handler:
                    handler = Common.create_from_class_path(handler)
                    # handler can return a list of search_keys
                    search_key = handler.get_search_key()
                else:
                    search_key = values.get("search_key")
                
                stype = values.get("search_type")
                
                search_key_set = set()
                if search_key:
                    if isinstance(search_key, list):
                        search_key_set = set(search_key)
                    else:
                        search_key_set = set()
                        search_key_set.add(search_key)

                # filter for search_type first if it exists
                # check if any search_key is contained in intersect_keys, skip if not 
                if stype and stype in changed_types:
                    if len(search_key_set) > 0:
                        if len(intersect_keys  - search_key_set) == len(intersect_keys):
                            continue
                elif len(intersect_keys  - search_key_set) == len(intersect_keys):
                    continue
                
                # evaluate any compare expressions
                compare = values.get("compare")
                if compare:
                    search_key = values.get("search_key")
                    if search_key:
                        sobject = Search.get_by_search_key(search_key)
                    else:
                        sobject = None
                    cmp_result = Search.eval(compare, sobject, single=True)
                    if cmp_result == True:
                        continue
                    
                    # some value to display
                    value = "Loading ..."
                else:
                    value = HtmlElement.eval_update(values)
              
                if value == None:
                    continue
                
                results[id] = value

        my.info = {
            "updates": results,
            "timestamp": timestamp
        }



        #print "Dyn Cmd duration", time.time()  - start
        return results



def main():
    update = {
        "X123": {
            "search_key": "vfx/asset?project=vfx&code=chr001",
            "column": "name"
        },
        "X124": {
            "search_key": "sthpw/login?code=admin",
            "expression": "@GET(.first_name) + ' ' + @GET(.last_name)"
        }
    }
    cmd = DynamicUpdateCmd(update=update)
    Command.execute_cmd(cmd)

def test_time():

    from pyasm.search import SearchType
    sobj = SearchType.create('sthpw/note')
    sobj.set_value('process','TEST')
    sobj.set_value('note','123')
    sobj.commit()


    sobj.set_value('note', 'new note')
    sobj.commit()

    # check change_timestamp
    change_t = Search.eval("@SOBJECT(sthpw/change_timestamp['search_type','sthpw/note']['search_code','%s'])"%sobj.get_code(), single=True)
    if change_t:
        change_t_timestamp = change_t.get('timestamp')
        change_t_timestamp = parser.parse(change_t_timestamp)

        from pyasm.common import SPTDate
        now = SPTDate.now()

        diff = now - change_t_timestamp
        # should be roughly the same minute, not hours apart
        print "Change timestamp diff is ", diff.seconds 

if __name__ == '__main__':
    from pyasm.security import Batch
    Batch(site="vfx_test", project_code="vfx")

    main()
    #test_time()




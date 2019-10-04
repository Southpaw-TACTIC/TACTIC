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


__all__ = ['DynamicUpdateWdg', 'DynamicUpdateCmd','DynamicUpdateHandler']

import tacticenv
from pyasm.common import jsonloads, Common
from pyasm.security import Batch
from pyasm.common import Environment
from pyasm.search import Search, Transaction
from pyasm.command import Command
from pyasm.biz import Project, Task, ExpressionParser

import time

from datetime import datetime, timedelta
from dateutil import parser

from tactic.ui.common import BaseRefreshWdg


class DynamicUpdateWdg(BaseRefreshWdg):

    def get_display(self):

        top = self.top

        interval = 5000

        top.add_behavior( {
            'type': 'load',
            'interval': interval,
            'cbjs_action': self.get_onload_js()
        } )

        top.add_behavior( {
            'type': 'unload',
            'cbjs_action': '''
            var top = document.id(document.body);
            clearInterval( top.spt_update_interval_id );
            top.spt_update_interval_id = 0;
            top.spt_update_src_el = null;
            '''
        } )

        return top


    def get_onload_js(self):
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
    var div = document.id(document.createElement("div"));
    document.id(document.body).appendChild(div);
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


var top = document.id(document.body);

if (top.spt_update_interval_id) {
    clearInterval( top.spt_update_interval_id );
}

top.spt_update_src_el = bvr.src_el;

//setTimeout( function() {
top.spt_update_interval_id = setInterval( function() {

    var top = document.id(document.body);
    if (spt.body.is_active() == false) {
        return;
    }


    if ( document.id(top.spt_update_src_el).isVisible() == false) {
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
        if (!update_el.isVisible() || update_el.hasClass("spt_update_lock")) {
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

                var el = document.id(el_id);
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
    
    '''Determine client specified updates based on server change_timestamp
        and sobject_log tables.

        Parameters
            last_timestamp - timestamp of the last update check (optional) 
            updates - dictionary of update dictionaries by HTML el id

        Return 
            timestamp - the timestamp the command was last executed
            updates - a dictionary of HTML el ids and update values.
                The update value is determined by HtmlElement.eval_update
                based on the client specified update dictionary for that el id. 
                When the update dictionary does not match a server event, 
                the command will take early exit and not return any value.
        
        The following is a list of example client update dictionaries for single DOM elements,
        followed by the the general event required for the command to return a result for el id, 
        and the returned value.

        update = {'expression': "@COUNT(sthpw/task['status', 'NEQ', 'complete'])"}
        expression is evaluated each interval and the inner HTML of task quantity indicator
            is replaced with returned update value.
        
        update = {'search_key': 'sthpw/task?code=TASK00001709', 'column': 'status'}
        When there a change to the specified task, it's status is returned.

        update = {'search_key': 'vfx/shot?project=vfx&code=13', 'compare': '@COUNT(vfx/shot.sthpw/file) < 1',
            cbjs_action: notification_script}
        If there is a change to specified shot, compare is evaluated, and if shot has at least one associated 
            file, then notification_script is executed.
        
        update = {'search_type': 'vfx/asset', 'value': True, cbjs_action: script}
        script is executed when there is a change in vfx/asset sType. Value True is returned.
       
        update = {'expr_key': 'vfx/shot?project=vfx&code=13', 
            'compare': '@COUNT(sthpw/task['status', 'NEQ', 'complete']) < 1', cbjs_action: script} 
        When shot specified has one or more incomplete tasks, the script is executed. 
        
        For each el id specified in the return dictionary, the following occurs based on the el update dictionary:
        - js preaction is executed if specified
        - js cbjs_action is executed if specified, if not:
            Otherwise, if the value returned is "__REFRESH__", the el is refreshed.
            Otherwise, if the el is a select or input field, the input value is updated.
            Otherwise, if the value returned is boolean, then then true or false is placed in the el.
            Otherwise, the inner HTML of the el is replaced with the returned value.
        - js postaction will execute if specified
        
        '''

    def execute(self):
  
        start = time.time()

        from pyasm.common import SPTDate
        timestamp = SPTDate.now()
        timestamp = SPTDate.add_gmt_timezone(timestamp)
        timestamp = SPTDate.convert_to_local(timestamp)
        format = '%Y-%m-%d %H:%M:%S'
        timestamp = timestamp.strftime(format)
        
        updates = self.kwargs.get("updates")

        if isinstance(updates, basestring):
            updates = jsonloads(updates)
        last_timestamp = self.kwargs.get("last_timestamp")
        #assert last_timestamp
        if not last_timestamp:
            self.info = {
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
                    handler = Common.create_from_class_path(handler, args=[], kwargs={'update':values})
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
        
        from pyasm.web import HtmlElement

        results = {}
        for id, values_list in updates.items():
            if isinstance(values_list, dict):
                values_list = [values_list]
            
            for values in values_list:

                handler = values.get("handler")
                if handler:
                    handler = Common.create_from_class_path(handler, kwargs={'update': values})
                    # handler can return a list of search_keys
                    search_key = handler.get_search_key()
                else:
                    search_key = values.get("search_key")
               
                stype = values.get("search_type")
                if stype and stype.find("?project=") == -1:
                    from pyasm.search import SearchType
                    stype = SearchType.build_search_type(stype)
                
                search_key_set = set()
                if search_key:
                    if isinstance(search_key, list):
                        search_key_set = set(search_key)
                    else:
                        search_key_set = set()
                        search_key_set.add(search_key)
                if stype and stype not in changed_types:
                    continue  
                if stype and stype in changed_types:
                    if search_key_set and len(intersect_keys  - search_key_set) == len(intersect_keys):
                        continue
                elif search_key_set and len(intersect_keys  - search_key_set) == len(intersect_keys):
                    continue
               
                feed_expr = values.get("feed_expr")
                if feed_expr:
                    feed_search = Search.eval(feed_expr)
                    feed_search.add_filter("timestamp", last_timestamp, op=">")
                    sobjects = feed_search.get_sobjects()
                    if not sobjects:
                        continue
                    values['feed_sobjects'] = sobjects
                    
                # evaluate any compare expressions
                compare = values.get("compare")
                if compare:
                    search_key = values.get("search_key")
                    expr_key = values.get("expr_key")
                    if search_key:
                        sobject = Search.get_by_search_key(search_key)
                    elif expr_key:
                        sobject = Search.get_by_search_key(expr_key)
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

        self.info = {
            "updates": results,
            "timestamp": timestamp
        }



        #print("Dyn Cmd duration", time.time()  - start)



import unittest

class UpdateTest(unittest.TestCase):

    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
   
        self.updates = None
        self.last_timestamp = None

        self.search_key = None
        self.task_sk = None

    def test_all(self):
        '''entry point function'''

        Batch(site="demo")

        # Allows for triggers
        from pyasm.web import WebInit
        WebInit().execute()

        # Set up test environment
        from pyasm.unittest import Sample3dEnvironment
        test_env = Sample3dEnvironment(project_code='sample3d')
        Project.set_project("sample3d")
        test_env.create()
        
        # Commit environment setup transaction 
        #transaction = Transaction.get()
        #transaction.commit()
   
        # Get updates - creates shots and tasks
        self.updates = self._get_updates()
        
        try:
            self._test_no_updates()
            self._test_insert()
            self._test_status_change()
            self._test_compare()
            self._test_empty_update()
            #self._test_time()
        finally:
            test_env.delete()
   
    def _get_updates(self):
        '''Create sObject and tasks that we will test to receive updates on.
        Current transaction is commited in _test_insert.'''
       
        Transaction.get(create=True) 
 
        from pyasm.search import SearchType
        sobj = SearchType.create("prod/asset")
        sobj.set_defaults()
        sobj.commit()
        search_key = sobj.get_search_key()
        self.search_key = search_key
        search_type = sobj.get_search_type()
        search_code = sobj.get_value('code')

        tasks = Task.add_initial_tasks(sobj, pipeline_code='__default__')
        first_task = tasks[0]
        task_sk = first_task.get_search_key()
        self.task_sk = task_sk

        script = '''console.log('hello world.')'''
        
        updates = {}
       
        # Expression counts the number of incomplete tasks for sobject 
        expr = '''@COUNT(@SOBJECT(prod/asset['code', '%s'].sthpw/task['status', 'NEQ', 'complete']))''' % search_code
        # Compare is True iff all tasks are all complete.
        compare = '''@COUNT(@SOBJECT(sthpw/task['status', 'NEQ', 'complete'])) < 1'''

        # Test expression by itself
        updates["001"] = {'expression': expr}
        
        # Test search_key and column
        updates["002"] = {'search_key': task_sk, 'column': 'status'}
        
        # Test compare and search_key
        updates["003"] = {'search_key': search_key, 'compare': compare, 'cbjs_action': script}
        
        # Test listen for search_type 
        updates["004"] = {'search_type': search_type, 'value': True, 'cbjs_action': script}
      
        # Test expr_key and compare 
        updates["005"] = {'expr_key': search_key, 'compare': compare}
    
        # Test search_key and expression
        expression = '''@COUNT(@SOBJECT(sthpw/task['status', 'NEQ', 'complete']))'''
        updates["006"] = {'search_key': search_key, 'expression': expression}

        return updates

    def _test_no_updates(self): 
        '''Test no updates and set the initial timestamp'''
        transaction = Transaction.get(create=True)
        transaction.commit()
        
        from pyasm.command import Command
        cmd = DynamicUpdateCmd(last_timestamp=self.last_timestamp, updates=self.updates)
        Command.execute_cmd(cmd)
        self.last_timestamp = cmd.get_info("timestamp")
        updates = cmd.get_info("updates") 

        self.assertEquals(updates, {})

    def _test_insert(self):
        '''Test insertion of tasks and shots.'''

        # Commit creation of asset and tasks
        transaction = Transaction.get()
        transaction.commit()
        time.sleep(3)
        
        # Test initial insert of shot and tasks
        cmd = DynamicUpdateCmd(last_timestamp=self.last_timestamp, updates=self.updates)
        Command.execute_cmd(cmd)
        self.last_timestamp = cmd.get_info("timestamp")
        updates = cmd.get_info("updates")  
       
        sobject = Search.get_by_search_key(self.search_key)
        num_tasks = Search.eval("@COUNT(@SOBJECT(sthpw/task))", sobject)
        self.assertEquals(updates["001"], num_tasks)
        
        task = Search.get_by_search_key(self.task_sk)
        status = task.get_value("status")
        self.assertEquals(updates["002"], status)
        
        self.assertEquals(updates["003"], "Loading ...")
        self.assertEquals(updates["004"], True)
        self.assertEquals(updates["005"], "Loading ...")
        self.assertEquals(updates["006"], num_tasks)
  
  
    def _test_status_change(self):
        '''Test a change to a single task.'''
        
        # Clear expression cache
        ExpressionParser.clear_cache()
        
        transaction = Transaction.get(create=True)
        task = Search.get_by_search_key(self.task_sk) 
        new_status = 'pending'
        task.set_value("status", new_status)
        task.commit()
        transaction.commit()
        
        time.sleep(3)

        cmd = DynamicUpdateCmd(last_timestamp=self.last_timestamp, updates=self.updates)
        Command.execute_cmd(cmd)
        self.last_timestamp = cmd.get_info("timestamp")
        updates = cmd.get_info("updates")
        
        sobject = Search.get_by_search_key(self.search_key)
        num_tasks = Search.eval("@COUNT(@SOBJECT(sthpw/task))", sobject)
        self.assertEquals(updates["001"], num_tasks)
        self.assertEquals(updates["002"], new_status)
        self.assertEquals(updates["003"], "Loading ...")
        self.assertEquals(updates["004"], True)
        self.assertEquals(updates["005"], "Loading ...")
        self.assertEquals(updates["006"], num_tasks)

    def _test_compare(self):
        '''Test early exiting of compare statements.'''
 
        # Clear expression cache
        ExpressionParser.clear_cache()

        transaction = Transaction.get(create=True)

        sobject = Search.get_by_search_key(self.search_key)
        tasks = Search.eval("@SOBJECT(sthpw/task)", sobject)
        new_status = 'complete'
        for task in tasks:
            task.set_value("status", new_status)
            task.commit()

        transaction.commit()
        
        time.sleep(3)

        cmd = DynamicUpdateCmd(last_timestamp=self.last_timestamp, updates=self.updates)
        Command.execute_cmd(cmd)
        self.last_timestamp = cmd.get_info("timestamp")
        updates = cmd.get_info("updates")
 
        self.assertEquals(updates["001"], 0)
        self.assertEquals(updates["002"], new_status)
        self.assertEquals(updates.get("003"), None)
        self.assertEquals(updates["004"], True)
        self.assertEquals(updates.get("005"), None)
        self.assertEquals(updates["006"], 0)


    def _test_empty_update(self):
        cmd = DynamicUpdateCmd(last_timestamp=self.last_timestamp, updates=self.updates)
        Command.execute_cmd(cmd)
        self.last_timestamp = cmd.get_info("timestamp")
        updates = cmd.get_info("updates")

        self.assertEquals(updates["001"], 0)
        self.assertEquals(updates.get("002"), None)
        self.assertEquals(updates.get("003"), None)
        self.assertEquals(updates.get("004"), None)
        self.assertEquals(updates.get("005"), None)
        self.assertEquals(updates.get("006"), None)


    def _test_time():

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
            print("Change timestamp diff is ", diff.seconds )


class DynamicUpdateHandler(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_search_key(self):
        pass

    def get_value(self):
        pass

if __name__ == '__main__':
    unittest.main()



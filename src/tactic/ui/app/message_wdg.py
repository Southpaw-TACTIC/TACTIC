###########################################################
#
# Copyright (c) 2005-2013, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

from pyasm.common import jsonloads

from pyasm.web import DivWdg, SpanWdg

from tactic.ui.common import BaseRefreshWdg
from pyasm.search import Search
from pyasm.web import Table
from pyasm.widget import TextWdg, IconWdg, ThumbWdg, TextWdg, TextAreaWdg
from tactic.ui.widget import ActionButtonWdg, IconButtonWdg


__all__ = ['ChatWdg', 'SubscriptionWdg', 'MessageWdg']



class ChatWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top;
        my.set_as_panel(top)
        top.add_class("spt_chat_top")

        top.add_behavior( {
            'type': 'load',
            'cbjs_action': MessageWdg.get_onload_js()
        } )


        top.add( my.get_add_chat_wdg() )

        search = Search("sthpw/subscription")
        search.add_filter("category", "chat")
        search.add_user_filter()
        chats = search.get_sobjects()
        keys = [x.get_value("message_code") for x in chats]

        table = Table()
        top.add(table)
        table.add_row()
        for key in keys:
            table.add_cell( my.get_chat_wdg(key, interval=True) )

        return top


    def get_add_chat_wdg(my):

        div = DivWdg()
        div.add_border()
        div.add_style("padding: 20px")
        div.add_class("spt_add_chat_top")

        div.add("User: ")
        text = TextWdg("user")
        div.add(text)
        text.add_class("spt_add_chat_user")

        add_button = ActionButtonWdg(title="Start Chat")
        div.add(add_button)
        add_button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_add_chat_top");
            var el = top.getElement(".spt_add_chat_user");
            var user = el.value;
            if (!user) {
                alert("Specify a valid user to chat with");
                return;
            }


            // new chat
            var server = TacticServerStub.get();
            var category = "chat";
            var key = spt.message.generate_key();
            var login = "admin";
            server.insert("sthpw/subscription", {'message_code':key, login: login, category: category} );
            server.insert("sthpw/subscription", {'message_code':key, login: user, category: category} );

            var message = "";
            var category = "chat";
            server.log_message(key, message, {category:category, status:"start"});

            '''
        } )

        return div



    def get_chat_wdg(my, key, interval=False):

        div = DivWdg()
        div.add_class("spt_chat_left_top")
        div.add_style("margin: 20px")

        title_wdg = DivWdg()
        div.add(title_wdg)
        title_wdg.add(key)
        title_wdg.add_color("background", "background3")
        title_wdg.add_style("padding: 5px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_border()

        history_div = DivWdg()
        div.add(history_div)
        history_div.add_class("spt_chat_history")
        history_div.add_style("width: 400px")
        history_div.add_style("height: 200px")
        history_div.add_style("padding: 5px")
        history_div.add_border()
        history_div.add_style("overflow-y: auto")
        #history_div.add_style("font-size: 0.9em")

        if interval:

            div.add_behavior( {
            'type': 'load',
            'key': key,
            'cbjs_action': r'''
            var text_el = bvr.src_el.getElement(".spt_chat_text");
            var history_el = bvr.src_el.getElement(".spt_chat_history");
            var callback = function(message) {
                //history_el.setStyle("background", "red");
                var login = message.login;
                var timestamp = message.timestamp;
                if (timestamp) {
                    var parts = timestamp.split(" ");
                    parts = parts[1].split(".");
                    timestamp = parts[0];
                }
                else {
                    timestamp = "";
                }

                var tmp = message.message || "";

                var msg = "";
                msg += "<table style='margin-top: 5px; font-size: 0.9em; width: 100%'><tr><td>";
                msg += "<b>"+login+"</b><br/>";
                msg += tmp.replace(/\n/g,'<br/>');
                msg += "</td><td style='width: 75px; vertical-align: top'>";
                msg += "<br/>"+ timestamp;
                msg += "</td></tr></table>";

                if (msg == history_el.last_msg) {
                    return;
                }
                history_el.innerHTML =  history_el.innerHTML + msg;

                // remember last message
                history_el.last_msg = msg;
            }
            spt.message.set_interval(bvr.key, callback, 3000);
            '''
            } )

        text = TextAreaWdg("chat")
        div.add(text)
        text.add_class("spt_chat_text")
        text.add_style("width: 412px")
        text.add_style("padding: 5px")
        text.add_style("margin-top: -1px")
        
        text.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        bvr.src_el.addEvent("keydown", function(e) {

        var keys = ['tab','keys(control+enter)', 'enter'];
        var key = e.key;
        var input = bvr.src_el
        if (keys.indexOf(key) > -1) e.stop();

        if (key == 'tab') {
        }
        else if (key == 'enter') {
            if (e.control == false) {
                pass;
            }
            else {
                 // TODO: check if it's multi-line first 
                 //... use ctrl-ENTER for new-line, regular ENTER (RETURN) accepts value
                //var tvals = parse_selected_text(input);
                //input.value = tvals[0] + "\\n" + tvals[1];
                //spt.set_cursor_position( input, tvals[0].length + 1 );
            }
        }
        } )
        '''
        } )



        button = ActionButtonWdg(title="Send")
        div.add(button)
        button.add_behavior( {
        'type': 'click_up',
        'key': key,
        'cbjs_action': '''

        var top = bvr.src_el.getParent(".spt_chat_left_top");
        var text_el = top.getElement(".spt_chat_text");
        var message = text_el.value;
        if (!message) {
            return;
        }

        var history_el = top.getElement(".spt_chat_history");

        var category = "chat";
        var server = TacticServerStub.get();

        var key = bvr.key;
        var last_message = server.log_message(key, message, {category:category, status:"in_progress"});

        text_el.value = "";

            '''
        } )


        return div






class SubscriptionWdg(BaseRefreshWdg):
    def get_display(my):

        div = DivWdg()

        sobject_subscription = SObjectSubscriptionWdg()
        div.add(sobject_subscription)

        return div




class SObjectSubscriptionWdg(BaseRefreshWdg):


    def get_subscriptions(my, category):

        search = Search("sthpw/subscription")
        search.add_user_filter()
        if category:
            search.add_filter("category", category)


        #search.add_join("sthpw/message")

        search.add_order_by("message.timestamp", direction="desc")

        subscriptions = search.get_sobjects()

        return subscriptions


    def get_display(my):
        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_subscription_top")

        interval = 10 * 1000

        inner = DivWdg()
        top.add(inner)
        inner.add_behavior( {
            'type': 'load',
            'interval': interval,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_subscription_top");
            timeout_id = setTimeout( function() {
                spt.panel.refresh(top);
            }, bvr.interval );
            bvr.src_el.timeout_id = timeout_id;
            '''
        } )


        inner.add_behavior( {
            'type': 'unload',
            'cbjs_action': '''
            if (bvr.src_el.timeout_id)
                clearTimeout(bvr.src_el.timeout_id);
            '''
        } )

        #mode = "all"
        mode = "new"

        categories = ['chat','sobject','script']
        categories = [None]

        has_entries = False
        for category in categories:
            category_wdg = my.get_category_wdg(category, mode)
            if category_wdg:
                inner.add(category_wdg)
                has_entries = True

        if not has_entries:
            no_entries = DivWdg()
            inner.add(no_entries)
            no_entries.add_style("padding: 50px")
            no_entries.add_style("width: 400px")
            no_entries.add_style("height: 100px")
            no_entries.add_style("margin: 100px auto")
            no_entries.add_style("text-align: center")
            no_entries.add_border()
            no_entries.add_color("background", "background3")
            no_entries.add("No messages")

        if my.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top


    def get_preview_wdg(my, subscription):

        category = subscription.get_value("category")

        size = 60

        if category == 'sobject':
            message_code = subscription.get_value("message_code")
            sobject = Search.get_by_search_key(message_code)
            thumb = DivWdg()

            thumb_wdg = ThumbWdg()
            thumb.add(thumb_wdg)
            thumb_wdg.set_sobject(sobject)
            thumb_wdg.set_icon_size(size)

            search_code = sobject.get_code()

            thumb.add_behavior( {
                'type': 'click_up',
                'search_key': message_code,
                'search_code': search_code,
                'cbjs_action': '''
                var class_name = 'tactic.ui.tools.SObjectDetailWdg';
                var kwargs = {
                    search_key: bvr.search_key
                }
                spt.tab.set_main_body_tab();
                var title = "Detail ["+bvr.search_code+"]";
                spt.app_busy.show("Loading " + bvr.search_code);
                spt.tab.add_new(bvr.search_code, title, class_name, kwargs);
                spt.app_busy.hide();
                '''
                } )



        else:
            thumb = DivWdg()
            thumb.add_style("width: %s" % size)
            thumb.add_style("height: %s" % (size*3/4))
            thumb.add_border()
            thumb.add_color("background", "background")
            thumb.add("<br/>")
            thumb.add(category)
            thumb.add_style('text-align: center')

        thumb.add_style("margin: 3px")
        return thumb


    def get_category_wdg(my, category, mode="new"):

        subscriptions = my.get_subscriptions(category)
        if not subscriptions:
            return

        div = DivWdg()
        div.add_style("width: 100%")

        title_div = DivWdg()
        div.add(title_div)
        title_div.add_style("padding: 10px")
        title_div.add_border()
        title_div.add_color("background", "background3")
        title = category or "Subscriptions"
        title_div.add("%s " % title)
        

        summary_div = SpanWdg()
        title_div.add(summary_div)
        summary_div.add_style("font-size: 0.8em")
        summary_div.add_style("opacity: 0.5")


        search_keys = [x.get_search_key() for x in subscriptions]
        button = ActionButtonWdg(title="Clear All")
        div.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'search_keys': search_keys,
            'cbjs_action': '''
            var server = TacticServerStub.get();
            for (var i = 0; i < bvr.search_keys.length; i++) {
                var search_key = bvr.search_keys[i];
                server.update(search_key, {'last_cleared':'NOW'});
            }
            '''
        } )



        # types of subscriptions

        table = Table()
        table.add_style("width: 100%")
        table.add_border()
        table.add_color("background", "background3")


        div.add(table)
        ss = []
        for subscription in subscriptions:
            table.add_row()
            td = table.add_cell()

            message_code = subscription.get_value("message_code")

            search = Search("sthpw/message")
            search.add_filter("code", message_code)
            message = search.get_sobject()

            # show the thumb
            if not message:
                if mode == "all":
                    td = table.add_cell(my.get_preview_wdg(subscription))

                    td = table.add_cell()
                    td.add("No Messages")
                continue

            # FIXME: this should be done in the query
            if mode != "all":
                message_timestamp = message.get_value("timestamp")
                subscription_cleared = subscription.get_value("last_cleared")
                if subscription_cleared > message_timestamp:
                    continue


            size = 60

            category = message.get_value("category")
            td = table.add_cell()
            td.add( my.get_preview_wdg(subscription) )


            #td = table.add_cell(message_code)

            message_value = message.get_value("message")
            if message_value.startswith("{") and message_value.endswith("}"):
                message_value = jsonloads(message_value)
                update_data = message_value.get("update_data")

                if category == "sobject":
                    search_type = message_value.get("search_type")
                    if search_type == "sthpw/note":
                        description = "<b>Note Added:</b><br/>%s" % update_data.get("note")
                    elif search_type == "sthpw/task":
                        description = "<b>Task modified:</b><br/>%s" % update_data.get("process")
                    elif search_type == "sthpw/snapshot":
                        sobject = message_value.get("sobject")
                        description = "<b>Files Checked In:</b><br/>%s" % sobject.get("process")
                    else:
                        description = "<b>Data modified:</b><br/>%s" % update_data

                else:
                    description = message_value.get("description")


            else:
                description = message_value

            td = table.add_cell()
            td.add(description)
            td = table.add_cell()
            #td.add(message.get_value("status"))
            #td = table.add_cell()
            timestamp = message.get_datetime_value("timestamp")
            if timestamp:
                timestamp_str = timestamp.strftime("%b %d, %Y - %H:%M")
            else:
                timestamp_str = ""
            td.add(timestamp_str)

            #td = table.add_cell()
            #td.add(subscription.get_value("last_cleared"))

            td = table.add_cell()
            icon = IconButtonWdg(title="Remove Subscription", icon=IconWdg.DELETE)
            td.add(icon)



            ss.append(subscription)

        num_sobjects = len(ss)
        if not num_sobjects:
            return None
        summary_div.add("(%s changes)" % num_sobjects)

        #from tactic.ui.panel import FastTableLayoutWdg
        #table = FastTableLayoutWdg(search_type="sthpw/subscription",show_shelf=False)
        #div.add(table)
        #table.set_sobjects(ss)





        return div





class MessageWdg(BaseRefreshWdg):

    def get_display(my):

        div = DivWdg()
        div.add_class("spt_message_top")
        div. add("<h1>Message</h1>")

        outer = DivWdg()
        div.add(outer)
        outer.add_style("width: 250px")
        outer.add_border()

        progress = DivWdg()
        outer.add(progress)
        progress.add_class("spt_message_progress")
        progress.add_style("background", "#AAD")
        progress.add_style("width: 0%")
        progress.add_style("height: 20px")


        div.add("<img src='/context/icons/common/indicator_snake.gif'/>")
        text = TextWdg("complete")
        div.add(text)
        text.add_class("spt_message_text");





        div.add_behavior( {
            'type': 'load',
            'cbjs_action': my.get_onload_js()
        } )

        div.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            var key = spt.message.generate_key();

            // create a subscription
            var server = TacticServerStub.get();
            login = spt.Environment.get().get_user();
            server.insert("sthpw/subscription", {'message_code':key, login: login, category: "script"} );

            var server = TacticServerStub.get();
            var x = function() {};
            server.execute_python_script("message/action", {key:key}, {on_complete: x});

            var el = bvr.src_el.getElement(".spt_message_text");
            var progress_el = bvr.src_el.getElement(".spt_message_progress");

            var callback = function(message) {
                console.log(message);
                if (message.status == "complete") {
                    el.value = "OK DONE FINSHIED"
                    width = "100"
                } else {
                    var value = JSON.parse(message.message);
                    el.value = value.progress;
                    width = value.progress;
                }
                progress_el.setStyle("width", width+"%");
            }
            spt.message.set_interval(key, callback, 1000);
            '''
        } )


        div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.message.stop_all_intervals();
            console.log("stopped");
            '''
        } )




        return div


    def get_onload_js(cls):
        return r'''
if (spt.message) {
    return;
}


spt.message = {}

spt.message.intervals = {};


spt.message.set_interval = function(key, callback, interval) {

    var f = function(message) {
        try {
            if (message) {
                callback(message);
            }
            else {
                console.log("WARNING: message is undefined!!");
                spt.message.stop_interval(key);
                return;
            }
        }
        catch(e) {
            spt.message.stop_interval(key);
            alert(e);
        }
        if (message.status == "complete") {
            spt.message.stop_interval(key);
        }
    }


    var interval_id = setInterval( function() {
        spt.message.async_poll(key, f);
    } , interval );
    spt.message.intervals[key] = interval_id;
} 

spt.message.stop_interval = function(key) {
    clearInterval(spt.message.intervals[key]);
} 

spt.message.stop_all_intervals = function() {
    for (var key in spt.message.intervals) {
        spt.message.stop_interval(key);
    }
} 

spt.message.generate_key = function(length) {
    if (!length) {
        length = 20;
    }

    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    for( var i=0; i < length; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;

    
}

spt.message.poll = function(key) {
    var server = TacticServerStub.get();
    var messages = server.eval("@SOBJECT(sthpw/message['code','"+key+"'])");
    var message = messages[0];
    return message;

}


spt.message.async_poll = function(key, callback) {
    var server = TacticServerStub.get();
    var expr = "@SOBJECT(sthpw/message['code','"+key+"'])";

    server.async_eval(expr, {single:true,cbjs_action:callback});
}



        '''
    get_onload_js = classmethod(get_onload_js)



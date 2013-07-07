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
from pyasm.widget import TextWdg, IconWdg
from tactic.ui.widget import ActionButtonWdg, IconButtonWdg


__all__ = ['SubscriptionWdg', 'MessageWdg']



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

        mode = "all"

        categories = ['chat','sobject','script']

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



    def get_category_wdg(my, category, mode="new"):

        subscriptions = my.get_subscriptions(category)
        if not subscriptions:
            return

        div = DivWdg()

        title_div = DivWdg()
        div.add(title_div)
        title_div.add_style("padding: 10px")
        title_div.add_border()
        title_div.add_color("background", "background3")
        title_div.add("%s " % category)
        

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
        table.add_style("width: 700px")
        table.add_border()
        table.add_color("background", "background3")
        table.add_style("margin: 30px")

        from pyasm.widget import ThumbWdg

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
                    sobject = Search.get_by_search_key(message_code)
                    thumb = ThumbWdg()
                    thumb.set_sobject(sobject)
                    thumb.set_icon_size(80)
                    td.add(thumb)
                    td = table.add_cell(sobject.get_code())

                    td = table.add_cell()
                    td.add("No Messages")
                continue

            # FIXME: this should be done in the query
            if mode != "all":
                message_timestamp = message.get_value("timestamp")
                subscription_cleared = subscription.get_value("last_cleared")
                if subscription_cleared > message_timestamp:
                    continue


            category = message.get_value("category")
            if category == "sobject":
                sobject = Search.get_by_search_key(message_code)
                thumb = ThumbWdg()
                thumb.set_sobject(sobject)
                thumb.set_icon_size(80)
                td.add(thumb)


            #td = table.add_cell(message_code)

            message_value = message.get_value("message")
            if message_value.startswith("{") and message_value.endswith("}"):
                message_value = jsonloads(message_value)

                description = message_value.get("description")

                if category == "sobject":
                    description = message_value.get("update_data")


            else:
                description = message_value

            td = table.add_cell()
            td.add(description)
            td = table.add_cell()
            td.add(message.get_value("status"))
            td = table.add_cell()
            td.add(message.get_value("timestamp"))
            td = table.add_cell()
            td.add(subscription.get_value("last_cleared"))

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
                if (message.status == "complete") {
                    el.value = "OK DONE FINSHIED"
                    width = "100%"
                } else {
                    var value = JSON.parse(message.message);
                    el.value = value.progress;
                    width = value.progress;
                }
                progress_el.setStyle("width", width);
            }
            spt.message.set_interval(key, callback, 1000);
            '''
        } )


        div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            clearInterval( spt.message.interval_id );
            console.log("stopped");
            '''
        } )




        return div


    def get_onload_js(my):
        return r'''
spt.message = {}

spt.message.interval_id = null;


spt.message.set_interval = function(key, callback, interval) {
    var interval_id = setInterval( function() {
        var message = spt.message.poll(key);
        callback(message);
        if (message.status == "complete") {
            spt.message.stop_interval();
        }
    } , interval );
    spt.message.interval_id = interval_id;
} 

spt.message.stop_interval = function() {
    clearInterval(spt.message.interval_id);
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
        '''


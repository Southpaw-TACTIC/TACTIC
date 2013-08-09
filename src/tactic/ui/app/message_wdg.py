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

from pyasm.common import jsonloads, Environment, Common

from pyasm.web import DivWdg, SpanWdg

from tactic.ui.common import BaseRefreshWdg
from pyasm.search import Search, SearchType
from pyasm.command import Command
from pyasm.web import Table
from pyasm.widget import TextWdg, IconWdg, ThumbWdg, TextWdg, TextAreaWdg
from tactic.ui.widget import ActionButtonWdg, IconButtonWdg


__all__ = ['ChatWdg', 'ChatSessionWdg', 'ChatCmd', 'SubscriptionWdg', 'SubscriptionBarWdg', 'MessageWdg']



class ChatWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top;
        my.set_as_panel(top)
        top.add_class("spt_chat_top")


        inner = DivWdg()
        top.add(inner)
        inner.add_behavior( {
            'type': 'load',
            'cbjs_action': MessageWdg.get_onload_js()
        } )



        search = Search("sthpw/subscription")
        search.add_filter("category", "chat")
        search.add_user_filter()
        chats = search.get_sobjects()
        keys = [x.get_value("message_code") for x in chats]

        chat_list_div = DivWdg()
        chat_list_div.add("<b>Chat Sessions</b><br/>")
        inner.add(chat_list_div)
        for chat in chats:
            chat_div = DivWdg()
            chat_list_div.add(chat_div)

            # find all the users with the same chat
            key = chat.get_value("message_code")
            chat_div.add(key)

            search = Search("sthpw/subscription")
            search.add_filter("message_code", key)
            subscriptions = search.get_sobjects()
            users = [x.get_value("login") for x in subscriptions]
            chat_div.add(" : ")
            chat_div.add(users)

            chat_div.add_behavior( {
                'type': 'click_up',
                'key': key,
                'cbjs_action': '''
                var class_name = 'tactic.ui.app.ChatSessionWdg';
                var kwargs = {
                    'key': bvr.key,
                }
                spt.panel.load_popup("Chat: " + bvr.key, class_name, kwargs);

                '''
            } )



        #keys = my.kwargs.get("keys")
        #if not keys:
        #    return

        inner.add( my.get_add_chat_wdg() )

        for key in keys:
            session_div = DivWdg()
            session_div.add_style("width: 400px")
            inner.add(session_div)
            session_div.add_style("float: left")
            session_div.add_style("margin: 15px")

            session = ChatSessionWdg(key=key)
            session_div.add(session)

        inner.add("<br clear='all'/>")

        if my.kwargs.get("is_refresh") == 'true':
            return inner
        else:
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

            var class_name = 'tactic.ui.app.ChatCmd';
            var kwargs = {
                users: [user]
            }
            server.execute_cmd(class_name, kwargs);

            spt.panel.refresh(bvr.src_el);
            '''
        } )

        return div


class ChatCmd(Command):

    def execute(my):

        login = Environment.get_user_name()
        users = my.kwargs.get("users")

        everyone = [login]
        everyone.extend(users)

        # find out if there already is a subscription between this user
        # and others
        search = Search("sthpw/subscription")
        search.add_filter("login", login)
        search.add_filter("category", "chat")
        login_subscriptions = search.get_sobjects()
        keys = [x.get_value("message_code") for x in login_subscriptions]

        create = True

        # find the subscriptions for each user with the same keys
        for user in users:
            search = Search("sthpw/subscription")
            search.add_filters("message_code", keys)
            search.add_filter("login", user)
            user_subscriptions = search.get_sobjects()
            if user_subscriptions:
                create = False


        # create a new subscription
        if create:
            key = Common.generate_random_key()
            message = SearchType.create("sthpw/message")
            message.set_value("code", key)
            message.set_value("login", login)
            message.set_value("category", "chat")
            message.set_value("message", "Welcome!!!")
            message.commit()

            # create a subscription for each person
            for person in everyone:
                subscription = SearchType.create("sthpw/subscription")
                subscription.set_value("message_code", key)
                subscription.set_value("login", person)
                subscription.set_value("category", "chat")
                subscription.commit()





class ChatSessionWdg(BaseRefreshWdg):

    def get_display(my):
        top = my.top
        my.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)
        inner.add_behavior( {
            'type': 'load',
            'cbjs_action': MessageWdg.get_onload_js()
        } )

        inner.add_style("min-width: 400px")


        key = my.kwargs.get("key")
        interval = True
        
        top.add( my.get_chat_wdg(key, interval) )
        return top


    def get_chat_wdg(my, key, interval=False):

        div = DivWdg()
        div.add_class("spt_chat_session_top")
        div.add_color("background", "background")

        title_wdg = DivWdg()
        div.add(title_wdg)
        title_wdg.add_color("background", "background3")
        title_wdg.add_style("padding: 5px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_border()

        icon = IconButtonWdg(title="Remove Chat", icon=IconWdg.DELETE)
        icon.add_style("float: right")
        icon.add_style("margin-top: -5px")
        title_wdg.add(icon)
        icon.add_behavior( {
            'type': 'click_up',
            'key': key,
            'cbjs_action': '''
            var server = TacticServerStub.get();

            var top = bvr.src_el.getParent(".spt_chat_session_top");
            spt.behavior.destroy_element(top);
            '''
        } )


        current_user = Environment.get_user_name()
        logins = Search.eval("@SOBJECT(sthpw/subscription['message_code','%s'].sthpw/login)" % key)
        for login in logins:
            if login.get_value("login") == current_user:
                continue

            thumb = ThumbWdg()
            thumb.set_icon_size(45)
            thumb.set_sobject(login)
            thumb.add_style("float: left")
            thumb.add_style("margin: -5px 10px 0px -5px")
            title_wdg.add(thumb)
            title_wdg.add(login.get_value("display_name"))

        title_wdg.add("<br clear='all'/>")


        history_div = DivWdg()
        div.add(history_div)
        history_div.add_class("spt_chat_history")
        history_div.add_style("width: auto")
        history_div.add_style("height: auto")
        history_div.add_style("max-height: 400px")
        history_div.add_style("padding: 5px")
        history_div.add_class("spt_resizable")

        history_div.add_border()
        history_div.add_style("overflow-y: auto")
        #history_div.add_style("font-size: 0.9em")


        search = Search("sthpw/message_log")
        search.add_filter("message_code", key)
        message_logs = search.get_sobjects()
        last_login = None;
        last_date = None;
        for message_log in message_logs:

            login = message_log.get("login")
            message = message_log.get("message")
            timestamp = message_log.get_datetime_value("timestamp")
            #timestamp = timestamp.strftime("%b %d, %Y - %H:%M")
            timestamp_str = timestamp.strftime("%H:%M")
            date_str = timestamp.strftime("%b %d, %Y")
        
            msg = "";
            msg += "<table style='margin-top: 5px; font-size: 0.9em; width: 100%'><tr><td>";

            if date_str != last_date:
                msg += "<hr/><b>"+date_str+"</b><hr/></td></tr>";
                msg += "<tr><td>";
                last_login = None

            if login != last_login:
                msg += "<b>"+login+"</b><br/>";
            msg += message.replace("\n",'<br/>');
            msg += "</td><td style='text-align: right; margin-bottom: 5px; width: 75px; vertical-align: top'>";
            msg += timestamp_str;
            msg += "</td></tr></table>";

            history_div.add(msg)

            last_login = login
            last_date = date_str

        history_div.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            bvr.src_el.scrollTop = bvr.src_el.scrollHeight;
            '''
        } )




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
                msg += "</td><td style='text-align: right; margin-bottom: 5px; width: 75px; vertical-align: top'>";
                msg += timestamp;
                msg += "</td></tr></table>";

                if (msg == history_el.last_msg) {
                    return;
                }
                history_el.innerHTML =  history_el.innerHTML + msg;

                // remember last message
                history_el.last_msg = msg;


                history_el.scrollTop = history_el.scrollHeight;
            }
            spt.message.set_interval(bvr.key, callback, 3000, bvr.src_el);
            '''
            } )

        text = TextAreaWdg("chat")
        div.add(text)
        text.add_class("spt_chat_text")
        text.add_style("width: 100%")
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

        var top = bvr.src_el.getParent(".spt_chat_session_top");
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

    def get_subscriptions(my, category, mode="new"):

        search = Search("sthpw/subscription")
        search.add_user_filter()
        if category:
            search.add_filter("category", category)



        if mode == "new":
            search.add_op("begin")
            search.add_filter("last_cleared", '"message"."timestamp"', quoted=False, op="<")
            search.add_filter("last_cleared", "NULL", quoted=False, op="is")
            search.add_op("or")

            # use an inner join because if there are no messages, we don't
            # want the subscription
            search.add_order_by("message.timestamp", direction="desc", join="INNER")
            user = Environment.get_user_name()
            search.add_filter("login", user, op="!=", table="message")
        else:
            search.add_order_by("message.timestamp", direction="desc")

        subscriptions = search.get_sobjects()


        return subscriptions


    def set_refresh(my, inner, interval):

        inner.add_behavior( {
            'type': 'load',
            'interval': interval,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_subscription_top");
            timeout_id = setTimeout( function() {
                spt.panel.refresh(top, {async: true});
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





    def get_display(my):
        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_subscription_top")

        interval = 30 * 1000

        inner = DivWdg()
        top.add(inner)
        my.set_refresh(inner,interval)

        inner.add_style("min-width: 400px")
        inner.add_style("min-height: 300px")


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

        message_code = subscription.get_value("message_code")

        if category == 'sobject':
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



        elif category == 'chat':
            thumb = DivWdg()
            thumb.add_style("width: %s" % size)
            thumb.add_style("height: %s" % (size*3/4))
            thumb.add_border()
            thumb.add_style('text-align: center')
            thumb.add_class("hand")

            message = Search.get_by_code("sthpw/message", message_code)
            login_code = message.get_value("login")

            login = Search.get_by_code("sthpw/login", login_code)
            thumb_wdg = ThumbWdg()
            thumb.add(thumb_wdg)
            thumb_wdg.set_sobject(login)
            thumb_wdg.set_icon_size(size)


            key = subscription.get_value("message_code")
            thumb.add_behavior( {
                'type': 'click_up',
                'key': key,
                'cbjs_action': '''
                var class_name = 'tactic.ui.app.ChatSessionWdg';
                var kwargs = {
                    'key': bvr.key,
                }
                spt.panel.load_popup("Chat: " + bvr.key, class_name, kwargs);
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
            thumb.add_class("hand")





        thumb.add_style("margin: 3px")
        return thumb


    def get_category_wdg(my, category, mode="new"):

        subscriptions = my.get_subscriptions(category, mode)
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
            spt.panel.refresh(bvr.src_el);
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

            size = 60

            category = message.get_value("category")
            td = table.add_cell()
            td.add( my.get_preview_wdg(subscription) )


            #td = table.add_cell(message_code)

            message_value = message.get_value("message")
            if message_value.startswith("{") and message_value.endswith("}"):

                # FIXME: this is needed because the json has some bad
                # \\ issues. 
                message_value = message_value.replace(r"\\", "\\");
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

                if category == "chat":
                    login = message.get("login")
                    timestamp = message.get("timestamp")

                    message_value = message.get("message")
                    message_value = message_value.replace("\n", "<br/>")

                    description = '''
                    <b>%s</b><br/>
                    %s
                    ''' % (login, message_value)
                else:
                    description = message_value


            td = table.add_cell()
            icon = IconButtonWdg(title="Subscription History", icon=IconWdg.HISTORY)
            td.add(icon)
            subscription_key = subscription.get_search_key()
            message_code = subscription.get_value("message_code")
            icon.add_behavior( {
                'type': 'click_up',
                'message_code': message_code,
                'cbjs_action': '''
                var class_name = 'tactic.ui.panel.FastTableLayoutWdg';
                var message_code = bvr.message_code;
                alert(message_code);
                var kwargs = {
                    search_type: 'sthpw/message_log',
                    show_shelf: false,
                    expression: "@SOBJECT(sthpw/message_log['message_code','"+message_code+"'])",
                };
                spt.tab.set_main_body_tab();
                spt.tab.add_new("Message History", "Message History", class_name, kwargs);
                '''
            } )
 

            td = table.add_cell()

            desc_div = DivWdg()
            td.add(desc_div)
            desc_div.add(description)
            desc_div.add_style("padding: 0px 20px")
            desc_div.add_style("max-width: 600px")

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
            icon = IconButtonWdg(title="Unsubscribe", icon=IconWdg.DELETE)
            td.add(icon)
            subscription_key = subscription.get_search_key()
            icon.add_behavior( {
                'type': 'click_up',
                'search_key': subscription_key,
                'cbjs_action': '''
                    if (!confirm("Confirm subscription delete?")) {
                        return;
                    }
                    var top = bvr.src_el.getParent(".spt_subscription_top");
                    var server = TacticServerStub.get();
                    server.delete_sobject(bvr.search_key);
                    spt.panel.refresh(top);
                '''
            } )






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



class SubscriptionBarWdg(SubscriptionWdg):

    ARGS_KEYS = {
        'mode': {
            'description': "tab|dialog|popup - determines how the details should open",
            'type': 'SelectWdg',
            'values': 'tab|dialog|popup'
        }
    }

    def get_display(my):
        top = my.top
        top.add_class("spt_subscription_top")
        my.set_as_panel(top)

        top.add_style("width: 100px")
        top.add_style("height: 20px")

        top.add_class("hand")




        interval = my.kwargs.get("interval")
        if not interval:
            interval = 10 * 1000
        else:
            interval = int(interval) * 1000

        inner = DivWdg()
        top.add(inner)

        my.set_refresh(inner,interval)

        mode = my.kwargs.get("mode")
        if not mode:
            mode = "tab"

        mode = "dialog"
        if mode == "dialog":
            from tactic.ui.container import DialogWdg
            dialog = DialogWdg(display=False, show_title=False)
            inner.add(dialog)
            dialog.set_as_activator(inner)
            subscription_wdg = SubscriptionWdg()
            dialog.add(subscription_wdg)
            subscription_wdg.add_style("width: 400px")
            subscription_wdg.add_color("background", "background")
            subscription_wdg.add_style("height: 400px")

        elif mode == "popup":
            top.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var class_name = 'tactic.ui.app.SubscriptionWdg';
                var kwargs = {};
                spt.panel.load_popup("Subscriptions", class_name, kwargs);
                '''
            } )
        else:
            top.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                spt.tab.set_main_body_tab();
                var class_name = 'tactic.ui.app.SubscriptionWdg';
                var kwargs = {};
                spt.tab.add_new("Subscriptions", "Subscriptions", class_name, kwargs);
                '''
            } )


        color = inner.get_color("border") 
        inner.add_style("border-style: solid")
        inner.add_style("border-size: 1px")
        inner.add_style("border-color: transparent")
        inner.set_round_corners(5)
        inner.add_style("padding: 2px")

        inner.add_behavior( {
            'type': 'mouseenter',
            'color': color,
            'cbjs_action': '''
            bvr.src_el.setStyle("border", "solid 1px "+bvr.color);
            '''
        } )
        inner.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            bvr.src_el.setStyle("border-color", "transparent");
            '''
        } )






        category = None
        subscriptions = my.get_subscriptions(category)



        if not subscriptions:
            inner.add_style("display: none")


        num = len(subscriptions)
        if num == 1:
            msg = "%s Message" % num
        else:
            msg = "%s Messages" % num

        icon = IconWdg(msg, IconWdg.STAR)
        inner.add(icon)
        inner.add(msg)

        if my.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top





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
            spt.message.set_interval(key, callback, 1000, bvr.src_el);
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
spt.message.elements = {};


spt.message.set_interval = function(key, callback, interval, element) {

    var f = function(message) {
        try {
            if (message) {
                callback(message);
            }
            else {
                console.log("WARNING: message is undefined for key ["+key+"]");
                //spt.message.stop_interval(key);
                return;
            }
        }
        catch(e) {
            spt.message.stop_interval(key);
            alert(e);
        }
        if (message.status == "complete") {
            console.log("stopping interval: " + key);
            spt.message.stop_interval(key);
        }
    }


    // stop this interval if it already started/registered
    spt.message.stop_interval(key);


    var interval_id = setInterval( function() {
        spt.message.async_poll(key, f);
    } , interval );
    spt.message.intervals[key] = interval_id;

    if (element) {
        var id = element.getAttribute("id");
        if (!id) {
            element.setAttribute("id", key);
            spt.message.elements[key] = key;
        }
        else {
            spt.message.elements[key] = id;
        }
        element.addClass("spt_notify_destroyed");
    }
    else
        spt.message.elements[key] = null;
} 

spt.message.stop_interval = function(key) {
    if (!spt.message.intervals[key]) {
        return;
    }

    clearInterval(spt.message.intervals[key]);
    delete spt.message.intervals[key];
    delete spt.message.elements[key];
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
    for( var i=0; i < length; i++ ) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }

    return text;

    
}

spt.message.poll = function(key) {
    var server = TacticServerStub.get();
    var messages = server.eval("@SOBJECT(sthpw/message['code','"+key+"'])");
    var message = messages[0];
    return message;

}


spt.message.async_poll = function(key, callback) {
    // before polling, check that the element still exists
    var el_id = spt.message.elements[key];
    var el = $(el_id);
    if (!el || el.hasClass("spt_destroyed")) {
        spt.message.stop_interval(key);
        return;
    }

    var server = TacticServerStub.get();
    var expr = "@SOBJECT(sthpw/message['code','"+key+"'])";

    server.async_eval(expr, {single:true,cbjs_action:callback});
}



// TEST pooling of queries from different "apps"

spt.message.keys = {};

spt.message.register_key = function() {
    spt.message.results[keys] = true;
}

spt.message.async_polls = function(keys, callback) {
    // before polling, check that the element still exists
    /*
    var el = spt.message.elements[key];
    if (el && el.parentNode == null) {
        spt.message.stop_interval(key);
        return;
    }
    */

    var keys_string = keys.join("|");

    var server = TacticServerStub.get();
    var expr = "@SOBJECT(sthpw/message['code','in','"+keys_string+"'])";

    server.async_eval(expr, {single:false,cbjs_action:callback});
}



        '''
    get_onload_js = classmethod(get_onload_js)



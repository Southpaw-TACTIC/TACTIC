########################################################### #
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['NotifyWdg', 'NotifyPollWdg', 'NotifyPollCmd']

from pyasm.common import Container, Environment
from pyasm.command import Command
from pyasm.web import DivWdg
from pyasm.search import Search

from tactic.ui.common import BaseRefreshWdg


class NotifyWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        top.set_id("spt_notify_top")

        top.add_style("position: fixed")
        top.add_style("bottom: -30")
        top.add_style("left: 0")
        top.add_style("right: 0")
        top.add_style("z-index: 1000")

        top.add_color("background", "background2", 10)
        top.add_style("height: 20px")
        top.add_style("width: 100%")
        top.add_style("padding: 5px")
        top.add_border()


        msg_div = DivWdg()
        top.add(msg_div)
        msg_div.add_class("spt_notify_message")




        top.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
spt.notify = {};

spt.notify.show = function() {
    new Fx.Tween('spt_notify_top').start('bottom', 0);
}

spt.notify.hide = function() {
    new Fx.Tween('spt_notify_top').start('bottom', -30);
}


spt.notify.set_message = function(message) {
    var el = $('spt_notify_top').getElement(".spt_notify_message");
    spt.behavior.replace_inner_html(el, message);
}



spt.notify.show_message = function(message, duration) {
    if (typeof(duration) == 'undefined') {
        duration = 3000;
    }

    spt.notify.show();
    spt.notify.set_message(message);
    setTimeout( function() {
        spt.notify.hide();
    }, duration );

}
            '''
        } )


        return top


class NotifyPollWdg(BaseRefreshWdg):


    def get_display(my):

        top = my.top

        top.add_behavior( {
        'type': 'load',
        'cbjs_action': '''

        var class_name = 'tactic.ui.app.NotifyPollCmd';

        var id = setInterval( function() {
            var server = TacticServerStub.get();
            var kwargs = {};
            var html = server.get_widget(class_name, { args: kwargs } );
            spt.notify.show_message(html);
        }
        , 5000);


        setTimeout( function() {
            clearInterval(id);
        }, 20000 );


        '''
        } )


        return top


    def get_onload_js(my):
        return r'''

        '''


#class NotifyPollCmd(Command):
class NotifyPollCmd(BaseRefreshWdg):

    #def is_undoable(cls):
    #    return False
    #is_undoable = classmethod(is_undoable)


    def get_display(my):

        print "NotifyPollCmd"

        user = Environment.get_user_name()
        print "user: ", user

        # find out if there is anything interesting to post
        #search = Search("sthpw/message")
        #search.add_filter("login", user)



        search = Search("sthpw/login")
        sobjects = search.get_sobjects()

        codes = [x.get_code() for x in sobjects]
        codes = ", ".join(codes)

        div = DivWdg()
        div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var class_name = 'tactic.ui.panel.ViewPanelWdg';
            var search_type = "sthpw/login";
            var view = 'table';
            var kwargs = {
                'search_type': search_type,
                'view': view
            }
            spt.tab.add_new("Login", "Login", class_name, kwargs);
            '''
        } )
        div.add("cow")
        div.add_class("handle")


        #my.info = {
        #    'msg': div.get_buffer_display()
        #}

        return div





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
        top.add_style("top: 60px")
        top.add_style("z-index: 10000")
        top.add_style("width: 200px")
        top.add_style("text-align: center")
        top.add_style("margin-top: -100px")

        top.add_color("background", "background", -3)
        top.add_style("height: 20px")
        top.add_style("padding: 5px")
        top.add_border()


        msg_div = DivWdg()
        top.add(msg_div)
        msg_div.add_class("spt_notify_message")




        top.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
spt.notify = {};

spt.notify.last_settings = {};

spt.notify.show = function() {
    new Fx.Tween('spt_notify_top').start('opacity', 1);
    new Fx.Tween('spt_notify_top').start('marginTop', 0);
}

spt.notify.hide = function() {
    new Fx.Tween('spt_notify_top').start('opacity', 0);
    new Fx.Tween('spt_notify_top').start('marginTop', -60);
}



spt.notify.set_message = function(message, kwargs) {
    var el = $('spt_notify_top').getElement(".spt_notify_message");
    spt.behavior.replace_inner_html(el, message);

    spt.notify.last_settings = {};

    for (var key in kwargs) {
        spt.notify.last_settings[key] = $('spt_notify_top').getStyle(key);
        $('spt_notify_top').setStyle(key, kwargs[key]);
    }
}



spt.notify.show_message = function(message, duration, kwargs) {
    if (!duration) {
        duration = 5000;
    }

    spt.notify.show();
    spt.notify.set_message(message, kwargs);
    setTimeout( function() {
        spt.notify.hide();
    }, duration );


    var el = $('spt_notify_top');
    var size = el.getSize();

    var window_size = $(window).getSize();
    el.setStyle("left", (window_size.x-size.x)/2);


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





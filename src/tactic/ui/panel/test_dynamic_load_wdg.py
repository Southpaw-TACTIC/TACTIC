###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["TestDynamicLoadWdg"]


from pyasm.web import DivWdg
from pyasm.common import Common

from tactic.ui.common import BaseRefreshWdg


class TestDynamicLoadWdg(BaseRefreshWdg):

    def get_display(self):

        do_single_on_load_bvr = True

        if do_single_on_load_bvr:
            return self.get_display_single_on_load_bvr()
        else:
            return self.get_display_on_load_bvr_on_each_widget()


    def get_display_single_on_load_bvr(self):
        class_path = Common.get_full_class_name(self)

        top = DivWdg()
        top.add_styles("border: 1px solid black;")

        count = self.kwargs.get('count')
        print "count: ", count
        if count:
            count = int(count)
        else:
            count = 0

        top.add('top: %s' % count)
        top.add_class('my_dynamic_add_div_%s' % count)

        max = 10

        if count == 0:

            top.add_behavior( {
                'type': 'load',
                'cbjs_action': '''
                    var server = TacticServerStub.get();

                    var widget_class = '%s';
                    var count = 1;
                    var max = %s;

                    var main = document.id('main_body');

                    for( var c=count; c <= max; c++ ) {
                        spt.app_busy.show("Dynamic Loading ...", "Loading widget with count of " + c);
                        var div = document.createElement('div');
                        args = { "count": '' + c };
                        html = server.get_widget(widget_class, {"args": args}) + '<br/>';
                        spt.behavior.replace_inner_html(div, html);
                        main.appendChild(div);
                    }

                    spt.app_busy.hide();
                ''' % (class_path, max)
            } )

        return top


    def get_display_on_load_bvr_on_each_widget(self):
        class_path = Common.get_full_class_name(self)

        top = DivWdg()
        top.add_styles("border: 1px solid black;")

        count = self.kwargs.get('count')
        print "count: ", count
        if count:
            count = int(count)
        else:
            count = 0

        count += 1
        top.add('top: %s' % count)
        top.add_class('my_dynamic_add_div_%s' % count)

        if count < 10:

            top.add_behavior( {
                'type': 'load',
                'cbjs_action': '''
                    var server = TacticServerStub.get();
                    var widget_class = '%s';
                    var args = {
                        count: '%s'
                    };
                    var html = server.get_widget(widget_class, {args:args});
                    var main = document.id('main_body');

                    var div = document.createElement('div');
                    spt.behavior.replace_inner_html(div, html);
                    main.appendChild(div);

                ''' % (class_path, count)
            } )

        return top


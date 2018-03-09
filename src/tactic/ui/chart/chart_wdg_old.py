###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = []

from pyasm.common import Environment, Common, jsonloads
from pyasm.biz import Project
from pyasm.web import Widget, DivWdg, HtmlElement, WebContainer
from pyasm.widget import SelectWdg, TextWdg
from pyasm.search import Search, SearchType
from tactic.ui.common import BaseRefreshWdg

import types

# DEPRECATED


class ChartWdgOld(BaseRefreshWdg):

    ARGS_KEYS = {
        'chart': 'chart object to display',
        'data_file':  'file name to use for data',
        'width': 'width of the chart'

    }

    def get_display(self):

        chart_data = self.kwargs.get('chart')
        data_file = self.kwargs.get('data_file')
        width = self.kwargs.get('width')
        if not width:
            width = '100%'

        if chart_data:
            if type(chart_data) in types.StringTypes:
                data = jsonloads(chart_data)
            elif type(chart_data) == types.DictType:
                data = chart_data
            else:
                data = chart_data.get_data()

            file = '__NONE__'

        else:
            data = {}
            if data_file:
                file = data_file
            else:
                file = '__NONE__'
             
        top = DivWdg()

        inner = DivWdg()
        top.add(inner)


        # the element that gets replaced
        div = DivWdg()
        inner.add(div)
        inner.add_color("background", "background")
        inner.add_style("padding: 15px")


        import random
        number = random.randint(0, 1000000)
        chart_id = 'my_chart%s' % number
        div.set_id(chart_id)


        # TEST TEST TEST: dynamic loading of js
        # FIXME: this does not work!!!???!!! 
        """
        env = Environment.get()
        install_dir = env.get_install_dir()
        js_path = "%s/src/context/spt_js/ofc/js/swfobject.js" % install_dir
        f = open(js_path)
        init_js = f.read()
        f.close()
        """

        top.add_behavior({
            'type': 'load',
            'data': data,
            'file': file,
            'width': width,
            'chart_id': chart_id,
            'cbjs_action': '''

            // initialize the js
            // FIXME: why does this not work??!!!!???
            /*
            var js_file = "ofc/js/swfobject.js";
            var url = "/context/spt_js/" + js_file;
            var js_el = document.createElement("script");
            js_el.setAttribute("type", "text/javascript");
            js_el.setAttribute("src", url);
            var head = document.getElementsByTagName("head")[0];
            head.appendChild(js_el);
            */


            var flashvars;
            if (bvr.file != '__NONE__') {
                flashvars = {
                    "data-file":    '/context/spt_js/ofc/data-files/'+bvr.file
                };
            }
            else {
                flashvars = null;

                open_flash_chart_data = function() {
                    return JSON.stringify(bvr.data);
                }
            }

            var params = {
                wmode:      'transparent'
            };


            var ofc_url = "/context/spt_js/ofc/open-flash-chart.swf";
            var attrs = {};
            var width = bvr.width;
            var height = "300";

            swfobject.embedSWF(ofc_url, bvr.chart_id, width, height, "9.0.0", "expressInstall.swf", flashvars, params, attrs);

            window.addEvent('domready', function(){
                    $(bvr.chart_id).makeResizable();
            });

            '''
        })


        top.add("<br clear='all'/>")

        return top



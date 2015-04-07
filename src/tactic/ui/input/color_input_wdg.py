###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

# Color wheel input

__all__ = ['ColorWdg', 'ColorInputWdg']

from pyasm.common import Date, Common
from pyasm.web import Table, DivWdg, SpanWdg, WebContainer, Widget
from pyasm.widget import IconWdg, IconButtonWdg, BaseInputWdg, TextWdg
from tactic.ui.common import BaseRefreshWdg

import random

from text_input_wdg import TextInputWdg



class ColorWdg(Widget):
    '''This is drawn once in the page to reuse by repositioning it'''
    def get_display(my):

        top = DivWdg()

        inner = DivWdg()
        top.add(inner)

        inner.add_style('position: absolute')
        inner.add_style('top: 100')
        inner.add_style('left: 100')
        inner.add_style("z-index: 1000")
        import random
        number = random.randint(1, 1000)
        rainbow_id = "rainbow_%s" % number
        inner.set_id(rainbow_id);

        #top.add('''
        #<img id="%s" src="/context/spt_js/mooRainbow/rainbow.png" alt="[r]" width="16" height="16" />
        #''' % rainbow_id)


        inner.add_behavior( { 
            "type": "load",
            'rainbow_id': rainbow_id,
            "cbjs_action": '''

            spt.color = {};
            spt.color.top = bvr.src_el;

            spt.color.init = function() {
                var js_file = "mooRainbow/Source/mooRainbow.js";
                var url = "/context/spt_js/" + js_file;
                var js_el = document.createElement("script");
                js_el.setAttribute("type", "text/javascript");
                js_el.setAttribute("src", url);
                var head = document.getElementsByTagName("head")[0];
                head.appendChild(js_el);

                setTimeout( function() {

                spt.color.rainbow = new MooRainbow(bvr.rainbow_id, {
                    id: bvr.rainbow_id,
                    startColor: [58, 142, 246],
                    imgPath:    '/context/spt_js/mooRainbow/Assets/images/',
                    onComplete: function(color) {
                        if (spt.color.rainbow){
                            var cbk = spt.color.rainbow.cbk;
                            cbk(color);
                        }
                    }
                });
                //make it rise above the Edit popup
                spt.color.rainbow.layout.setStyle('z-index','10000');
                spt.color.rainbow.spt_id = bvr.rainbow_id;

                }, 300 );

            }

            spt.color.get = function() {
                if (! spt.color.rainbow ) {
                    spt.color.init();
                }

                return spt.color.rainbow;
            }

            '''
        } )


        return inner


#
# Use this for input
#

class ColorInputWdg(BaseInputWdg):

    ARGS_KEYS = {
    }


    def __init__(my, name=None, **kwargs):
        if not name:
            name = kwargs.get("name")
        my.top = DivWdg()
        my.input = None
        my.kwargs = kwargs
        super(ColorInputWdg, my).__init__(name)


    def add_style(my, name, value=None):
        my.top.add_style(name, value)

    def set_input(my, input):
        my.input = input
        my.input.set_name(my.get_input_name() )

    def get_input(my):
        return my.input


    def add(my, widget):
        my.top.add(widget)


    def get_display(my):
        top = my.top

        if not my.input:
            my.input = TextInputWdg(name=my.get_input_name())

        value = my.get_value()
        if value:
            my.input.set_value(value)
            my.input.add_style("background", value)
        top.add(my.input)

        start_color = my.kwargs.get("start_color")
        if start_color:
            my.input.set_value(start_color)
            my.input.add_style("background", start_color)

        my.input.add_class("spt_color_input")
     
        if not start_color:
            start_color = [0, 0, 255]
        elif start_color.startswith("#"):
            start_color = start_color.replace("#", "")
            r, g, b = start_color[:2], start_color[2:4], start_color[4:]
            r, g, b = [int(n, 16) for n in (r, g, b)]

            start_color = [r, g, b]

        behavior = {
            'type': 'click_up',
            'name': my.get_name(),
            'start_color': start_color,
            'cbjs_action': '''
            var pos = bvr.src_el.getPosition();
            var input = bvr.src_el.getElement(".spt_color_input");
            var cell_edit = bvr.src_el.getParent(".spt_cell_edit");
            var current_color = input.value;
            input.setStyle("background-color", current_color);

            if (!current_color) {
                current_color = bvr.start_color;
            }
            else {
                var c = spt.css.convert_hex_to_rgb_obj(current_color);
                current_color = [c.r, c.g, c.b];
            }

            

            var options = {
                startColor: current_color,
                onComplete: function(color) {
                    input.value=color.hex;
                    
                }
            };

            var cbk = function(color) {
                input.value = color.hex;
                input.setStyle("background-color", color.hex);
                input.blur();
                if (cell_edit)
                    spt.table.accept_edit(cell_edit, input.value, true);
            };

            var rainbow = null;
            var rainbow = spt.color.get();
            // function to actually display the mooRainbow picker
            var display_dialog = function() {

                rainbow.cbk = cbk;
                rainbow.manualSet( current_color );

                // set the position
                spt.color.top.setStyle('left', pos.x);
                spt.color.top.setStyle('top', pos.y+20);
                //spt.color.top.setStyle('z-index', '1000');
                rainbow.show();
            }
        
            if (rainbow) {
                display_dialog();
            } else { // this could be run at the very first time it is drawn
                setTimeout(function() {
                rainbow = spt.color.get();
                display_dialog();
            
                }, 1000)
            }
            '''
        }
        top.add_behavior(behavior)

        return top


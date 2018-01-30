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
    def get_display(self):

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


    def __init__(self, name=None, **kwargs):
        if not name:
            name = kwargs.get("name")
        self.top = DivWdg()
        self.input = None
        self.kwargs = kwargs
        super(ColorInputWdg, self).__init__(name)

        if not self.input:
            self.input = TextInputWdg(name=self.get_input_name())



    def add_style(self, name, value=None):
        self.top.add_style(name, value)

    def set_input(self, input):
        self.input = input
        self.input.set_name(self.get_input_name() )

    def get_input(self):
        return self.input


    def add(self, widget):
        self.top.add(widget)


    def add_behavior(self, behavior):
        return self.input.add_behavior(behavior)



    def get_display(self):
        top = self.top


        value = self.get_value()
        if value:
            self.input.set_value(value)
            self.input.add_style("background", value)
        top.add(self.input)

        start_color = self.kwargs.get("start_color")

        if not value:
            if start_color and start_color.find(","):
                colors = start_color.split(",")

            elif not start_color or start_color == "random":
                #'rgba(188, 207, 215, 1.0)',
                colors = [
                    '#bccfd7',
                    '#bcd7cf',
                    '#d7bccf',
                    '#d7cfbc',
                    '#cfbcd7',
                    '#cfd7bc',
                ]

            import random
            num = random.randint(0,len(colors)-1)
            start_color = colors[num]
            #start_color = top.get_color(start_color, -10)


        if start_color:
            self.input.set_value(start_color)
            self.input.add_style("background", start_color)

        self.input.add_class("spt_color_input")
     
        if not start_color:
            start_color = [0, 0, 255]
        elif start_color.startswith("#"):
            start_color = start_color.replace("#", "")
            r, g, b = start_color[:2], start_color[2:4], start_color[4:]
            r, g, b = [int(n, 16) for n in (r, g, b)]

            start_color = [r, g, b]

        behavior = {
            'type': 'click',
            'name': self.get_name(),
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
                if (cell_edit) {
                    input.blur();
                    spt.table.accept_edit(cell_edit, input.value, true);
                }
                else {
                    input.focus();
                    input.blur();
                }
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


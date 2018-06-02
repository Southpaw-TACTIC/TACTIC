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

__all__ = ['ColorInputWdgOLD']

from pyasm.common import Date, Common
from pyasm.web import Table, DivWdg, SpanWdg, WebContainer
from pyasm.widget import IconWdg, IconButtonWdg, BaseInputWdg, TextWdg
from tactic.ui.common import BaseRefreshWdg


# DEPRECATED: this is moved to tatic.ui.input...


class ColorInputWdgOLD(BaseInputWdg):

    def get_display(self):

        raise Exception("tactic.widget.ColorInputWdg is deprecated")

        color_div = DivWdg()
        color_div.add_style("z-index: 1000")
        #color_div.add_style("float: left")
        import random
        number = random.randint(1, 1000)
        rainbow_id = "rainbow_%s" % number

        color_div.add('''
        <img id="%s" src="/context/spt_js/mooRainbow/rainbow.png" alt="[r]" width="16" height="16" />
        ''' % rainbow_id)
        #<input id="selfInput" name="selfInput" type="text" size="13" />

        text = TextWdg(self.get_name())
        text.set_id("selfInput")
        behavior = {
            'type': 'keyboard',
            'kbd_handler_name': 'DgTableMultiLineTextEdit'
        }
        text.add_behavior(behavior)
        color_div.add(text)


        color_div.add_behavior( { 
            "type": "load",
            "cbjs_action": '''
            var r = new MooRainbow('%s', {
                startColor: [58, 142, 246],
                imgPath:    '/context/spt_js/mooRainbow/images/',
                onComplete: function(color) { document.id(myInput).value=color.hex; }
            });
            ''' % rainbow_id
        } )



        return color_div



            


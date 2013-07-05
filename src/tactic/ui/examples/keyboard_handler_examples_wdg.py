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
__all__ = ["KeyboardHandlerExampleWdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from base_example_wdg import BaseExampleWdg


class KeyboardHandlerExampleWdg(BaseExampleWdg):

    def get_example_title(my):
        return "Various Keyboard Handler Examples"


    def get_example_description(my):
        return "A few examples of multi-line keyboard handlers"


    def get_example_display(my):

        div = DivWdg()

        int_edit_div = DivWdg()
        int_edit_div.add_styles( "width: auto; height: auto;" )
        int_edit_div.add_class( "SPT_INPUT_WRAPPER" )

        int_edit = HtmlElement.input()
        int_edit.set_attr("type", "text")
        int_edit.set_attr("value", "856")
        int_edit.set_attr("name", "int_edit")
        int_edit.add_behavior( { 'type': 'keyboard', 'kbd_handler_name': 'IntegerTextEdit',
                                 'validation_warning': 'You must enter a number greater than 50',
                                 'cbjs_validation':
                                 '''
                                 log.debug( "Check the value: " + value );
                                 if( parseInt( value ) <= 50 ) {
                                     return false;
                                 }
                                 return true;
                                 '''
                                 } )

        int_edit_div.add( int_edit )
        int_edit_div.add( "<img class='SPT_INPUT_VALIDATION_WARNING' src='/context/icons/silk/exclamation.png' " \
                            "title='' style='display: none;' />" )
        int_edit_div.add( " Enter a value of 50 or less to fail validation, anything over 50 to succeed" \
                          " -- Integer edit example (uses 'kbd_handler_name' of 'IntegerTextEdit')" )

        div.add( int_edit_div )
        div.add( "<br/><br/>" )

        float_edit = HtmlElement.input()
        float_edit.set_attr("type", "text")
        float_edit.set_attr("value", "12.45")
        float_edit.set_attr("name", "int_edit")
        float_edit.add_behavior( { 'type': 'keyboard', 'kbd_handler_name': 'FloatTextEdit' } )

        div.add( float_edit )
        div.add( " Float edit example (uses 'kbd_handler_name' of 'FloatTextEdit')" )
        div.add( "<br/><br/>" )

        textarea = HtmlElement.textarea( 10, 40, "This is a multi-line example." )
        textarea.add_behavior( { 'type': 'keyboard', 'kbd_handler_name': 'MultiLineTextEdit' } )

        div.add( textarea )
        div.add( " Multi-line edit example (uses 'kbd_handler_name' of 'MultiLineTextEdit')" )
        div.add( "<br/><br/>" )

        return div



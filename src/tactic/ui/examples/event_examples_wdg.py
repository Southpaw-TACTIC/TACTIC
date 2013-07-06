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
__all__ = ["NamedEventListenExampleWdg","DomEventListenExampleWdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from tactic.ui.activator import ButtonForDropdownMenuWdg, AttachContextMenuWdg

from base_example_wdg import BaseExampleWdg


class NamedEventListenExampleWdg(BaseExampleWdg):

    def get_example_title(my):
        return "Named Event Listen Behavior Examples"


    def get_example_description(my):
        return "A few examples of using a 'listen' behavior on an SPT named event."


    def get_example_display(my):

        div = DivWdg()

        # ---------------------------------------------------------------------------------------------------------

        my.setup_next_example(div,"Demonstrates the adding of a 'listen' type behavior Named Event in Javascript " \
                                  "dynamically")

        dummy_listener_div = DivWdg()
        dummy_listener_div.set_id("dummy_listener_div")
        dummy_listener_div.set_style("border: 1px solid #000000; background: #AAAAAA; color: #000000; " \
                                     "width: 1000px; padding: 10px;")
        dummy_listener_div.add("This DIV has no listener on it, add one dynamically by running:<br/><br/>" \
                               "<pre>\n    spt.named_events.add_listener( $('dummy_listener_div'), 'mike_test_event', " \
                               "{ 'cbjs_action': 'bvr.src_el.setStyle(\"background-color\",\"red\");' } );\n" \
                               "    spt.named_events.fire_event('mike_test_event',{});\n" \
                               "</pre><br/>" \
                               "in the TACTIC Script Editor.")
        div.add( dummy_listener_div )

        # ---------------------------------------------------------------------------------------------------------

        my.setup_next_example(div,"Demonstrates the firing of an SPT Named Event for 'listen' type behavior. This " \
                                  "example also shows the adding of stacked 'listen' type behaviors on a single " \
                                  "element listening for a single event name (allowing 2 actions to occur on the " \
                                  "firing of one event name)" )

        named_event_name = 'SingleNamedEvent'
        named_fire_div = DivWdg()
        named_fire_div.set_id( "%s_Firer" % named_event_name )
        named_fire_div.set_style("border: 1px solid #000000; background: #AAAAAA; color: #000000; width: 200px; " \
                                 "cursor: pointer; padding: 4px;")
        named_fire_div.add("Click me to Fire an SPT Named Event!")
        named_fire_div.add_behavior( {'type': 'click',
                                      'cbjs_action': 'spt.named_events.fire_event("%s",bvr);' % named_event_name,
                                      'cbfn_preprocess': 'spt.ui_play.named_event_fire_preprocess',
                                      'cbfn_postprocess': 'spt.ui_play.named_event_fire_postprocess'} )
        div.add( named_fire_div )

        div.add( '<br/>' )

        named_listener_div = DivWdg()
        named_listener_div.set_style("border: 1px solid #000000; background: #0000AA; width: 200px; padding: 4px;")
        named_listener_div.add("Listening for an SPT Named Event!")
        named_listener_div.add_behavior( {'type': 'listen', 'event_name': named_event_name,
                                          'cbjs_action': 'alert("Named event [%s] has fired!");' % named_event_name} )

        # show ability to stack more call-backs on the same event for the same element ...
        named_listener_div.add_behavior( {'type': 'listen', 'event_name': named_event_name,
                                          'cbjs_action': 'bvr.src_el.setStyle("background-color","red");'} )
        

        div.add( named_listener_div )

        # ---------------------------------------------------------------------------------------------------------

        my.setup_next_example( div, "Demonstrates the ability for a single Named Event 'listen' behavior to listen to " \
                               "multiple event names, but execute a single call-back" )

        event_name_list  = [
                            'MultipleNamedEvents_Event_One',
                            'MultipleNamedEvents_Event_Two',
                            'MultipleNamedEvents_Event_Three',
                            'MultipleNamedEvents_Event_Four'
                          ]

        named_listener_div = DivWdg()
        named_listener_div.set_id( "MultiNamedEventListenerDiv" )
        named_listener_div.set_style("border: 1px solid #000000; background: #005500; width: 300px; padding: 4px;")
        named_listener_div.add("Listening on MULTIPLE SPT Named Events!")
        named_listener_div.add_behavior( {'type': 'listen', 'event_name': event_name_list,
                                          'cbfn_action': 'spt.ui_play.named_event_listen_cbk'} )

        div.add( named_listener_div )

        div.add( '<br/>' )

        for event_name in event_name_list:
            named_fire_div = DivWdg()
            named_fire_div.set_id( "%s_Firer" % event_name )
            named_fire_div.set_style("border: 1px solid #000000; background: #AAAAAA; color: #000000; width: 200px; " \
                                     "cursor: pointer; padding: 4px;")
            named_fire_div.add("Click me to Fire '%s'!" % event_name)

            behavior = {'type': 'click', 'cb_fire_named_event': event_name}
            if event_name.endswith( "_One" ):
                behavior['cbjs_preprocess'] = 'log.debug(">>> Ran cbjs_preprocess!");'
                behavior['cbjs_postprocess'] = 'log.debug(">>> Ran cbjs_postprocess!");'
            named_fire_div.add_behavior( behavior )

            div.add( named_fire_div )
            div.add( '<br/>' )

        # ------------------------------------------------------------------------------------------------------------

        my.setup_next_example( div, "Demonstrates the use of the convenience short cut for adding a 'listen' " \
                                    "type behavior by using HtmlElement.add_named_listener() method" )

        # Add a div to click on to fire the desired named event ...
        event_name = "whatever_refresh"
        named_fire_div = DivWdg()
        named_fire_div.set_id( "%s_Firer" % event_name )
        named_fire_div.set_style("border: 1px solid #000000; background: #CC0000; color: #000000; width: 200px; " \
                                 "cursor: pointer; padding: 4px;")
        named_fire_div.add("Click me to Fire '%s'!" % event_name)
        named_fire_div.add_behavior( {'type': 'click',
                                      'cbjs_action' : 'alert("About to fire event on postaction ...");',
                                      'cbjs_postaction' : 'spt.named_events.fire_event("%s",bvr);' % event_name,
                                      'cbjs_preprocess': 'log.debug("Running preprocess on postaction fire event!");',
                                      'cbjs_postprocess': 'log.debug("Running postprocess on postaction fire event!");'
                                      } )

        div.add( named_fire_div )
        div.add( '<br/>' )

        # Now call convenience function to more easily set up a named listener behavior ... still needs to be
        # parked on an HTML element, so call it from the top level div in this get_display() method ...
        #
        # NOTE: the last parameter is for any extra bvr specification, like preaction or postaction call-backs
        #       ... if no specs to add then use {} as last param
        #
        div.add_named_listener( event_name, 'alert("Named event [%s] has fired!");' % event_name,
                                {'cbjs_postaction': 'spt.panel.refresh("main_body");'} )


        # ------------------------------------------------------------------------------------------------------------

        my.setup_next_example( div, "" )

        return div


class DomEventListenExampleWdg(BaseExampleWdg):

    def get_example_title(my):
        return "DOM Event Listen Behavior Example"


    def get_example_description(my):
        return "Example of using a 'dom_listen' behavior on a firing of a DOM event. NOTE: that this seems to only " \
                "work if the DOM event is fired and 'listened to' from the same HTML element. Not sure how useful " \
                "this is."


    def get_example_display(my):

        div = DivWdg()

        # --- Example of FIRING a DOM event for a 'dom_listen' behavior type --------------------------------------

        dom_event_name = 'domselffire'
        dom_fire_div = DivWdg()
        dom_fire_div.set_style("border: 1px solid #000000; background: #0000AA; width: 200px; height: 100px; " \
                                 "cursor: pointer;")
        dom_fire_div.add("Firing a DOM event (for 'dom_event' type behavior)!")
        dom_fire_div.add_behavior( {'type': 'click',
                                    'cbfn_action': 'spt.ui_play.dom_event_self_fire_action',
                                    'options': {'event_name': dom_event_name} } )
        dom_fire_div.add_behavior( {'type': 'dom_listen', 'event_name': dom_event_name,
                                    'cbfn_action': 'spt.ui_play.dom_listen_cbk'} )
        div.add( dom_fire_div )

        return div



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
__all__ = ["ClientSideAddBehaviorExampleWdg","BehaviorHandoffExampleWdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from tactic.ui.activator import ButtonForDropdownMenuWdg, AttachContextMenuWdg

from base_example_wdg import BaseExampleWdg


class ClientSideAddBehaviorExampleWdg(BaseExampleWdg):

    def get_example_title(self):
        return "Client-side Add Behavior Example"


    def get_example_description(self):
        return "Above are div elements, each labeled with the class name they are tagged with. They all are " \
               "generated with NO behaviors. Click on them when they are just loaded to verify! Then open up " \
               "the JS Editor and copy and paste the following text (as an example) into the " \
               "editor and click 'Run' to add a behavior client-side ...<br/><br/> " \
               "<div class='look_fnt_code' style='border: 1px solid black; background: white; color: black; padding: 4px;'>" \
               "var el = document.getElement('.SPT_GIZMO_TWO');<br/>" \
               "if( el ) {<br/>" \
               "&nbsp;&nbsp;&nbsp;&nbsp;el.setStyle( 'cursor', 'pointer' );<br/>" \
               "&nbsp;&nbsp;&nbsp;&nbsp;spt.behavior.add( el, " \
                            "{'type':'click_up', 'cbfn_action': 'spt.fx_anim.toggle_slide_el', " \
                            "'dst_el': 'side_bar'} )<br/>" \
               "&nbsp;&nbsp;&nbsp;&nbsp;alert('Now click on SPT_GIZMO_TWO to see the behavior added!');<br/>" \
               "}<br/></div>" \
               "<br/>Once you've run the above code in the JS Editor, click on SPT_GIZMO_TWO again to see what it " \
               "did! Go ahead and try adding behaviors in the same way to the other div elements above!"


    def get_example_display(self):

        div = DivWdg()
        dinfo_list = [
            {'class_name': 'SPT_GIZMO_ONE', 'bgcolor': '#669999', 'color': '#000000'},
            {'class_name': 'SPT_GIZMO_TWO', 'bgcolor': '#0099CC', 'color': '#000000'},
            {'class_name': 'SPT_GIZMO_THREE', 'bgcolor': '#996666', 'color': '#000000'},
            {'class_name': 'SPT_GIZMO_FOUR', 'bgcolor': '#CC9966', 'color': '#000000'}
        ]

        for dinfo in dinfo_list:
            gizmo = DivWdg()
            gizmo.add_class( dinfo.get('class_name') )
            gizmo.add_looks( 'fnt_serif' )
            gizmo.add_styles( 'background: %s; color: %s;' % (dinfo.get('bgcolor'), dinfo.get('color')) )
            gizmo.add_styles( 'width: 200px; border: 1px solid black;' )
            gizmo.add( dinfo.get('class_name') )

            div.add( gizmo )
            div.add( '<br/><br/>' )

        return div


class BehaviorHandoffExampleWdg(BaseExampleWdg):

    def get_example_title(self):
        return "Behavior Handoff Example"


    def get_example_description(self):
        return "Example of using a '_handoff_' property in behavior spec in order to handoff a behavior to another " \
                " widget."


    def get_example_display(self):

        div = DivWdg()

        # --- Example of using _handoff_ property in behavior -----------------------------------------------------

        table = Table()
        table.add_row()
        td = table.add_cell()
        td.set_style( "background: #0f0f0f; color: #9f9f9f; border: 1px solid black; padding: 4px;" )
        td_id = 'HandOffSource'
        td.set_id(td_id)
        td.add( "Element '%s' with '_handoff_' property in bvr spec" % td_id )
        td.add_behavior( {
                '_handoff_': '$(@.parentNode).getElement("#HandOffTarget")',

                'type': 'click',
                'cbfn_action': 'spt.ui_play.test_handoff',
                'dst_el': '$(@.parentNode).getElement("#DestElForBvr");'
            } )

        td = table.add_cell()
        td.set_style( "background: #2f2f2f; color: #9f9f9f; border: 1px solid black; padding: 4px; cursor: pointer;" )
        td_id = 'HandOffTarget'
        td.set_id(td_id)
        td.add( "Element '%s' that receives the handed off behavior" % td_id );

        td = table.add_cell()
        td.set_style( "background: #4f4f4f; color: #9f9f9f; border: 1px solid black; padding: 4px;" )
        td_id = 'DestElForBvr'
        td.set_id(td_id)
        td.add( "Element '%s' specified as dst_el for handed off behavior" % td_id );
        div.add( table )

        return div

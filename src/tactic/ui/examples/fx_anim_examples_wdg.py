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
__all__ = ["SptFxSliderExampleWdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from tactic.ui.activator import ButtonForDropdownMenuWdg, AttachContextMenuWdg

from base_example_wdg import BaseExampleWdg


class SptFxSliderExampleWdg(BaseExampleWdg):

    def get_example_title(my):
        return "SPT Fx Slider Example"


    def get_example_description(my):
        return "Example of using an SPT Fx Slider (vs. a MooTools Fx Slider). The SPT Fx Slider can adapt to " \
                "dynamically changing dimensions of its content, where the MooTools Fx Slider cannot. Currently still " \
                "some clunkiness in the SPT Fx Slider -- needs some refinement to be able to be used more extensively."


    def get_example_display(my):

        div = DivWdg()

        # --- Example of new spt.fx animation slider --------------------------------------------------------------

        slide_div = DivWdg()
        slide_div.set_id( "ui_play_sliding_thing" )
        slide_div.set_style( "background: #9f9f9f; color: #0f0f0f; border: 1px solid black;" )
        slide_div.add( "For a moment after Mr. and Mrs. Darling left the house the night-lights by the beds of the three children continued to burn clearly. They were awfully nice little night-lights, and one cannot help wishing that they could have kept awake to see Peter; but Wendy&#39;s light blinked and gave such a yawn that the other two yawned also, and before they could close their mouths all the three went out. There was another light in the room now, a thousand times brighter than the night-lights, and in the time we have taken to say this, it had been in all the drawers in the nursery, looking for Peter&#39;s shadow, rummaged the wardrobe and turned every pocket inside out. It was not really a light; it made this light by flashing about so quickly, but when it came to rest for a second you saw it was a fairy, no longer than your hand, but still growing. It was a girl called Tinker Bell exquisitely gowned in a skeleton leaf, cut low and square, through which her figure could be seen to the best advantage. She was slightly inclined to embonpoint." )

        div.add( slide_div )

        div.add( '<br/>' )
        click_slide = DivWdg()
        click_slide.add( "Click Me to Slide!" )
        click_slide.set_style( "background: #0f0f0f; color: #9f9f9f; border: 1px solid black; width: 100px; " \
                               "cursor: pointer;" )

        click_slide.add_behavior( { 'type': 'click_up',
                                    'dst_el': 'ui_play_sliding_thing',
                                    'cbfn_action': 'spt.fx.slide_anim_cbk',
                                    'options': { 'direction': 'vertical',
                                                 'duration': 500,  # time in milliseconds
                                                 'frame_rate': 15   # frames per second
                                                }
                                    } )

        div.add( click_slide )
        return div



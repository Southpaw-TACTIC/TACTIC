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
__all__ = ["PanningScrollExampleWdg"]

from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table, WebContainer
from pyasm.widget import SelectWdg, WidgetConfig, IconWdg

from base_example_wdg import BaseExampleWdg



class PanningScrollExampleWdg(BaseExampleWdg):

    def get_example_title(self):
        return "Use of Drag Behavior For Panning Scroll"


    def get_example_description(self):
        return "Example of Panning Scroll using drag behavior (use ALT+LMB to pan inner div below) ..."


    def get_example_display(self):

        scroll_div = DivWdg()

        scroll_div.add_style( "width: 150px" )
        scroll_div.add_style( "height: 80px" )
        scroll_div.add_style( "background: #880000" )
        scroll_div.add_style( "border: 2px solid #111111" )
        scroll_div.add_style( "overflow: hidden" )

        lots_of_text = '''
TACTIC is an asset and production management system for managing productions and their assets. It can be used by one user&#44; or by hundreds. Task management and asset management can often be a daunting task in productions. Managing the relationships between these items takes effort&#44; and there can be many oportunities for things to get lost or overlooked. TACTIC takes care of managing these relationships between assets and tasks. It creates a clean and easy-to-manage readable filesystem where users only need to check out and check in their assets. They do not need to worry about where a file goes&#44; what it&#39;s called&#44; or if it&#39;s being versioned correctly. The TACTIC architecture allows asset management to be possible in just about any production environment. For new productions&#44; TACTIC provides predefined&#44; ready-to-use 3D and Flash production modules out of the box. Existing productions can build their project from the ground up to manage their specific types of processes and files using a custom TACTIC project. 
How Does TACTIC Work? TACTIC provides a simple system of containers (also called "search types"). The type of production asset being managed determines the type of search type required. A search type is added to the system for every production asset (which in TACTIC terms is called an "SObject")&#44; so the SObject can be managed when it is checked out and back in. Production management is made possible when a pipeline (a set of production processes) is associated with the SObject&#44; denoting which departments it needs to flow through to get to the finish line. In the predefined project modules&#44; search types also provide built-in handling for different file types&#44; and in some cases deep integration with the production software. This may allow users to use the TACTIC interface to check out and open files directly into their production environment (for example&#44; XSI&#44; Maya&#44; Houdini or Flash)&#44; and then save them and check them back in one step. 
        '''
        sd_contents_div = DivWdg()
        sd_contents_div.add( lots_of_text )
        sd_contents_div.add_style( "width: 500px" )
        sd_contents_div.add_style( "height: 200px" )

        sd_contents_div.add_style( "text-align: justify" )

        '''
        # original raw behavior to do panning scroll ...
        test_bvr = {
                'type': 'drag',
                'modkeys': 'ALT',
                'dst_el': '@.parentNode',
                'cbfn_setup': 'spt.mouse.panning_scroll_setup',
                'cbfn_motion': 'spt.mouse.panning_scroll_motion'
        }
        '''
        # use of implemented 'panning_scroll' behavior ...
        test_bvr = {'type': 'panning_scroll'}

        sd_contents_div.add_behavior( test_bvr )

        scroll_div.add( sd_contents_div )

        return scroll_div




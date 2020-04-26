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
__all__ = ["SwfWdg"]

import os, types

from pyasm.common import Xml, Common, Environment, Container
from pyasm.biz import Project
from pyasm.search import Search, SearchType, SearchKey, SObject
from pyasm.web import Widget, DivWdg, HtmlElement, SpanWdg, Table, FloatDivWdg, WebContainer
from pyasm.widget import SelectWdg, FilterSelectWdg, WidgetConfig, WidgetConfigView, TextWdg, ButtonWdg, CheckboxWdg, ProdIconButtonWdg, HiddenWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import LabeledHidableWdg, PopupWdg
from tactic.ui.panel import TableLayoutWdg

from action_wdg import TableActionWdg, ViewActionWdg



class SwfWdg(BaseRefreshWdg):
    '''Panel which displays a complete view, including filters, search
    and results'''

    def get_args_keys(self):
        return {
        "search_key": "The search_key of the SObject",
        "path": "path to the input file",
        "height": "height for swf",
        "width": "width of swf",



        }

    def get_display(self):

        search_key = self.kwargs.get("search_key")
        title = self.kwargs.get("title")
        swf_url = self.kwargs.get("swf_url")
        flash_vars = self.kwargs.get("flash_vars")
	title = self.kwargs.get("title")
        height = self.kwargs.get("height")
        width = self.kwargs.get("width")
        
	#Get the value for the swf id
	swf_file = swf_url.split("/")[-1]
	id = swf_file.split(".")[0]
    

        # define the top widget
        div = DivWdg()
        div.add_class("spt_view_panel")

        if not swf_url :
            return div

        div.add( search_key )
        
        swf = '''
        <object 
	    classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" 
	    codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0"
	    width="%s" 
	    height="%s" 
	    id="%s" 
	    align="middle">
            <param name="movie" value="%s" />
            <param name="quality" value="high" />
	    <param name="flashVars" value="file=%s" />
            <embed 
	        src="%s"
		flashVars="%s"
	        quality="high"
	        wmode='transparent'
	        width="%s" height="%s"
	        name="%s"
	        align="middle"
	        allowScriptAccess="sameDomain"
	        type="application/x-shockwave-flash"
	        pluginspage="http://www.macromedia.com/go/getflashplayer"
            />
        </object>
        ''' % (width, height, id, id, flash_vars, swf_url, flash_vars, width, height, id)

	swfDiv = DivWdg( swf )
	div.add( swfDiv )

        return div




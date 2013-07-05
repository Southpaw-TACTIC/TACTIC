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

__all__ = ['BinTableElementWdg', 'ThumbPublishWdg', 'InstancePublishWdg']

from pyasm.biz import SObjectInstance
from pyasm.search import Search, SearchType
from pyasm.web import Widget, HtmlElement, DivWdg, WebContainer
from pyasm.widget import BaseTableElementWdg, ThumbWdg, PublishLinkWdg, IconButtonWdg, IconWdg


class BinTableElementWdg(BaseTableElementWdg):
    ''' a wdg that shows bin type and bin code '''
    def get_title(my):
        return "Bin"

    def get_simple_display(my):
        return my.get_display()



    def get_display(my):

        sobject = my.get_current_sobject()

        bins = sobject.get_bins()
        widget = Widget()
        bins_str = ", ".join( ["%s" % bin.get_label() for bin in bins] )
        widget.add( bins_str )
        return widget

    def get_simple_display(my):
        return my.get_display()


class ThumbPublishWdg(ThumbWdg):
    ''' A ThumbWdg with a publish link '''
    
    def get_display(my):
        widget = Widget()
        
        thumb = super(ThumbPublishWdg, my).get_display()

        widget.add(thumb)
        sobject = my.get_current_sobject()
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()

        publish_link = PublishLinkWdg(search_type,search_id) 
        div = DivWdg(publish_link)
        div.set_style('clear: left; padding-top: 6px')
        widget.add(div)

        # build an iframe to show publish browsing
        browse_link = IconButtonWdg("Publish Browser", IconWdg.CONTENTS)
        iframe = WebContainer.get_iframe()
        iframe.set_width(100)

        url = WebContainer.get_web().get_widget_url()
        url.set_option("widget", "pyasm.prod.web.PublishBrowserWdg")
        url.set_option("search_type", search_type)
        url.set_option("search_id", search_id)
        script = iframe.get_on_script(url.to_string())
        browse_link.add_event("onclick", script)

        div.add(browse_link)
        div.set_style('padding-top: 6px')


        return widget




class InstancePublishWdg(BaseTableElementWdg):

    def get_display(my):

        sobject = my.get_current_sobject()
        instances = SObjectInstance.get_by_sobject(sobject, "prod/asset")

        widget = Widget()
        for instance in instances:
            thumb = ThumbPublishWdg()
            thumb.set_icon_size(60)
            thumb.set_sobject(instance)
            widget.add( "<b>%s</b>" % instance.get_value("asset_code") )
            widget.add(thumb)
            widget.add(HtmlElement.br(clear="all"))

        return widget

        
        


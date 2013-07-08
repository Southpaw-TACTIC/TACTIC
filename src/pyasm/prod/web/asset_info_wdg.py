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

__all__ = ['AssetInfoWdg', 'CondensedAssetInfoWdg', 'ShotInfoWdg', 'CondensedShotInfoWdg', 'SubmissionInfoWdg', 'GeneralInfoWdg']

from pyasm.web import *
from pyasm.widget import BaseTableElementWdg, ExpandableTextWdg, PublishLinkWdg, ThumbWdg

from frame_info_wdg import FrameRangeWdg


class AssetInfoWdg(BaseTableElementWdg):
    '''widget to display the code, name and description in one column'''

    def init(my):
        my.thumb = None

    def get_display(my):
        my.sobject = my.get_current_sobject()
        custom_css = my.get_option('css')

    
        table = Table(css='embed')
        if custom_css:
            table.add_class(custom_css)
        table.add_style("width: 200px")
        table.add_col(css='large')
        table.add_col()
        table.add_color('color','color')
        my._add_code(table)
        my._add_name(table)
        my._add_description(table)
    
        return table

    def get_simple_display(my):
        sobject = my.get_current_sobject()
        code = sobject.get_code()
        name = sobject.get_name()
        description = sobject.get_value("description")
        return "%s, %s, %s" % (code, name, description)

    
    def _add_code(my, table):
        table.add_row()
        table.add_cell(HtmlElement.i("Code:"))
        table.add_cell( "<b>%s</b>" % my.sobject.get_code() )

    def _add_name(my, table):
        name = my.sobject.get_value("name", no_exception=True)
        if not name:
            return
        
        table.add_row()
        table.add_cell("<i>Name:</i>")
        table.add_cell( my.sobject.get_value("name") )

    def _add_description(my, table):
        table.add_row()
        table.add_cell("<i>Description:</i>")
        expand = ExpandableTextWdg()
        expand.set_id('asset_info_desc')
        description = my.sobject.get_value("description", no_exception=True)
        expand.set_value( WikiUtil().convert(description) )
        expand.set_max_length(240) 
        table.add_cell( expand )


class CondensedAssetInfoWdg(AssetInfoWdg):
    '''widget to display the code, name and description in one column'''

    def get_display(my):
        my.sobject = my.get_current_sobject()
        custom_css = my.get_option('css')
    
        div = DivWdg(css=custom_css)
        div.add_color('color','color')
        div.add_style('width', '18em')

        code_span = SpanWdg('%s <i>%s</i>' \
            %(my.sobject.get_code(), my.sobject.get_value('name')))
        
        expand = ExpandableTextWdg()
        expand.set_id('asset_info_desc')
        description = my.sobject.get_value("description")
        expand.set_value( WikiUtil().convert(description) )
        desc_span = SpanWdg('Desc: ')
        desc_span.add(expand)
        div.add(code_span)
        div.add(HtmlElement.br())
        div.add(desc_span)
        
    
        return div


class ShotInfoWdg(AssetInfoWdg):
    '''widget to display the code, name and description in one column'''


    def preprocess(my):
        my.thumb = ThumbWdg()
        my.thumb.set_icon_size('60')
        my.thumb.set_sobjects(my.sobjects)
        my.thumb.preprocess()


    def get_display(my):
        if not my.thumb:
            my.preprocess()
        
        my.sobject = my.get_current_sobject()

        table = Table(css='embed')
        table.add_color('color','color')
        table.add_style("width: 300px")
        table.add_row()

        th = table.add_header("<i>Code: </i> <b style='font-size: 1.2em'>%s</b>" % my.sobject.get_code() )
        # add status
        th.add_style('text-align','left')
        status_span = SpanWdg("", css='large')
        th.add(status_span)

        status = my.sobject.get_value("status")
        if status:
            status_span.add(my.sobject.get_value("status"))
        
        table.add_row()
        
        my.thumb.set_current_index(my.get_current_index())
        thumb_td = table.add_cell(my.thumb)
        row_span = 2
       
        if my.sobject.has_value("priority"):
            row_span = 3
            # add priority
            table.add_cell("<i>Priority: </i>")
            priority = my.sobject.get_value("priority")
            if not priority:
                table.add_cell("None")
            else:
                table.add_cell(my.sobject.get_value("priority") )
            # this row should be added only if priority is added
            table.add_row()
        
        thumb_td.set_attr('rowspan', row_span) 

        # add pipeline
        table.add_cell("<i>Pipeline: </i>")
        status = my.sobject.get_value("pipeline_code")
        if not status:
            table.add_cell("None")
        else:
            table.add_cell(my.sobject.get_value("pipeline_code") )

        my._add_frame_range(table)

        table.add_row()
        td = table.add_cell( "<i>Description: </i>")
        description = my.sobject.get_value("description")
        expand = ExpandableTextWdg()
        expand.set_id('asset_info_desc')
        expand.set_value( WikiUtil().convert(description) )
        expand.set_max_length(300) 
        td.add(expand)

        main_div = DivWdg(table)
        
        if my.get_option("publish") == "false":
            return main_div
            
        #my._add_publish_link(main_div)

        return main_div


    def get_simple_display(my):
        sobject = my.get_current_sobject()
        code = sobject.get_code()
        description = sobject.get_value("description")
        status = sobject.get_value("status")
        return "%s, %s, %s" % (code, status, description)



    def _add_frame_range(my, table):

        frame_wdg = FrameRangeWdg()
        frame_wdg.set_sobject(my.sobject)
        table.add_row()
        table.add_cell("<i>Frame Info:</i>")
        table.add_cell( frame_wdg )

    def _add_publish_link(my, main_div):
        publish_link = PublishLinkWdg(my.sobject.get_search_type(), my.sobject.get_id())
        div = DivWdg(publish_link)
        div.add_style('padding-top','5px')
        main_div.add(div)


        # build an iframe to show publish browsing
        search_type = my.sobject.get_search_type()
        search_id = my.sobject.get_id()
        from pyasm.widget import IconButtonWdg, IconWdg
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



class CondensedShotInfoWdg(ShotInfoWdg):
    '''widget to display the code, name and description in one column'''

    def get_display(my):
        my.sobject = my.get_current_sobject()
        custom_css = my.get_option('css')
    
        div = DivWdg(css=custom_css)
        div.add_color('color','color')
        div.add_style('width', '18em')

        code_span = SpanWdg('%s' % (my.sobject.get_code()))
        
        expand = ExpandableTextWdg()
        expand.set_id('shot_info_desc')
        description = my.sobject.get_value("description")
        expand.set_value( WikiUtil().convert(description) )
        desc_span = SpanWdg()
        desc_span.add(expand)
        div.add(code_span)
        div.add(HtmlElement.br())
        div.add(desc_span)
        
    
        return div




class SubmissionInfoWdg(AssetInfoWdg):
    '''widget information about a submission in a condensed manner'''

    def preprocess(my):
        my.thumb = ThumbWdg()
        my.thumb.set_sobjects(my.sobjects)
        my.thumb.preprocess()


    def get_display(my):
        
        my.sobject = my.get_current_sobject()

        table = Table(css='embed')
        table.add_style("width: 300px")
        table.add_color('color','color')
        table.add_row()
        td = table.add_cell("<i>Code: </i> <b style='font-size: 1.2em'>%s</b>" % my.sobject.get_code() )
        td.add_style("background: #e0e0e0")
        table.add_row()

        my.thumb.set_current_index(my.get_current_index())
        table.add_cell(my.thumb)

        table2 = Table(css='embed')
        table2.add_row()
        table2.add_cell("<i>Status: </i>")
        status = my.sobject.get_value("status")
        if not status:
            table2.add_cell("<i style='color: #c0c0c0'>None</i>")
        else:
            table2.add_cell(my.sobject.get_value("status") )

        my._add_frame_range(table2)
        table.add_cell( table2 )

        table.add_row()
        td = table.add_cell( "<i>Description: </i>")

        description = my.sobject.get_value("description")
        #td.add(WikiUtil().convert(description))

        expand = ExpandableTextWdg()
        expand.set_id('asset_info_desc')
        expand.set_value( WikiUtil().convert(description) )
        expand.set_max_length(300) 
        td.add(expand)

        return table

class GeneralInfoWdg(AssetInfoWdg):
    '''widget to display the code, name and description in one column'''

    def get_display(my):
        my.sobject = my.get_current_sobject()
        custom_css = my.get_option('css')
    
        table = Table(css='embed')
        table.add_color('color','color')
        if custom_css:
            table.add_class(custom_css)
        table.add_style("width: 200px")
        table.add_col(css='large')
        table.add_col()
        my._add_code(table)
        my._add_description(table)


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

    def init(self):
        self.thumb = None

    def get_display(self):
        self.sobject = self.get_current_sobject()
        custom_css = self.get_option('css')

    
        table = Table(css='embed')
        if custom_css:
            table.add_class(custom_css)
        table.add_style("width: 200px")
        table.add_col(css='large')
        table.add_col()
        table.add_color('color','color')
        self._add_code(table)
        self._add_name(table)
        self._add_description(table)
    
        return table

    def get_simple_display(self):
        sobject = self.get_current_sobject()
        code = sobject.get_code()
        name = sobject.get_name()
        description = sobject.get_value("description")
        return "%s, %s, %s" % (code, name, description)

    
    def _add_code(self, table):
        table.add_row()
        table.add_cell(HtmlElement.i("Code:"))
        table.add_cell( "<b>%s</b>" % self.sobject.get_code() )

    def _add_name(self, table):
        name = self.sobject.get_value("name", no_exception=True)
        if not name:
            return
        
        table.add_row()
        table.add_cell("<i>Name:</i>")
        table.add_cell( self.sobject.get_value("name") )

    def _add_description(self, table):
        table.add_row()
        table.add_cell("<i>Description:</i>")
        expand = ExpandableTextWdg()
        expand.set_id('asset_info_desc')
        description = self.sobject.get_value("description", no_exception=True)
        expand.set_value( WikiUtil().convert(description) )
        expand.set_max_length(240) 
        table.add_cell( expand )


class CondensedAssetInfoWdg(AssetInfoWdg):
    '''widget to display the code, name and description in one column'''

    def get_display(self):
        self.sobject = self.get_current_sobject()
        custom_css = self.get_option('css')
    
        div = DivWdg(css=custom_css)
        div.add_color('color','color')
        div.add_style('width', '18em')

        code_span = SpanWdg('%s <i>%s</i>' \
            %(self.sobject.get_code(), self.sobject.get_value('name')))
        
        expand = ExpandableTextWdg()
        expand.set_id('asset_info_desc')
        description = self.sobject.get_value("description")
        expand.set_value( WikiUtil().convert(description) )
        desc_span = SpanWdg('Desc: ')
        desc_span.add(expand)
        div.add(code_span)
        div.add(HtmlElement.br())
        div.add(desc_span)
        
    
        return div


class ShotInfoWdg(AssetInfoWdg):
    '''widget to display the code, name and description in one column'''


    def preprocess(self):
        self.thumb = ThumbWdg()
        self.thumb.set_icon_size('60')
        self.thumb.set_sobjects(self.sobjects)
        self.thumb.preprocess()


    def get_display(self):
        if not self.thumb:
            self.preprocess()
        
        self.sobject = self.get_current_sobject()

        table = Table(css='embed')
        table.add_color('color','color')
        table.add_style("width: 300px")
        table.add_row()

        th = table.add_header("<i>Code: </i> <b style='font-size: 1.2em'>%s</b>" % self.sobject.get_code() )
        # add status
        th.add_style('text-align','left')
        status_span = SpanWdg("", css='large')
        th.add(status_span)

        status = self.sobject.get_value("status")
        if status:
            status_span.add(self.sobject.get_value("status"))
        
        table.add_row()
        
        self.thumb.set_current_index(self.get_current_index())
        thumb_td = table.add_cell(self.thumb)
        row_span = 2
       
        if self.sobject.has_value("priority"):
            row_span = 3
            # add priority
            table.add_cell("<i>Priority: </i>")
            priority = self.sobject.get_value("priority")
            if not priority:
                table.add_cell("None")
            else:
                table.add_cell(self.sobject.get_value("priority") )
            # this row should be added only if priority is added
            table.add_row()
        
        thumb_td.set_attr('rowspan', row_span) 

        # add pipeline
        table.add_cell("<i>Pipeline: </i>")
        status = self.sobject.get_value("pipeline_code")
        if not status:
            table.add_cell("None")
        else:
            table.add_cell(self.sobject.get_value("pipeline_code") )

        self._add_frame_range(table)

        table.add_row()
        td = table.add_cell( "<i>Description: </i>")
        description = self.sobject.get_value("description")
        expand = ExpandableTextWdg()
        expand.set_id('asset_info_desc')
        expand.set_value( WikiUtil().convert(description) )
        expand.set_max_length(300) 
        td.add(expand)

        main_div = DivWdg(table)
        
        if self.get_option("publish") == "false":
            return main_div
            
        #self._add_publish_link(main_div)

        return main_div


    def get_simple_display(self):
        sobject = self.get_current_sobject()
        code = sobject.get_code()
        description = sobject.get_value("description")
        status = sobject.get_value("status")
        return "%s, %s, %s" % (code, status, description)



    def _add_frame_range(self, table):

        frame_wdg = FrameRangeWdg()
        frame_wdg.set_sobject(self.sobject)
        table.add_row()
        table.add_cell("<i>Frame Info:</i>")
        table.add_cell( frame_wdg )

    def _add_publish_link(self, main_div):
        publish_link = PublishLinkWdg(self.sobject.get_search_type(), self.sobject.get_id())
        div = DivWdg(publish_link)
        div.add_style('padding-top','5px')
        main_div.add(div)


        # build an iframe to show publish browsing
        search_type = self.sobject.get_search_type()
        search_id = self.sobject.get_id()
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

    def get_display(self):
        self.sobject = self.get_current_sobject()
        custom_css = self.get_option('css')
    
        div = DivWdg(css=custom_css)
        div.add_color('color','color')
        div.add_style('width', '18em')

        code_span = SpanWdg('%s' % (self.sobject.get_code()))
        
        expand = ExpandableTextWdg()
        expand.set_id('shot_info_desc')
        description = self.sobject.get_value("description")
        expand.set_value( WikiUtil().convert(description) )
        desc_span = SpanWdg()
        desc_span.add(expand)
        div.add(code_span)
        div.add(HtmlElement.br())
        div.add(desc_span)
        
    
        return div




class SubmissionInfoWdg(AssetInfoWdg):
    '''widget information about a submission in a condensed manner'''

    def preprocess(self):
        self.thumb = ThumbWdg()
        self.thumb.set_sobjects(self.sobjects)
        self.thumb.preprocess()


    def get_display(self):
        
        self.sobject = self.get_current_sobject()

        table = Table(css='embed')
        table.add_style("width: 300px")
        table.add_color('color','color')
        table.add_row()
        td = table.add_cell("<i>Code: </i> <b style='font-size: 1.2em'>%s</b>" % self.sobject.get_code() )
        td.add_style("background: #e0e0e0")
        table.add_row()

        self.thumb.set_current_index(self.get_current_index())
        table.add_cell(self.thumb)

        table2 = Table(css='embed')
        table2.add_row()
        table2.add_cell("<i>Status: </i>")
        status = self.sobject.get_value("status")
        if not status:
            table2.add_cell("<i style='color: #c0c0c0'>None</i>")
        else:
            table2.add_cell(self.sobject.get_value("status") )

        self._add_frame_range(table2)
        table.add_cell( table2 )

        table.add_row()
        td = table.add_cell( "<i>Description: </i>")

        description = self.sobject.get_value("description")
        #td.add(WikiUtil().convert(description))

        expand = ExpandableTextWdg()
        expand.set_id('asset_info_desc')
        expand.set_value( WikiUtil().convert(description) )
        expand.set_max_length(300) 
        td.add(expand)

        return table

class GeneralInfoWdg(AssetInfoWdg):
    '''widget to display the code, name and description in one column'''

    def get_display(self):
        self.sobject = self.get_current_sobject()
        custom_css = self.get_option('css')
    
        table = Table(css='embed')
        table.add_color('color','color')
        if custom_css:
            table.add_class(custom_css)
        table.add_style("width: 200px")
        table.add_col(css='large')
        table.add_col()
        self._add_code(table)
        self._add_description(table)


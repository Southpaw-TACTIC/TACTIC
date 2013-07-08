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

__all__ = ['IFrameLink', 'FrameInfoWdg', 'FrameRangeWdg','BackPlateInfoWdg']

from pyasm.common import Container, Xml
from pyasm.search import Search
from pyasm.web import Widget, WebContainer, SpanWdg, DivWdg, FloatDivWdg, HtmlElement, WidgetException, WikiUtil
from pyasm.prod.biz import Render, Shot
from pyasm.widget import BaseTableElementWdg, IconWdg, IconButtonWdg, TableWdg, HintWdg
from pyasm.biz import Snapshot, File, FileGroup

import os


from version_history_wdg import *


class IFrameLink(BaseTableElementWdg):

    def get_display(my):

        sobject = my.get_current_sobject()

        widget_class = my.get_option("class")
        
        if widget_class == '':
            raise WidgetException("No widget class defined")

        url = WebContainer.get_web().get_widget_url()
        url.set_option("widget", widget_class)
        url.set_option("search_key", sobject.get_search_key())

        ref = url.get_url()

        iframe = Container.get("iframe")
        iframe.set_width(90)
        action = iframe.get_on_script(ref)

        info_type = my.get_option("info_type")
        
        button = IconButtonWdg("%s info" % info_type, IconWdg.INFO)
        button.add_event("onclick", "%s" % (action) )
        button.add_style("margin: 3px 5px")

        return button



class FrameInfoWdg(Widget):

    def get_display(my):

        web = WebContainer.get_web()
        search_key = web.get_form_value("search_key")

        widget = Widget()

        sobject = Search.get_by_search_key(search_key)

        table = TableWdg( sobject.get_search_type(), "render" )
        table.set_sobject(sobject)
        widget.add(table)



        # get all of the snapshots with a context render
        sobject_snapshot = Snapshot.get_latest_by_sobject(sobject,"render")
        if sobject_snapshot:
            search_type = sobject.get_search_type()
            search_id = sobject.get_value('search_id')
            
            render_snapshots = Snapshot.get_by_search_type(search_type,search_id,"render")

            table = TableWdg("sthpw/snapshot")
            table.set_sobjects(render_snapshots)
            widget.add(table)



        widget.add(HtmlElement.h3("Rendered Frames"))
        if sobject_snapshot:
            widget.add("Render version: v%0.3d" % sobject_snapshot.get_value("version") )

        # get latest snapshot of the render
        renders = Render.get_all_by_sobject(sobject)
        if not renders:
            widget.add("<h4>No renders found</h4>")
            return widget

        render = renders[0]
        snapshot = Snapshot.get_latest_by_sobject(render,"render")
        if snapshot == None:
            widget.add("<h4>No snapshots found</h4>")
            return widget


        # get the images
        web_dir = snapshot.get_web_dir()
        lib_dir = snapshot.get_lib_dir()

        xml = snapshot.get_xml_value("snapshot")
        file_nodes = xml.get_nodes("snapshot/file")
        file_name = icon_file_name = ''
        frame_range = icon_frame_range = None
        
        for file_node in file_nodes: 
            if Xml.get_attribute(file_node, 'type') == 'main':
                file_name, frame_range = my._get_frame_info(file_node, sobject)
            if Xml.get_attribute(file_node, 'type') == 'icon':
                icon_file_name, icon_frame_range = my._get_frame_info(file_node, sobject)
            
        file_names = [file_name]
        icon_file_names = [icon_file_name]        

        if "##" in file_name:
            file_names = FileGroup.expand_paths(file_name, frame_range)
        if "##" in icon_file_name:
            icon_file_names = FileGroup.expand_paths(icon_file_name, \
                icon_frame_range)    
        
        div = DivWdg()
        for k in range(len(file_names)):
            file_name = file_names[k]

            # ignore frames that don't exist
            lib_path = "%s/%s" % (lib_dir, file_name)
            if not os.path.exists(lib_path):
                continue
           
            try:
                icon_file_name = icon_file_names[k]
            except IndexError:
                icon_file_name = file_names[k]
                
            file_path = "%s/%s" % (web_dir, file_name)
            icon_file_path = "%s/%s" % (web_dir, icon_file_name)
            
            img = HtmlElement.img(icon_file_path)
            img.set_attr("width", "60")
            img.add_event("onmouseover","hint_bubble.show(event,'Ctrl + Click to open in new window')")

            href = HtmlElement.href(img, file_path)
            div.add(href)

        widget.add(div)

        widget.add( "<h3>Render History</h3>" )
        widget.add( my.get_render_history(renders) )

        return widget

    def _get_frame_info(my, file_node, sobject):
        '''get the full file name and frame range'''
        file_name = Snapshot._get_file_name(file_node)
        frame_range = sobject.get_frame_range()

        return file_name, frame_range

    def get_render_history(my, renders):
        table = TableWdg("prod/render", "history")
        table.set_sobjects( renders )
        return table








class FrameRangeWdg(BaseTableElementWdg):
    '''widget that displays a simple frame range'''

    def get_title(my):
        widget = Widget()
        widget.add("Frame Range")
        
        return widget

    def get_simple_display(my):
        sobject = my.get_current_sobject()
        start = sobject.get_frame_start()
        end = sobject.get_frame_end()
        range = "%s - %s" % (start, end)
        frame_in, frame_out = sobject.get_frame_handles()
        
        inout = "%s - %s" % (frame_in, frame_out)
        return '%s<br/>(%s)' %(range, inout)

    def _get_frame_num(my, sobject, attr):
        if not sobject.has_value(attr):
            return 0
        frame_start = sobject.get_value(attr)
        try:
            return int(frame_start)
        except ValueError, e:
            return 1     
    
    def _get_frame_handles(my, sobject):
        frame_in = sobject.get_value("frame_in", no_exception=True)
        frame_out = sobject.get_value("frame_out", no_exception=True)
        if frame_in:
            frame_in = int(frame_in)
        else:
            frame_in = 0
        if frame_out:
            frame_out = int(frame_out)
        else:
            frame_out = 0
        return frame_in, frame_out

    def get_text_value(my):
        sobject = my.get_current_sobject()
        if isinstance(sobject, Shot):
            frame_range = sobject.get_frame_range()
            frame_start = frame_range.frame_start
            frame_end = frame_range.frame_end
            frame_in, frame_out = sobject.get_frame_handles()
        else:
            from pyasm.prod.biz import FrameRange
            frame_start = my._get_frame_num(sobject, "tc_frame_start")
            frame_end = my._get_frame_num(sobject, "tc_frame_end")
            frame_range = FrameRange(frame_start, frame_end, 1 )
            frame_in, frame_out = my._get_frame_handles(sobject)

        if frame_range.frame_end == frame_range.frame_start == 0:
            return 'n/a'
   
        total = frame_range.frame_end - frame_range.frame_start + 1
        result = '%s - %s (%s)' % (frame_start, frame_end, total)

        if frame_in:
            handle_total = frame_out - frame_in + 1
            result += ', %s - %s (%s)' % (frame_in, frame_out, handle_total)

        return result

    def get_display(my):
        sobject = my.get_current_sobject()
        if isinstance(sobject, Shot):
            frame_range = sobject.get_frame_range()
            frame_in, frame_out = sobject.get_frame_handles()
            frame_notes = sobject.get_frame_notes()
        else:
            from pyasm.prod.biz import FrameRange
            frame_start = my._get_frame_num(sobject, "tc_frame_start")
            frame_end = my._get_frame_num(sobject, "tc_frame_end")
            frame_range = FrameRange(frame_start, frame_end, 1 )
            frame_in, frame_out = my._get_frame_handles(sobject)
            frame_notes = sobject.get_value("frame_note", no_exception=True)
        
        frame_notes = WikiUtil().convert(frame_notes)    
        if frame_range.frame_end == frame_range.frame_start == 0:
            return 'n/a'

        widget = SpanWdg()
        widget.set_attr("nowrap", "1")

        offset = 2
        label_width = 16
        if frame_range.frame_start > 99:
            label_width = 20
        # start / end frame
        duration_color = '#969353'
        div = DivWdg()
        div.add_tip('START -- END (TOTAL)')
        wdg_width = 100
        div.add_style('width', wdg_width)
        
        total = frame_range.frame_end - frame_range.frame_start + 1
        start_frame = SpanWdg(str(frame_range.frame_start), css='small smaller')
        end_frame = SpanWdg(str(frame_range.frame_end), css='small smaller')

        end_div = FloatDivWdg(end_frame)

        duration_width = wdg_width * 0.2 - offset

        spacer_width = float('%.2f' %((duration_width + offset) * (frame_range.frame_start -1 ) /\
                frame_range.frame_end))

        start_div = FloatDivWdg(start_frame, width= label_width+spacer_width )
        start_div.add_class('right_content')
        duration = FloatDivWdg( width=duration_width )
        duration.add_style("border: 1px dotted %s" % duration_color)
        duration.add_style("margin-top: 3px")
        duration.add_style("height: 3px")
        duration.add_style("line-height: 3px")
        div.add(start_div)
        div.add(duration)
        div.add(end_div)
        dur_text = FloatDivWdg('(%s)' %total, css='smaller')
        div.add(dur_text)
        widget.add(div)
        widget.add(HtmlElement.br())
        if frame_in:
            # in / out frame
            duration_color = '#b8b365'
            div = DivWdg()
            div.add_tip('IN -- OUT')
            div.add_style('width', wdg_width)
            
            handle_total = frame_out - frame_in + 1
            in_frame = SpanWdg(str(frame_in), css='small smaller')
            out_frame = SpanWdg(str(frame_out), css='small smaller')
           
            if frame_range.frame_start == 0:
                frame_range.frame_start = 0.001

            spacer_width = float('%.2f' % ((spacer_width) * \
                float(frame_in) /frame_range.frame_start )) 

            in_div = FloatDivWdg(in_frame, width=label_width + spacer_width)
            in_div.add_class('right_content')
            out_div = FloatDivWdg(out_frame)

            factor =  float(handle_total) / total
            if factor > 1:
                factor = 1
            duration_width = (duration_width + offset) * factor - offset
            duration = FloatDivWdg( width=duration_width )
            duration.add_style("border: 1px solid %s" % duration_color)
            duration.add_style("background", duration_color)
            duration.add_style("margin-top: 5px")
            duration.add_style("line-height: 1px")
            duration.add('&nbsp;')
            
            # IE needs that to draw a 1px wide div
            bar = FloatDivWdg('<!-- -->', width=1)
            bar.add_style("margin-top: 1px")
            bar.add_style("height: 10px")
            bar.add_style("line-height: 10px")
            bar.add_style("background", duration_color)
            div.add(in_div)
            div.add(bar)
            div.add(duration)
            div.add(bar)
            div.add(out_div)
            

            dur_text = SpanWdg('(%s)' %handle_total, css='smaller')
            div.add(dur_text)
            widget.add(div)
      
        if frame_notes:
            widget.add(HtmlElement.br())
            widget.add(frame_notes)

        return widget






class BackPlateInfoWdg(FrameInfoWdg):

    def get_display(my):

        web = WebContainer.get_web()
        search_key = web.get_form_value("search_key")

        widget = Widget()

        sobject = Search.get_by_search_key(search_key)

        # get all of the snapshots with a context render
        sobject_snapshot = Snapshot.get_latest_by_sobject(sobject,"backplate")

        widget.add(HtmlElement.h3("BackPlate Frames"))
        if not sobject_snapshot:
            widget.add("No backplates checked in")
            return widget

        # get the images
        web_dir = sobject_snapshot.get_web_dir()

        xml = sobject_snapshot.get_xml_value("snapshot")
        file_nodes = xml.get_nodes("snapshot/file")
        file_name = icon_file_name = ''
        frame_range = icon_frame_range = None
        
        for file_node in file_nodes: 
            if Xml.get_attribute(file_node, 'type') == 'main':
                file_name, frame_range = my._get_frame_info(file_node, sobject)
            if Xml.get_attribute(file_node, 'type') == 'icon':
                icon_file_name, icon_frame_range = my._get_frame_info(file_node, sobject)
            
        file_names = [file_name]
        icon_file_names = [icon_file_name]        

        if "##" in file_name:
            file_names = FileGroup.expand_paths(file_name, frame_range)
        if "##" in icon_file_name:
            icon_file_names = FileGroup.expand_paths(icon_file_name, \
                icon_frame_range)    
        
        div = DivWdg()
        for k in range(len(file_names)):
            file_name = file_names[k]
            
            try:
                icon_file_name = icon_file_names[k]
            except IndexError:
                icon_file_name = file_names[k]
                
            file_path = "%s/%s" % (web_dir, file_name)
            icon_file_path = "%s/%s" % (web_dir, icon_file_name)
            
            img = HtmlElement.img(icon_file_path)
            img.add_event("onmouseover","hint_bubble.show(event,'Ctrl + Click to open in new window')")

            href = HtmlElement.href(img, file_path)
            div.add("%0.4d" % (k+1))
            div.add(href)

            if k != 0 and (k+1) % 4 == 0:
                div.add("<br/>")
                div.add("<br/>")

        widget.add(div)

        return widget



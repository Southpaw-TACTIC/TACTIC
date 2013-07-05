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

__all__ = ['DependencyLink', 'DependencyWdg']

from pyasm.common import Xml, TacticException, Container
from pyasm.biz import File, FileGroup, FileRange, Snapshot, Project, SObjectNotFoundException
from pyasm.search import Search
from pyasm.web import Widget, WebContainer, HtmlElement, DivWdg, SpanWdg, FloatDivWdg

from table_element_wdg import FunctionalTableElement
from icon_wdg import IconButtonWdg, IconWdg
from file_wdg import ThumbWdg
from web_wdg import SwapDisplayWdg
from tactic.ui.common import BaseRefreshWdg

import os, re

class DependencyLink(FunctionalTableElement):

    def get_display(my):

        sobject = my.get_current_sobject()
        search_type = sobject.get_search_type()
        search_id = sobject.get_id()

        
        button = IconButtonWdg("Dependency", IconWdg.DEPENDENCY)
        
        button.add_style("margin: 3px 5px")

        # view doesn't matter
        behavior = my.get_edit_behavior('pyasm.widget.DependencyWdg', search_type, \
            search_id)
        button.add_behavior(behavior)

        return button

    def get_edit_behavior(my, class_name, search_type, search_id, view=''):
        '''get the default edit behavior'''
        behavior = {
            "type": "click_up",
            "cbfn_action": "spt.popup.get_widget",
            "options": {
                "title": "Dependency: %s" % search_type,
                "class_name": class_name, "popup_id": 'dependency_popup'
            },
            "args": {
                "search_type": search_type,
                "search_id": search_id,
                "view": view,
            }
        }
        return behavior



class DependencyWdg(BaseRefreshWdg):
    '''widget that follows a snapshot's dependencies and prints them out'''
    MAX_NODE_LENGTH = 100
    def init(my):
        my.show_title = True
        my.mode = my.kwargs.get('mode')

    def set_show_title(my, flag):
        my.show_title = flag


    def get_display(my):
        
        if my.mode == 'detail':
            upstream = True
            div = DivWdg()
            my.snapshot_code = my.kwargs.get('snapshot_code')
            ref_snapshot = Snapshot.get_by_code(my.snapshot_code)
            my._handle_snapshot(ref_snapshot, div, upstream, recursive=False)
            return div


        my.web = WebContainer.get_web()

        if my.sobjects:
            snapshot = my.sobjects[0]
        else:
            search_type = my.kwargs.get("search_type")
            search_id = my.kwargs.get("search_id")

            snapshot = None
            if search_type == Snapshot.SEARCH_TYPE:
                snapshot = Search.get_by_id(search_type, search_id)
            else:
                snapshot = Snapshot.get_latest(search_type, search_id)
        if not snapshot:
            my.add(HtmlElement.h3("No snapshot found"))
            return super(DependencyWdg,my).get_display()



        widget = DivWdg()
        widget.add_style('min-width: 700px')
        
      
        if my.show_title:
            my.add(HtmlElement.h3("Asset Dependency"))

        from tactic.ui.panel import TableLayoutWdg
        table = TableLayoutWdg(search_type="sthpw/snapshot", mode='simple', view='table', width='700px')
        table.add_style('min-width: 700px')
        table.set_sobject(snapshot)
        widget.add(table)


        sobject = snapshot.get_sobject()
        search_type_obj = sobject.get_search_type_obj()

        #file_div = DivWdg(css='left_content discussion_child')
        file_div = DivWdg()
        file_div.add_color("background", "background", -20)
        file_div.add_color("color", "color")
        file_div.add_style("padding: 5px")
        file_div.add_border()




        #file_div.add_style('margin','0 10px 0 10px')
        file_div.add_style('padding','10px 0 0 10px')
        #file_div.add_style('-moz-border-radius: 6px')
        title = DivWdg()
        title.add_style("font-weight: bold")
        title.add_style("font-size: 1.2em")
        #title.add_style('margin-left', '10px')

        if my.show_title:
            title.add(search_type_obj.get_title() )
            title.add(" - ")
            title.add(sobject.get_code() )
            if sobject.has_value("description"):
                title.add(" : ")
                title.add(sobject.get_value("description") )

            file_div.add(title)
            file_div.add(HtmlElement.br())

        # find out how many 1st level ref nodes we are dealing with
        xml = snapshot.get_xml_value("snapshot")
        
        #my.total_ref_count = len(xml.get_nodes("snapshot/file/ref | snapshot/ref |snapshot/input_ref| snapshot/fref"))

        my._handle_snapshot(snapshot, file_div, upstream=True, recursive=True )
        my._handle_snapshot(snapshot, file_div,  upstream=False, recursive=True )

        #widget.add(widget)
        widget.add(file_div)
        widget.add(HtmlElement.br(2))

        #return super(DependencyWdg,my).get_display()
        return widget


    def _handle_snapshot(my, snapshot, widget, upstream, recursive=True):
        ''' handle the files and refs in this snapshot '''
       
 
        if upstream:
            my._handle_files(snapshot, widget, upstream, recursive)
        # handle the refs in this snapshot
        my._handle_refs(snapshot, widget, upstream, recursive)

       
        return len(widget.widgets)

    def _handle_files(my, snapshot, widget, upstream, recursive=True):

        web_dir = snapshot.get_web_dir()
        xml = snapshot.get_xml_value("snapshot")

        # handle files
        files = xml.get_nodes("snapshot/file")
        for file in files:
            
            file_code = Xml.get_attribute(file, "file_code")
            file_type = Xml.get_attribute(file, "type")
            file_range = Xml.get_attribute(file, "file_range")
            #file_range = "1-4/1"

            dir = snapshot.get_client_lib_dir(file_type=file_type)
            lib_dir = snapshot.get_lib_dir(file_type=file_type)
            open_button = IconButtonWdg( "Explore: %s" % dir, IconWdg.LOAD, False)
            if dir == lib_dir:
                open_button.add_behavior({'type':'click_up', 'cbjs_action': '''var applet = spt.Applet.get();
                                       
                                            spt.alert('You are not allowed to browse directories on a web server.');
                                    '''})
            else:
                open_button.add_behavior({'type':'click_up', 
                                        'dir' : dir,
                                        'cbjs_action': '''
                                        var applet = spt.Applet.get();
                                        
                                        var dir = bvr.dir;
                                      
                                        applet.open_explorer(dir);'''})
            open_button.add_class('small')
            open_button.add_style('float: left')
            widget.add(open_button)

            if file_range:
                file_name = Xml.get_attribute(file, "name")
                widget.add("%s [code = %s, type = %s]" % (file_name, file_code, file_type))
                widget.add(HtmlElement.br(2))

                # display all of the paths
                file_names = FileGroup.expand_paths( file_name, FileRange.get(file_range) )
                for file_name in file_names:
                    #link = HtmlElement.href(file_name, "%s/%s" % (web_dir, file_name), target="_blank" )
                    link = SpanWdg(file_name)
                    link.add_color("color", "color")
                    widget.add(link)
                    widget.add(HtmlElement.br())

            else:
                thumb = DependencyThumbWdg()
                thumb.set_show_filename(True)
                thumb.set_sobject(snapshot)
                thumb.set_icon_size(15)
                thumb.set_image_link_order([file_type])
                thumb.set_option('detail', 'false')

                widget.add(SpanWdg(thumb, css='small'))
                widget.add("[code = %s, type = %s]" % ( file_code, file_type))

            widget.add(HtmlElement.br())
            

            block = DivWdg()
            block.add_style("margin-left: 30px")
            block.add_style("margin-top: 10px")
            nodes = xml.get_nodes("snapshot/file[@file_code='%s']/ref" % file_code)
            widget.add(HtmlElement.br(clear="all"))
            # handle sub refs
            for node in nodes:
                my._handle_ref_node(node, block, upstream, recursive)
                block.add(HtmlElement.br())
            if nodes:
                widget.add(block)

            widget.add(HtmlElement.br())



        files = xml.get_nodes("snapshot/unknown_ref")
        if files:
            widget.add(HtmlElement.b("Unknown ref."))
        for file in files:
            block = DivWdg()
            block.add_style("margin-left: 30px")
            block.add_style("margin-top: 10px")

            block.add( IconWdg( "Unknown", IconWdg.UNKNOWN) )

            path = Xml.get_attribute(file, "path")
            block.add(path)
            widget.add(block)



    def _handle_refs(my, snapshot, widget, upstream, recursive=True):

        xml = snapshot.get_xml_value("snapshot")
        
        # go through the references
        if upstream:
            nodes = xml.get_nodes("snapshot/ref")
            if nodes:
                widget.add(HtmlElement.b('Upstream ref.'))
                block = DivWdg()
                
                block.add_style("margin-left: 30px")
                block.add_style("margin-top: 10px")
                for node in nodes:
                    my._handle_ref_node(node, block, upstream, recursive)
                    block.add(HtmlElement.br())
                widget.add(block)
               

            # go through the input references
            nodes = xml.get_nodes("snapshot/input_ref")
            if nodes:
                widget.add(HtmlElement.br())
                widget.add(HtmlElement.b("Input ref."))
                block = DivWdg()
                block.add_style("margin-left: 30px")
                block.add_style("margin-top: 10px")
                for node in nodes:
                    my._handle_ref_node(node, block, upstream, recursive)
                widget.add(block)
    
        else:
            # go through the forward references
            nodes = xml.get_nodes("snapshot/fref")
            if nodes:
                widget.add(HtmlElement.b("Downstream ref."))
                block = DivWdg()
                block.add_style("margin-left: 30px")
                block.add_style("margin-top: 10px")
                for node in nodes:
                    my._handle_ref_node(node, block, upstream, recursive)
                widget.add(block)



    def _handle_ref_node(my, node, widget, upstream=False, recursive=True):

        # get the reference snapshot (should maybe use the loader or
        # at least share the code
        instance = Xml.get_attribute(node,"instance")
        search_type = Xml.get_attribute(node,"search_type")
        search_id = Xml.get_attribute(node,"search_id")
        context = Xml.get_attribute(node,"context")
        version = Xml.get_attribute(node,"version")
        # this is often the Maya file node name or XSI long clip name
        node_name = Xml.get_attribute(node, "node")
        my_name = Xml.get_node_name(node)

        # get the snapshot
        ref_snapshot = Snapshot.get_by_version(search_type, search_id,\
                    context, version)
        #ref_snapshot = Snapshot.get_latest(search_type,search_id, context)
        if ref_snapshot == None:
            widget.add("|---> <font color='red'>Error: No reference found for [%s, %s, %s]</font>" % \
                (search_type, search_id, context) )
            return

        toggle_id = my.generate_unique_id('toggle')
        widget.add(FloatDivWdg(), toggle_id)
        version = ref_snapshot.get_value("version")

        
        try: 
            sobject = ref_snapshot.get_sobject()
        except SObjectNotFoundException, e:
            widget.add('[%s|%s] may have been deleted or is not viewable.' % (ref_snapshot.get_value('search_type'),\
                ref_snapshot.get_value('search_id')))
            return
        search_type_obj = sobject.get_search_type_obj()

        # this is the top level icon usually
        thumb_span = SpanWdg()
        thumb_span.add_style("float: left")
        
        thumb = ThumbWdg()
        thumb.set_sobject(ref_snapshot)
        thumb.set_icon_size(15)

        # for input_ref, just get the latest icon
        if my_name == 'ref':
            thumb.set_version(version)

        # this has to be a FloatDivWdg
        widget.add(FloatDivWdg(thumb))
        
        info_div = DivWdg()
        info_span = SpanWdg(css='med')
        info_span.add_color("color", "color")
        info_div.add(info_span)
        widget.add(info_div)
        info_span.add(HtmlElement.b(search_type_obj.get_title()) )

        widget.add("&nbsp;&nbsp;")

        if instance != "":
            info_span.add(" : ")
            info_span.add( instance )

        info_span.add(" : ")
        info_span.add(sobject.get_code() )

        if sobject.has_value("description"):
            info_span.add(" : ")
            info_span.add(sobject.get_value("description") )

        info_span.add( " : %s" % (context) )
        info_span.add( " : v%0.2d " % (int(version)) )

        if ref_snapshot.is_current():
            info_span.add( IconWdg("Currency", IconWdg.DOT_GREEN) )
        else:
            info_span.add( IconWdg("Currency", IconWdg.DOT_RED) )
        
        #if not recursive:
        #    return

        # input ref may not have node_name
        if node_name:
            node_name_len = len(node_name)
            suffix = ''
            if node_name_len > my.MAX_NODE_LENGTH:
                node_name_len = my.MAX_NODE_LENGTH
                suffix = '...'
            node_data = "<b>node</b> : %s %s" % (node_name[:node_name_len], suffix)
            node_span = SpanWdg(node_data)
            node_span.add_style('padding-left: 22px')
            widget.add(node_span)
        
        widget.add(HtmlElement.br())
        # more info of this ref node is put into this div
        div_id = 'toggle_content_%s' % toggle_id
        div = DivWdg(id=div_id)
        div.add_style('display: none')
        swap = SwapDisplayWdg.get_triangle_wdg()
        swap.add_style('float: left')
        div.add_style('margin: 0 20px 0 20px')
        div.add(HtmlElement.br()) 
       
        # stop the recursion after this around
        if recursive:
            recursive = False
        else:
            return
       
        # set up the toggle scripts
        title = None
        SwapDisplayWdg.create_swap_title(title, swap, div)
        swap.get_on_widget().add_behavior({'type': 'click_up', 
            'cbjs_action': 
            "spt.panel.load('%s', 'pyasm.widget.DependencyWdg', {'mode':'detail', \
            'snapshot_code': '%s'}, {}, false)" %(div_id, ref_snapshot.get_code())})
       
        widget.add(HtmlElement.br()) 
        widget.set_widget(swap, toggle_id)
        widget.add(div)
        
        """ 
        # set recursive to False here to keep it simple for now 
        widget_len = my._handle_snapshot(ref_snapshot, div, upstream, recursive=False)
        # add the toggle swap on if there are contents in the content div
        if widget_len:
            widget.set_widget(swap, toggle_id)
            widget.add_style("margin-left: 12px")
            widget.add(HtmlElement.br()) 
            widget.add(div)
        """
        
            



class DependencyThumbWdg(ThumbWdg):

    def set_text_link(my, widget, div, image_link):
        '''override how the text link is drawn'''
        div.add_style('float', 'left')
        div.add_style('margin-left', '10px')
        filename = os.path.basename(image_link)
        if len(filename) > 40:
            filename = "%s..." % (filename[0:40])

        span = SpanWdg(css='med')
        #href = HtmlElement.href(filename, image_link)
        href = SpanWdg(filename)
        href.add_color("color", "color")
        span.add(href)
        widget.add(span)
        span.add_tip('Right-click and choose [Save Link As..] to save to disk.')


    def get_icon_info(my, image_link, repo_path=None, icon_type='icon'):
        icon_size = my.get_icon_size()
        
        p = re.compile(r'.*(\.jpg|\.png|\.tif)$')
        if p.match(image_link) and my.info.has_key(icon_type):
            icon_link = my.info.get('icon')
        else:
            icon_link = ThumbWdg.find_icon_link(image_link)
        
        if image_link.endswith(".pdf"):
            icon_size = int( 80.0 / 120.0 * float(icon_size) )

        return icon_link, icon_size


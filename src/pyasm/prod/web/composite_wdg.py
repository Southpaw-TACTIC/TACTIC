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

__all__ = ['LayerTableElementWdg', 'CompLayerTableElementWdg', 'ExploreTableElementWdg']

from pyasm.common import Container
from pyasm.web import DivWdg, Table, HtmlElement, SpanWdg, Widget
from pyasm.widget import IconButtonWdg, IconWdg, GeneralAppletWdg
from pyasm.biz import Snapshot
from pyasm.prod.biz import Render, Shot, Layer

from tactic.ui.common import BaseTableElementWdg

class LayerTableElementWdg(BaseTableElementWdg):

    def get_title(self):
        widget = Widget()

        if not Container.get('GeneralAppletWdg'):
            widget.add( GeneralAppletWdg() )
            Container.put('GeneralAppletWdg', True)
        widget.add(super(LayerTableElementWdg, self).get_title())
        return widget

    def get_display(self):
        sobject = self.get_current_sobject()


        # this is a comp object ... need to find the shot
        if not isinstance(sobject, Shot) :
            shot = sobject.get_parent("prod/shot")
        else:
            shot = sobject

        # now get all of the layers
        layers = shot.get_all_children("prod/layer")
        div = DivWdg()
    
        #div.set_style('width: 100px; overflow": auto')
        table = Table(css='embed')

        table.add_row()
        table.add_cell( shot.get_code() )

        render = Render.get_last(shot)
        if not render:
            table.add_cell("<i>No renders</i>")
        else:
            render = Snapshot.get_current_by_sobject(render)
            table.add_cell( self.get_open_wdg(render) )
            dir = render.get_web_dir()
            table.add_cell( "<i>%s</i>" % dir )


        for layer in layers:
            table.add_row()
            table.add_cell( layer.get_value("name") )

            render = Render.get_last(layer)
            if render:
                render = Snapshot.get_current_by_sobject(render)
            if not render:
                table.add_cell("<i>No renders</i>")
            else:
                table.add_cell( self.get_open_wdg(render) )
                dir = render.get_client_lib_dir()
                table.add_cell( "<i>%s</i>" % dir )


        div.add(table)
        return div

    def get_open_wdg( sobject, file_type=None):
        ''' given a snapshot. open the sandbox in explorer '''

        span = SpanWdg()

        # explore button
        dir = sobject.get_client_lib_dir(file_type=file_type)
        open_button = IconButtonWdg( "Explore: %s" % dir, IconWdg.LOAD, False)
        open_button.add_event("onclick", "Applet.open_explorer('%s')" % dir)
        open_button.add_class('small')
        span.add(open_button)

        #dir = sobject.get_sandbox_dir()
        #copy_button = IconButtonWdg( "Copy to sandbox: %s" % dir, IconWdg.DOWNLOAD, False)
        #span.add(copy_button)

        return span
    get_open_wdg = staticmethod(get_open_wdg)


class CompLayerTableElementWdg(LayerTableElementWdg):

    def get_display(self):
        sobject = self.get_current_sobject()

        

        context = self.kwargs.get('context')
        if not context:
            context = "publish"
            
        snapshot = Snapshot.get_latest_by_sobject(sobject, context)
        if not snapshot:
            return "Nothing checked in"
        xml = snapshot.get_xml_value("snapshot")
        print xml.to_string()


        # this is a comp object ... need to find the shot
        shot = sobject.get_parent("prod/shot")

        # now get all of the layers
        layers = shot.get_all_children("prod/layer")




        div = DivWdg()

        table = Table(css='embed')

        # get the renders for each of the references in the snapshot
        #ref_nodes = xml.get_nodes("snapshot/file/ref")
        ref_nodes = xml.get_nodes("snapshot/input_ref")
        unknown_ref_nodes = xml.get_nodes("snapshot/unknown_ref")
        if ref_nodes:
            table.add_row_cell('Ref:')
            
            self.draw_node(ref_nodes, table)
        if unknown_ref_nodes:
            table.add_row_cell('Unknown Ref:')
            for node in unknown_ref_nodes:
                table.add_row()
                table.add_cell(xml.get_attribute(node, 'path'))

        div.add(table)
        return div

    def draw_node(self, ref_nodes, table):
        if not ref_nodes:
            return
        
        for ref_node in ref_nodes:
            snapshot = Snapshot.get_ref_snapshot_by_node(ref_node, mode='latest')
            if not snapshot:
                print "Snapshot for ref_node does not exist"
                continue

            render = snapshot.get_parent()
            table.add_row()


            parent = render.get_parent()
            table.add_cell( parent.get_name() )

            table.add_cell( self.get_open_wdg(render) )

            dir = render.get_client_lib_dir()
            table.add_cell( "<i>%s</i>" % dir )


        

class ExploreTableElementWdg(LayerTableElementWdg):

    def get_display(self):
        sobject = self.get_current_sobject()

        snapshots = []
        if isinstance(sobject, Layer):
            # for layer renders, we try to get all render sobjects
            renders = Render.get_all_by_sobject(sobject)
            if renders:
                snapshots = Snapshot.get_by_sobjects(renders, is_current=True)
        else: # for object that has direct snapshots like plates
            snapshot = Snapshot.get_current_by_sobject(sobject)
            if snapshot:
                snapshots.append(snapshot)

        if not snapshots:
            return "<i>- no files -</i>"

        div = DivWdg()

        for snapshot in snapshots:
            file_types = snapshot.get_all_file_types()
            table = Table(css='embed')

            for file_type in file_types:
                table.add_row()
                
                table.add_cell( self.get_open_wdg(snapshot, file_type) )
                dir = snapshot.get_client_lib_dir(file_type=file_type)
                
                
                table.add_cell( "%s: <i>%s</i>" % (file_type, dir) )
         

            div.add(table)
        return div

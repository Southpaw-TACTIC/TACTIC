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

__all__ = ['SessionWdg']

from pyasm.biz import Snapshot
from pyasm.web import Widget, Table, DivWdg
from pyasm.prod.biz import SessionContents
from pyasm.widget import ThumbWdg
from pyasm.prod.web import LatestVersionContextWdg
from tactic.ui.common import BaseRefreshWdg
from loader_wdg import IntrospectWdg

class SessionWdg(BaseRefreshWdg):
    
    def init(self):
        super(SessionWdg, self).init()
        self.is_refresh = self.kwargs.get('is_refresh') =='true'
  
    def get_display(self):

        self.is_refresh = self.kwargs.get('is_refresh') =='true'
      
        if not self.is_refresh:
            top = DivWdg(css='spt_view_panel')
            self.set_as_panel(top)
        else:
            top = Widget() 

        div = DivWdg(css="filter_box")
        div.add("<b>Current Session</b>")
        top.add(div)

        # the button which initiates the introspection
        button = IntrospectWdg()
        #button.add_style("float", "right")
        top.add(button)

        top.add("<br clear='all'/>")


        session = SessionContents.get()
        if not session:
            widget.add("<h3>No contents in session</h3>")
            return widget

        table = Table()
        table.add_class("table")
        table.add_style("width: 100%")
        table.add_row()
        table.add_header("&nbsp;")
        table.add_header("Type")
        table.add_header("Asset")
        table.add_header("Node Name")
        table.add_header("Node Type")
        table.add_header("Reference")
        table.add_header("Session")
        table.add_header("Latest")

        node_names = session.get_node_names()
        for node_name in node_names:
            table.add_row()


            # snapshot_code
            snapshot_code = session.get_snapshot_code(node_name, "shot")
            if not snapshot_code:
                snapshot_code = session.get_snapshot_code(node_name, "anim")
            if not snapshot_code:
                snapshot_code = session.get_snapshot_code(node_name, "asset")

            snapshot = Snapshot.get_by_code(snapshot_code)
            sobject = None

            if snapshot:

                sobject = snapshot.get_sobject()
                base = sobject.get_search_type_obj().get_base_search_type()

                thumb = ThumbWdg()
                thumb.set_icon_size(60)

                # FIXME: make this more automatic
                if base == "prod/shot_instance":
                    thumb_sobj = sobject.get_parent("prod/asset")
                    thumb.set_sobject(thumb_sobj)
                else:
                    thumb.set_sobject(sobject)

                table.add_cell(thumb)

                title = sobject.get_search_type_obj().get_title()
                table.add_cell( title )

                # TODO: this should be more automatic!
                if base == "prod/shot_instance":
                    asset_code = sobject.get_value("asset_code")
                    shot_code = sobject.get_value("shot_code")
                    name = sobject.get_value("name")
                    table.add_cell("%s: %s in %s" % (name,asset_code,shot_code))
                else:
                    code = sobject.get_code()
                    name = sobject.get_name()
                    if code == name:
                        table.add_cell( "%s" % (code) )
                    else:
                        table.add_cell( "%s - %s" % (code, name) )

            else:
                table.add_cell("<i>No snapshot</i>")
                table.add_cell("---")
                table.add_cell("---")
                

            # display the node name
            table.add_cell(node_name)

            # display node type
            table.add_cell( session.get_node_type(node_name) )


            # display if it is a reference
            is_reference = session.is_reference(node_name)
            if is_reference:
                table.add_cell( "Yes" )
            else:
                table.add_cell( "No" )


            if snapshot:
                # add the snapshot info
                context = snapshot.get_value("context")
                version = snapshot.get_value("version")
                table.add_cell( "%s v%0.2d" % (context, version))
            else:
                table.add_cell("---")

            table.add_cell( self.get_version_wdg(session,snapshot,node_name) )

        top.add(table)
        return top       



    def get_version_wdg(self, session, snapshot, node_name):

        if not snapshot:
            return "---"

        session_context = snapshot.get_value("context")
        session_version = snapshot.get_value("version")

        # get the latest
        latest = Snapshot.get_latest_by_sobject(snapshot.get_sobject(),session_context)
        latest_context = latest.get_value("context")
        latest_version = latest.get_value("version")


        version_wdg = LatestVersionContextWdg()
        data = {'session_version': session_version, \
            'session_context': session_context,  \
            'latest_context': latest_context, \
            'latest_version': latest_version }
        version_wdg.set_options(data)
    
        return version_wdg




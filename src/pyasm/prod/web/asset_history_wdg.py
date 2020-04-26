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

# TODO: this class is poorly named.  It should be AssetHistoryLoadWdg


__all__ = ['AssetHistoryWdg', 'ShotHistoryWdg', 'InstanceHistoryWdg', 'LayerHistoryWdg']

from pyasm.search import Search
from pyasm.web import *
from pyasm.widget import *
from pyasm.prod.biz import *
from pyasm.biz import *
from pyasm.common import Common
from asset_loader_wdg import *


from tactic.ui.common import BaseRefreshWdg
class AssetHistoryWdg(BaseRefreshWdg):
    '''history that includes the loader'''
    CB_NAME = 'load_snapshot'
    def init(self):
        self.parent_key = self.kwargs.get("search_key")
        if not self.parent_key:
            self.parent_key = WebContainer.get_web().get_form_value('search_key')
    
        self.parent = Search.get_by_search_key(self.parent_key)
        self.search_type = self.parent.get_search_type()
        self.base_search_type = Project.extract_base_search_type(self.search_type)

        self.search_id = self.parent.get_id()
        self.asset_search_type = self.kwargs.get('asset_search_type')

    
    def _get_value(self, sobject, snapshot):
        loader = AssetLoaderWdg(parent_key=self.parent_key)
        value = loader.get_input_value(sobject, snapshot)
        return value

    def get_default_versions_filter(self):
        return "last 10"


    def get_snapshot_search(self):
        search = Search(Snapshot.SEARCH_TYPE)
        search.add_filter("search_type", self.search_type)
        search.add_filter("search_id", self.search_id)
        return search

    def get_snapshot_contexts(self, search_type, search_id):
        '''get the contexts for the snapshots'''
        return Snapshot.get_contexts(search_type, search_id)


    def get_master_checkbox(self, select):
        '''turn them all off first, then turn on the one for the selected context'''
        master = SpanWdg(css='med')
       
        master.add_color("color", "color")

        cb_name = '%s_%s' %(self.base_search_type, self.CB_NAME)
        value = select.get_value()
        if value:
            master_cb = CheckboxWdg('master_control', label='Toggle all current [%s]' %value)
            master_cb.add_behavior({'type': 'click_up',
                'propagate_evt': True,
                'cbjs_action': '''
                    var context_sel = bvr.src_el.getParent('.spt_history_wdg').getElement('.spt_context_select')
                    var filter = '.spt_history_' + context_sel.value;
                    var inputs = spt.api.Utility.get_inputs(bvr.src_el.getParent('.spt_table'),'%s','.spt_history');
                    for (var i = 0; i < inputs.length; i++)
                        inputs[i].checked = false;
                    var inputs = spt.api.Utility.get_inputs(bvr.src_el.getParent('.spt_table'),'%s', filter);
                    for (var i = 0; i < inputs.length; i++)
                        inputs[i].checked = bvr.src_el.checked;
                        ''' %(cb_name, cb_name)})
            master.add(master_cb)
        return master

    def get_display(self):
        
        web = WebContainer.get_web()
        args = web.get_form_args()

        if not self.search_type:
            self.search_type = args.get('search_type')
        if not self.search_id:
            self.search_id = args.get('search_id')
        # get from cgi
        if not self.search_type:
            self.search_type = web.get_form_value("search_type")
            self.search_id = web.get_form_value("search_id")
        if not self.asset_search_type:
            self.asset_search_type = web.get_form_value('asset_search_type')




        context_filter = web.get_form_value("context_%s_%s" % (self.search_type, self.search_id) )
        versions_filter = web.get_form_value("versions_%s_%s" % (self.search_type, self.search_id) )

        div_id = "history_%s_%s" % (self.search_type, self.search_id)
        ajax = AjaxLoader(div_id)
        if ajax.is_refresh():
            div = Widget()
        else:
            div = DivWdg()
            div.add_color('background','background2')
            div.add_class('spt_history_wdg')
            div.add_style("display: block")
            div.add_style("float: right")
            div.add_style("width: 95%")
            div.add_style("margin-left: 50px") 
            div.set_id( div_id )

        div.add( self.get_filter_wdg(self.search_type, self.search_id, div_id) )

        # get the sobject
        sobject = Search.get_by_id(self.search_type, self.search_id)

        # get the snapshots
        search = self.get_snapshot_search()

        if context_filter:
            search.add_filter("context", context_filter)

        if not versions_filter:
            versions_filter = self.get_default_versions_filter()
            self.select.set_value(versions_filter)

        if versions_filter == 'current':
            search.add_filter("is_current", True)
        elif versions_filter == 'latest':
            search.add_filter("is_latest", True)
        elif versions_filter == 'last 10':
            search.add_limit(10)
        elif versions_filter == 'today':
            from pyasm.search import Select
            search.add_where(Select.get_interval_where(versions_filter))
        elif versions_filter == 'all':
            pass
        else:
            search.add_filter("is_latest", True)


        search.add_order_by("timestamp desc")
        snapshots = search.do_search()

        div.add(self.get_table(sobject,snapshots) )

        return div


    def get_filter_wdg(self, search_type, search_id, div_id):
        filter_wdg = DivWdg()
        filter_wdg.add_style("margin-bottom: 5px")
        filter_wdg.add_style("text-align: right")

        ajax = AjaxLoader()
        ajax.set_option("search_key", self.parent_key)
        ajax.set_option("search_type", search_type)
        if self.asset_search_type:
            ajax.set_option("asset_search_type", self.asset_search_type)
        ajax.set_option("search_id", search_id)
        ajax.add_element_name("context_%s_%s" % (search_type, search_id) )
        ajax.add_element_name("versions_%s_%s" % (search_type, search_id) )
        # add a shot id
        ajax.add_element_name("shot_id")
        ajax.set_display_id(div_id)

        cls = self.__class__
        class_path = '%s.%s' %(cls.__module__, cls.__name__)
        ajax.set_load_class( class_path )
        refresh_script = ajax.get_refresh_script(show_progress=False)


        # add a context selector
        select = SelectWdg("context_%s_%s" % (search_type, search_id) )
        select.add_class('spt_context_select')
        select.add_event("onchange", refresh_script)

        # find all of the contexts that have been checked in
        
        contexts = self.get_snapshot_contexts(search_type, search_id)
        select.set_option("values", contexts )

        select.add_empty_option("-- Select --")
        select.set_persist_on_submit()
        span = SpanWdg(css="med")
        span.add_color("color", "color")
        span.add("Context: ")
        span.add(select)
        # add the fast check checkbox that checks all current for a context
        filter_wdg.add(self.get_master_checkbox(select))
        filter_wdg.add(span)

        # add a versions selector
        self.select = SelectWdg("versions_%s_%s" % (search_type, search_id) )
        self.select.add_empty_option("-- Select --")
        self.select.add_event("onchange", refresh_script)
        self.select.set_option("values", "latest|current|today|last 10|all")
        self.select.set_persist_on_submit()
        span = SpanWdg(css="med")
        span.add_color("color", "color")
        span.add("Versions: ")
        span.add(self.select)
        filter_wdg.add(span)

        button = IconButtonWdg("Refresh", IconWdg.REFRESH, long=False)
        button.add_event("onclick", refresh_script)
        filter_wdg.add(button)


        return filter_wdg


    def get_table(self, sobject, snapshots):

        table = Table()
        table.add_color("color", "color")
        table.set_class("embed")
        table.add_style("font-size: 0.9em")

        tr = table.add_row()
        tr.add_style('text-align: left')
        table.add_header("&nbsp;")
        table.add_header("Code")
        table.add_header("Context")
        table.add_header("Ver#")
        table.add_header("Rev#")
        table.add_header("Level")
        table.add_header("Icon")
        table.add_header("Type")
        table.add_header("Dependency")
        
        table.add_header("User")
        table.add_header("Time")
        table.add_header("Comment")
        th = table.add_header("Load")
        table.add_header("&nbsp;")
        th.add_style("text-align: center")

        # get the session
        session = SessionContents.get()

        # add the file type icon
        thumb = ThumbWdg()
        thumb.set_icon_size(15)
        thumb.set_sobjects(snapshots)



        count = 0
        for snapshot in snapshots:
            current = None
            tr = table.add_row()
            tr.add_color("background", "background2")
            tr.add_color("color", "color")

            palette = tr.get_palette()
            # selection colors
            hilite = palette.color("background2", +15)
            tr.add_behavior( {
                        'type': 'hover',
                        'mod_styles': 'background-color: %s' %hilite,
                    } )
           
          
            time_wdg = DateTimeWdg()
            time_wdg.set_name("timestamp")
            time_wdg.set_sobject(snapshot)

            context = snapshot.get_value("context")
            version = snapshot.get_value("version")
            revision = snapshot.get_value("revision", no_exception=True)

            if snapshot.is_current():
                current = IconWdg("current", IconWdg.CURRENT)
                table.add_cell(current)
            else:
                table.add_blank_cell()

            #render_link = RenderLinkTableElement()
            #render_link.set_sobject(snapshot)
            #table.add_cell( render_link )
            '''
            label = snapshot.get_label()
            if label:
                try:
                    icon = IconWdg(label, eval('IconWdg.%s' %label.upper()))
                except:
                    icon = HtmlElement.b(label[0].upper())
                table.add_cell(icon)
            else:
                table.add_blank_cell()
            '''   
            table.add_cell( snapshot.get_code() )
            
            table.add_cell( "<b>%s</b>" % context )
            table.add_cell( "v%0.3d" % version )

            if revision:
                table.add_cell( "r%0.3d" % revision )
            else:
                table.add_cell( "---" )


            # add level
            level_type = snapshot.get_value("level_type")
            level_id = snapshot.get_value("level_id")
            if level_type and level_id:
                sobject = Search.get_by_id(level_type, level_id)
                table.add_cell(sobject.get_code())
            else:
                table.add_cell("---")



            thumb.set_current_index(count)
            table.add_cell(thumb.get_display())
            count += 1

            table.add_cell( snapshot.get_value("snapshot_type") )

            dependency_wdg = DependencyLink()
            dependency_wdg.set_sobject(snapshot)
            table.add_cell( dependency_wdg )

            
            
            table.add_cell( snapshot.get_value("login") )
            table.add_cell( time_wdg)
            wiki_wdg = WikiElementWdg("description")
            wiki_wdg.set_sobject(snapshot)
            table.add_cell( wiki_wdg )

            if context == "icon":
                td = table.add_cell("X")
                td.add_style("text-align: center")
                continue

            #value = "%s|%s" % (snapshot.get_code(),context)
            value = self._get_value(sobject, snapshot)


            load_checkbox = CheckboxWdg('%s_%s' %(self.base_search_type, self.CB_NAME))
            load_checkbox.add_behavior({'type': 'click_up',
            'propagate_evt': True})

            load_checkbox.set_option("value", value )
            load_checkbox.add_class('spt_history')
            if current:
                load_checkbox.add_class('spt_history_%s'%context)

            td = table.add_cell( load_checkbox )
            td.add_style("text-align: center")

            # check to see if this snapshot is in the session
            if session and session.get_node_by_snapshot(snapshot) is not None:
                table.add_cell( IconWdg(icon=IconWdg.GOOD) )
            else:
                table.add_blank_cell()

        return table

        # TODO: should eventually replace the table above with the table
        # below.  First have to make it look the same
        #div = HtmlElement.div()
        #div.add_style("float: right")
        #div.add_style("width: 95%")
        #table2 = TableWdg("sthpw/snapshot")
        #table2.set_sobjects(snapshots)
        #div.add(table2)
        #self.add(div)


class ShotHistoryWdg(AssetHistoryWdg):
    '''history that includes the loader'''

    def _get_value(self, sobject, snapshot):
        loader = ShotLoaderWdg(parent_key=self.parent_key)
        value = loader.get_input_value(sobject, snapshot)
        return value



class InstanceHistoryWdg(AssetHistoryWdg):
    '''Asset Instance History'''

    def _get_value(self, sobject, snapshot):
        loader = InstanceLoaderWdg(parent_key=self.parent_key)

        value = loader.get_input_value(sobject, snapshot)
        return value


    def get_snapshot_contexts(self, search_type, search_id):
        '''get the contexts for the snapshots'''
        contexts = Snapshot.get_contexts(search_type, search_id)

        # add all of the asset snapshots
        #self.instance_search_type = self.kwargs.get('search_type')
        instance = Search.get_by_id(search_type, search_id)
        if not self.asset_search_type:
            self.asset_search_type = 'prod/asset'
        #asset = instance.get_asset(search_type = self.asset_search_type)

        asset_code = instance.get_value("asset_code")
        asset = Search.get_by_code(self.asset_search_type, asset_code)
        if not asset:
            return contexts
        asset_id = asset.get_id()
        asset_search_type = asset.get_search_type()

        asset_contexts = Snapshot.get_contexts(asset_search_type, asset_id)
        contexts.extend(asset_contexts)
        contexts = Common.get_unique_list(contexts)
        contexts.sort()
        return contexts
        
    def get_snapshot_search(self):
        web = WebContainer.get_web()

        args = web.get_form_args()

        if not self.search_type:
            self.search_type = args.get('search_type')
            self.search_id = args.get('search_id')

        if not self.search_type:
            self.search_type = web.get_form_value("search_type")
            self.search_id = web.get_form_value("search_id")

        # add all of the asset snapshots
        #instance = ShotInstance.get_by_id(self.search_id)
        instance = Search.get_by_id(self.search_type, self.search_id)
        #asset = instance.get_asset(self.asset_search_type)
        asset_code = instance.get_value("asset_code")
        asset = Search.get_by_code(self.asset_search_type, asset_code)
        asset_search_type = ''
        asset_id = ''
        if asset: 
            asset_id = asset.get_id()
            asset_search_type = asset.get_search_type()

        snapshot_type = "sthpw/snapshot" 
        search = Search(snapshot_type)
        where = "(search_id = '%s' and search_type ='%s')" % \
            (self.search_id, self.search_type)
        
        where2 = "(search_id = '%s' and search_type ='%s')" % \
            (asset_id, asset_search_type)
        if asset_search_type and asset_id:
            search.add_where("(%s or %s)" % (where,where2) )
        else:
            search.add_where(where)
        # ignore icon checkins
        search.add_where("context != 'icon'")

        search.add_order_by("timestamp desc")
        return search




class LayerHistoryWdg(AssetHistoryWdg):

    def _get_value(self, sobject, snapshot):
        loader = LayerLoaderWdg()
        value = loader.get_input_value(sobject, snapshot)
        return value






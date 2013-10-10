###########################################################
#
# Copyright (c) 2005-2008, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#

__all__ = ['SObjectDetailWdg', 'TaskDetailWdg', 'SObjectSingleProcessDetailWdg']

from tactic.ui.common import BaseRefreshWdg

from pyasm.web import DivWdg, WebContainer, Table, WebState
from pyasm.search import Search, SearchType, SearchKey
from tactic.ui.panel import TableLayoutWdg

from pyasm.widget import ProdIconButtonWdg, IconWdg, TextWdg, ThumbWdg
from pyasm.widget import WidgetConfig, WidgetConfigView

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import TabWdg, Menu, MenuItem
from tactic.ui.tools import PipelineCanvasWdg
from tactic.ui.widget import SingleButtonWdg, IconButtonWdg


class SObjectDetailWdg(BaseRefreshWdg):
    '''Single SObject Widget'''

    def get_display(my):

        my.sobject = my.get_sobject()

        top = DivWdg()
        top.add_class("spt_detail_top")
        top.add_color("background", "background")
        top.add_color("color", "color")

        if not my.sobject:
            top.add("No SObject defined for this widget")
            return top

        if my.parent:
            my.search_type = my.parent.get_base_search_type()
            my.search_key = SearchKey.get_by_sobject(my.parent)
            top.add_attr("spt_parent_key", my.search_key) 
            my.pipeline_code = my.parent.get_value("pipeline_code", no_exception=True)
            my.full_search_type = my.parent.get_search_type()
        else:
            my.pipeline_code = my.sobject.get_value("pipeline_code", no_exception=True)
            my.search_type = my.sobject.get_base_search_type()
            my.search_key = SearchKey.get_by_sobject(my.sobject)
            my.full_search_type = my.sobject.get_search_type()

        if not my.pipeline_code:
            my.pipeline_code = 'default'


        top.add_style("text-align: left")
        my.set_as_panel(top)

        table = Table()
        #from tactic.ui.container import ResizableTableWdg
        #table = ResizableTableWdg()
        table.add_color("background", "background")
        table.add_color("color", "color")
        top.add(table)
        table.set_max_width()

        table.add_row()

        # left
        #td = table.add_cell(resize=False)
        td = table.add_cell()
        #td.add_style("padding: 10px")
        td.add_style("width: 200px")
        td.add_style("min-width: 200px")
        td.add_style("vertical-align: top")
        #td.add_border()
        #td.add_style("border-style: solid")
        #td.add_style("border-width: 1px 0 1px 1px")
        #td.add_color("border-color", "border")
        #td.add_color("background", "background", -10)


        if my.parent:
            code = my.parent.get_code()
        else:
            code = my.sobject.get_code()

        # add the tile
        title = DivWdg()
        td.add(title)
        title.add_gradient("background", "background3", 0, -10)
        title.add_style("height: 20px")
        title.add_style("padding: 4px")
        title.add_style("font-weight: bold")
        title.add_style("font-size: 1.4em")
        title.add("%s" % code)
        title.add_border()


        div = DivWdg()
        td.add(div)
        div.add_class("spt_sobject_detail_top")

        thumb_table = Table()
        div.add(thumb_table)
        thumb_table.add_row()

        thumb = ThumbWdg()

        # use a larger version for clearer display
        thumb.set_icon_type('web')
        # prefer to see the original image, then web
        thumb.set_option('image_link_order', 'main|web|.swf')
        thumb.set_option("detail", "false")
        thumb.set_option("icon_size", "100%")

        td = thumb_table.add_cell(thumb)
        td.add_style("vertical-align: top")
        td.add_style("width: 200px")
        td.add_style("padding: 20px")

        if my.parent:
            thumb.set_sobject(my.parent)
        else:
            thumb.set_sobject(my.sobject)

        sobject_info_wdg = my.get_sobject_info_wdg()
        sobject_info_wdg.add_style("width: 200px")


        td.add(sobject_info_wdg)

        if my.search_type == 'sthpw/task' and not my.parent:
            pass
        else:
            sobject_info_wdg = my.get_sobject_detail_wdg()
            td = table.add_cell()
            td.add(sobject_info_wdg)
            td.add_style("vertical-align: top")
            #td.add_color("background", "background", -10)
            td.add_style("overflow: hidden")
            #td.add_style("border-style: solid")
            #td.add_style("border-width: 1px 1px 1px 0px")
            #td.add_color("border-color", "border")


        # right
        td = table.add_cell()
        td.add_style("text-align: left")
        td.add_style("vertical-align: top")
        #td.add_color("background", "background", -10)
        td.add_class("spt_notes_wrapper")
        #td.add_border()

        # add the title
        title = DivWdg()
        td.add(title)
        title.add_gradient("background", "background3", 0, -10)
        title.add_style("height: 20px")
        title.add_style("padding: 4px")
        title.add_style("font-weight: bold")
        title.add("Notes")
        title.add_border()

        notes_div = DivWdg()
        td.add(notes_div)
        from tactic.ui.widget.discussion_wdg import DiscussionWdg
        discussion_wdg = DiscussionWdg(search_key=my.search_key, context_hidden=False, show_note_expand=False)
        notes_div.add(discussion_wdg)
        notes_div.add_style("min-width: 300px")
        notes_div.add_style("height: 200")
        notes_div.add_style("overflow-y: auto")
        notes_div.add_class("spt_resizable")



        # get the process
        if my.parent:
            process = my.sobject.get_value("process")
        else:
            process = ''



        # content
        tr = table.add_row()
        td = table.add_cell()
        td.add_attr("colspan", "5")
        #td.add_attr("colspan", "3")

        # create a state for tab.  The tab only passes a search key
        # parent key
        search_key = SearchKey.get_by_sobject(my.sobject)
        parent = my.sobject.get_parent()
        if parent:
            parent_key = parent.get_search_key()
        else:
            parent_key = ""

        state = {
            'search_key': search_key,
            'parent_key': parent_key,
            'process': process,
        }
        WebState.get().push(state)


        config_xml = my.get_config_xml()
        config = WidgetConfig.get(view="tab", xml=config_xml)


        if process:
            custom_view = "tab_config_%s" % process
        else:
            custom_view = "tab_config"
        search = Search("config/widget_config")
        search.add_filter("category", "TabWdg")
        search.add_filter("search_type", my.search_type)
        search.add_filter("view", custom_view)
        custom_config_sobj = search.get_sobject()
        if custom_config_sobj:
            custom_config_xml = custom_config_sobj.get_value("config")
            custom_config = WidgetConfig.get(view=custom_view, xml=custom_config_xml)
            config = WidgetConfigView(search_type='TabWdg', view=custom_view, configs=[custom_config, config])

        #menu = my.get_extra_menu()
        #tab = TabWdg(config=config, state=state, extra_menu=menu)
        tab = TabWdg(config=config, state=state, show_add=False, show_remove=False, tab_offset=5 )
        tab.add_style("margin: 0px -2px -2px -2px")
        td.add(tab)
        td.add_style("padding-top: 10px")

        return top




    def get_extra_menu(my):

        menu = Menu(width=180)
        menu.set_allow_icons(False)

        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Edit Tab Config')
        menu_item.add_behavior( {
        'cbjs_action': '''
        var activator = spt.smenu.get_activator(bvr);
        spt.tab.top = activator.getParent(".spt_tab_top");
        var element_name = 'edit_tab_config';
        var title = 'Edit Tab Config';
        var class_name = 'tactic.ui.manager.ViewManagerWdg';
        var kwargs = {
            search_type: 'prod/asset',
            view: 'tab_config_model'
        }
        spt.tab.add_new(element_name, title, class_name, kwargs);

        '''
        } )
        menu.add(menu_item)


        return menu



    def get_config_xml(my):
        if my.kwargs.get("use_parent") in [True, 'true']:
            search_key = my.sobject.get_search_key()
        else:
            search_key = my.kwargs.get("search_key")
        search_key = search_key.replace("&", "&amp;")

        config_xml = '''
        <config>
        <tab>
        <!--
        <element name="notes">
          <display class='tactic.ui.widget.discussion_wdg.DiscussionWdg'>
            <search_key>%s</search_key>
            <note_format>full</note_format>
          </display>
        </element>
        -->
        <element name="snapshots" title="Check-in History">
          <display class='tactic.ui.panel.ViewPanelWdg'>
            <search_type>sthpw/snapshot</search_type>
            <view>table</view>
            <parent_key>%s</parent_key>
            <width>100%%</width>
          </display>
        </element>
        <element name="tasks">
          <display class='tactic.ui.panel.ViewPanelWdg'>
            <search_type>sthpw/task</search_type>
            <view>table</view>
            <parent_key>%s</parent_key>
            <width>100%%</width>
          </display>
        </element>
        <element name="checkin" title="Checkin">
          <display class='tactic.ui.widget.CheckinWdg'>
            <search_key>%s</search_key>
          </display>
        </element>

        <element name="edit" title="Edit">
          <display class='tactic.ui.panel.EditWdg'>
            <search_key>%s</search_key>
            <view>edit</view>
          </display>
        </element>

        <element name="pipeline" title="Pipeline">
          <display class='tactic.ui.tools.TaskDetailPipelineWrapperWdg'>
            <search_key>%s</search_key>
            <pipeline>%s</pipeline>
          </display>
        </element>
 

        </tab>
        </config>
        ''' % (search_key, search_key, search_key, search_key, search_key, search_key, my.pipeline_code)
        return config_xml


    def get_sobject(my):

        search_key = my.kwargs.get("search_key")
        child_key = my.kwargs.get("child_key")

        if child_key:
            child = Search.get_by_search_key(child_key)
            sobject = child.get_parent()
            my.kwargs["search_key"] = sobject.get_search_key()
        else:
            sobject = Search.get_by_search_key(search_key)

        use_parent = my.kwargs.get("use_parent")
        if use_parent in [True, 'true']:
            sobject = sobject.get_parent()

        my.parent = None

        return sobject


    def get_sobject_info(my):
        titles = ['Code', 'Name', 'Description']
        exprs = []
        exprs.append( "@GET(.code)")
        exprs.append( "@GET(.name)")

        return titles, exprs


    def get_sobject_info_wdg(my):
        div = DivWdg()
        return div

        attr_table = Table()
        div.add(attr_table)

        attr_table.add_color("color", "color")

        sobject = my.get_sobject()

        titles, exprs = my.get_sobject_info()
        for title, expr in zip(titles, exprs):
            try:
                value = Search.eval(expr, sobject)
            except Exception, e:
                print "WARNING: ", e.message
                continue


            if value == '':
                value = '<i>none</i>'
            if len(value) > 100:
                value = "%s..." % value[:100]

            attr_table.add_row()
            th = attr_table.add_header("%s: " % title)
            th.add_style("text-align: left")
            td = attr_table.add_cell(value)

        #return attr_table
        return div


    def get_sobject_detail_wdg(my):
        div = DivWdg()
        #div.add_style("float: right")
        div.add_style("width: 100%")
        div.add_style("height: 100%")
        div.add_style("padding-top: 5px")


        """
        button_div.add_class("spt_left")
        div.add(button_div)
        button = IconButtonWdg(title="Show More Details", icon=IconWdg.RIGHT)
        button_div.add(button)
        button_div.add_style("position: absolute")
        button_div.add_style("margin-left: -30px")
        button_div.add_style("margin-top: -2px")
        button_div.add_style("display: none")

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_detail_top");
        var detail = top.getElement(".spt_sobject_detail");
        spt.toggle_show_hide(detail);
        var left = top.getElement(".spt_left");
        spt.hide(left);
        var right = top.getElement(".spt_right");
        spt.show(right);
        '''
        } )


        button_div = DivWdg()
        button_div.add_class("spt_right")
        div.add(button_div)
        button = IconButtonWdg(title="Show More Details", icon=IconWdg.LEFT)
        button_div.add(button)
        button_div.add_style("position: absolute")
        button_div.add_style("margin-left: -30px")
        button_div.add_style("margin-top: -2px")
        #button_div.add_style("display: none")

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_detail_top");
        var detail = top.getElement(".spt_sobject_detail");
        spt.toggle_show_hide(detail);
        var left = top.getElement(".spt_left");
        spt.show(left);
        var right = top.getElement(".spt_right");
        spt.hide(right);
        '''
        } )
        """



        info_div = DivWdg()
        div.add( info_div )
        #info_div.add_style("display: none")
        info_div.add_class("spt_sobject_detail")
        #info_div.add_style("width: 300px")
        info_div.add_style("padding: 30px 0px 30px 0px")

        info_table = Table()
        info_table.add_color("color", "color")
        info_div.add(info_table)


        edit_div = DivWdg()
        info_div.add(edit_div)
        edit_div.add_style("margin-top: -35px")
        edit_div.add_style("margin-left: 1px")
        edit_div.add_style("margin-right: -2px")
        #edit_div.add_style("overflow: scroll")
        edit_div.add_style("height: 100%")

        view = my.kwargs.get("detail_view")
        if not view:
            view = "edit"

        ignore = ["preview", "notes"]

        element_names = ['name','description','tasks']
        config = WidgetConfigView.get_by_search_type(search_type=my.full_search_type, view=view)
        config_element_names = config.get_element_names()
        for x in config_element_names:
            if x in ignore:
                continue
            if x not in element_names:
                element_names.append(x)



        # add the tile
        title = DivWdg()
        edit_div.add(title)
        title.add_gradient("background", "background3", 0, -10)
        title.add_style("height: 20px")
        title.add_style("padding: 4px")
        title.add_style("font-weight: bold")
        title.add("&nbsp")
        title.add_border()

        from tactic.ui.panel.edit_layout_wdg import EditLayoutWdg
        edit = EditLayoutWdg(search_type=my.full_search_type, mode='view', view="detail", search_key=my.search_key, width=400, title=' ', ignore=ignore, element_names=element_names)
        edit_div.add(edit)

        return div




class TaskDetailWdg(SObjectDetailWdg):

    def get_sobject(my):
        search_key = my.kwargs.get("search_key")
        my.sobject = Search.get_by_search_key(search_key)
        my.parent = my.sobject.get_parent()
        return my.sobject


    def get_sobject_info(my):

        titles = ['Description']
        exprs = []
        exprs.append( "@GET(parent.description)")
        return titles, exprs


    def get_task_info(my):
        process = my.sobject.get_value("process")
        #titles = ['Process', 'Status', 'Assigned', 'Supervisor','Priority','Start Date', 'End Date', '# Notes', '# Snapshots']
        titles = ['Process', 'Status', 'Assigned', 'Supervisor','Priority','Start Date', 'End Date']

        exprs = []
        exprs.append( "@GET(.process)")
        exprs.append( "@GET(.status)")
        exprs.append( "@GET(.assigned)")
        exprs.append( "@GET(.supervisor)")
        exprs.append( "@GET(.priority)")
        exprs.append( "{@GET(.bid_start_date),%b %d, %Y}")
        exprs.append( "{@GET(.bid_end_date),%b %d, %Y}")

        #exprs.append( "@COUNT(parent.sthpw/note['process','%s'])" % process)
        #exprs.append( "@COUNT(parent.sthpw/snapshot['process','%s'])" % process)
        return titles, exprs


    def get_sobject_info_wdg(my):
        attr_table = Table()
        attr_table.add_color("color", "color")
        attr_table.add_color("background", "background", -5)
        attr_table.add_border()
        attr_table.set_box_shadow("0px 0px 5px")

        sobject = my.get_sobject()

        tr, td = attr_table.add_row_cell()
        td.add("<b>Task Info<hr/></b>")
        td.add_style("padding-top: 5px")
        td.add_style("padding-left: 5px")


        titles, exprs = my.get_task_info()
        for title, expr in zip(titles, exprs):
            try:
                value = Search.eval(expr, sobject, single=True)
            except Exception, e:
                print "WARNING: ", e.message
                continue

            if value == '':
                value = '<i>none</i>'
            attr_table.add_row()
            th = attr_table.add_cell("%s: " % title)
            th.add_style("text-align: left")
            th.add_style("padding-right: 15px")
            th.add_style("padding-left: 5px")
            th.add_style("padding-bottom: 2px")
            td = attr_table.add_cell(value)
    

        return attr_table


 

    def get_config_xml(my):

        process = my.sobject.get_value("process")
        context = my.sobject.get_value("context")
        process_title = "Process - %s" % (process)
        process_name = "process_%s" % process
        parent_key = ''
        if my.parent:
            parent_key = SearchKey.get_by_sobject(my.parent).replace("&","&amp;")
        search_key = SearchKey.get_by_sobject(my.sobject).replace("&","&amp;")

        config_xml = []

        config_xml.append( '''
        <config>
        <tab>''' )


        config_xml.append( '''
        <element name="%s" title="%s">
          <display class='tactic.ui.tools.SObjectSingleProcessDetailWdg'>
            <search_key>%s</search_key>
            <process>%s</process>
            <context>%s</context>
          </display>
        </element>
        ''' % (process_name, process_title, parent_key, process, context) )

        display_options = my.kwargs
        options_list = []
        for key, value in display_options.items():
            if key in ['search_key','process', 'parent_key','checkin_ui_options','checkin_script_path','checkin_script','checkin_relative_dir']:
                continue
            options_list.append('<%(key)s>%(value)s</%(key)s>'%({'key':key, 'value': value}))

        """
        config_xml.append( '''
        <element name="checkout_%s" title="Checkout: %s ">
          <display class='tactic.ui.table.TaskCheckoutManageWdg'>
            <search_key>%s</search_key>
            <parent_key>%s</parent_key>
             %s
          </display>
        </element>
        ''' % (process_name, process_title, search_key, search_key, '\n'.join(options_list)) )
        """

        display_options = my.kwargs
        options_list = []
        for key, value in display_options.items():
            if key in ['search_key','process','show_versionless_folder']:
                continue
            options_list.append('<%(key)s>%(value)s</%(key)s>'%({'key':key, 'value': value}))

        wdg_xml = '''
        <element name="checkin_%s" title="Checkin: %s ">
          <display class='tactic.ui.widget.CheckinWdg'>
            <search_key>%s</search_key>
            <process>%s</process>
            <context>%s</context>
            %s
          </display>
        </element>
        
        ''' % (process_name, process_title, parent_key, process, context, '\n'.join(options_list))

        config_xml.append( wdg_xml)

        config_xml.append( '''
        </tab>
        </config>
        ''' )

        config_xml = "".join(config_xml)

        return config_xml


__all__.append("TaskDetailPipelineWrapperWdg")
__all__.append("TaskDetailPipelineWdg")
class TaskDetailPipelineWrapperWdg(BaseRefreshWdg):

    def get_display(my):
        search_key = my.kwargs.get("search_key")
        my.sobject = Search.get_by_search_key(search_key)
        my.parent = my.sobject.get_parent()

        pipeline_code = my.kwargs.get("pipeline")
        top = my.top
        top.add_class("spt_pipeline_wrapper")
        top.add_color("background", "background")
        if not my.parent:
            top.add('Parent of this task cannot be found.')
            return top
        top.add(my.get_pipeline_wdg(pipeline_code) )
        return top


    def get_pipeline_wdg(my, pipeline_code):
        div = DivWdg()

        title = DivWdg()
        title.add_gradient("background", "background3", 0)
        title.add_style("height: 20px")
        title.add_style("font-weight: bold")
        title.add_style("padding: 4px")
        title.add_border()
        title.add("Pipeline")
        div.add(title)

        kwargs = {
            'width': 800,
            'height': 300,
            'pipeline': pipeline_code,
            'scale': 0.7,
        }
        pipeline = TaskDetailPipelineWdg(**kwargs)
        div.add(pipeline)
        load_div = DivWdg()
        div.add(load_div)


        # This is only for tasks!!!!
        enabled_tasks = set()
        from pyasm.biz import Task
        process = ''
        
        if my.parent:
            tasks = Task.get_by_sobject(my.parent)
            if my.sobject.has_value("process"):
                process = my.sobject.get_value("process")
        else:
            tasks = Task.get_by_sobject(my.sobject)

        for task in tasks:
            enabled_tasks.add(task.get_value("process"))

        enabled_tasks = list(enabled_tasks)


        load_div.add_behavior( { 
        'type': 'load',
        'process': process,
        'enabled_tasks': enabled_tasks,
        'pipeline': pipeline_code,
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_pipeline_wrapper");
        spt.pipeline.init_cbk(top);

        var nodes = spt.pipeline.get_nodes_by_group(bvr.pipeline);
        for (var i = 0; i < nodes.length; i++) {
            var has_task = false;
            var node = nodes[i];
            var node_name = spt.pipeline.get_node_name(node);
            for (var j = 0; j < bvr.enabled_tasks.length; j++) {
                if (node_name == bvr.enabled_tasks[j]) {
                    has_task = true;
                    break;
                }
            }

            if (!has_task && node) {
                spt.pipeline.disable_node(node);
            }
        }

        spt.pipeline.unselect_all_nodes();

        var node = spt.pipeline.get_node_by_name(bvr.process);
        //process and node name could be different
        if (node) {
            node.setStyle("font-weight", "bold");
            spt.pipeline.select_node(node);
            //spt.pipeline.center_node(node);
        }
        spt.pipeline.fit_to_canvas(bvr.pipeline);

        '''
        } )


        #div.add_style("padding: 10px")
        div.add_border()


        return div



class TaskDetailPipelineWdg(PipelineCanvasWdg):

    def get_node_context_menu(my):

        menu = Menu(width=180)
        menu.set_allow_icons(False)
        menu.set_setup_cbfn( 'spt.dg_table.smenu_ctx.setup_cbk' )


        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)


        menu_item = MenuItem(type='action', label='Load Detail Report')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);
            var name = node.getAttribute("spt_element_name");

            var top = node.getParent(".spt_detail_top");
            spt.tab.top = top.getElement(".spt_tab_top");

            var search_key = top.getAttribute("spt_parent_key");
            if (!search_key) {
                search_key = top.getAttribute("spt_search_key");
            }

            var class_name = 'tactic.ui.tools.sobject_wdg.SObjectSingleProcessDetailWdg';
            var kwargs = {
                search_key: search_key,
                process: name
            }

            var title = "Detail ["+name+"]";
            var element_name = "detail_"+name;
            spt.tab.add_new(element_name, title, class_name, kwargs);
            '''
        } )
        menu.add(menu_item)


        return menu




class SObjectSingleProcessDetailWdg(BaseRefreshWdg):
    '''Shows the task, snapshot and notes information for an sobject'''

    def get_sobject(my):
        search_key = my.kwargs.get("search_key")
        my.sobject = Search.get_by_search_key(search_key)
        my.parent = None
        if my.sobject:
            my.parent = my.sobject.get_parent()
        return my.sobject


    def get_display(my):
        top = DivWdg()

        sobject = my.get_sobject()
        if not sobject:
            return top
        process = my.kwargs.get("process")

        #from tactic.ui.table import TaskElementWdg
        #task_wdg = TaskElementWdg()
        #task_wdg.set_sobject(my.sobject)
        #top.add(task_wdg)

        search = Search('sthpw/task')
        search.add_parent_filter(sobject)
        search.add_filter("process", process)
        tasks = search.get_sobjects()

        tasks_div = DivWdg()
        top.add(tasks_div)
        #tasks_div.add_style("padding: 0px 0px 20px 0px")
        tasks_div.add_style("margin: 10px")
        tasks_div.set_box_shadow()

        title = DivWdg()
        title.add_gradient("background", "background3", 0, -10)
        title.add_color("color", "color3", -10)
        title.add_border()
        title.add_style("height: 20px")
        title.add_style("padding: 4px")
        title.add_style("font-weight: bold")
        title.add("All Tasks for process '%s':" % process)
        tasks_div.add(title)


        task_wdg = TableLayoutWdg(search_type="sthpw/task",view='single_process', show_row_select="false", show_insert="false", show_gear="false", show_search_limit="false", show_search=False, show_refresh="false", show_shelf="false")
        task_wdg.set_sobjects(tasks)
        tasks_div.add(task_wdg)


        #from tactic.ui.container import ResizableTableWdg
        #table = ResizableTableWdg()
        table = Table()
        top.add(table)
        table.add_style("width: 100%")
        table.add_row()


        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("width: 50%")

        notes_div = DivWdg()
        td.add(notes_div)
        notes_div.set_box_shadow()
        notes_div.add_style("margin: 10px")

        title = DivWdg()
        notes_div.add(title)
        title.add_gradient("background", "background3", 0, -10)
        title.add_color("color", "color3", -10)
        title.add_border()
        title.add_style("height: 20px")
        title.add_style("padding: 4px")
        title.add_style("font-weight: bold")
        title.add("Notes:")


        from tactic.ui.widget.discussion_wdg import DiscussionWdg
        discussion_wdg = DiscussionWdg(search_key=sobject.get_search_key(), process=process, context_hidden=True, show_note_expand=True)
        notes_div.add(discussion_wdg)

        search = Search('sthpw/snapshot')
        search.add_parent_filter(sobject)
        search.add_filter("process", process)
        snapshots = search.get_sobjects()

        td = table.add_cell()
        td.add_style("vertical-align: top")
        td.add_style("width: 50%")
        td.add_style("padding: 0 0 0 0")

        snapshots_div = DivWdg()
        td.add(snapshots_div)
        snapshots_div.set_box_shadow()
        snapshots_div.add_style("margin: 10px")


        title = DivWdg()
        title.add_gradient("background", "background3", 0, -10)
        title.add_color("color", "color3", -10)
        title.add_border()
        title.add_style("height: 20px")
        title.add_style("padding: 4px")
        title.add_style("font-weight: bold")
        title.add("Snapshots:")
        snapshots_div.add(title)


        snapshot_wdg = TableLayoutWdg(search_type="sthpw/snapshot",view='table', mode='simple', show_row_select=False, width='100%', show_shelf="false")
        snapshot_wdg.set_sobjects(snapshots)
        snapshots_div.add(snapshot_wdg)



        return top







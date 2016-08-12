###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["ProjectConfigWdg", "UserConfigWdg", "UserPanelWdg"]

from pyasm.common import Common, Environment
from pyasm.search import Search, SearchKey, SearchType
from pyasm.biz import Project
from pyasm.web import DivWdg, Table, WebContainer, SpanWdg, HtmlElement
from pyasm.widget import ThumbWdg, IconWdg, CheckboxWdg
from tactic.ui.container import SmartMenu

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import IconButtonWdg, SingleButtonWdg, ActionButtonWdg
from tactic.ui.panel import ViewPanelWdg

class ProjectConfigWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    } 

    def get_help_alias(my):
        return 'project-startup-configuration'

    def get_panel_wdg(my, td, panel):

        title = panel.get("title")
        widget = panel.get("widget")
        width = panel.get("width")

        #height = panel.get("height")
        #if not height:
        #    height = "250px"
        #td.add_style("height: %s" % height)

        if width:
            td.add_style("width: %s" % width)

        td.add_border()

        div = DivWdg()
        div.add_style("padding: 5px")
        #div.add_style("padding: 10px")


        title_wdg = DivWdg()
        div.add(title_wdg)
        title_wdg.add_style("padding: 5px")
        #title_wdg.add_style("margin: -12px -12px 10px -12px")
        title_wdg.add_style("margin: -6px -7px 5px -7px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_style("font-size: 14px")
        title_wdg.add_style("height: 25px")

        if title:
            title_wdg.add_color("background", "background", -5)
            title_wdg.add_color("color", "color", -10)
            title_wdg.add_border()
            title_wdg.add(title)

            from tactic.ui.app import HelpButtonWdg
            help_wdg = HelpButtonWdg(alias=my.get_help_alias())
            help_wdg.add_style("float: right")
            help_wdg.add_style("margin-top: -5px")
            title_wdg.add(help_wdg)

        else:
            title_wdg.add_style("height: 10px")

        if widget:
            div.add(widget)

        return div


    def get_panels(my):

        panels = []

        search_type_panel = DivWdg()
        search_type_panel.add_style("padding-top: 3px")
        search_type_panel.add_style("overflow-y: auto")
        search_type_panel.add( SearchTypePanel() )
        search_type_panel.add_style("min-height: 100px")
        search_type_panel.add_style("height: 300px")
        search_type_panel.add_class("spt_resizable")


        panel = {
            'widget': search_type_panel,
            'title': 'Searchable Type (sType) List',
            'width': '50%'
        }
        panels.append(panel)

        from tactic.ui.container import TabWdg
        config_xml = '''
        <config>
        <tab>
        <element name="Help">
            <display class='tactic.ui.app.HelpContentWideWdg'>
              <alias>main</alias>
              <width>1000px</width>
            </display>
        </element>
        </tab>
        </config>
        '''

        div = DivWdg()
        tab = TabWdg(show_add=False, config_xml=config_xml, tab_offset=5)
        div.add(tab)
        div.add_style("margin: 0px -6px -6px -6px")


        panel = {
            'widget': div,
            #'title': 'Data',
            'title': None,
            'width': '100%',
        }
        panels.append(panel)

        return panels


    def get_display(my):

        # set the sobjects to all the widgets then preprocess
        for widget in my.widgets:
            widget.set_sobjects(my.sobjects)
            widget.set_parent_wdg(my)
            # preprocess the elements
            widget.preprocess()


        top = my.top
        my.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)
        inner.add_color("background", "background")
        inner.add_color("color", "color")
        inner.add_class("spt_dashboard_top")

        title = DivWdg()
        inner.add(title)
        title.add(my.get_title())
        title.add_style("font-size: 18px")
        title.add_style("font-weight: bold")
        title.add_style("text-align: center")
        title.add_style("padding: 10px")
        #title.add_style("margin: -10px -10px 10px -10px")

        #temp solution. Disable the frame title showing, so have more space for the view table
        title.add_style("display: none")

        title.add_color("background", "background3")

        #table = Table()
        from tactic.ui.container import ResizableTableWdg
        table = ResizableTableWdg()
        inner.add(table)
        table.set_max_width()

        panels = my.get_panels()

        for panel in panels:
            tr = table.add_row()
            td = table.add_cell(resize=False)
            td.add_style("min-height: 100px")

            td.add_style("vertical-align: top")


            panel = my.get_panel_wdg(td, panel)
            td.add(panel)

        return top



    def get_title(my):
        return "Project Configuration"


class UserConfigWdg(ProjectConfigWdg):

    def get_title(my):
        return "Manage Users"

    def get_help_alias(my):
        return 'project-startup-manage-users'


    def get_panels(my):

        panels = []

        show_security = my.kwargs.get("show_security") or ""
        show_add = my.kwargs.get("show_add") or ""
        view = my.kwargs.get("view") or ""
        filter_mode = my.kwargs.get("filter_mode") or ""
        show_help = my.kwargs.get("show_help") or ""
        show_search_limit = my.kwargs.get("show_search_limit") or ""

        from tactic.ui.container import TabWdg
        config_xml = []

        config_xml.append('''
        <config>
        ''')

        config_xml.append('''
        <tab>
        <element name="Users">
            <display class='tactic.ui.startup.UserPanelWdg'>
                <show_security>%s</show_security>
                <show_add>%s</show_add>
                <view>%s</view>
                <filter_mode>%s</filter_mode>
                <show_help>%s</show_help>
                <show_search_limit>%s</show_search_limit>
            </display>
        </element>
          ''' %(show_security, show_add, view, filter_mode, show_help, show_search_limit))

        config_xml.append('''
        <element name="Group Assignment">
            <display class='tactic.ui.startup.UserSecurityWdg'/>
        </element>
        </tab>
          ''')

        config_xml.append('''
        </config>
        ''')


        config_xml = "\n".join(config_xml)

        tab = TabWdg(show_add=False, config_xml=config_xml)


        panel = {
            'widget': tab,
            'title': None,
            'width': '100%',
            'height': '100%'
        }
        panels.append(panel)

        return panels



class SearchTypePanel(BaseRefreshWdg):

    def get_display(my):

        web = WebContainer.get_web()
        show_multi_project = web.get_form_value('show_multi_project')
        project = Project.get()
        search_type_objs = project.get_search_types(include_multi_project=show_multi_project)


        top = my.top
        top.add_class("spt_panel_stype_list_top")
        #top.add_style("min-width: 400px")
        #top.add_style("max-width: 1000px")
        #top.add_style("width: 100%")
        top.center()



        button = SingleButtonWdg(title="Advanced Setup", icon=IconWdg.ADVANCED)
        top.add(button)
        button.add_style("float: right")
        button.add_style("margin-top: 0px")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var class_name = 'tactic.ui.app.ProjectStartWdg';
            spt.tab.set_main_body_tab()
            spt.tab.add_new("project_setup", "Project Setup", class_name)
            '''
        } )


        button = SingleButtonWdg(title="Add", tip="Add New Searchable Type (sType)", icon="BS_PLUS")
        top.add(button)
        button.add_style("float: left")
        button.add_style("margin-top: 0px")
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var class_name = 'tactic.ui.app.SearchTypeCreatorWdg';

            var kwargs = {
            };
            var popup = spt.panel.load_popup("Create New Searchable Type", class_name, kwargs);

            var top = bvr.src_el.getParent(".spt_panel_stype_list_top");
            popup.on_register_cbk = function() {
                spt.panel.refresh(top);
            }

            '''
        } )

        cb = CheckboxWdg('show_multi_project', label=' show multi-project')
        if show_multi_project:
            cb.set_checked()
        cb.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
                var panel = bvr.src_el.getParent('.spt_panel_stype_list_top')
                spt.panel.refresh(panel, {show_multi_project: bvr.src_el.checked});
            '''
            })
        span = SpanWdg(css='small')
        top.add(span)
        top.add(cb)
        top.add("<br clear='all'/>")
        #search_type_objs = []
        if not search_type_objs:
            arrow_div = DivWdg()
            top.add(arrow_div)
            icon = IconWdg("Click to Add", IconWdg.ARROW_UP_LEFT_32)
            icon.add_style("margin-top: -20")
            icon.add_style("margin-left: -15")
            icon.add_style("position: absolute")
            arrow_div.add(icon)
            arrow_div.add("&nbsp;"*5)
            arrow_div.add("<b>Click to Add</b>")
            arrow_div.add_style("position: relative")
            arrow_div.add_style("margin-top: 5px")
            arrow_div.add_style("margin-left: 20px")
            arrow_div.add_style("float: left")
            arrow_div.add_style("padding: 25px")
            arrow_div.set_box_shadow("0px 5px 20px")
            arrow_div.set_round_corners(30)
            arrow_div.add_color("background", "background")

            div = DivWdg()
            top.add(div)
            div.add_border()
            div.add_style("min-height: 180px")
            div.add_style("width: 600px")
            div.add_style("margin: 30px auto")
            div.add_style("padding: 20px")
            div.add_color("background", "background3")
            icon = IconWdg( "WARNING", IconWdg.WARNING )
            div.add(icon)
            div.add("<b>No Searchable Types have been created</b>")
            div.add("<br/><br/>")
            div.add("Searchables Types contain lists of items that are managed in this project.  Each item will automatically have the ability to have files checked into it, track tasks and status and record work hours.")
            div.add("<br/>"*2)
            div.add("For more information, read the help docs: ")
            from tactic.ui.app import HelpButtonWdg
            help = HelpButtonWdg(alias="main")
            div.add(help)
            div.add("<br/>")
            div.add("Click on the 'Add' button above to start adding new types.")
            return top


        div = DivWdg()
        top.add(div)
        #div.add_style("max-height: 300px")
        #div.add_style("overflow-y: auto")



        table = Table()
        div.add(table)
        table.add_style("margin-top: 10px")
        table.set_max_width()



        # group mouse over
        table.add_relay_behavior( {
            'type': "mouseover",
            'bvr_match_class': 'spt_row',
            'cbjs_action': "spt.mouse.table_layout_hover_over({}, {src_el: bvr.src_el, add_color_modifier: -2})"
        } )
        table.add_relay_behavior( {
            'type': "mouseout",
            'bvr_match_class': 'spt_row',
            'cbjs_action': "spt.mouse.table_layout_hover_out({}, {src_el: bvr.src_el})"
        } )



        tr = table.add_row()
        tr.add_color("color", "color")
        tr.add_gradient("background", "background", -10)
        th = table.add_header("")
        th.add_style("text-align: left")
        th = table.add_header("Title")
        th.add_style("text-align: left")
        th = table.add_header("# Items")
        th.add_style("text-align: left")
        th = table.add_header("View")
        th.add_style("text-align: left")
        th = table.add_header("Add")
        th.add_style("text-align: left")
        th = table.add_header("Import")
        th.add_style("text-align: left")
        th = table.add_header("Custom Columns")
        th.add_style("text-align: left")
        th = table.add_header("Workflow")
        th.add_style("text-align: left")
        th = table.add_header("Notifications")
        th.add_style("text-align: left")
        th = table.add_header("Triggers")
        th.add_style("text-align: left")
        th = table.add_header("Edit")
        th.add_style("text-align: left")
        #th = table.add_header("Security")
        #th.add_style("text-align: left")



        for i, search_type_obj in enumerate(search_type_objs):
            tr = table.add_row()
            tr.add_class("spt_row")

            if not i or not i%2:
                tr.add_color("background", "background3")
            else:
                tr.add_color("background", "background", -2 )


            thumb = ThumbWdg()
            thumb.set_sobject(search_type_obj)
            thumb.set_icon_size(30)
            td = table.add_cell(thumb)



            search_type = search_type_obj.get_value("search_type")
            title = search_type_obj.get_title()

            table.add_cell(title)

            try:
                search = Search(search_type)
                count = search.get_count()
                if count:
                    table.add_cell("%s item/s" % count)
                else:
                    table.add_cell("&nbsp;")
            except:
                td = table.add_cell("&lt; No table &gt;")
                td.add_style("font-style: italic")
                td.add_style("color: #F00")
                continue



            #search = Search(search_type)
            #search.add_interval_filter("timestamp", "today")
            #created_today = search.get_count()
            #table.add_cell(created_today)



            td = table.add_cell()
            button = IconButtonWdg(title="View", icon=IconWdg.ZOOM)
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'title': title,
                'cbjs_action': '''

                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                    view: 'table',
                    'simple_search_view': 'simple_search'
                };

                // use tab
                var top = bvr.src_el.getParent(".spt_dashboard_top");
                spt.tab.set_tab_top(top);
                spt.tab.add_new(bvr.title, bvr.title, class_name, kwargs);
                //spt.panel.load_popup(bvr.title, class_name, kwargs);

                '''
            } )
            button.add_style("float: left")


            arrow_button = IconButtonWdg(tip="More Views", icon=IconWdg.ARROWHEAD_DARK_DOWN)
            arrow_button.add_style("margin-left: 20px")
            td.add(arrow_button)

            cbk = '''
            var activator = spt.smenu.get_activator(bvr);

            var class_name = bvr.class_name;
            var layout = bvr.layout;

            var kwargs = {
                search_type: bvr.search_type,
                layout: layout,
                view: bvr.view,
                simple_search_view: 'simple_search',
                element_names: bvr.element_names,
            };

            // use tab
            var top = activator.getParent(".spt_dashboard_top");
            spt.tab.set_tab_top(top);
            spt.tab.add_new('%s', '%s', class_name, kwargs);
            ''' % (title, title)


            from tactic.ui.panel import SwitchLayoutMenu
            SwitchLayoutMenu(search_type=search_type, activator=arrow_button, cbk=cbk, is_refresh=False)

            td = table.add_cell()
            button = IconButtonWdg(title="Add", icon=IconWdg.ADD)
            td.add(button)
            button.add_behavior( {
                'type': 'listen',
                'search_type': search_type,
                'event_name': 'startup_save:' + search_type_obj.get_title(),
                'title': search_type_obj.get_title(),
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_dashboard_top");
                spt.tab.set_tab_top(top);
                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                    view: 'table',
                    'simple_search_view': 'simple_search'
                };

                spt.tab.add_new(bvr.title, bvr.title, class_name, kwargs);
 

                '''
            } )
            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'title': search_type_obj.get_title(),
                'cbjs_action': '''

                var top = bvr.src_el.getParent(".spt_dashboard_top");
                spt.tab.set_tab_top(top);

                var class_name = 'tactic.ui.panel.EditWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                    view: "insert",
                    save_event: "startup_save:" + bvr.title
                }
                spt.panel.load_popup("Add New Items ("+bvr.title+")", class_name, kwargs);

                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                    view: 'table',
                    'simple_search_view': 'simple_search'
                };

                spt.tab.add_new(bvr.title, bvr.title, class_name, kwargs);
                '''
            } )


            """
            td = table.add_cell()
            button = IconButtonWdg(title="Check-in", icon=IconWdg.PUBLISH)
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'title': title,
                'cbjs_action': '''

                var class_name = 'tactic.ui.panel.ViewPanelWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                    view: 'checkin',
                    element_names: ['preview','code','name','description','history','general_checkin','notes']
                };

                // use tab
                var top = bvr.src_el.getParent(".spt_dashboard_top");
                spt.tab.set_tab_top(top);
                spt.tab.add_new(bvr.title, bvr.title, class_name, kwargs);
                //spt.panel.load_popup(bvr.title, class_name, kwargs);

                '''
            } )
            """





            td = table.add_cell()
            button = IconButtonWdg(title="Import", icon=IconWdg.IMPORT)
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'title': "Import Data",
                'cbjs_action': '''

                var class_name = 'tactic.ui.widget.CsvImportWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                };

                spt.panel.load_popup(bvr.title, class_name, kwargs);

                '''
            } )



            td = table.add_cell()
            button = IconButtonWdg(title="Custom Columns", icon=IconWdg.COLUMNS)
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_type': search_type,
                'title': "Add Custom Columns",
                'cbjs_action': '''
                var class_name = 'tactic.ui.startup.ColumnEditWdg';
                var kwargs = {
                    search_type: bvr.search_type,
                };
                spt.panel.load_popup(bvr.title, class_name, kwargs);

                '''
            } )





            td = table.add_cell()
            button = IconButtonWdg(title="Workflow", icon=IconWdg.PIPELINE)
            button.add_style("float: left")
            td.add(button)

            search = Search("sthpw/pipeline")
            search.add_filter("search_type", search_type)
            count = search.get_count()
            if count:
                check = IconWdg( "Has Items", IconWdg.CHECK, width=8 )
                td.add(check)
                #check.add_style("margin-left: 0px")
                check.add_style("margin-top: 4px")




            button.add_behavior( {
                'type': 'click_up',
                'title': 'Workflow',
                'search_type': search_type,
                'cbjs_action': '''
                var class_name = 'tactic.ui.startup.PipelineEditWdg';
                var kwargs = {
                    search_type: bvr.search_type
                };
                spt.panel.load_popup(bvr.title, class_name, kwargs);
                '''
            } )
 


            td = table.add_cell()
            button = IconButtonWdg(title="Notifications", icon=IconWdg.MAIL)
            button.add_style("float: left")
            td.add(button)

            search = Search("sthpw/notification")
            search.add_filter("search_type", search_type)
            count = search.get_count()
            if count:
                check = IconWdg( "Has Items", IconWdg.CHECK, width=8 )
                td.add(check)
                #check.add_style("margin-left: 0px")
                check.add_style("margin-top: 4px")






            button.add_behavior( {
                'type': 'click_up',
                'title': 'Trigger',
                'search_type': search_type,
                'cbjs_action': '''

                var class_name = 'tactic.ui.tools.TriggerToolWdg';
                var kwargs = {
                    mode: "search_type",
                    search_type: bvr.search_type
                };
                spt.panel.load_popup(bvr.title, class_name, kwargs);
                '''
            } )


            td = table.add_cell()
            button = IconButtonWdg(title="Triggers", icon=IconWdg.ARROW_OUT)
            td.add(button)
            button.add_style("float: left")

            search = Search("config/trigger")
            search.add_filter("search_type", search_type)
            count = search.get_count()
            if count:
                check = IconWdg( "Has Items", IconWdg.CHECK, width=8 )
                td.add(check)
                #check.add_style("margin-left: 0px")
                check.add_style("margin-top: 4px")


            button.add_behavior( {
                'type': 'click_up',
                'title': 'Trigger',
                'search_type': search_type,
                'cbjs_action': '''

                var class_name = 'tactic.ui.tools.TriggerToolWdg';
                var kwargs = {
                    mode: "search_type",
                    search_type: bvr.search_type
                };
                spt.panel.load_popup(bvr.title, class_name, kwargs);
                '''
            } )





            td = table.add_cell()
            button = IconButtonWdg(title="Edit Searchable Type", icon=IconWdg.EDIT)
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_key': search_type_obj.get_search_key(),
                'cbjs_action': '''

                var class_name = 'tactic.ui.panel.EditWdg';
                var kwargs = {
                    search_type: "sthpw/sobject",
                    view: "edit_startup",
                    search_key: bvr.search_key
                }
                spt.panel.load_popup("Edit Searchable Type", class_name, kwargs);


                '''
            } )


 
            """
            td = table.add_cell()
            button = IconButtonWdg(title="Security", icon=IconWdg.LOCK)
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'title': 'Trigger',
                'search_type': search_type,
                'cbjs_action': '''
                alert("security");
                '''
            } )
            """


        columns_wdg = DivWdg()
        top.add(columns_wdg)


        return top



class UserPanelWdg(BaseRefreshWdg):

    def get_help_alias(my):
        return 'project-startup-manage-users'

    def get_display(my):

        filter_mode = my.kwargs.get("filter_mode")
        show_add = my.kwargs.get("show_add") or True
        show_security = my.kwargs.get("show_security") or True
        show_search_limit = my.kwargs.get("show_search_limit") or True
        show_help = my.kwargs.get("show_help") or True

        project = Project.get().get_code()

        if filter_mode == "project":
            new_filter = "sthpw/login_group['project_code', '%s'].sthpw/login_in_group." % project 
        else:
            new_filter = ""

        expr_filter = "%ssthpw/login['login','not in','admin|guest']['begin']['license_type','user']['license_type','is','NULL']['or']" % new_filter
        current_users = Search.eval("@COUNT(%s)" %expr_filter)

        top = my.top
        top.add_class("spt_panel_user_top")
        top.add_style("min-width: 400px")
        
        tool_div = DivWdg()
        # tool_div.add_style('margin-bottom','8px')
        tool_div.add_style('display','inline-flex')
        tool_div.add_style('width','50%')
        tool_div.add_style('margin-bottom','-4px')

        if show_add not in ['false', False]:
            button = ActionButtonWdg(title="Add", tip="Add New User")
            button.add_style('align-self: flex-end')
            tool_div.add(button)
        
            button.add_style("float: left")
            button.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''

                var class_name = 'tactic.ui.panel.EditWdg';
                
                var kwargs = {
                    search_type: "sthpw/login",
                    view: "insert",
                    show_header: false
                }
                var popup = spt.panel.load_popup("Create New User", class_name, kwargs);
                var tab_top = bvr.src_el.getParent(".spt_tab_top");
                popup.on_save_cbk = function(){
                    spt.tab.set_tab_top(tab_top);
                    spt.tab.reload_selected();
                }

                '''
            } )
        else:
            tool_div.add_style('position','relative')
            tool_div.add_style('top','-8px')


        show_count = my.kwargs.get("show_count")
        if show_count in ['true', True]:
            security = Environment.get_security()
            license = security.get_license()
            num_left = license.get_num_licenses_left()
            current_users = license.get_current_users()
            #max_users = license.get_max_users()


            div = DivWdg('Users')
            div.add_style('align-self: flex-end')
            div.add_styles("margin: 0 0 6px 20px")
            badge_span = SpanWdg(css='badge')
            badge_span.add_style('margin-left','6px')
            badge_span.add(current_users)
            div.add(badge_span)
            tool_div.add(div)

            tool_div2 = DivWdg()
            # tool_div.add_style('margin-bottom','8px')
            tool_div2.add_style('display','inline-flex')
            tool_div2.add_style('justify-content','flex-end')
            tool_div2.add_style('width','50%')

            top.add(tool_div)
            top.add(tool_div2)


            if num_left < 1000:
                div = DivWdg('Users Left')
                div.add_style('align-self: flex-end')
                div.add_styles("margin: 0 0 6px 20px")
                badge_span = SpanWdg(css='badge')
                badge_span.add_style('margin-left','6px')
                badge_span.add(num_left)
                div.add(badge_span)
                tool_div.add(div)

                top.add(tool_div)




        if show_security not in ['false', False]:
            button = ActionButtonWdg(title="Security")
            button.add_style('align-self: flex-end')
            #button.add_styles("position: absolute; right: 10px;")
            tool_div2.add(button)
            #button.add_style("margin-top: -8px")
            button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var class_name = 'tactic.ui.startup.SecurityWdg';
            spt.tab.set_main_body_tab()
            spt.tab.add_new("Security", "Security", class_name)
            '''
            } )
        else:
            tool_div.add_style('position','relative')
            tool_div.add_style('top','0px')



        br = HtmlElement.br(clear=True)
        top.add(br)



        if not current_users:
            div = DivWdg()
            top.add(div)
            div.add_style("text-align: center")
            div.add_border()
            div.add_style("min-height: 150px")
            div.add_style("margin: 15px 30px 30px 30px")
            div.add_style("padding: 30px 20px 0px 20px")
            div.add_color("background", "background3")
            icon = IconWdg( "WARNING", IconWdg.WARNING )
            div.add(icon)
            div.add("<b>No users have been added</b>")
            div.add("<br/><br/>")
            div.add("For more information, read the help docs: ")
            from tactic.ui.app import HelpButtonWdg
            help = HelpButtonWdg(alias=my.get_help_alias())
            div.add(help)
            div.add("<br/>")
            div.add("Click on the 'Add' button above to start adding new users.")

            return top




        div = DivWdg()
        top.add(div)
        #div.add_style("max-height: 300px")
        #div.add_style("overflow-y: auto")

        view = my.kwargs.get("view")

        if not view:
            view = "manage_user"


        expr = "@SEARCH(%s)" %expr_filter
        panel = ViewPanelWdg(
                search_type='sthpw/login',
                view=view,show_insert='false',
                show_gear='false',
                show_select='false',
                #height='700',
                expression=expr,
                simple_search_view='simple_manage_filter',
                show_column_manager='false',
                show_layout_switcher='false',
                show_expand='false',
                show_search_limit=show_search_limit,
                show_help=show_help
        )
        div.add(panel)
        div.add_style('margin-top', '4px')

        return top


        """


        table = Table()
        table.set_max_width()
        table.add_style("margin-top: 10px")
        div.add(table)


        # group mouse over
        table.add_relay_behavior( {
            'type': "mouseover",
            'bvr_match_class': 'spt_row',
            'cbjs_action': "spt.mouse.table_layout_hover_over({}, {src_el: bvr.src_el, add_color_modifier: -2})"
        } )
        table.add_relay_behavior( {
            'type': "mouseout",
            'bvr_match_class': 'spt_row',
            'cbjs_action': "spt.mouse.table_layout_hover_out({}, {src_el: bvr.src_el})"
        } )




        tr = table.add_row()
        tr.add_color("color", "color")
        tr.add_color("background", "background", -10)
        th = table.add_header("&nbsp;")
        th.add_style("padding: 8px 3px")
        th.add_style("text-align: left")
        th = table.add_header("Login")
        th.add_style("padding: 8px 3px")
        th.add_style("text-align: left")
        th = table.add_header("First Name")
        th.add_style("padding: 8px 3px")
        th.add_style("text-align: left")
        th = table.add_header("Last Name")
        th.add_style("padding: 8px 3px")
        th.add_style("text-align: left")
        th = table.add_header("Display Name")
        th.add_style("padding: 8px 3px")
        th.add_style("text-align: left")
        th = table.add_header("Activity")
        th.add_style("padding: 8px 3px")
        th.add_style("text-align: left")
        th = table.add_header("Groups")
        th.add_style("padding: 8px 3px")
        th.add_style("text-align: left")
        th = table.add_header("Security")
        th.add_style("padding: 8px 3px")
        th.add_style("text-align: left")
        th = table.add_header("Edit")
        th.add_style("padding: 8px 3px")
        th.add_style("text-align: left")



        expr = "@SOBJECT(%s)" %expr_filter
        logins = Search.eval(expr)

        for i, login in enumerate(logins):
            tr = table.add_row()
            tr.add_class("spt_row")

            if not i or not i%2:
                tr.add_color("background", "background")
            else:
                tr.add_color("background", "background", -2 )

            thumb = ThumbWdg()
            thumb.set_sobject(login)
            thumb.set_icon_size(45)
            td = table.add_cell(thumb)

            td = table.add_cell(login.get_value("login"))
            td.add_style("padding: 3px")
            td = table.add_cell(login.get_value("first_name"))
            td.add_style("padding: 3px")
            td = table.add_cell(login.get_value("last_name"))
            td.add_style("padding: 3px")

            td = table.add_cell(login.get_value("display_name"))
            td.add_style("padding: 3px")           

            search_key = login.get_search_key()
            login_code = login.get_code()
            full_name = login.get_full_name()

            td = table.add_cell()
            button = IconButtonWdg(tip="Activity", icon=IconWdg.CALENDAR)
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'login_code': login_code,
                'full_name': full_name,
                'cbjs_action': '''

                var class_name = 'tactic.ui.tools.ScheduleUserToolWdg';
                var kwargs = {
                    login: bvr.login_code
                }

                var title = bvr.full_name + ' Schedule';
                var top = bvr.src_el.getParent(".spt_dashboard_top");
                spt.tab.set_tab_top(top);
                spt.tab.add_new("user_schedule", title, class_name, kwargs);
                //spt.panel.load_popup("Activty", class_name, kwargs);


                '''
            } )

 
            td = table.add_cell()
            button = IconButtonWdg(title="Groups", icon=IconWdg.GROUP_LINK)
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_key': search_key,
                'cbjs_action': '''

                var class_name = 'tactic.ui.startup.GroupAssignWdg';
                var kwargs = {
                    search_key: bvr.search_key
                };
                var popup = spt.panel.load_popup("Group Assignment", class_name, kwargs);
                '''
            } )

  
            td = table.add_cell()
            button = IconButtonWdg(title="Security", icon=IconWdg.LOCK)
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_key': search_key,
                'cbjs_action': '''

                var class_name = 'tactic.ui.startup.GroupSummaryWdg';
                var kwargs = {
                    search_key: bvr.search_key
                };
                var popup = spt.panel.load_popup("Security Summary", class_name, kwargs);
                '''
            } )




            td = table.add_cell()
            button = IconButtonWdg(title="Edit User", icon=IconWdg.EDIT)
            td.add(button)
            button.add_behavior( {
                'type': 'click_up',
                'search_key': search_key,
                'cbjs_action': '''

                var top = bvr.src_el.getParent(".spt_panel_user_top");
                var class_name = 'tactic.ui.panel.EditWdg';
                var kwargs = {
                    search_type: "sthpw/login",
                    view: "edit",
                    search_key: bvr.search_key
                }
                var popup = spt.panel.load_popup("Create New User", class_name, kwargs);

                popup.on_save_cbk = function() {
                    spt.panel.refresh(top);
                }

                '''
            } )

        return top

        """







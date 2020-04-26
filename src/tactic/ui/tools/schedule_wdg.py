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

__all__ = ['ScheduleToolWdg', 'ScheduleUserToolWdg']


from pyasm.common import Environment
from pyasm.web import DivWdg, HtmlElement, SpanWdg, Table
from pyasm.widget import ThumbWdg, SwapDisplayWdg
from pyasm.security import Login
from pyasm.search import Search

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import ResizableTableWdg

from pipeline_canvas_wdg import *
from pipeline_wdg import *

class ScheduleToolWdg(BaseRefreshWdg):

    def init(self):
        self.sobject_display_expr = self.kwargs.get('sobject_display_expr')
        self.tab_view = self.kwargs.get('tab_view')

    def get_display(self):
        top = self.top
        top.add_color("background", "background")
        top.add_color("color", "color")
        top.add_class("spt_schedule_top")


        table = Table()
        #table = ResizableTableWdg()
        top.add(table)
        table.add_color("color", "color")

        table.add_row()
        left = table.add_cell()
        user_wdg = self.get_group_wdg()
        left.add(user_wdg)
        left.add_style("vertical-align: top")
        left.add_border()
        left.add_style("width: 250px")

        right = table.add_cell()
        right.add_class("spt_schedule_content")
        #right.add_border()
        right.add_style("overflow-x: hidden")
        right.add("&nbsp")
        right.add_style("min-width: 500px")
        right.add_style("width: 100%")
        right.add_style("height: 500px")



        div = DivWdg()
        right.add(div)

        div.add_style("height: 100px")
        div.add_style("width: 400px")
        div.add_color("background", "background3")
        div.add_color("color", "color3")
        #div.add_border()
        div.center()
        div.add_style("margin-top: 50px")
        div.add_style("padding-top: 75px")

        div.add_style("text-align: center")
        div.add("<b>Select a user on the left</b>")


        return top


    def get_group_wdg(self):

        div = DivWdg()

        title_wdg = DivWdg()
        div.add(title_wdg)
        title_wdg.add_style("padding: 5px")
        title_wdg.add_style("font-weight: bold")
        title_wdg.add_style("font-size: 14px")
        title_wdg.add_gradient("background", "background" )
        title_wdg.add("Users")
        title_wdg.add_style("min-width: 200px")


        filtered_groups = self.kwargs.get("groups")
        if isinstance(filtered_groups, basestring):
            filtered_groups = filtered_groups.split("|")

        search = Search("sthpw/login_group")
        if filtered_groups:
            search.add_filters("login_group", filtered_groups)

        security = Environment.get_security()
        if not security.check_access("builtin", "view_site_admin", "allow"):
            search.add_filter("login_group", "admin", op="!=")
        search.add_project_filter()

        groups = search.get_sobjects()


        groups_div = DivWdg()
        div.add(groups_div)
        for group in groups:

            group_div = DivWdg()
            groups_div.add(group_div)

            title_div = DivWdg()
            group_div.add(title_div)
            title_div.add_color("background", "background3")
            title_div.add_color("color", "color3")
            title_div.add_style("margin-top: 5px")
            title_div.add_style("padding: 2px")

            swap = SwapDisplayWdg()
            title_div.add(swap)
            swap.add_style("float: left")
            
            title = DivWdg( group.get_value("login_group") )
            title_div.add(title)
            #title.add_style("float: left")
            title.add_style("font-weight: bold")
            title.add_style("padding-top: 2px")


            content_div = DivWdg()
            group_div.add(content_div)

            SwapDisplayWdg.create_swap_title(title, swap, div=content_div, is_open=True, action_script=None)

            logins = group.get_logins()
            logins_div = self.get_logins_wdg(logins)
            content_div.add(logins_div)
            content_div.add_style("padding-left: 15px")

        return div


    def get_logins_wdg(self, logins):
        logins_div = DivWdg()
        for login in logins:
            login_div = DivWdg()
            logins_div.add(login_div)
            login_div.add_style("padding: 5px")
            #login_div.add_style("height: 30px")
            login_div.add_style("margin: 0 5px 5px 0")
            login_div.add_attr("spt_login", login.get_value("login"))

            thumb_div = DivWdg()
            login_div.add(thumb_div)
            thumb_div.add_style("float: left")
            thumb_div.add_style("margin-right: 5px")
            thumb_div.add_style("padding-top: 1px")

            thumb = ThumbWdg()
            thumb.set_sobject(login)
            thumb_div.add(thumb)
            thumb.set_icon_size(15)

            login_div.add(login.get_full_name())

            login_div.add_behavior( {
            'type': 'click_up',
            'sobject_display_expr' : self.sobject_display_expr,
            'tab_view' : self.tab_view,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_schedule_top");
            var class_name = 'tactic.ui.tools.schedule_wdg.ScheduleUserToolWdg';
            var login = bvr.src_el.getAttribute("spt_login")

            var kwargs = {
                login: login
            };
            if (bvr.sobject_display_expr)
                kwargs['sobject_display_expr'] = bvr.sobject_display_expr;
            if (bvr.tab_view)
                kwargs['tab_view'] = bvr.tab_view;

            var content = top.getElement(".spt_schedule_content");
            spt.panel.load(content, class_name, kwargs);
            ''' 
            } )
            login_div.add_hover()


        return logins_div


    def get_schedule_wdg(self):

        div = DivWdg()
        div.add_style("width: 500px")
        div.add_style("height: 500px")
        div.add("Click on a user to display their schedule")
        return div



class ScheduleUserToolWdg(BaseRefreshWdg):

    def init(self):
        self.sobject_display_expr = self.kwargs.get('sobject_display_expr')
        self.tab_view = self.kwargs.get('tab_view')

    def get_display(self):

        top = self.top
        login = self.kwargs.get("login")
        if not login or login == "$LOGIN":
            login = Environment.get_user_name()


        login_sobj = Login.get_by_code(login)

        #top.add_style("margin-top: -2px")
        #top.add_style("margin-left: -2px")


        thumb_div = DivWdg()
        thumb_div.add_style("float: left")
        thumb_div.add_style("margin-right: 5px")
        thumb_div.add_style("margin-bottom: 5px")
        thumb_div.add_style("padding-top: 1px")
        thumb = ThumbWdg()
        thumb.set_sobject(login_sobj)
        thumb_div.add(thumb)
        thumb.set_icon_size(90)
        thumb.set_aspect("height")

        full_name = login_sobj.get_full_name()

        info_wdg = DivWdg()
        top.add(info_wdg)

        name_wdg = DivWdg()
        info_wdg.add(thumb_div)
        info_wdg.add(name_wdg)
        name_wdg.add("&nbsp;"*3)
        name_wdg.add(full_name)
        name_wdg.add_style("font-size: 1.5em")
        name_wdg.add_style("font-weight: bold")
        name_wdg.add_style("padding: 5px")
        #name_wdg.add_style("margin-left: -10px")
        name_wdg.add_color("background", "background3")
        name_wdg.add_style("height: 20px")
        name_wdg.add_style("margin-bottom: 0px")
        name_wdg.add_border()

        info_wdg.add("<br/>")



        from tactic.ui.container import TabWdg

        # return if the supplied tab view has a config xml
        if self.tab_view:
            search = Search("config/widget_config")
            search.add_filter("category", "TabWdg")
            search.add_filter("view", self.tab_view)
            config_sobj = search.get_sobject()
            if config_sobj:
              
                config_xml = config_sobj.get_value('config')
                # replace the variable $login with the login clicked
                if login:
                    config_xml = config_xml.replace('$login', login)
               
                tab = TabWdg(config_xml=config_xml, view=self.tab_view, show_add=False, show_remove=False)
                top.add(tab)
                return top



        config_xml = []
        config_xml.append('<config>')
        config_xml.append('<tab>')

        config_xml.append('''
        <element name='schedule'>
          <display class='tactic.ui.widget.TaskCalendarWdg'>
            <assigned>%s</assigned>
            <sobject_display_expr>%s</sobject_display_expr>
            <show_header>true</show_header>
            <show_border>false</show_border>
          </display>
        </element> 
        ''' % (login, self.sobject_display_expr))


        config_xml.append('''
        <element name='activity'>
          <display class='tactic.ui.widget.ActivityCalendarWdg'>
            <login>%s</login>
            <cell_width>100px</cell_width>
            <cell_height>50px</cell_height>
            <show_header>true</show_header>
            <show_border>false</show_border>
          </display>
        </element> 
        ''' % login)
 


        config_xml.append('''
        <element name='tasks'>
          <display class='tactic.ui.panel.FastTableLayoutWdg'>
            <search_type>sthpw/task</search_type>
            <view>table</view>
            <expression>@SOBJECT(sthpw/task['assigned','%s']['@ORDER_BY', 'bid_start_date desc'])</expression>
            <mode>simple</mode>
          </display>
        </element> 
        ''' % login)
 

        config_xml.append('''
        <element name='work_hours'>
          <display class='tactic.ui.widget.SObjectCalendarWdg'>
            <login>%s</login>
            <!--
            <cell_width>100px</cell_width>
            -->
            <cell_height>50px</cell_height>
            <show_header>true</show_header>
            <show_border>false</show_border>
            <search_type>sthpw/work_hour</search_type>
            <handler>tactic.ui.widget.WorkHourCalendarDayWdg</handler>
            <start_date_col>day</start_date_col>
            <end_date_col>day</end_date_col>
          </display>
        </element> 
        ''' % login)



        config_xml.append('''
         <element name='recent transactions'>
          <display class='tactic.ui.panel.FastTableLayoutWdg'>
            <search_type>sthpw/transaction_log</search_type>
            <view>table</view>
            <expression>@SOBJECT(sthpw/transaction_log['login','%s']['@ORDER_BY','timestamp desc']['@LIMIT','30'])</expression>
            <element_names>code,timestamp,namespace,description,transaction_log_hidden</element_names>
            <show_shelf>false</show_shelf>
            <show_select>false</show_select>
          </display>
        </element> 
        ''' % login)



        config_xml.append('</tab>')
        config_xml.append('</config>')
        config_xml = "".join(config_xml)

        tab = TabWdg(config_xml=config_xml, view='tab', show_add=False, show_remove=False)
        top.add(tab)
        tab.add_style("margin-left: -2px")
        tab.add_style("margin-right: -2px")

        return top





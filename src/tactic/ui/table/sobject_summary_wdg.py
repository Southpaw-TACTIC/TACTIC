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


__all__ = ['SObjectSummaryElementWdg', 'SObjectFilesElementWdg']

from pyasm.common import TacticException, jsonloads

from tactic.ui.common import SimpleTableElementWdg
from pyasm.web import DivWdg
from pyasm.widget import IconWdg

from button_wdg import ButtonElementWdg
from pyasm.biz import Project
from pyasm.search import Search

class SObjectSummaryElementWdg(SimpleTableElementWdg):

    ARGS_KEYS = {
    }

    def is_sortable(self):
        return False

    def is_editable(self):
        return False

    def get_required_columns(self):
        return []

    def get_display(self):

        top = self.top
        top.add_style("min-width: 110px")


        sobject = self.get_current_sobject()
        
        if isinstance(sobject, Project):
            num_tasks = Search.eval("@COUNT(sthpw/task['project_code','%s'])"%sobject.get_code())
            num_snapshots = Search.eval("@COUNT(sthpw/snapshot['project_code','%s'])"%sobject.get_code())
            num_notes = Search.eval("@COUNT(sthpw/note['project_code','%s'])"%sobject.get_code())
            work_hours = Search.eval("@GET(sthpw/work_hour['project_code','%s'].straight_time)"%sobject.get_code())
        else:
            num_tasks = Search.eval("@COUNT(sthpw/task['project_code',$PROJECT])", sobjects=[sobject])
            num_snapshots = Search.eval("@COUNT(sthpw/snapshot['project_code',$PROJECT])", sobjects=[sobject])
            num_notes = Search.eval("@COUNT(sthpw/note['project_code',$PROJECT])", sobjects=[sobject])
            work_hours = Search.eval("@GET(sthpw/work_hour['project_code',$PROJECT].straight_time)", sobjects=[sobject])

        """
        tasks = sobject.get_related_sobjects("sthpw/task")
        snapshots = sobject.get_related_sobjects("sthpw/snapshot")
        notes = sobject.get_related_sobjects("sthpw/note")
        work_hours = sobject.get_related_sobjects("sthpw/work_hour")
        """
        line_div = DivWdg()
        top.add(line_div)
        line_div.add_style("padding: 3px")
        icon = IconWdg("Number of task", IconWdg.CALENDAR)
        line_div.add(icon)
        #num_tasks = len(tasks)
        if not num_tasks:
            num_tasks = 0
            line_div.add_style("opacity: 0.15")
            line_div.add_style("font-style: italic")
        line_div.add("%s task(s)<br/>" % num_tasks)


        line_div.add_behavior( {
            'type': 'click_up',
            'search_key': sobject.get_search_key(),
            'cbjs_action': '''
            var row = bvr.src_el.getParent(".spt_table_row");
            var class_name = 'tactic.ui.panel.ViewPanelWdg';
            var kwargs = {
                search_type: 'sthpw/task',
                view: 'table',
                search_key: bvr.search_key,
                show_shelf: false
            }
            spt.table.remove_hidden_row(row);
            spt.table.add_hidden_row(row, class_name, kwargs);
            '''
        } )



        line_div = DivWdg()
        top.add(line_div)
        line_div.add_style("padding: 3px")
        icon = IconWdg("Number of check-in(s)", IconWdg.PUBLISH)
        line_div.add(icon)
        #num_snapshots = len(snapshots)
        if not num_snapshots:
            num_snapshots = 0
            line_div.add_style("opacity: 0.15")
            line_div.add_style("font-style: italic")
        line_div.add("%s check-in(s)<br/>" % num_snapshots )

        line_div.add_behavior( {
            'type': 'click_up',
            'search_key': sobject.get_search_key(),
            'cbjs_action': '''
            var row = bvr.src_el.getParent(".spt_table_row");
            var class_name = 'tactic.ui.panel.ViewPanelWdg';
            var kwargs = {
                search_type: 'sthpw/snapshot',
                view: 'table',
                search_key: bvr.search_key,
                show_shelf: false
            }
            spt.table.remove_hidden_row(row);
            spt.table.add_hidden_row(row, class_name, kwargs);
            '''
        } )




        line_div = DivWdg()
        top.add(line_div)
        line_div.add_style("padding: 3px")
        icon = IconWdg("Number of notes", IconWdg.NOTE)
        line_div.add(icon)
        #num_notes = len(notes)
        if not num_notes:
            num_notes = 0
            line_div.add_style("opacity: 0.15")
            line_div.add_style("font-style: italic")
        line_div.add("%s note(s)<br/>" % num_notes)


        line_div = DivWdg()
        top.add(line_div)
        line_div.add_style("padding: 3px")
        icon = IconWdg("Work Hours", IconWdg.CLOCK)
        line_div.add(icon)
        total = 0
        for work_hour in work_hours:
            straight_time = work_hour
            if straight_time:
                total += straight_time
        if not work_hours:
            work_hours = 0
            line_div.add_style("opacity: 0.15")
            line_div.add_style("font-style: italic")
        line_div.add("%s work hours<br/>" % total)


        return top



class SObjectFilesElementWdg(ButtonElementWdg):

    def is_editable(cls):
        return False
    is_editable = classmethod(is_editable)


    def init(self):
        # FIXME: this dos not work here yet .. do it in javascript
        #layout = self.get_layout_wdg()
        #print "layout: ", layout

        mode = self.get_option("mode")
        if not mode:
            mode = 'popup'

        self.set_option('icon', "FOLDER")
        self.kwargs['cbjs_action'] = '''
            var class_name = 'tactic.ui.checkin.SObjectDirListWdg';
            var row = bvr.src_el.getParent(".spt_table_row");


            spt.table.set_table(bvr.src_el);
            var search_keys = spt.table.get_selected_search_keys();
            if (search_keys.length == 0) {
                var search_key = row.getAttribute("spt_search_key");
                search_keys = [search_key];
            }

            var kwargs = {
                search_keys: search_keys
            };

            var mode = 'xxx';
            var layout = bvr.src_el.getParent(".spt_tool_top");
            if (layout != null) {
                mode = 'tool'
            }

            if (mode == 'tool') {
                spt.app_busy.show("Loading ...");
                var layout = bvr.src_el.getParent(".spt_tool_top");
                var element = layout.getElement(".spt_tool_content");
                spt.panel.load(element, class_name, kwargs);
                spt.app_busy.hide();
            }
            else {
                spt.panel.load_popup("Files", class_name, kwargs);
            }
            '''



        super(SObjectFilesElementWdg, self).init()



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

__all__ = ['IngestionToolWdg', 'IngestionToolWdg2', 'IngestionToolDirListWdg', 'IngestionToolShelfWdg', 'IngestionProcessWdg']

import tacticenv

import os, re

from pyasm.common import Common, jsonloads, jsondumps
from pyasm.biz import Project
from pyasm.command import Command
from pyasm.search import Search, SearchType
from pyasm.web import DivWdg, Table, WebContainer
from pyasm.widget import TextWdg, SelectWdg, TextAreaWdg, IconWdg, HiddenWdg, CheckboxWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ActionButtonWdg, IconButtonWdg, DirListWdg
from tactic.ui.container import DynamicListWdg, ResizableTableWdg, TabWdg


class IngestionToolWdg2(BaseRefreshWdg):

    def get_value(my, name):
        web = WebContainer.get_web()
        value = web.get_form_value(name)
        if not value:
            value = my.kwargs.get(name)

        return value
        



    def get_display(my):

        top = my.top
        top.add_class("spt_ingestion_top")
        my.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)
        inner.add_color("background", "background")
        inner.add_border()
        inner.add_style("padding: 10px")

        my.session_code = my.get_value("session_code")
        if my.session_code:
            my.session = Search.get_by_code("config/ingest_session", my.session_code)

        else:

            my.session_code = "session101"

            my.session = SearchType.create("config/ingest_session")
            my.session.set_value("code", my.session_code)

            base_dir = my.get_value("base_dir")
            if base_dir:
                my.session.set_value("base_dir", base_dir)

            location = my.get_value("location")
            if location:
                my.session.set_value("location", location)
            else:
                my.session.set_value("location", "local")
            my.session.commit()


        my.paths = my.get_value("paths")
 

        nav_div = DivWdg()
        inner.add(nav_div)
        nav_div.add( my.get_nav_wdg() )
        inner.add("<hr/>")

        table = ResizableTableWdg()
        inner.add(table)
        table.add_color("color", "color")

        left = table.add_cell()
        left_div = DivWdg()
        left.add(left_div)
        left_div.add(my.get_session_wdg())
        left_div.add_style("padding: 10px")
        left_div.add_style("height: 100%")
        left_div.add_style("min-height: 500px")
        left_div.add_border()
        left_div.set_round_corners(corners=["TL","TR"])
        left_div.add_class("SPT_RESIZABLE")

        right = table.add_cell()
        right.add(my.get_content_wdg())
        return top


    def get_nav_wdg(my):

        #base_dir = my.kwargs.get("base_dir")
        #location = my.kwargs.get("location")
        base_dir = my.session.get_value("base_dir")
        location = my.session.get_value("location")

        nav_wdg = DivWdg()

        nav_wdg.add("<b>Session 101 - Clean up my Crap</b><hr/>")
    

        nav_wdg.add_style("margin-bottom: 10px")
        nav_wdg.add_class("spt_file_nav")
        nav_wdg.add_style("width: 575px")
        nav_wdg.add_border()
        nav_wdg.set_round_corners()
        nav_wdg.add_style("padding: 5px")

        button = ActionButtonWdg(title="Scan", tip="Scan for files in specified folder")
        button.add_style("float: right")
        button.add_style("margin-top: -5px")
        nav_wdg.add(button)


        from tactic.ui.input import TextInputWdg
        title_wdg = "Session Title: "
        nav_wdg.add(title_wdg)
        text = TextInputWdg(name="title")
        text.add_class("spt_title")
        text.add_style("width: 300px")
        nav_wdg.add(text)

        nav_wdg.add("<br/><br/>")


        folder_wdg = "Base folder of this session: "
        nav_wdg.add(folder_wdg)

        text = TextInputWdg(name="base_dir")
        text.add_class("spt_base_dir")
        text.add_style("width: 300px")
        if base_dir:
            text.set_value(base_dir)
        nav_wdg.add(text)

        # add a hidden paths variable
        text = HiddenWdg("paths")
        text.add_class("spt_paths")
        nav_wdg.add(text)

        nav_wdg.add("<br/>")

        # add a hidden paths variable
        select = SelectWdg("location")
        if location:
            select.set_value(location)
        nav_wdg.add("<br/>")
        nav_wdg.add("Folder is on ")
        nav_wdg.add(select)
        select.set_option("values", "local|server")

        
        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''

        var top = bvr.src_el.getParent(".spt_ingestion_top");
        var nav = top.getElement(".spt_file_nav");

        var nav_values = spt.api.Utility.get_input_values(nav,null,false);

        var base_dir = nav_values.base_dir;
        var location = nav_values.location;

        spt.app_busy.show("Scanning", base_dir);

        if (location == 'local') {
            var applet = spt.Applet.get();
            var paths = applet.list_dir(base_dir, 2);
            var paths_el = nav.getElement(".spt_paths");
            var js_paths = [];
            for (var i = 0; i < paths.length; i++) {
                var js_path = paths[i].replace(/\\\\/g,"/");
                if (applet.is_dir(js_path) ) {
                    js_path = js_path + '/';
                    js_paths.push(js_path);
                }
                //if (i > 100) break;
                else {
                    js_paths.push(js_path);
                }
            }

            paths_el.value = js_paths.join("|");

        }

        //var nav_values = spt.api.Utility.get_input_values(nav,null,false);
        //spt.panel.refresh(top, nav_values);

        spt.tab.set_tab_top(top);
        spt.tab.select("files")
        var class_name = "tactic.ui.tools.IngestionToolDirListWdg";
        var kwargs = {
            base_dir: base_dir,
            location: location,
            paths: js_paths
        }
        spt.tab.load_selected("files", "Files", class_name, kwargs);

        spt.app_busy.hide();
        '''
        } )

        return nav_wdg



    def get_session_wdg(my):

        div = DivWdg()
        div.add_style("width: 150px")

        search = Search("config/ingest_rule")
        rules = search.get_sobjects()

        add = ActionButtonWdg(title="+", tip="Add new rule", size='small')
        div.add(add)
        add.add_style("margin-top: -6px")
        add.add_behavior( {
        'type': 'click_up',
        'session_code': my.session.get_code(),
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_ingestion_top");
        spt.tab.set_tab_top(top);
        var class_name = 'tactic.ui.tools.IngestionToolWdg';
        var kwargs = {
            session_code: bvr.session_code
        };
        spt.tab.select("rules");
        spt.tab.load_selected("rules", "Rules", class_name, kwargs);
        '''
        } )
        add.add_style("float: right")


        div.add("<b>Rules</b><hr/>")

        if not rules:
            div.add("<br/><i>No rules found</i><br/>")

        for rule in rules:
            rule_code = rule.get_code()
            rule_title = rule.get_value("title")

            rule_div = DivWdg()
            div.add(rule_div)
            rule_div.add_style("padding: 3px")

            hover = rule_div.get_color("background", -10)
            rule_div.add_behavior( {
                'type': 'hover',
                'hover': hover,
                'cbjs_action_over': '''
                bvr.src_el.setStyle("background", bvr.hover);
                ''',
                'cbjs_action_out': '''
                bvr.src_el.setStyle("background", "");
                '''
            } )
            rule_div.add_class("hand")

            checkbox = CheckboxWdg("whatever")
            rule_div.add(checkbox)

            rule_div.add(rule_title)

            rule_div.add_behavior( {
            'type': 'click_up',
            'rule_code': rule_code,
            'session_code': my.session_code,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_ingestion_top");
            spt.tab.set_tab_top(top);
            var class_name = 'tactic.ui.tools.IngestionToolWdg';
            var kwargs = {
                location: 'server',
                rule_code: bvr.rule_code,
                session_code: bvr.session_code
            };
            spt.tab.select("rules");
            spt.tab.load_selected("rules", "Rules", class_name, kwargs);
            '''
            } )


        return div




    def get_content_wdg(my):

        base_dir = my.session.get_value("base_dir")
        location = my.session.get_value("location")
        session_code = my.session.get_code()

        div = DivWdg()
        #repo_dir = "/home/apache/inhance_repo"
        repo_dir = "/home/apache/assets/simulation/vehicles"
        repo_location = "server"
        config_xml = []
        config_xml.append('''
        <config>
        <tab>
        ''')

        config_xml.append('''
        <element name='files'>
          <display class='tactic.ui.tools.IngestionToolDirListWdg'>
            <base_dir>%s</base_dir>
            <location>%s</location>
            <session_code>%s</session_code>
            <cache_key>paths</cache_key>
          </display>
        </element>
        ''' % (base_dir, location, session_code) )

        config_xml.append('''
        <element name='rules'>
          <display class='tactic.ui.tools.IngestionToolWdg'>
            <session_code>%s</session_code>
          </display>
        </element>
        ''' % (session_code) )

        config_xml.append('''
        <element name='repository'>
          <display class='tactic.ui.tools.IngestionToolDirListWdg'>
            <base_dir>%s</base_dir>
            <location>%s</location>
            <session_code>%s</session_code>
            <cache_key>repo_paths</cache_key>
          </display>
        </element>
        ''' % ( repo_dir, repo_location, my.session_code ) )

        config_xml.append('''
        <element name='tools'>
          <display class='tactic.ui.tools.IngestionToolShelfWdg'>
            <base_dir>%s</base_dir>
            <location>%s</location>
          </display>
        </element>
        ''' % ( base_dir, location ) )

        config_xml.append('''
        </tab>
        </config>
        ''')


        config_xml = "".join(config_xml)
        tab = TabWdg(config_xml=config_xml, width="700px")
        div.add(tab)
        return div



class IngestionToolDirListWdg(BaseRefreshWdg):

    def get_display(my):

        session_code = my.kwargs.get("session_code")
        session_code = 'session101'

        session = Search.get_by_code("config/ingest_session", session_code)

        data = session.get_json_value("data")
        if data == None:
            data = {}

        top = my.top
        top.add_class("spt_ingest_dir_list_top")
        my.set_as_panel(top)

        inner = DivWdg()
        top.add(inner)
        inner.add_style("padding: 10px")
        inner.add_color("background", "background")

        base_dir = my.kwargs.get("base_dir")
        location = my.kwargs.get("location")
        rescan = my.kwargs.get("rescan")
        if rescan in [True, 'true']:
            rescan = True
        else:
            rescan = False

        rescan = ActionButtonWdg(title='Rescan', tip="Rescan file system")
        inner.add(rescan)
        rescan.add_style("float: right")
        rescan.add_behavior( {
        'type': 'click_up',
        'base_dir': base_dir,
        'cbjs_action': '''
        spt.app_busy.show("Scanning", "Scanning files in " + bvr.base_dir);
        var top = bvr.src_el.getParent(".spt_ingest_dir_list_top");
        spt.panel.refresh(top);
        spt.app_busy.hide();
        '''
        } )

        import datetime
        last_scan = datetime.datetime.now()
        last_scan_wdg = DivWdg()
        inner.add(last_scan_wdg)
        last_scan_wdg.add("Last Scan: %s" % last_scan)
        last_scan_wdg.add_style("margin-bottom: 5px")


        found_wdg = DivWdg()
        inner.add(found_wdg)
        found_wdg.add_style("margin-bottom: 5px")

        inner.add("<hr/>")



        show_handled = my.kwargs.get("show_handled")
        show_handled = False
        if show_handled in [False, 'false']:
            try:
                scan_path = "/tmp/scan"
                import codecs
                f = codecs.open(scan_path, 'r', 'utf-8')
                ignore = jsonloads( f.read() )
                f.close()
            except Exception, e:
                print("Error: ", e.message)
                ignore = None
        else:
            ignore = None


        # check for rescan
        cache_key = my.kwargs.get("cache_key")
        rescan = True
        if rescan == True:
            paths = []
        else:
            paths = data.get(cache_key)
            if not paths:
                paths = []
        dir_list_wdg = DirListWdg(paths=paths, base_dir=base_dir, location=location, ignore=ignore, depth=2)

        # cache the paths
        if rescan:
            paths = dir_list_wdg.get_paths()
            data['paths'] = paths

            session.set_json_value("data", data)
            session.commit()


        # add the paths found
        num_paths = dir_list_wdg.get_num_paths()
        found_wdg.add("Found: %s items" % num_paths)

        inner.add(dir_list_wdg)

        return top


class IngestionToolShelfWdg(BaseRefreshWdg):
    '''These are the tools withing the Ingestion tool widget'''
    def get_display(my):
        top = my.top
        top.add_color("background", "background")
        top.add_class("spt_ingestion_shelf_top")

        #base_dir = my.kwargs.get("base_dir")
        #location = my.kwargs.get("location")
        base_dir = "/home/apache/Structures"
        location = "server"

        scan = ActionButtonWdg(title="Scan Files", tip="Scan Files")
        top.add(scan)
        scan.add_behavior( {
        'type': 'click_up',
        'base_dir': base_dir,
        'location': location,
        'cbjs_action': '''
        var class_name = 'tactic.ui.tools.IngestionToolDirListWdg';
        var kwargs = {
            base_dir: bvr.base_dir,
            location: bvr.location
        };
        var top = bvr.src_el.getParent(".spt_ingestion_shelf_top");
        var content = top.getElement(".spt_content");
        spt.panel.load(content, class_name, kwargs);

        '''
        } )
        scan.add_style("float: left")


        scan = ActionButtonWdg(title="Handled", tip="Show Handled Files")
        top.add(scan)
        scan.add_behavior( {
        'type': 'click_up',
        'base_dir': base_dir,
        'location': location,
        'cbjs_action': '''
        var class_name = 'tactic.ui.tools.IngestionToolScanWdg';
        var kwargs = {
        };
        var top = bvr.src_el.getParent(".spt_ingestion_shelf_top");
        var content = top.getElement(".spt_content");
        spt.panel.load(content, class_name, kwargs);

        '''
        } )
        scan.add_style("float: left")


        scan = ActionButtonWdg(title="Not Handled", tip="Show Files Not Handled")
        top.add(scan)
        scan.add_behavior( {
        'type': 'click_up',
        'base_dir': base_dir,
        'location': location,
        'cbjs_action': '''
        var class_name = 'tactic.ui.tools.IngestionToolScanWdg';
        var kwargs = {
        };
        var top = bvr.src_el.getParent(".spt_ingestion_shelf_top");
        var content = top.getElement(".spt_content");
        spt.panel.load(content, class_name, kwargs);

        '''
        } )





        top.add("<hr/>")


        content = DivWdg()
        top.add(content)
        content.add_style("height: 100%")
        content.add_style("padding: 10px")
        content.add_class("spt_content")
        content.add("&nbsp;")

        return top




class IngestionToolWdg(BaseRefreshWdg):

    def get_value(my, name):
        value = my.kwargs.get(name)
        if not value:
            web = WebContainer.get_web()
            value = web.get_form_value(name)
        if my.data and not value:
            value = my.data.get(name)

        return value
        

    def get_display(my):

        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_ingestion_top")
        top.add_color("background", "background", -5)

        my.data = {}

        rules_div = DivWdg()
        top.add(rules_div)
        rules_div.add_style("padding: 10px")

        rules_div.add("Rules: ")

        rules_select = SelectWdg("rule_code")
        rule_code = my.get_value('rule_code')
        if rule_code:
            rules_select.set_value(rule_code)
        rules_select.set_option("query", "config/ingest_rule|code|title")
        rules_select.add_empty_option("-- New --")
        rules_div.add(rules_select)
        rules_select.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_ingestion_top");
        value = bvr.src_el.value;
        var class_name = 'tactic.ui.tools.IngestionToolWdg';
        spt.panel.load(top, class_name, {rule_code: value} );
        '''
        } )

        rules_div.add("<hr/>")

        # read from the database
        if rule_code:
            search = Search("config/ingest_rule")
            search.add_filter("code", rule_code)
            sobject = search.get_sobject()
        else:
            sobject = None
        if sobject:
            my.data = sobject.get_value("data")
            if my.data:
                my.data = jsonloads(my.data)

        session_code = my.kwargs.get("session_code")
        if session_code:
            session = Search.get_by_code("config/ingest_session", session_code)
        else:
            if sobject:
                session = sobject.get_related_sobject("config/ingest_session")
                print("sobject: ", sobject.get_code(), sobject.get_value("spt_ingest_session_code"))
                print("parent: ", session)
            else:
                session = None


        if not session:
            #session = SearchType.create("config/ingest_session")
            #session.set_value("code", "session101")
            #session.set_value("location", "local")
            ##session.set_value("base_dir", "C:")
            top.add("No session defined!!!")
            return top



        rule = ""
        filter = ""
        ignore = ""


        # get the base path
        if sobject:
            base_dir = sobject.get_value("base_dir")
        else:
            base_dir = ''

        #else:
        #    base_dir = my.get_value("base_dir")
        #if not base_dir:
        #    base_dir = ''

        if sobject:
            title = sobject.get_value("title")
        else:
            title = ''

        if sobject:
            code = sobject.get_value("code")
        else:
            code = ''


        file_list = my.get_value("file_list")
        scan_type = my.get_value("scan_type")
        action_type = my.get_value("action_type")
        rule = my.get_value("rule")
        if not rule:
            rule = base_dir

        # get the rule for this path
        checkin_mode = "dir"
        depth = 0

        table = Table()
        rules_div.add(table)
        table.add_color("color", "color")


        from tactic.ui.input.text_input_wdg import TextInputWdg


        # add the title
        table.add_row()
        td = table.add_cell()
        td.add("Title: ")
        td = table.add_cell()

        text = TextInputWdg(name="title")
        td.add(text)
        if title:
            text.set_value(title)
        text.add_class("spt_title")
        text.add_style("width: 400px")
        #text.add_color("background", "background", -10)

        # add the optional code
        table.add_row()
        td = table.add_cell()
        td.add("Code (optional): ")
        td = table.add_cell()

        text = TextInputWdg(name="code")
        td.add(text)
        if code:
            text.set_value(code)
            text.set_readonly()
            text.add_color("background", "background", -10)
        text.add_class("spt_code")
        text.add_style("width: 400px")





        table.add_row()
        td = table.add_cell()
        td.add_style("height: 10px")
        td.add("<hr/>")


        table.add_row()
        td = table.add_cell()
        td.add("<b>Scan:</b><br/>")
        td.add("The following information will be used to find the paths that will be operated on by the ingestion process<br/><br/>")


        # add a scan type
        table.add_row()
        td = table.add_cell()
        td.add("Type: ")
        select = SelectWdg("scan_type")
        select.add_class("spt_scan_type")
        td = table.add_cell()
        td.add(select)
        select.set_value( my.get_value("action") )
        labels = ['Simple List', 'Rule', 'Script']
        values = ['list', 'rule', 'script']
        select.set_option("values", values)
        select.set_option("labels", labels)
        if scan_type:
            select.set_value(scan_type)

        table.add_row() 
        table.add_cell("&nbsp;")

        select.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_ingestion_top");
        value = bvr.src_el.value;

        var elements = top.getElements(".spt_scan_list");
        for (var i = 0; i < elements.length; i++) {
          if (value == 'list')
            spt.show(elements[i]);
          else
            spt.hide(elements[i]);
        }

        var elements = top.getElements(".spt_scan_rule");
        for (var i = 0; i < elements.length; i++) {
          if (value == 'rule')
            spt.show(elements[i]);
          else
            spt.hide(elements[i]);
        }
        var elements = top.getElements(".spt_scan_script");
        for (var i = 0; i < elements.length; i++) {
          if (value == 'script')
            spt.show(elements[i]);
          else
            spt.hide(elements[i]);
        }

        '''
        } )

        # add in a list of stuff
        tbody = table.add_tbody()
        tbody.add_class("spt_scan_list")
        if scan_type != 'list':
            tbody.add_style("display: none")

        tr = table.add_row()
        td = table.add_cell()
        td.add("List of files: ")
        td = table.add_cell()

        text = TextAreaWdg(name="file_list")
        td.add(text)
        text.add_style("width: 400px")
        #text.set_readonly()
        #text.add_color("background", "background", -10)
        text.set_value(file_list)

        table.close_tbody()



        # add rule scan mode
        tbody = table.add_tbody()
        tbody.add_class("spt_scan_rule")
        if scan_type != 'rule':
            tbody.add_style("display: none")



        # add the path
        tr = table.add_row()
        td = table.add_cell()
        td.add("Starting Path: ")
        td = table.add_cell()

        hidden = HiddenWdg("session_code", session.get_code() )
        td.add(hidden)

        text = TextInputWdg(name="base_dir")
        td.add(text)
        text.set_value(base_dir)
        text.add_style("width: 400px")
        #text.set_readonly()
        #text.add_color("background", "background", -10)
        text.set_value(base_dir)



        # add rule
        tr = table.add_row()
        td = table.add_cell()
        td.add("Tag Rule: ")
        td = table.add_cell()

        text = TextInputWdg(name="rule")
        td.add(text)
        text.add_style("width: 400px")
        text.set_value(rule)


        tr = table.add_row()
        td = table.add_cell()
        td.add("Filter: ")
        td = table.add_cell()
        text = TextWdg("filter")
        td.add(text)
        text.set_value( my.get_value("filter") )
        text.add_style("width: 400px")
        text.add_style("padding: 2px")
        text.add_style("-moz-border-radius: 5px")




        tr = table.add_row()
        td = table.add_cell()
        td.add("Ignore: ")
        td = table.add_cell()
        text = TextWdg("ignore")
        td.add(text)
        text.set_value( my.get_value("ignore") )
        text.set_value(ignore)
        text.add_style("width: 400px")
        text.add_style("padding: 2px")
        text.add_style("-moz-border-radius: 5px")


        table.add_row()
        td = table.add_cell()
        td.add("Validation script: ")
        td.add_style("vertical-align: top")
        td.add_style("padding-top: 5px")
        td = table.add_cell()
        text = TextInputWdg(name="validation_script")
        text.set_value( my.get_value("validation_script") )
        text.add_style("width: 400px")
        td.add(text)

        icon = IconButtonWdg(title='Edit Validation Script', icon=IconWdg.EDIT)
        icon.add_style("float: right")
        td.add(icon)
        icon.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.named_events.fire_event("show_script_editor");

        var top = bvr.src_el.getParent(".spt_ingestion_top");
        var values = spt.api.Utility.get_input_values(top, null, false);

        var kwargs = {
            script_path: values.validation_script
        }
        setTimeout( function() {
        spt.js_edit.display_script_cbk(evt, kwargs)
        }, 500 );
        '''
        } )



        table.close_tbody()



        # add the script path
        tbody = table.add_tbody()
        tbody.add_class("spt_scan_script")
        if scan_type != 'script':
            tbody.add_style("display: none")


        tr = table.add_row()
        td = table.add_cell()
        td.add("Script Path: ")
        td = table.add_cell()

        text = TextInputWdg(name="script_path")
        td.add(text)
        text.add_style("width: 400px")


        table.close_tbody()



        table.add_row()
        td = table.add_cell("<hr/>")



        table.add_row()
        td = table.add_cell()
        td.add("<b>Action</b><br/>")
        td.add("The following information define the actions that will be used on each matched path<br/><br/>")


        # pick the type of action
        table.add_row()
        td = table.add_cell()
        td.add("Type: ")
        select = SelectWdg("action_type")
        td = table.add_cell()
        td.add(select)
        labels = ['Checkin', 'Ignore']
        values = ['checkin', 'ignore']
        select.set_option("values", values)
        select.set_option("labels", labels)
        select.add_empty_option("-- Select --")
        if action_type:
            select.set_value(action_type)

        select.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_ingestion_top");
        value = bvr.src_el.value;

        var elements = top.getElements(".spt_action_ignore");
        for (var i = 0; i < elements.length; i++) {
          if (value == 'ignore')
            spt.show(elements[i]);
          else
            spt.hide(elements[i]);
        }

        var elements = top.getElements(".spt_action_checkin");
        for (var i = 0; i < elements.length; i++) {
          if (value == 'checkin')
            spt.show(elements[i]);
          else
            spt.hide(elements[i]);
        }

        '''
        } )



        table.add_row()
        td = table.add_cell("<br/>")



        # add the script path
        tbody = table.add_tbody()
        tbody.add_class("spt_action_checkin")
        if action_type != 'checkin':
            tbody.add_style("display: none")



        # add the checkin type
        table.add_row()
        td = table.add_cell()
        td.add("Action: ")
        select = SelectWdg("action")
        td = table.add_cell()
        td.add(select)
        select.set_value( my.get_value("action") )
        labels = ['File Checkin', 'Directory Checkin', 'Sequence Checkin']
        values = ['file', 'directory', 'sequence', 'ignore']
        select.set_option("values", values)
        select.set_option("labels", labels)





        table.add_row()
        td = table.add_cell()
        td.add("Mode: ")
        select = SelectWdg("mode")
        td = table.add_cell()
        td.add(select)
        labels = ['Copy', 'Move', 'In Place']
        values = ['copy', 'move', 'inplace']
        select.set_option("values", values)
        select.set_option("labels", labels)






        # add the search_type
        table.add_row()
        td = table.add_cell()
        td.add("sType: ")
        td = table.add_cell()
        select = SelectWdg("search_type")
        td.add(select)
        search_types = Project.get().get_search_types()
        values = [x.get_value("search_type") for x in search_types]
        select.set_option("values", values)

        search_type = my.kwargs.get("search_type")
        if search_type:
            select.set_value(search_type)



        # add the search_type
        table.add_row()
        td = table.add_cell()
        td.add("Context: ")
        td = table.add_cell()
        select = SelectWdg("context")
        td.add(select)
        select.set_option("values", ['publish', 'by rule', 'custom'])




        # add extra values
        extra_div = DivWdg()
        text = TextWdg("extra_name")
        text.add_attr("spt_is_multiple", "true")
        extra_div.add(text)
        extra_div.add(" = ")
        text = TextWdg("extra_value")
        extra_div.add(text)
        text.add_attr("spt_is_multiple", "true")

        template_div = DivWdg()
        text = TextWdg("extra_name")
        text.add_attr("spt_is_multiple", "true")
        template_div.add(text)
        template_div.add(" = ")
        text = TextWdg("extra_value")
        template_div.add(text)
        text.add_attr("spt_is_multiple", "true")


        table.close_tbody()



        table.add_row()
        td = table.add_cell("<br/>")

        table.add_row()
        td = table.add_cell()
        td.add("Extra Keywords: ")
        td.add_style("vertical-align: top")
        td.add_style("padding-top: 5px")
        td = table.add_cell()
        text = TextWdg("keywords")
        text.add_style("width: 300px")
        td.add(text)





        table.add_row()
        td = table.add_cell()
        td.add("Extra Values: ")
        td.add_style("vertical-align: top")
        td.add_style("padding-top: 5px")
        td = table.add_cell()
        extra_list = DynamicListWdg()
        td.add(extra_list)
        extra_list.add_item(extra_div)
        extra_list.add_template(template_div)


        table.add_row()
        table.add_cell("&nbsp;")



        table.add_row()
        td = table.add_cell()
        td.add("Process script: ")
        td.add_style("vertical-align: top")
        td.add_style("padding-top: 5px")
        td = table.add_cell()
        text = TextWdg("process_script")
        text.add_style("width: 300px")
        td.add(text)
        text.set_value( my.get_value("process_script") )


        icon = IconButtonWdg(title='Edit Process Script', icon=IconWdg.EDIT)
        icon.add_style("float: right")
        td.add(icon)
        icon.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.named_events.fire_event("show_script_editor");

        var top = bvr.src_el.getParent(".spt_ingestion_top");
        var values = spt.api.Utility.get_input_values(top, null, false);

        var kwargs = {
            script_path: values.process_script
        }

        // need to wait for this
        setTimeout( function() {
        spt.js_edit.display_script_cbk(evt, kwargs)
        }, 500 );
        '''
        } )



        table.add_row()
        td = table.add_cell()
        td.add("Custom Naming: ")
        td.add_style("vertical-align: top")
        td.add_style("padding-top: 5px")
        td = table.add_cell()
        text = TextWdg("naming")
        text.add_style("width: 300px")
        td.add(text)




        table.add_row()
        td = table.add_cell()

        #td.add("<br clear='all'/>")
        td.add("<hr/>")


        behavior = {
            'type': 'click_up',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_ingestion_top");
            var values = spt.api.Utility.get_input_values(top, null, false);

            spt.app_busy.show("Scanning ...", values.base_dir);

            var class_name = 'tactic.ui.tools.IngestionProcessWdg';

            var server = TacticServerStub.get();
            values.mode = bvr.mode;

            values.is_local = 'true';

            // scan client side
            if (values.is_local == 'true') {
                var base_dir = values.base_dir;
                var applet = spt.Applet.get();
                var files = applet.list_recursive_dir(base_dir);
                // turn into a string
                var files_in_js = [];
                for (var i = 0; i < files.length; i++) {
                    var file = files[i].replace(/\\\\/g, "/");
                    files_in_js.push( file );
                }
                values.files = files_in_js;
                values.base_dir = base_dir;

                /*
                var server = TacticServerStub.get();
                var handoff_dir = server.get_handoff_dir();
                var applet = spt.Applet.get();
                for (var i = 0; i < files_in_js.length; i++) {
                    try {
                        var parts = files_in_js[i].split("/");
                        var filename = parts[parts.length-1];
                        spt.app_busy.show("Copying files to handoff", filename);
                        applet.copy_file(files_in_js[i], handoff_dir+"/"+filename);
                    } catch(e) {
                        log.error(e);
                    }

                }
                */
            }

            var info_el = top.getElement(".spt_info");
            spt.panel.load(info_el, class_name, values);
            spt.app_busy.hide();
            '''
        }


        # Save button
        button = ActionButtonWdg(title="Save", tip="Save Rule")
        td.add(button)
        button.add_style("float: right")
        behavior['mode'] = 'save'
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_ingestion_top");
            var values = spt.api.Utility.get_input_values(top, null, false);
            spt.app_busy.show("Saving ...");

            var class_name = 'tactic.command.CheckinRuleSaveCmd';
            var server = TacticServerStub.get();
            server.execute_cmd(class_name, values);

            spt.panel.refresh(top, {});

            spt.app_busy.hide();

            '''
        } )



 
        # Scan button
        button = ActionButtonWdg(title="Scan", tip="Click to Scan")
        td.add(button)
        button.add_style("float: left")


        # set a limit
        #limit = TextWdg("limit")
        #td.add(limit)
        #text.add_style("float: left")


        behavior = behavior.copy()
        behavior['mode'] = 'scan'
        button.add_behavior(behavior)

        # Test button
        button = ActionButtonWdg(title="Test", tip="Do a test of this rule")
        td.add(button)
        behavior = behavior.copy()
        behavior['mode'] = 'test'
        button.add_behavior(behavior)
        button.add_style("float: left")




        # Ingest button
        button = ActionButtonWdg(title="Ingest", tip="Click to start ingesting")
        td.add(button)
        behavior = behavior.copy()
        behavior['mode'] = 'checkin'
        button.add_behavior(behavior)



        table.add_behavior( {
            'type': 'listen',
            'event_name': 'file_browser|select',
            'cbjs_action': '''
            var dirname = bvr.firing_data.dirname;
            var top = bvr.src_el.getParent(".spt_ingestion_top");
            var kwargs = {
              base_dir: dirname
            };

            spt.panel.load(top, top.getAttribute("spt_class_name"), kwargs);
            '''
        })


        top.add( my.get_info_wdg() )

        return top


    def get_info_wdg(my):

        div = DivWdg()
        div.add_class("spt_info")


        return div



class IngestionProcessWdg(BaseRefreshWdg):

    def get_display(my):
        top = my.top

        top.add_style("padding: 10px")

        from tactic.command import IngestionCmd
        cmd = IngestionCmd(**my.kwargs)
        Command.execute_cmd(cmd)
        info = cmd.get_info()

        paths_matched = info.get("paths_matched")
        paths_not_matched = info.get("paths_not_matched")
        paths_irregular = info.get("paths_irregular")
        paths_invalid = info.get("paths_invalid")

        tags = info.get("tags")

        top.add("<br/>")
        #category_div = my.get_category_wdg(paths_matched, "Matched Paths", tags)
        #category_div = my.get_category_preview_wdg(paths_matched, "Matched Paths", tags)
        #top.add(category_div)

        category_div = my.get_category_wdg2(paths_matched, "Matched Paths", tags)
        top.add(category_div)


        top.add("<br/>")
        category_div = my.get_category_wdg2(paths_invalid, "Invalid Paths")
        top.add(category_div)

        top.add("<br/>")
        category_div = my.get_category_wdg2(paths_irregular, "Irregular Paths")
        top.add(category_div)
 

        top.add("<br/>")
        category_div = my.get_category_wdg2(paths_not_matched, "Unmatched Paths")
        top.add(category_div)


        return top


    def get_category_wdg(my, paths, title=None, tags={}):
        div = DivWdg()

        if not paths:
            paths = []

        base_dir = my.kwargs.get("base_dir")

        if not title:
            title = "Paths"

        count = len(paths)
        div.add("%s (%s)<hr/>" % (title, count) )
        if not paths:
            div.add("-- None --<br/>")

        paths_div = DivWdg()
        div.add(paths_div)
        paths_div.add_style("max-height: 500px")
        paths_div.add_style("overflow-y: auto")
        paths_div.add_style("overflow-x: auto")

        for path in paths:
            path_div = DivWdg()
            paths_div.add(path_div)
            rel_path = path.replace("%s/" % base_dir, "")
            path_div.add(rel_path)

            if tags:
                path_tags = tags.get(path)
                path_div.add( "&nbsp;"*10)
                path_div.add(path_tags['sobject'])

        return div


    def get_category_preview_wdg(my, paths, title=None, tags={}):

        div = DivWdg()

        if not title:
            title = "Paths"
        div.add("%s (%s)<hr/>" % (title, len(paths)) )
        if not paths:
            div.add("-- None --<br/>")

        paths_div = DivWdg()
        div.add(paths_div)

        from pyasm.widget import ThumbWdg

        for path in paths:
            path_div = DivWdg()
            paths_div.add(path_div)
            path_div.add_style("float: left")
            path_div.add_style("min-height: 60px")
            path_div.add_style("margin: 15px")
            path_div.add_style("width: 60px")

            icon_link = ThumbWdg.find_icon_link(path)
            path_div.add("<div><img width='60px' src='%s'/></div>" % icon_link)
            filename = os.path.basename(path)
            #path_div.add(path)
            path_div.add(filename)

            if tags:
                path_tags = tags.get(path)
                path_div.add( "&nbsp;"*10)
                path_div.add(path_tags['sobject'])

        div.add("<br clear='all'/>")
        return div




    def get_category_wdg2(my, paths, title=None, tags={}):

        if not paths:
            paths = []

        div = DivWdg()

        if not title:
            title = "Paths"
        div.add("%s (%s)<hr/>" % (title, len(paths)) )
        #if not paths:
        #    div.add("-- None --<br/>")

        table = Table()
        div.add(table)
        table.add_color("color", "color")

        base_dir = my.kwargs.get("base_dir")

        sobjects = []
        tags_keys = set()
        for path in paths:
            sobject = SearchType.create("sthpw/virtual")

            basename = os.path.basename(path)
            dirname = os.path.dirname(path)

            # FIXME: need session base
            reldir = dirname.replace("%s" % base_dir, "")
            reldir = dirname


            if not reldir:
                reldir = '&nbsp;'
            else:
                reldir.lstrip("/")
            if not basename:
                basename = '&nbsp;'

            sobject.set_value("folder", reldir)
            sobject.set_value("file_name", basename)
            sobjects.append(sobject)

            if tags:
                path_tags = tags.get(path)
                if path_tags:
                    for key, value in path_tags.get("sobject").items():
                        sobject.set_value(key, value)
                        tags_keys.add(key)

        from tactic.ui.panel import TableLayoutWdg
        element_names = ['path']
        element_names.extend( list(tags_keys) )
        #show_metadata = False
        #if not show_metadata:
        #    element_names.remove('metadata')


        config_xml = my.get_config_xml(list(tags_keys))

        layout = TableLayoutWdg(search_type='sthpw/virtual', view='report', config_xml=config_xml, element_names=element_names, mode='simple')
        # FIXME: just show first 200 results
        layout.set_sobjects(sobjects[:200])

        div.add(layout)

        return div


    def get_config_xml(my, tags_keys):
        xml = []
        xml.append("<config>")
        xml.append("<report>")
        xml.append('''
        <element name="folder"/>
        <element name="file_name"/>
        ''')

        for key in tags_keys:

            if key == 'metadata':
                xml.append('''
                <element name="%s">
                  <display class='tactic.ui.table.JsonElementWdg'/>
                </element>
                ''' % key)

            else:

                xml.append('''
                <element name="%s">
                </element>
                ''' % key)

        xml.append("</report>")
        xml.append("</config>")
        xml = "\n".join(xml)
        return xml



__all__.append('IngestionToolScanWdg')
class IngestionToolScanWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top

        scan_path = "/tmp/scan"
        if not os.path.exists(scan_path):
            top.add("No results in current scan session")
            return top

        base_dir = "/home/apache"
        total_count = 0

        mode = 'not'
        if mode == 'scan':
            # find all the files in the scanned data
            f = open(scan_path)
            data = jsonloads( f.read() )
            f.close()


        elif mode == 'not':
            # find all of the files not in the scanned data
            f = open(scan_path)
            scan_data = jsonloads( f.read() )
            f.close()

            data = {}
            count = 0
            limit = 5000
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    total_count += 1
                    path = "%s/%s" % (root, file)
                    if scan_data.get(path) == None:
                        continue

                    count +=1
                    if count > limit:
                        break

                    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
                    data[path] = {"size": size}
                if count > limit:
                    break

        elif mode == 'bad':
            data = {}
            count = 0
            limit = 5000
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    path = "%s/%s" % (root, file)
                    if not my.check_irregular(path):
                        continue

                    count +=1
                    if count > limit:
                        break

                    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
                    data[path] = {"size": size}
                if count > limit:
                    break



        elif mode == 'png':
            data = {}
            count = 0
            limit = 5000
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    path = "%s/%s" % (root, file)
                    if not path.endswith(".png"):
                        continue

                    count +=1
                    if count > limit:
                        break

                    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
                    data[path] = {"size": size}
                if count > limit:
                    break

        elif mode == 'custom':
            data = {}
            count = 0
            limit = 5000

            # What does this look like???
            handler = Hander()


            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    path = "%s/%s" % (root, file)
                    if not handler.validate():
                        continue

                    count +=1
                    if count > limit:
                        break

                    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(path)
                    data[path] = {"size": size}
                if count > limit:
                    break


        paths = data.keys()
        paths.sort()


        sobjects = []
        for path in paths:
            sobject = SearchType.create("sthpw/virtual")

            basename = os.path.basename(path)
            dirname = os.path.dirname(path)
            reldir = dirname.replace("%s" % base_dir, "")

            basename = os.path.basename(path)
            dirname = os.path.dirname(path)
            reldir = dirname.replace("%s" % base_dir, "")
            if not reldir:
                reldir = '&nbsp;'
            else:
                reldir.lstrip("/")
            if not basename:
                basename = '&nbsp;'

            sobject.set_value("folder", reldir)
            sobject.set_value("file_name", basename)
            sobjects.append(sobject)

            info = data.get(path)
            if info:
                sobject.set_value("size", info.get("size"))


        from tactic.ui.panel import TableLayoutWdg
        element_names = ['folder','file_name', 'size']
        #element_names.extend( list(tags_keys) )
        #show_metadata = False
        #if not show_metadata:
        #    element_names.remove('metadata')


        #config_xml = my.get_config_xml(list(tags_keys))

        #layout = TableLayoutWdg(search_type='sthpw/virtual', view='report', element_names=element_names, mode='simple')
        #layout.set_sobjects(sobjects)
        #top.add(layout)

        top.add("Matched %s items of %s<br/>" % (len(sobjects), total_count) )
        table = Table()
        table.add_color("color", "color")
        top.add(table)
        table.add_row()
        for element_name in element_names:
            title = Common.get_display_title(element_name)
            td = table.add_cell("<b>%s</b>" % title)
            td.add_border()
            td.add_color("color", "color", +5)
            td.add_gradient('background', 'background', -20)
            td.add_style("height: 20px")
            td.add_style("padding: 3px")


        for row, sobject in enumerate(sobjects):
            tr = table.add_row()
            if row % 2:
                background = tr.add_color("background", "background")
            else:
                background = tr.add_color("background", "background", -2)
            tr.add_attr("spt_background", background)


            for element_name in element_names:
                td = table.add_cell(sobject.get_value(element_name))
                td.add_border()

        return top



    def check_irregular(my, path):
        p = re.compile("[\!\@\$\%\^\&\*\(\)\{\}\[\]\:]")
        if p.search(path):
            return True
        else:
            return False


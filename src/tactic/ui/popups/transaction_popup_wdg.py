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
__all__ = ["TransactionPopupWdg"]


from pyasm.common import Environment, Config
from pyasm.biz import Project
from pyasm.web import *

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import PopupWdg
#from tactic.ui.activator import ButtonForDropdownMenuWdg

from tactic.ui.app import UndoLogWdg
from pyasm.widget import IconWdg
from tactic.ui.widget import TextBtnSetWdg, ActionButtonWdg, ButtonNewWdg, ButtonRowWdg

import datetime

class TransactionPopupWdg(BaseRefreshWdg):

    def init(self):
        pass


    def get_args_keys(self):
        return {
        }

    def get_buttons(self):
        button_div = DivWdg()


        button_row = ButtonRowWdg()
        button_div.add(button_row)
        button_row.add_style("float: right")
        button_row.add_style("padding-top: 5px")
        button_row.add_style("padding-bottom: 3px")
        button_row.add_style("padding-right: 5px")

        button = ButtonNewWdg(title="Refresh", icon=IconWdg.REFRESH)
        button_row.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.app_busy.show("Refreshing");
            var top = bvr.src_el.getParent(".spt_undo_log_top");
            spt.panel.refresh(top)
            spt.app_busy.hide();
            '''
        } )


        button = ButtonNewWdg(title="Undo the last transaction", icon=IconWdg.UNDO)
        button_row.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.undo_cbk(evt, bvr);
            spt.panel.refresh('UndoLogWdg');
            '''
        } )



        button = ButtonNewWdg(title="Redo the last transaction", icon=IconWdg.REDO)
        button_row.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.redo_cbk(evt, bvr);
            spt.panel.refresh('UndoLogWdg');
            '''
        } )


        # concept of a work session, which holds transaction codes
        session = {}

        # how should this session be stored?  Timestamp based?
        now = datetime.datetime.now()
        today = now.strftime("%Y-%m-%d")
        now = now.strftime("%Y-%m-%d %H:%M:%S")


        location = Config.get_value("install", "server")
        login = Environment.get_user_name()
        project_code = Project.get_project_code()


        """
        button = ButtonNewWdg(title="Save Selected Transactions", icon=IconWdg.SAVE)
        button_row.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'login': login,
            'project_code': project_code,
            'session': session,
            'cbjs_action': '''


            var top = bvr.src_el.getParent(".spt_undo_log_top");
            var table = top.getElement(".spt_table");

            var search_keys = spt.dg_table.get_selected_search_keys(table);
            if (search_keys.length == 0) {
                spt.error("No transactions selected");
                return;
            }

            spt.app_busy.show("Saving Selected Transactions")
            bvr.session['search_keys'] = search_keys.join("|");

            var server = TacticServerStub.get();
            var kwargs = {
                login: bvr.login,
                project_code: bvr.project_code,
                session: bvr.session
            }

            var class_name = 'tactic.command.TransactionPluginCreateCmd';
            server.execute_cmd(class_name, kwargs);

            spt.panel.refresh('UndoLogWdg');

            spt.app_busy.hide();

            '''
        } )


        #button.add_arrow_behavior( {
        #    'type': 'click_up',
        #    'cbjs_action': '''alert('cow')'''
        #} )
        button.set_show_arrow_menu(True)

        from tactic.ui.container import SmartMenu, Menu, MenuItem
        menu = Menu(width=180)
        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)
        menu_item = MenuItem(type='action', label='Save Today\'s Transactions')
        menu.add(menu_item)

        session['start_time'] =  "%s 00:00:00" % today
        session['end_time'] =  now

        menu_item.add_behavior( {
            'type': 'click_up',
            'login': login,
            'project_code': project_code,
            'session': session,
            'cbjs_action': '''

            spt.app_busy.show("Saving Today's Transactions")

            var server = TacticServerStub.get();
            var kwargs = {
                login: bvr.login,
                project_code: bvr.project_code,
                session: bvr.session
            }

            var class_name = 'tactic.command.TransactionPluginCreateCmd';
            server.execute_cmd(class_name, kwargs);

            spt.panel.refresh('UndoLogWdg');

            spt.app_busy.hide();

            '''
        } )


        SmartMenu.add_smart_menu_set( button.get_arrow_wdg(), { 'BUTTON_MENU': menu } )
        SmartMenu.assign_as_local_activator( button.get_arrow_wdg(), "BUTTON_MENU", True )





        button = ButtonNewWdg(title="Upload Transaction Session", icon=IconWdg.UPLOAD)
        button_row.add(button)
        button.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''

            spt.app_busy.show("Select Transaction File");

            var applet = spt.Applet.get();
            var files = applet.open_file_browser();
            if (files.length == 0) {
                spt.alert("No files selected");
                spt.app_busy.hide();
                return;
            }

            var path = files[0];

            spt.app_busy.show("Installing Transaction File");

            var server = TacticServerStub.get();
            server.upload_file(path);

            var class_name = 'tactic.command.TransactionPluginInstallCmd';
            var kwargs = {
                path: path
            }

            try {
                var info = server.execute_cmd(class_name, kwargs);
            }
            catch(e) {
                spt.alert(e);
            }

            spt.panel.refresh('UndoLogWdg');

            spt.app_busy.hide();
            '''
        } )
        """



        return button_div


    def get_display(self):
        content_div = DivWdg()
        self.set_as_panel(content_div)
        content_div.add_class("spt_undo_log_top")
        content_div.add_style("width: 800px")

        buttons = content_div.add(self.get_buttons())
        content_div.add(buttons)
 
        undo_wdg = UndoLogWdg()
        undo_wdg.set_id('UndoLogWdg')
        content_div.add(undo_wdg)

        return content_div






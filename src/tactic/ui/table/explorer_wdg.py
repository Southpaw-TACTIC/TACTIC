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


__all__ = ['ExplorerTableElementWdg', 'ExplorerElementWdg']

from pyasm.common import TacticException, Common
from pyasm.biz import Project
from pyasm.web import Widget
from pyasm.widget import IconWdg
from tactic.ui.common import BaseTableElementWdg

from tactic.ui.widget import IconButtonWdg


class ExplorerElementWdg(BaseTableElementWdg):

    ARGS_KEYS = {
    'mode': {
        'description': 'Determines which directory to go to when the explorer button is pressed.',
        'type': 'SelectWdg',
        'values': 'sandbox|repository',
        'category': 'options'
    }
    }

  

    def get_decrement(my):
        decrement = my.get_option('decrement')
        if not decrement:
            decrement = 0
        else:
            decrement = int(decrement)

        return decrement

    def get_base_dir( my, sobject):
        decrement = my.get_decrement()
        base_dir = Project.get_sandbox_base_dir(sobject, decrement=decrement)
        return base_dir

    def get_lib_dir(my, sobject):
        snapshot = None
        base_dir = Project.get_project_lib_dir(sobject, snapshot)
        
        return base_dir


    def get_client_repo_dir(my, sobject):
        snapshot = None
        base_dir = Project.get_project_client_lib_dir(sobject, snapshot)
        #TODO: u could decrement the client repo dir here, if really needed
        return base_dir


    def get_title(my):
        widget = Widget()
        title = super(ExplorerElementWdg, my).get_title()
        widget.add( title )
        return widget


    def get_display(my):
        sobject = my.get_current_sobject()

        mode = my.get_option('mode')
        if not mode:
            mode = 'sandbox'

        widget = Widget()
        sobject_dir = ''
        sobject_lib_dir = ''
        # find the path to open explorer
        if sobject.is_insert():
            button = IconWdg("No Path Found", IconWdg.CROSS, long=False)
        else:
            try:
                if mode == 'sandbox':
                    sobject_dir = my.get_base_dir(sobject)
                elif mode in ['client_repo', 'repository']:
                    sobject_dir = my.get_client_repo_dir(sobject)
                    sobject_lib_dir = my.get_lib_dir(sobject)
                sobject_dir = sobject_dir.strip()
                sobject_dir = Common.process_unicode_string(sobject_dir)
            except TacticException as e:
                print("WARNING: ", str(e))
                button = IconWdg("No Path Found", IconWdg.CROSS, long=False)
            else:
                button = IconButtonWdg(title="Explore: %s" % sobject_dir, icon=IconWdg.LOAD)
                if sobject_dir == sobject_lib_dir:
                    button.add_behavior({'type':'click_up', 'cbjs_action':"spt.alert('You are not allowed to browse directories on a web server.');"})
                else:
                    button.add_behavior({'type':'click_up', 'cbjs_action':'''var applet = spt.Applet.get(); applet.makedirs('%s'); applet.open_explorer('%s');''' % (sobject_dir, sobject_dir)} )

        widget.add(button)

        return widget

    def is_editable(cls):
        '''to avoid all those CellEditWdg'''
        return False
    is_editable = classmethod(is_editable)


# DEPRECATED use ExplorerElementWdg
class ExplorerTableElementWdg(ExplorerElementWdg):
    pass

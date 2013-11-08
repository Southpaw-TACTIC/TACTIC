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

__all__ = ['MetadataElementWdg']

import types, re, os

from pyasm.common import TacticException, Container, Date, jsonloads, jsondumps
from pyasm.search import Search, SearchKey, SObject
from pyasm.web import DivWdg, Widget, WebContainer, Table, HtmlElement, WikiUtil, SpanWdg
from pyasm.widget import IconWdg, TextWdg, TextAreaWdg, SelectWdg, ThumbWdg, PublishLinkWdg, IconButtonWdg, CheckboxWdg, SwapDisplayWdg, ProdIconButtonWdg
from pyasm.biz import Project, NamingUtil, ExpressionParser, Snapshot
from tactic.ui.common import BaseTableElementWdg, SimpleTableElementWdg
from tactic.ui.widget import ActionButtonWdg

from button_wdg import ButtonElementWdg
class MetadataElementWdg(ButtonElementWdg):
    '''The element widget that displays according to type'''

    ARGS_KEYS = {
        'context': 'The context of the snapshot to get the file path from'
    }


    def is_editable(my):
        return False

    def get_required_columns(my):
        return []

    def get_display(my):

        my.set_option('icon', "CONTENTS")


        sobject = my.get_current_sobject()
        search_type = sobject.get_search_type()

        context = my.get_option("context")
        if not context:
            context = "publish"

        process = my.get_option("process")
        if not process:
            process = "publish"


        if sobject.get_base_search_type() == "sthpw/snapshot":
            snapshot = sobject
            sobject = snapshot.get_parent()
            search_type = sobject.get_search_type()

        else:
            if process:
                snapshot = Snapshot.get_latest_by_sobject(sobject, process=process)
            else:
                snapshot = Snapshot.get_latest_by_sobject(sobject, context=context)

        if not snapshot:
            top = DivWdg()
            return top





        top = DivWdg()
        icon = IconButtonWdg( "Show Metadata", eval( "IconWdg.%s" % my.get_option('icon') ) )
        top.add(icon)


        lib_path = snapshot.get_lib_path_by_type("main")
        basename = os.path.basename(lib_path)
        dirname = os.path.dirname(lib_path)

        my.behavior['basename'] = basename
        my.behavior['dirname'] = dirname
        my.behavior['search_type'] = search_type


        cbjs_action = '''

        var class_name = 'tactic.ui.tools.repo_browser_wdg.RepoBrowserContentWdg';
        var kwargs = {
            basename: '%(basename)s',
            dirname: '%(dirname)s',
            search_type: '%(search_type)s'
        };

        //spt.tab.set_main_body_tab();
        //spt.tab.add_new("Detail", "Detail", class_name, kwargs);
        spt.panel.load_popup("Detail", class_name, kwargs);

        ''' % (my.behavior)

        my.behavior['type'] = 'click_up'
        my.behavior['cbjs_action'] = cbjs_action

        icon.add_behavior(my.behavior)

        return top




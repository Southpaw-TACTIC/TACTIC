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

__all__ = ['SimpleAppServer']

import cStringIO, os, re

from pyasm.common import Container
from web_container import WebContainer
from app_server import BaseAppServer


# DEPRECATED


class AppServerException(Exception):
    pass

class FakeSecurity(object):
    # TODO: for now, TACTIC needs a security class, so create a fake one
    def check_access(self, *args):
        return True

    def get_user_name(self):
        return ""


class SimpleAppServer(BaseAppServer):
    '''A simple application server without security restrictions.'''

    def execute(self):
        self.buffer = cStringIO.StringIO()
        try:
            # clear the main containers
            Container.create()
            # clear the buffer
            WebContainer.clear_buffer()

            # initialize the web environment object and register it
            adapter = self.get_adapter()
            WebContainer.set_web(adapter)
           
            # get the display
            self._get_display()
        finally:
            WebContainer.get_buffer().write( self.buffer.getvalue() )



    def _get_display(self):
        WebContainer.set_security(FakeSecurity())

        page = self.get_page_widget()

        # create some singletons and store in container
        cmd_delegator = WebContainer.get_cmd_delegator()
        
        # add the event container
        event_container = WebContainer.get_event_container()

        from pyasm.widget import TopWdg, BottomWdg

        top = TopWdg()
        bottom = BottomWdg()
        page = self.get_page_widget()

        web = WebContainer.get_web()
  
        from widget import Widget
        widget = Widget()
        widget.add( top )
        widget.add( page )
        #widget.add( self.get_form_wdg() )
        widget.add( bottom )

        #widget.add(warning_report)
        widget.add(cmd_delegator)

        # create a web app and run it through the pipeline
        from web_app import WebApp
        web_app = WebApp()
        return web_app.get_display(widget)


    def get_form_wdg(self):
        web = WebContainer.get_web()
        from pyasm.web import Table
        table = Table()
        keys = web.get_form_keys()
        keys.sort()
        for key in keys:
            # skipping the upload data
            if not key:
                continue
            pat = re.compile(r'(\|files|\|images|\|snapshot|\|submission|\|publish_icon|\|publish_main)$')
            if pat.search(key):
                continue
            table.add_row()
            field = web.get_form_values(key)
            table.add_cell(key)
            table.add_cell(str(field))

        return table




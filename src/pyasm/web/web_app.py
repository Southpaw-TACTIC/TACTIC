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

__all__ = ['WebAppException', 'WebApp']


import types, time

from pyasm.common import *
from pyasm.search import SearchType, Sql
from widget import *
from html_wdg import *
from web_container import *



class WebAppException(Exception):
    pass



class WebApp(Base):
    """Defines a pipeline for displaying a web application"""
    def __init__(my):
        pass


    def get_display(my, widget):
        """run through the full web app pipeline"""

        if widget == None:
            raise WebAppException("No top level widget defined")

        # add to the access log
        # FIXME: this does not get committed if there is an exception.  The
        # transaction will back out.
        access_log_flag = False
        access_log = None
        if access_log_flag:
            access_log = SearchType.create("sthpw/access_log")
            access_log.set_value("url", "www.yahoo.com")
            access_log.set_value("start_time", Sql.get_timestamp_now(), quoted=False)
            access_log.commit()

            start = time.time()


        # do a security check on the widget
        # DEPRECATED
        widget.check_security()

        # draw all of the widgets
        widget = widget.get_display()
        if widget:
            Widget.get_display(widget)


        if access_log_flag:
            access_log.set_value("end_time", Sql.get_timestamp_now(), quoted=False)
            duration = time.time() - start
            duration = float(int(duration * 1000)) / 1000
            access_log.set_value("duration", str(duration) )
            access_log.commit()







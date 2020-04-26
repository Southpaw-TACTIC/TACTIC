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

__all__ = ['browser']

from pyasm.web import AppServer

from pyasm.search import Search
from pyasm.web import DivWdg, Widget, HtmlElement

# get the import to this project's modules
from pyasm.web import get_site_import
exec( get_site_import(__file__) )

class browser(AppServer):

    def get_page_widget(self):

        div = DivWdg()

        div.add_style("font-size: 1.5em")
        div.add_style("text-align: left")
        div.add_style("border-width: 1px")
        div.add_style("border-style: solid")
        div.add_style("padding: 10px")
        div.add_style("width: 80%")
        div.center()
    
        div.add( HtmlElement.p("We have detected that you are running Windows Internet Explorer") )
        div.add(HtmlElement.p("At present, we have chosen not to support Windows Internet Explorer") )

        div.add(HtmlElement.p("TACTIC is a complex web application and we comply to W3C standards.  Many browsers suport these standards.  However, Internet Explorer does not.  So in order to provide you with the best user experience, we strongly recommend you use one of the following browsers: Firefox or any Mozilla base browser, Safari, etc."))

        return div



#!/usr/bin/python
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


import unittest, string

from html_wdg import *
from web_state import *

class HtmlWdgTest(unittest.TestCase):

    def test_element(self):

        br = HtmlElement("br")
        self.assertEquals("<br/>\n", br.get_display() )

    def test_children(self):
        href = HtmlElement.href("yahoo", "http://www.yahoo.com")
        self.assertEquals("<a href=\"http://www.yahoo.com\">yahoo</a>\n", href.get_display() )

    def test_style(self):
        div = HtmlElement.div("Hello")
        style = "background-color: #f0f0f0"
        div.set_style(style)

        self.assertEquals("<div style=\"%s\">Hello</div>\n" % style, div.get_display() )


    def test_table(self):
        table = Table()
        table.add_row()
        table.add_cell( "Name:")
        table.add_cell( "Remko")
        table.add_row()
        table.add_cell( "Password:" )
        table.add_cell( "pig")

        html = Html()
        html.writeln("<table cellpadding=\"0\" cellspacing=\"0\">")
        html.writeln("<tr><td>Name:</td><td>Remko</td></tr>")
        html.writeln("<tr><td>Password:</td><td>pig</td></tr>")
        html.writeln("</table>")

        a = html.getvalue()
        a = string.replace( a ,"\n", "")

        b = table.get_display()
        b = string.replace( b ,"\n", "")

        self.assertEquals( a, b )







if __name__ == '__main__':
    unittest.main()




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
import tacticenv

import unittest, string

from .html_wdg import *
from .web_state import *

class HtmlWdgTest(unittest.TestCase):

    def test_all(self):
        
        from .web_container import WebContainer
        WebContainer.clear_buffer()

        self._test_element()
        self._test_children()
        self._test_style()
        self._test_table()

    def _test_element(self):
        """
        Tests the get_buffer_display function of a br HtmlElement.
        """
        br = HtmlElement("br")
        self.assertEqual("<br />", br.get_buffer_display() )

    def _test_children(self):
        """
        Tests the get_buffer_display function of a href HtmlElement.
        """

        href = HtmlElement.href("yahoo", "http://www.yahoo.com")
        self.assertEqual("<a href=\"http://www.yahoo.com\">yahoo</a>", href.get_buffer_display() )

    def _test_style(self):
        """
        Tests adding style to an HtmlElement.
        """

        div = HtmlElement.div("Hello")
        style = "background-color: #f0f0f0"
        div.set_style(style)

        self.assertEqual("<div style=\"%s\">Hello</div>" % style, div.get_buffer_display() )


    def _test_table(self):
        """
        Tests that get_display of a Table widget and the HTML equivalent of the table are equal.
        """


        table = Table()
        table.add_row()
        table.add_cell( "Name:")
        table.add_cell( "Remko")
        table.add_row()
        table.add_cell( "Password:" )
        table.add_cell( "pig")

        from .widget import Html
        html = Html()
        html.writeln('<table style=\'border-collapse: collapse\'>')
        html.writeln('<tr><td>Name:</td><td>Remko</td></tr>')
        html.writeln('<tr><td>Password:</td><td>pig</td></tr>')
        html.writeln('</table>')

        a = html.getvalue()
        a = a.replace("\n", "")

        b = table.get_buffer_display()
        b = b.replace("\n", "")

        self.assertEqual( a, b )







if __name__ == '__main__':
    unittest.main()




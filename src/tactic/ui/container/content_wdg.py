###########################################################
#
# Copyright (c) 2014, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ['ContentBoxWdg']

from pyasm.web import HtmlElement, DivWdg, Table
from pyasm.widget import IconWdg

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.panel import CustomLayoutWdg



class ContentBoxWdg(BaseRefreshWdg):

    def get_display(my):

        top = my.top
        top.add_style("margin: 15px")
        top.add_class("spt_content_box")

        style = HtmlElement.style()
        top.add(style)
        style.add('''
        .spt_content_box .spt_content_box_title {
            width: auto;
            border: none;
            background: #333;
            color: #FFF;
            height: 20px;
            padding: 8px;
            font-weight: bold;
            border: solid 1px #333;
        }

        .spt_content_box .spt_content_box_shelf {
            margin-top: 0px;
            border: solid 1px #AAA;
            padding: 8px 15px;
            height: 23px;
            background: #F8F8F8;
        }

        .spt_content_box .spt_content_box_content {
            width: auto;
            margin-top: -1px;
            border: solid 1px #AAA;
            padding: 15px 0px;
            background: #FFF;
            overflow-x: auto;

        }

        .spt_content_box .spt_content_box_footer {
            margin-top: -1px;
            border: solid 1px #AAA;
            padding: 8px 15px;
            height: 23px;
            background: #F8F8F8;
        }


        ''')


        top.add(my.get_title_wdg())

        inner = DivWdg()
        top.add(inner)
        inner.add_class("spt_content_box_inner")
        inner.add_style("overflow: hidden")
        inner.add_style("margin-top: 0px")


        # handle the shelf
        shelf_view = my.kwargs.get("shelf_view")
        if shelf_view:
            shelf_div = DivWdg()
            inner.add(shelf_div)
            shelf_div.add_class("spt_content_box_shelf")

            layout = CustomLayoutWdg(view=shelf_view)
            shelf_div.add(layout)



        content_div = DivWdg()
        content_div.add_class("spt_content_box_content")
        inner.add(content_div)

        content_height = my.kwargs.get("content_height")
        if not content_height:
            content_height = "300px"
        #content_div.add_style("max-height: %s" % content_height)
        content_div.add_style("overflow-x: auto")

        content_view = my.kwargs.get("content_view")
        #content_div.add(content_view)
        if content_view:
            layout = CustomLayoutWdg(view=content_view)
            content_div.add(layout)




        # handle the footer
        footer_view = my.kwargs.get("footer_view")
        if footer_view:
            footer_div = DivWdg()
            inner.add(footer_div)
            footer_div.add_class("spt_content_box_footer")

            layout = CustomLayoutWdg(view=footer_view)
            shelf_div.add(layout)


        return top



    def get_title_wdg(my):

        title = my.kwargs.get("title")
        if not title:
            title = "No Title"
        icon = my.kwargs.get("icon")
        if not icon:
            icon = "USER"

        title_div = DivWdg()
        title_div.add_class("spt_content_box_title")




        # icon on the left
        icon_div = DivWdg()
        title_div.add(icon_div)
        icon = IconWdg(icon="FOLDER")
        icon_div.add(icon)
        icon_div.add_styles('''float: left; height: 25px; margin-top: 0px; padding: 0px 8px;''')





        # icon on the right

        icon_div = DivWdg()
        title_div.add(icon_div)
        icon = IconWdg(icon="GEAR")
        icon_div.add(icon)
        icon_div.add_styles('''float: right; height: 25px; margin-top: 0px; padding: 0px 8px;''')




        icon_div = DivWdg()
        title_div.add(icon_div)
        icon = IconWdg(icon="ARROW_UP")
        icon_div.add(icon)
        icon_div.add_styles('''float: right; height: 25px; margin-top: 0px; padding: 0px 8px;''')
        icon_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_content_box");
            var content = top.getElement(".spt_content_box_content");
            var inner = top.getElement(".spt_content_box_inner");
            var state = inner.getAttribute("spt_state");
            if ( state != "closed" ) {
                var size = inner.getSize();
                dst = -size.y-5;
                inner.setAttribute("spt_state", "open");
            }
            else {
                dst = 0;
                inner.setAttribute("spt_state", "closed");
            }
            new Fx.Tween(content, {duration: 500}).start("margin-top", dst);


            '''
        } )

        icon_div = DivWdg()
        title_div.add(icon_div)
        icon = IconWdg(icon="DOT_RED")
        icon_div.add(icon)
        icon_div.add_styles('''float: right; height: 25px; margin-top: 0px; padding: 0px 8px;''')



        #title_div.add('''<div style="float: right; width: 20px; height: 20px; margin-top: -9px; margin-right: -8px; padding: 8px; border: solid 0px #000;">X</div>''')

        title_div.add(title)

        return title_div




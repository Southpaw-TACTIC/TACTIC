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
from pyasm.widget import IconWdg, WidgetConfig

from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import IconButtonWdg



class ContentBoxWdg(BaseRefreshWdg):

    def get_display(my):


        from tactic.ui.panel import CustomLayoutWdg

        top = my.top
        top.add_class("spt_content_box")
        top.add_class("spt_content_box_inline")
        top.add_style("min-width: 200px")

        #top.add_style("opacity: 0.1")

        """
        top.add_behavior( {
            'type': 'loadX',
            'cbjs_action': '''
            new Fx.Tween(bvr.src_el, {duration: 500}).start("opacity", 1.0);
            '''
        } )
        """

        colors = {
            #"color3": top.get_color("color3"),
            #"background3": top.get_color("background3"),
            #"background3": "rgba(18, 50, 91, 1.0)",
            "background3": "#323232",
            "color3": "#FFF",
            "border": top.get_color("border", -10),
        }

        style = HtmlElement.style()
        top.add(style)
        style.add('''
        .spt_content_box_inline {
            margin: 15px;
        }

        .spt_content_box_max {
            margin: 0px;
            width: 100%%;
            height: 100%%;
            background: rgba(0,0,0,0.0);
            z-index: 1000;
            position: fixed;
            top: 0px;
            left: 0px;
        }

        .spt_content_box_max .spt_content_box_content {
            //height: 100%% !important;
        }


        .spt_content_box .spt_content_box_title {
            width: auto;
            border: none;
            background: %(background3)s;
            color: %(color3)s;
            height: 18px;
            padding: 6px 8px;
            font-weight: bold;
            font-size: 1.2em;
            border: solid 1px %(border)s;
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
            margin-bottom: 5px;
            border: solid 1px #AAA;
            padding: 15px 0px 0px 0px;
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
        ''' % colors)


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

            if shelf_view == "true":
                pass
            else:
                layout = CustomLayoutWdg(view=shelf_view)
                shelf_div.add(layout)



        content_div = DivWdg()
        content_div.add_class("spt_content_box_content")
        inner.add(content_div)
        content_div.add_style("width: auto")

        content_height = my.kwargs.get("content_height")
        if content_height:
            content_div.add_style("height: %s" % content_height)
        content_div.add_style("overflow-x: auto")

        content_view = my.kwargs.get("content_view")
        #content_div.add(content_view)
        if content_view:
            layout = CustomLayoutWdg(view=content_view)
            content_div.add(layout)

            content_margin = my.kwargs.get("content_margin")
            if content_margin:
                layout.add_style("margin", content_margin)

        config_xml = my.kwargs.get("config_xml")
        if config_xml:
            config = WidgetConfig.get(view="tab", xml=config_xml)
            layout = config.get_display_widget("content")
            content_div.add(layout)


        content_wdg = my.get_widget("content")
        if not content_wdg and my.widgets:
            content_wdg = my.widgets[0]
        if content_wdg:
            content_div.add(content_wdg)


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
            widget = my.get_widget("title")
            if not widget and my.widgets:
                widget = my.widgets[0]
                title = widget.get_name().title()
        if not title:
            title = "No Title"


        icon = my.kwargs.get("icon")
        if not icon:
            icon = "G_FOLDER"

        title_div = DivWdg()
        title_div.add_class("spt_content_box_title")


        # icon on the left
        icon_div = DivWdg()
        title_div.add(icon_div)
        icon = IconWdg(icon=icon, width=16)
        icon_div.add(icon)
        icon_div.add_styles('''float: left; height: 25px; margin-top: 0px; padding: 0px 8px 0px 5px;''')





        # icon on the right
        show_gear = my.kwargs.get("show_gear")
        if show_gear in [True, 'true']:
            icon_div = DivWdg()
            title_div.add(icon_div)
            icon = IconWdg(icon="G_SETTINGS", width=16)
            icon_div.add(icon)
            icon_div.add_styles('''float: right; height: 25px; margin-top: 0px; padding: 0px 8px 0px 5px;''')




        icon_div = DivWdg()
        title_div.add(icon_div)
        icon = IconButtonWdg(icon="G_UP", width=16)
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
        icon = IconButtonWdg(icon="G_MAXIMIZE", width=16)
        icon_div.add(icon)
        icon_div.add_styles('''float: right; height: 25px; margin-top: 0px; padding: 0px 0px;''')

        icon_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_content_box");
            if (top.hasClass("spt_content_box_max")) {
                top.removeClass("spt_content_box_max");
                top.addClass("spt_content_box_inline");
                top.size = top.getSize();
                top.setStyle("height", top.size.y)


            }
            else {
                top.addClass("spt_content_box_max");
                top.removeClass("spt_content_box_inline");
                var size = top.size;
                top.setStyle("height", size.y)
            }
            '''
        } )



        #title_div.add('''<div style="float: right; width: 20px; height: 20px; margin-top: -9px; margin-right: -8px; padding: 8px; border: solid 0px #000;">X</div>''')

        title_div.add(title)

        return title_div




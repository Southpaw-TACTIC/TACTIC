############################################################
#
# Copyright (c) 2005-2011, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["WizardWdg", "TestWizardWdg"]

from pyasm.common import Common, jsonloads
from pyasm.web import *
from pyasm.widget import IconWdg, IconButtonWdg, SelectWdg, ProdIconButtonWdg, TextWdg

from tactic.ui.common import BaseRefreshWdg

import six
basestring = six.string_types

class WizardWdg(BaseRefreshWdg):
    ARGS_KEYS = {
        'submit_title': {
            'description': 'Title shown on submit button',
            'values': 'true|false',
            'category': 'Display'
        },
        'command': {
            'description': 'Python command class to run on submit',
            'category': 'Display'
        },
        'script': {
            'description': 'Python script path to run on submit',
            'category': 'Display'
        },
        'jsscript': {
            'description': 'Javascript path to run on submit',
            'category': 'Display'
        },

        'views': {
            'description': 'List of views to display for each page',
            'category': 'Display'
        }

    }


    def __init__(self, **kwargs):
        super(WizardWdg, self).__init__(**kwargs)

        self.submit_button = None

    def add_submit_button(self, button):
        self.submit_button = button


    def get_display(self):
        top = DivWdg()
        top.add_class("spt_wizard_top")

        self.height = self.kwargs.get("height")
        width = self.kwargs.get("width")
        if not width:
            width = ""
        self.width = width

        try:
            width = int(width)
            width = str(width) + "px"
        except ValueError:
            pass

        inner = DivWdg()
        top.add(inner)
        inner.add_style("width: %s" % width)

        inner.add_style("display: flex")
        inner.add_style("flex-direction: column")


        title = self.kwargs.get("title")
        if not title:
            title = "none"
        
        if title != "none":
            title_wdg = DivWdg()
            inner.add(title_wdg)
            title_wdg.add(title)
            title_wdg.add_style("font-size: 16px")
            title_wdg.add_style("font-weight: bold")

        inner.add("<br/>")


        self.titles = self.kwargs.get("titles")
        if isinstance(self.titles, basestring):
            self.titles = self.titles.split("|")
        if not self.titles:
            self.titles = []


        extra_data = self.kwargs.get("extra_data") or {}
        if isinstance(extra_data, basestring):
            extra_data = jsonloads(extra_data)




        views = self.kwargs.get("views")
        if views:
            from tactic.ui.panel import CustomLayoutWdg
            if isinstance(views, basestring):
                views = views.split("|")

            for i, view in enumerate(views):

                if i < len(self.titles):
                    title = self.titles[i]
                else:
                    title = widget.get_name()
                    title = title.replace(".", " ")
                    title = Common.get_display_title(title)

                widget = CustomLayoutWdg(view=view, **extra_data)
                self.add(widget, title)



        header_wdg = self.get_header_wdg()
        inner.add(header_wdg)

        # Removing these because they don't work very well ... produces double scrollbars
        #header_wdg.add_class("spt_popup_header")

        inner.add("<br/>")

        inner.add("<hr/>")

        pages_div = DivWdg()
        #pages_div.add_class("spt_popup_body")
        inner.add(pages_div)
        pages_div.add_style("overflow-y: auto")

        for i, widget in enumerate(self.widgets):
            page_div = DivWdg()
            page_div.add_class("spt_wizard_page")
            pages_div.add(page_div)

            page_div.add_style("padding: 10px")

            page_div.add_style("min-height: 300px")
            if self.height:
                height = self.height
                try:
                    height = int(height)
                    height = str(height) + "px"
                except ValueError:
                    pass
                page_div.add_style("height: %s" % height)

            page_div.add_style("overflow-y: auto")

            if i != 0:
                page_div.add_style("display: none")
            else:
                page_div.add_class("spt_wizard_selected")

            page_div.add(widget)


        pages_div.add("<hr/>")
        bottom_wdg = self.get_bottom_wdg()
        #bottom_wdg.add_class("spt_popup_footer")
        inner.add(bottom_wdg)

        return top

    def add(self, widget, name):
        widget.set_name(name)
        super(WizardWdg, self).add(widget, name)



    def get_header_wdg(self):
        div = DivWdg()
        div.add_style("text-align: center")
        width = self.width
        try:
            width = int(width)
            width = str(width) + "px"
        except ValueError:
            pass
        div.add_style("width: %s" % width)

        div.add("<hr/>")

        dots_div = DivWdg()
        dots_div.add_style("margin: -36px auto 0px auto")
        div.add(dots_div)
        dots_div.add_style("display: flex")
        dots_div.add_style("align-items: center")
        dots_div.add_style("jstify-content: space-arount")

        left = 50
        width = 50

        dots_div.add_style("width", str((left+width)*len(self.widgets)+left) + "px" )

        for i, widget in enumerate(self.widgets):
            on_dot = DivWdg()
            on_dot.add_style("box-sizing: border-box")
            on_dot.add_style("width: 30px")
            on_dot.add_style("height: 30px")
            on_dot.add_style("padding-top: 4px")
            on_dot.add_style("border-radius: 20px")
            on_dot.add_style("background: rgba(188,215,207,1.0)")
            on_dot.add_style("margin: 6px auto")
            on_dot.add_border()
            on_dot.add_class("spt_wizard_on_dot")
            on_dot.add_style("box-shadow: 0px 0px 10px rgba(0,0,0,0.1)")
            on_dot.add_style("font-weight: bold")

            off_dot = DivWdg()
            off_dot.add_style("box-sizing: border-box")
            off_dot.add_style("width: 20px")
            off_dot.add_style("height: 20px")
            off_dot.add_style("padding-top: 3px")
            off_dot.add_style("border-radius: 10px")
            off_dot.add_style("background: #DDD")
            off_dot.add_style("margin: 11px auto 12px auto")
            off_dot.add_border()
            off_dot.add_class("spt_wizard_off_dot")

            if i == 0:
                off_dot.add_style("display: none")
            else:
                on_dot.add_style("display: none")

            dots_div.add_style("position: relative")

            dot_div = DivWdg()
            dot_div.add_style("text-align: center")
            dot_div.add_attr("spt_selected_index", i)
            dot_div.add_class("spt_wizard_link")
            dot_div.add_class("hand")
            dots_div.add(dot_div)
            dot_div.add(on_dot)
            dot_div.add(off_dot)
            dot_div.add_style("width: %spx" % width)
            dot_div.add_style("float: left")
            dot_div.add_style("margin-left: %spx" % left)
            dot_div.add_style("text-align: center")

            on_dot.add("%s" % (i+1))
            off_dot.add("%s" % (i+1))
            off_dot.add_style("font-size: 0.7em")
            on_dot.add_style("text-align: center")
            off_dot.add_style("text-align: center")

            name_div = DivWdg()
            dot_div.add(name_div)

            if i < len(self.titles):
                title = self.titles[i]
            else:
                title = widget.get_name()
                title = title.replace(".", " ")
                title = Common.get_display_title(title)

            #title = "%d %s" % (i+1, title)
            name_div.add(title)
            name_div.add_style("font-weight: bold")
            name_div.add_style("width: 80px")
            name_div.add_style("margin-left: -17px")




        div.add_relay_behavior( {
            'type': 'mouseup',
            'bvr_match_class': 'spt_wizard_link',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_wizard_top");
            var top = bvr.src_el.getParent(".spt_wizard_top");
            var pages = top.getElements(".spt_wizard_page");
            var on_dots = top.getElements(".spt_wizard_on_dot");
            var off_dots = top.getElements(".spt_wizard_off_dot");

            var selected_index = parseInt( bvr.src_el.getAttribute("spt_selected_index"));

            for (var i = 0; i < pages.length; i++) {
                var page = pages[i];
                var on_dot = on_dots[i];
                var off_dot = off_dots[i];
                if (page.hasClass("spt_wizard_selected")) {
                    page.removeClass("spt_wizard_selected");
                }
                page.setStyle("display", "none");
                on_dot.setStyle("display", "none");
                off_dot.setStyle("display", "");
            }

            var back = top.getElement(".spt_wizard_back");
            var next = top.getElement(".spt_wizard_next");
            next.setStyle("display", "");
            back.setStyle("display", "");
            if (selected_index == 0) {
                back.setStyle("display", "none");
            }
            else if (selected_index == pages.length-1) {
                next.setStyle("display", "none");
            }

            var page = pages[selected_index];
            page.setStyle("display", "");
            page.addClass("spt_wizard_selected");
            var on_dot = on_dots[selected_index];
            var off_dot = off_dots[selected_index];
            on_dot.setStyle("display", "");
            off_dot.setStyle("display", "none");

            '''
        } )


        """
        for i, widget in enumerate(self.widgets):
            name_div = DivWdg()
            div.add(name_div)
            name_div.add_class("spt_wizard_link")
            name_div.add_attr("spt_selected_index", i)
            name_div.add_class("hand")
            name_div.add_style("float: left")
            name_div.add_style("margin-left: %spx" % left)
            name = widget.get_name()
            name_div.add(name)
            name_div.add_style("width: %spx" % width)
            name_div.add_style("text-align: center")
        """

        div.add("<br clear='all'/>")
        return div

    def get_bottom_wdg(self):
        from tactic.ui.widget import ActionButtonWdg
        div = DivWdg()
        div.add_style("margin: 10px 10px 0px 0px")


        back = ActionButtonWdg(title="< Back", tip="Go back to last page", color="secondary")
        div.add(back)
        back.add_class("spt_wizard_back")
        back.add_style("float: left")

        # FIXME: need to do this because set_style is not the same element as
        # add class
        back.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_wizard_top");
        var back = top.getElement(".spt_wizard_back");
        back.setStyle("display", "none");
        '''
        } )

        back.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_wizard_top");
        var pages = top.getElements(".spt_wizard_page");
        var on_dots = top.getElements(".spt_wizard_on_dot");
        var off_dots = top.getElements(".spt_wizard_off_dot");

        // check boundary
        if (pages[0].hasClass("spt_wizard_selected")) {
            return;
        }

        var selected_index = 0;
        for (var i = 0; i < pages.length; i++) {
            var page = pages[i];
            var on_dot = on_dots[i];
            var off_dot = off_dots[i];
            if (page.hasClass("spt_wizard_selected")) {
                page.removeClass("spt_wizard_selected");
                selected_index = i;
            }
            page.setStyle("display", "none");
            on_dot.setStyle("display", "none");
            off_dot.setStyle("display", "");
        }

        if (selected_index == 1) {
            var back = top.getElement(".spt_wizard_back");
            back.setStyle("display", "none");
        }
        if (selected_index == pages.length-1) {
            var next = top.getElement(".spt_wizard_next");
            next.setStyle("display", "");
        }

        var page = pages[selected_index-1];
        page.setStyle("display", "");
        page.addClass("spt_wizard_selected");
        var on_dot = on_dots[selected_index-1];
        var off_dot = off_dots[selected_index-1];
        on_dot.setStyle("display", "");
        off_dot.setStyle("display", "none");

        '''
        } )





        if self.submit_button:
            submit = self.submit_button
        else:
            submit_title = self.kwargs.get("submit_title")
            command = self.kwargs.get("command")
            script = self.kwargs.get("script")
            jsscript = self.kwargs.get("jsscript")

            if not submit_title:
                submit_title = "Submit"
            submit = ActionButtonWdg(title="%s >>" % submit_title, tip=submit_title, color="primary")
            submit.add_class("spt_wizard_submit")
            submit.add_behavior( {
            'type': 'click_up',
            'command': command,
            'script': script,
            'jsscript': jsscript,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_wizard_top");

            var values = spt.api.Utility.get_input_values(top);

            var server = TacticServerStub.get();
            try {
                if (bvr.command) {
                    spt.app_busy.show("Executing ...", "");
                    server.execute_cmd(bvr.command, values);
                }
                else if (bvr.jsscript) {
                    var values = spt.api.get_input_values(top, null, false);
                    spt.CustomProject.run_script_by_path(bvr.jsscript, values, bvr);
                }
                else if (bvr.script) {
                    var values = spt.api.get_input_values(top, null, false);
                    server.execute_python_script(bvr.script, {values:values});
                }
                else {
                    alert("No script or command defined");
                }
            }
            catch(e) {
                console.log(e);
                var xml = spt.parse_xml(e);
                var node = xml.getElementsByTagName("string")[0];
                if (node) {
                    var error = node.textContent;
                    spt.error("Error: " + error);
                    spt.app_busy.hide();
                }
                else {
                    alert(e);
                }
                throw(e);
            }
            spt.app_busy.hide();

            '''
            } )



        div.add(submit)
        submit.add_style("float: right")


        next = ActionButtonWdg(title="Next >", tip="Go to next page", color="secondary")
        div.add(next)
        next.add_style("margin-right: 5px")
        next.add_class("spt_wizard_next")
        next.add_style("float: right")

        next.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        var top = bvr.src_el.getParent(".spt_wizard_top");
        var pages = top.getElements(".spt_wizard_page");
        var on_dots = top.getElements(".spt_wizard_on_dot");
        var off_dots = top.getElements(".spt_wizard_off_dot");


        // check boundary
        if (pages[pages.length-1].hasClass("spt_wizard_selected")) {
            return;
        }

        var selected_index = 0;
        for (var i = 0; i < pages.length; i++) {
            var page = pages[i];
            var on_dot = on_dots[i];
            var off_dot = off_dots[i];
            if (page.hasClass("spt_wizard_selected")) {
                page.removeClass("spt_wizard_selected");
                selected_index = i;
            }

            page.setStyle("display", "none");
            on_dot.setStyle("display", "none");
            off_dot.setStyle("display", "");
        }

        if (selected_index == pages.length-2) {
            var next = top.getElement(".spt_wizard_next");
            next.setStyle("display", "none");
        }
        if (selected_index == 0) {
            var back = top.getElement(".spt_wizard_back");
            back.setStyle("display", "");
        }

        var page = pages[selected_index+1];
        page.setStyle("display", "");
        page.addClass("spt_wizard_selected");
        var on_dot = on_dots[selected_index+1];
        var off_dot = off_dots[selected_index+1];
        on_dot.setStyle("display", "");
        off_dot.setStyle("display", "none");

        '''
        } )


        div.add("<br clear='all'/>")
        return div


class TestWizardWdg(BaseRefreshWdg):

    def get_display(self):
        top = DivWdg()
        top.add_color("color", "color")
        top.add_color("background", "background")
        top.add_style("padding: 10px")
        top.add_border()

        wizard = WizardWdg(title="Project Creation Wizard")
        top.add(wizard)

        page = DivWdg()
        first = self.get_first_page()
        first.add_style("width: 500px")
        first.add_style("height: 300px")
        page.add(first)
        wizard.add(page, "First")


        page = DivWdg()
        second = self.get_second_page()
        second.add_style("width: 500px")
        second.add_style("height: 300px")
        page.add(second)
        wizard.add(page, "Second")

        page = DivWdg()
        third = DivWdg()
        third.add_style("width: 500px")
        third.add_style("height: 300px")
        third.add("Third Page")
        page.add(third)
        wizard.add(page, "Third")

        page = DivWdg()
        fourth = DivWdg()
        fourth.add_style("width: 500px")
        fourth.add_style("height: 300px")
        fourth.add("Fourth Page")
        page.add(fourth)
        wizard.add(page, "Fourth")



        return top

    def get_first_page(self):
        div = DivWdg()
        div.add("First Page")
        div.add("<br/>")
        div.add("<br/>")

        div.add("Project Name: ")
        div.add(TextWdg("project_name"))
        div.add("<br/>")
        div.add("<br/>")
        div.add("Project Title: ")
        div.add(TextWdg("project_title"))
        div.add("<br/>")

        return div

    def get_second_page(self):
        div = DivWdg()
        div.add("Second Page")
        div.add("<br/>")
        div.add("<br/>")

        div.add("Column1: ")
        div.add(TextWdg("column1"))
        div.add("<br/>")
        div.add("<br/>")
        div.add("Column2: ")
        div.add(TextWdg("column2"))
        div.add("<br/>")

        return div


__all__.append("ProjectWizardWdg")
class ProjectWizardWdg(BaseRefreshWdg):

    def get_display(self):
        top = DivWdg()
        top.add_color("color", "color")
        top.add_color("background", "background")
        top.add_style("padding: 15px")
        top.add_border()

        wizard = WizardWdg(title="Project Creation Wizard")
        top.add(wizard)

        page = DivWdg()
        first = self.get_first_page()
        first.add_style("width: 500px")
        first.add_style("height: 300px")
        page.add(first)
        wizard.add(page, "Project Title")


        page = DivWdg()
        first = self.get_second_page()
        first.add_style("width: 500px")
        first.add_style("height: 300px")
        page.add(first)
        wizard.add(page, "Foo")


        page = DivWdg()
        page.add("Hello world!!!")
        text = TextWdg("wow")
        page.add(text)
        wizard.add(page, "Hello!!")



        return top


    def get_first_page(self):
        div = DivWdg()

        div.add("<br/>")

        div.add("Project Title: ")
        text = TextWdg("project_title")
        div.add(text)
        div.add("<br/>"*2)

        div.add("The project title can be more descriptive and contain spaces")

        div.add("<br/><br/><hr/><br/>")

        div.add("Project Code: ")
        text = TextWdg("project_code")
        div.add(text)
        div.add("<br/>"*2)

        div.add('''* Note: the project code must contain only alphanumeric characters [A-Z]/[0-9] and only an '_' as a separator''')

        return div



    def get_second_page(self):
        div = DivWdg()

        div.add("Import Template")

        div.add("<br/>" * 2)

        div.add('''Import a template''')

        div.add("<br/>" * 2)

        div.add('''Copy from project ...''')

        return div




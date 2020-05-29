############################################################
#
#    Copyright (c) 2008, Southpaw Technology
#                        All Rights Reserved
#
#    PROPRIETARY INFORMATION.  This software is proprietary to
#    Southpaw Technology, and is not to be reproduced, transmitted,
#    or disclosed in any way without written permission.
#
#

__all__ = ['HiddenRowElementWdg', 'RowAddElementWdg', 'HiddenRowContainerWdg']

from pyasm.common import jsondumps, Common
from pyasm.web import DivWdg, SpanWdg
from pyasm.search import Search

from tactic.ui.common import BaseTableElementWdg, BaseRefreshWdg
from tactic.ui.widget import SwapDisplayWdg

class HiddenRowElementWdg(BaseTableElementWdg):

    ARGS_KEYS = {
    'dynamic_class': {
        'description': 'The sub widget to display',
        'type': 'recursive',
        'category': 'SubWidget'
    },
    'icon': {
        'description': "Icon to use",
        'type': 'TextWdg',
        'category': 'Display'
    },
    'icon_tip': {
        'description': "Tip for an icon. If unset, it's based on element name",
        'type': 'TextWdg',
        'category': 'Display'
    },

    'label': {
        'description': 'Expression to evaluate the label of widget',
        'type': 'TextWdg',
        'category': 'Display'
    }

    }



    def init(self):
        self.layout = None

    def is_editable(self):
        return False

    def get_width(self):
        return 30


    def handle_layout_behaviors(self, layout):

        self.layout = layout

        # FIXME: not needed ... but need a way to make calling this twice safe
        #SwapDisplayWdg.handle_top(self.layout)

        class_name = self.get_option("dynamic_class")
        if not class_name:
            class_name = "tactic.ui.panel.TableLayoutWdg"

        self.layout.generate_widget_key(class_name, self.kwargs)

        kwargs = jsondumps(self.kwargs)

        name = self.get_name()
        
        self.layout.add_relay_behavior( {
        'type': 'click',
        'col_name': name,
        'bvr_match_class': 'spt_hidden_row_%s' % name,
        'class_name': class_name,
        'cbjs_action': '''

        var swap_top = bvr.src_el.getElement(".spt_swap_top");
        var state = swap_top.getAttribute("spt_state");

        var row = bvr.src_el.getParent(".spt_table_row");
        var search_key = row.getAttribute("spt_search_key");
        search_key = search_key.replace(/\\&/, "\\&amp;");

        var class_name = bvr.src_el.getAttribute("SPT_WIDGET_KEY");

        eval("var kwargs = " + %s);
        kwargs['search_key'] = search_key;
        kwargs['__hidden__'] = true;
        kwargs['src_el'] = bvr.src_el;

        if (state == 'on') {
            spt.table.remove_hidden_row(row, bvr.col_name);
        }
        else {
            spt.table.add_hidden_row(row, class_name, kwargs);
        }

        ''' % (jsondumps(kwargs))
        } )




    def get_display(self):

        sobject = self.get_current_sobject()

        name = self.get_name()

        top = DivWdg()

        if sobject.is_insert():
            top.add_style("opacity: 0.3")
        else:
            # this gives the swap it's behaviors, so will be disabled
            # on insert
            top.add_class("spt_hidden_row_%s" % name)


        label = self.get_option("label")
        if label:
            label = Search.eval(label, sobject)
        else:
            label = None
        icon = self.get_option("icon")

        swap = SwapDisplayWdg(title=label, icon=icon, show_border=True)
        swap.set_behavior_top(self.layout)

        top.add(swap)

        return top



class RowAddElementWdg(HiddenRowElementWdg):
    ARGS_KEYS = {
    'search_type': {
        'description': 'The sub widget to display',
        'type': 'TextWdg',
        'category': 'Options'
    },
    }
 

    def handle_layout_behaviors(self, layout):

        name = self.get_name()
        self.layout = layout

        self.layout.add_relay_behavior( {
        'type': 'click',
        'bvr_match_class': 'spt_hidden_row_%s' % name,
        'cbjs_action': '''


        var related_types = bvr.src_el.getAttribute("spt_related_types");
        search_types = related_types.split(",");


        var swap_top = bvr.src_el.getElement(".spt_swap_top");
        var state = swap_top.getAttribute("spt_state");


        var row = bvr.src_el.getParent(".spt_table_row");

        var level = row.getAttribute("spt_level");
        if (level) {
            level = parseInt(level) + 1;
        }
        else {
            level = 1;
        }


        var parent_type = row.getAttribute("spt_parent_type");
        var search_key = row.getAttribute("spt_search_key");

        if (state != 'on') {
            for (var i = 0; i < search_types.length; i++) {
                if (search_types[i] == parent_type) {
                    continue;
                }
                spt.table.add_rows(row, search_types[i], level);
            }
        }
        else {

            var parts = search_key.split("?");
            var search_type = parts[0];

            var sibling = row.getNext();
            var count = 0;
            while (1) {
                if (sibling == null) break;

                var sibling_key = sibling.getAttribute("spt_search_key");
                var parts = sibling_key.split("?");
                var sibling_type = parts[0];

                if (sibling_type == search_type) {
                    break;
                }

                next = sibling.getNext();
                sibling.destroy()
                sibling = next;

                count += 1;
                if (count > 500) {
                    alert("Error: runaway count");
                    break;
                }
            }

            spt.table.recolor_rows();
        }
        '''
        } )




    def get_display(self):

        sobject = self.get_current_sobject()

        sobj_name = sobject.get_name()
        search_type = sobject.get_search_type_obj()
        stype_title = search_type.get_title()

        # get related types
        related_types = self.get_option("related_types")
        if not related_types:
            from pyasm.biz import Schema
            schema = Schema.get()
            related_types = schema.get_related_search_types(search_type.get_base_key())

        if isinstance(related_types, list):
            related_types = ",".join(related_types)

        related_types = "sthpw/task"

        name = self.get_name()

        top = DivWdg()
        top.add_attr("spt_related_types", related_types)
        top.add_style("min-width: 250px")

        if sobject.is_insert():
            top.add_style("opacity: 0.3")
        else:
            # this gives the swap it's behaviors, so will be disabled
            # on insert
            top.add_class("spt_hidden_row_%s" % name)


        self.set_option("label", "{}%s" % (sobj_name))
        label = self.get_option("label")
        if label:
            label = Search.eval(label, sobject)
        else:
            label = None
        if not label:
            label = sobject.get_code()

        icon = self.get_option("icon")
        icon = "DETAILS"

        #from pyasm.widget import ThumbWdg
        #thumb_div = DivWdg()
        #thumb = ThumbWdg()
        #thumb_div.add(thumb)
        #thumb.set_sobject(search_type)
        #thumb.set_option("icon_size", "16")
        #thumb_div.add_style("float: left")
        #thumb_div.add_style("width: 22px")

        title = DivWdg()
        #title.add(thumb_div)
        title.add(label)
        stype_div = SpanWdg("&nbsp;&nbsp;(%s)" % stype_title)
        title.add(stype_div)
        stype_div.add_style("opacity: 0.3")
        stype_div.add_style("font-syle: italic")
        stype_div.add_style("font-size: 9px")


        max_level = 1
        level = self.kwargs.get("level") or 0
        if level >= max_level:
            top.add(title)

        else:

            #swap = SwapDisplayWdg(title=label, icon=icon)
            swap = SwapDisplayWdg(title=title, icon=icon)
            swap.set_behavior_top(self.layout)
            swap.add_style("float: left")
            swap.add_class("spt_level_listen")

            top.add(swap)

        return top


# TEST
class HiddenRowContainerWdg(BaseRefreshWdg):
    def get_display(self):
        top = self.top

        class_name = self.kwargs.get("display_class_name")
        kwargs = self.kwargs.get("display_kwargs")

        top.add_style("border: solid 1px #777")
        top.add_style("position: absolute")
        top.add_style("z-index: 100")
        top.add_style("box-shadow: 2px 2px 4px 4px #aaa")
        top.add_style("background: #FFF")
        top.add_style("margin-right: 200px")
        top.add_style("margin-top: -20px")
        top.add_style("overflow: hidden")

        #widget_html = "<div style='border: solid 1px #777; position: absolute; z-index: 100; box-shadow: 2px 2px 4px 4px #aaa; background: #FFF; margin-right: 20px; margin-top: -20px; overflow: hidden'>" + widget_html + "</div>";

        widget = Common.create_from_class_path(class_name, kwargs)
        top.add(widget)

        show_pointer = self.kwargs.get("show_pointer")
        if show_pointer not in [False, 'false']:
            self.get_arrow_wdg()


        return top


    def get_arrow_wdg(self):

        pointer_wdg = DivWdg()
        pointer_wdg.add_class("spt_popup_pointer")
        widget.add(pointer_wdg)
        pointer_wdg.add_style("position: absolute")
        pointer_wdg.add_style("float: left")
        pointer_wdg.add_style("background-color", "transparent")
        #pointer_wdg.add("/\\")

        arrow = DivWdg()
        pointer_wdg.add(arrow)
        arrow.add_style("transform: rotate(-45deg)")
        arrow.add_style("-webkit-transform: rotate(-45deg)")

        arrow.add_style("border-style: solid")
        arrow.add_style("border-width: 1px 1px 0px 0px")
        arrow.add_style("border-color: #000")
        arrow.add_style("width: 20px")
        arrow.add_style("height: 20px")
        arrow.add_style("margin-top: 0px")
        arrow.add_color("background-color", "background", -10)


        pointer_wdg.add_style("left: %s" % (15-offset.get('x')))
        pointer_wdg.add_style("top: -10")
        pointer_wdg.add_style("height: 11")

        pointer_wdg.add_style("z-index: 10")

        return pointer_wdg





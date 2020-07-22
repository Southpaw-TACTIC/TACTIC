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

__all__ = ['BaseNodeWdg', 'PipelineCanvasWdg', 'NodeRenameWdg']

from tactic.ui.common import BaseRefreshWdg

from pyasm.biz import ProjectSetting, Task, Pipeline
from pyasm.common import Container, Common, jsondumps
from pyasm.web import DivWdg, WebContainer, Table, Widget, HtmlElement
from pyasm.command import Command
from pyasm.search import Search, SearchType

from pyasm.widget import ProdIconButtonWdg, IconWdg, TextWdg
from tactic.ui.container import GearMenuWdg, Menu, MenuItem

from tactic.ui.widget import ActionButtonWdg, IconButtonWdg



class BaseNodeWdg(BaseRefreshWdg):

    def get_node_type(self):
        return self.kwargs.get("node_type")

    def get_title(self):
        node_type = self.get_node_type()
        title = Common.get_display_title(node_type)
        return title

    def use_default_node_behavior(self):
        return True

    def get_title_background(self):
        return "rgba(0,0,0,0.5)"


    def show_default_name(self):
        return True

    def get_width(self):
        return 120

    def get_height(self):
        return 40


    def style_label(self, label):
        return


    def get_label_width(self):
        return

    def get_border_radius(self):
        return 0

    def get_border_width(self):
        return 1

    def get_border_color(self):
        return "black"

    def get_box_shadow(self):
        return ""

    def get_nob_offset(self):
        return 0

    def get_node_behaviors(self):
        return []

    def get_shape(self):
        return ""

    def show_title(self):
        return True

    def get_content(self):
        node_type = self.get_node_type()
        div = DivWdg()

        title = self.get_title()
        if not title:
            return div

        title_background = self.get_title_background()

        inner = DivWdg()
        div.add(inner)

        inner.add(title)

        inner.add_style("font-size: 8px")
        inner.add_style("background: %s" % title_background)
        inner.add_style("color: #FFF")
        inner.add_style("text-align: center")

        return div


    def get_display(self):


        top = self.top
        top.add_style("overflow: hidden")
        top.add_class("spt_custom_node")

        width = self.get_width()
        height = self.get_height()


        border_radius = self.get_border_radius()
        border_width = self.get_border_width()
        border_color = self.get_border_color()
        box_shadow = self.get_box_shadow()


        top.add_style("width", width)
        top.add_style("height", str(height)+"px")

        top.add_attr("spt_border_color", border_color)
        top.add_attr("spt_box_shadow", box_shadow)

        top.add_style("margin: 0px auto")



        shape = self.get_shape()

        if shape == "star":
            self.set_star_shape()

        elif shape == "parallelogram":
            self.set_parallelogram_shape()

        elif shape == "circle":
            top.add_style("border-radius: %spx" % (height/2))

        elif shape == "elipse":
            top.add_style("width", str(height)+"px")
            top.add_style("border-radius: %spx" % border_radius)

        elif shape == "diamond":
            top.add_style("transform: rotate(-45deg)")
            top.add_style("width", str(height)+"px")

        elif shape == "image":

            icon = self.get_icon()

            if icon.startswith("fa-"):
                top.add("<div style='position: absolute; top: 0px; left: 0px'><i class='fa %s fa-5x'> </i></div>" % icon)
                top.add_attr("spt_border_color", "transparent")
                top.add_style("border-color: transparent")
            else:
                top.add("<div style=''><img style='width: 100%%' src='%s'/></div>" % icon)
                top.add_style("overflow: hidden")
                top.add_style("border-radius: %spx" % border_radius)

            top.add_style("background: transparent")

        else:
            top.add_style("border-radius: %spx" % border_radius)

        top.add_style("border: solid %spx %s" % (border_width, border_color))
        top.add_style("box-shadow: %s" % box_shadow)


        content_div = DivWdg()
        content_div.add_style("overflow: hidden")
        top.add(content_div)


        if shape == "image":
            content_div.add_style("display: none")

        content = self.get_content()
        content_div.add(content)
        content.add_class("spt_content")
        content.add_style("width", "100%")
        content.add_style("height", "100%")

        # NOTE: is this necessary
        for widget in self.widgets:
            top.add(widget)


        is_refresh = self.kwargs.get("is_refresh")
        if is_refresh:
            return content

        return top


    def set_parallelogram_shape(self):
        div = self.top
        div.add_style("-webkit-transform: skew(20deg)")
        div.add_style("-moz-transform: skew(20deg)")
        div.add_style("-o-transform: skew(20deg)")
        div.add_border()


    def set_star_shape(self):

        # FIXME: this doesn't work too well yet

        div = self.top

        star = DivWdg()
        div.add(star)
        star.add_class("star-six")

        from pyasm.web import HtmlElement
        style = HtmlElement.style()
        div.add(style)
        style.add('''
        .star-six {
            width: 0px;
            height: 0px;
            border-left: 50px solid transparent;
            border-right: 50px solid transparent;
            border-bottom: 100px solid red;
            position: relative;
        }
        .star-six:after {
            width: 0px;
            height: 0px;
            border-left: 50px solid transparent;
            border-right: 50px solid transparent;
            border-top: 100px solid red;
            position: absolute;
            content: "";
            top: 30px;
            left: -50px;
        }
        ''')



class PipelineCanvasWdg(BaseRefreshWdg):
    '''Pipeline Widget'''

    def init(self):
        self.top = DivWdg()
        self.set_as_panel(self.top)
        self.top.add_class("spt_pipeline_top")
        self.unique_id = self.top.set_unique_id()

        self.is_editable = self.kwargs.get("is_editable")
        if self.is_editable in ['false', False]:
            self.is_editable = False
        else:
            self.is_editable = True
        #self.is_editable = False

        self.top.add_behavior( {
        'type': 'load',
        'cbjs_action': '''

            // This resizes pipeline canvas
            let container = bvr.src_el;
            container.last_size = {};
            var canvas = container.getElement("canvas");
            var resize = function() {
                let container = spt.pipeline.top;
                if (!container || !container.isVisible() ) {
                    return;
                }
                
                let size = container.getSize();
                spt.pipeline.set_size(size.x, size.y);
                container.last_size = size;
            }
            var interval_id = setInterval( resize, 250);
            container = interval_id;
        '''
        } )

        

        self.top.add_behavior( {
        'type': 'unload',
        'cbjs_action': '''
            let container = bvr.src_el;
            clearInterval( container.interval_id );
        '''
        } )

        self.top.add_behavior( { 
            'type': 'listen',
            'event_name': 'window_resize',
            'cbjs_action': '''
                let container = bvr.src_el;
                
                if (!container.isVisible()) return;
                
                if (!spt.pipeline) return;

                spt.pipeline.set_top(container);
                
                let size = container.getSize();
                spt.pipeline.set_size(size.x, size.y);
                container.last_size = size;
            '''
        } )

        default_node_type = self.kwargs.get("default_node_type") or ""
        self.top.add_attr("spt_default_node_type", default_node_type)


        self.background_color = self.kwargs.get("background_color")
        if not self.background_color:
            self.background_color = self.top.get_color("background", 10)

        self.top.add_style("height", "100%")
        self.top.add_style("width", "100%")

        # create an inner and outer divs
        self.nob_mode = self.kwargs.get('nob_mode')
        if not self.nob_mode:
            self.nob_mode = "visible"

        self.line_mode = self.kwargs.get('line_mode')
        if not self.line_mode:
            self.line_mode = "bezier"


        self.has_prefix = self.kwargs.get('has_prefix')
        if self.has_prefix in [True, 'true']:
            self.has_prefix = True
        else:
            self.has_prefix = False

        self.filter_node_name = self.kwargs.get('filter_node_name')
        if self.filter_node_name in [True, 'true']:
            self.filter_node_name = True
        else:
            self.filter_node_name = False

        self.allow_cycle = self.kwargs.get('allow_cycle')
        if self.allow_cycle in [False, 'false']:
            self.allow_cycle = False
        else:
            self.allow_cycle = True

        self.add_node_behaviors = self.kwargs.get("add_node_behaviors")
        if (self.add_node_behaviors in [False, 'false']):
            self.add_node_behaviors = False
        else:
            self.add_node_behaviors = True


    def get_node_description(self, node_type):

        node_descriptions = {
            'manual': 'A basic process where work is done by a person',
            'action': 'An automated process which can execute a script or command',
            'condition': 'An automated process which can execute a script or command',
            'approval': 'A process where a task will be created for a specific user whose job is to approve work down in the previous processes',
            'hierarchy': 'A process that references a sub-workflow',
            'dependency': 'A process that listens to another process and sets its status accordingly'
        }

        return node_descriptions.get(node_type)


    def get_unique_id(self):
        return self.unique_id


    def get_show_nobs(self):
        show_nobs =  self.kwargs.get("show_nobs")
        if show_nobs in ["false", False]:
            return False
        else:
            return True


    def get_canvas_title(self):

        canvas_title = DivWdg()
        canvas_title.add_border()
        canvas_title.add_style("padding: 3px 30px")
        canvas_title.add_style("position: absolute")
        canvas_title.add_style("font-weight: bold")
        canvas_title.add_style("top: 0px")
        canvas_title.add_style("left: 50%")
        canvas_title.add_style('transform: translateX(-50%)')
        canvas_title.add_style("z-index: 150")
        canvas_title.add_style("box-shadow: 0px 5px 5px rgba(0,0,0,0.05)")
        canvas_title.add_color("background", "background")

        canvas_title.add_class("spt_pipeline_editor_current2")
        canvas_title.add_class("hand")
        canvas_title.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_pipeline_link',
            'cbjs_action': '''
            spt.pipeline.clear_canvas();
            var pipeline_code = bvr.src_el.getAttribute("spt_pipeline_code");
            spt.pipeline.import_pipeline(pipeline_code);

            var pipeline_name = bvr.src_el.innerHTML;

            var parent = bvr.src_el.getParent(".spt_pipeline_editor_current2");
            var els = parent.getElements(".spt_pipeline_link");

            var html = [];
            for (var i = 0; i < els.length; i++) {
                html.push(els[i].outerHTML);
                if (els[i].innerHTML == pipeline_name) {
                    break;
                }
            }

            parent.innerHTML = html.join(" / ");
            spt.command.clear();
            spt.pipeline.fit_to_canvas();
            '''
        } )

        canvas_title.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_pipeline_link',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "rgba(0,0,0,0.2)");
            '''
        } )
        canvas_title.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_pipeline_link',
            'cbjs_action': '''
            bvr.src_el.setStyle("background", "");
            '''
        } )

        return canvas_title



    def get_snapshot_wdg(self):

        snapshot_top = DivWdg()
        snapshot_top.add_style("position: absolute")
        snapshot_top.add_style("top: 0px")
        snapshot_top.add_style("left: 0px")
        snapshot_top.add_style("z-index: 150")
        snapshot_top.add_style("border: solid 1px #DDD")
        snapshot_top.add_style("overflow: hidden")

        snapshot_top.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var pos = bvr.src_el.getPosition();

            var container = bvr.src_el.getElement(".spt_pipeline_snapshot");
            var canvas_size = container.size;
            var full_scale = container.scale;
            var cur_scale = spt.pipeline.get_scale();
            var ratio = full_scale / cur_scale;




            var outline = bvr.src_el.getElement(".spt_outline");
            outline_pos = outline.getPosition(bvr.src_el);
            outline_size = outline.getSize();

            var container_size = container.getSize();

            // find out where it hit the target
            var x = mouse_411.curr_x - pos.x;
            var y = mouse_411.curr_y - pos.y;

            var dx = (x - outline_pos.x - outline_size.x/2) * canvas_size.x / container_size.x / ratio;
            var dy = (y - outline_pos.y - outline_size.y/2) * canvas_size.y / container_size.y / ratio;

            spt.pipeline.move_all_nodes(-dx, -dy);
            spt.pipeline.move_all_folders(-dx, -dy);


            '''
        } )

        snapshot_wdg = DivWdg()
        snapshot_top.add(snapshot_wdg)
        snapshot_wdg.add_class("spt_pipeline_snapshot")

        outline_wdg = DivWdg()
        outline_wdg.add_class("spt_outline")
        snapshot_top.add(outline_wdg)
        outline_wdg.add_style("border", "solid 0.5px #666")
        #outline_wdg.add_style("width", "25px")
        #outline_wdg.add_style("height", "25px")
        outline_wdg.add_style("position: absolute")
        outline_wdg.add_style("top: 10px")
        outline_wdg.add_style("left: 10px")

        outline_wdg.add_style("background", "rgba(0,0,0,0.02)")

        return snapshot_top



    def get_styles(self):

        style = HtmlElement.style("""

            .spt_pipeline_canvas {
                z-index: 200;
                position: absolute;
                top: 0px;
                left: 0px;
                pointer-events: auto;
            }

        """)

        return style

    def get_display(self):

        top = self.top
        top.add_style("position: relative")

        top.add(self.get_styles())

        version_2_enabled = ProjectSetting.get_value_by_key("version_2_enabled")
        top.add_attr("version_2_enabled", version_2_enabled)

        show_title = self.kwargs.get("show_title")
        if show_title not in ['false', False]:
            top.add(self.get_canvas_title())


        top.add(self.get_snapshot_wdg())


        # outer is used to resize canvas
        outer = DivWdg()

        top.add(outer)
        outer.add_class("spt_pipeline_resize")
        outer.add_class("spt_resizable")
        outer.add_style("position: relative")

        outer.add_style("overflow: hidden")

        if self.kwargs.get("show_border") not in [False, 'false']:
            outer.add_border()


        from tactic.ui.input import TextInputWdg
        hot_key_div = DivWdg()
        outer.add(hot_key_div)
        hot_key_div.add_style("margin-left: -5000px")
        hot_key_div.add_style("position: absolute")
        #hot_key_div.add_style("z-index: 1000")

        hot_key_input = TextInputWdg(name="hot_key_input")
        hot_key_div.add(hot_key_input)
        hot_key_input.add_class("spt_hot_key")
        outer.add_behavior( {
            'type': 'mouseenter',
            'cbjs_action': '''
            spt.pipeline.init(bvr);

            var top = bvr.src_el.getParent(".spt_pipeline_top");
            top.hot_key_state = true;

            var input = bvr.src_el.getElement(".spt_hot_key");
            input.focus();
            '''

        } )
        outer.add_behavior( {
            'type': 'mouseup',
            'cbjs_action': '''
            var input = bvr.src_el.getElement(".spt_hot_key");
            input.focus();
            '''

        } )

        outer.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_pipeline_top");
            top.hot_key_state = false;

            var input = bvr.src_el.getElement(".spt_hot_key");
            input.blur();
            '''

        } )

        hot_key_input.add_behavior( {
            'type': 'blur',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_pipeline_top");
            if ( top.hot_key_state == false) return;

            bvr.src_el.focus();
            '''

        } )


        outer.add_attr("onmousemove", "spt.pipeline._mouse_pos = {x: event.clientX, y: event.clientY}")


        outer.add_behavior( {
            'type': 'keyup',
            'cbjs_action': '''
            var key = evt.key;

            //spt.pipeline.set_top(bvr.src_el.getElement(".spt_pipeline_top"));

            if (key == "a") {
                spt.pipeline.fit_to_canvas();
            }
            else if (key == "f") {
                var selected = spt.pipeline.get_selected_nodes();
                if (!selected.length) {
                    spt.pipeline.fit_to_canvas();
                }
                else {
                    spt.pipeline.fit_to_node(selected[0]);
                    spt.pipeline.select_single_node(selected[0]);
                    spt.pipeline.set_scale(1.25);
                }
            }
            else if (key == "s") {

                // FIXME: this is for pipeline editor
                var top = bvr.src_el.getParent(".spt_pipeline_top");
                top.hot_key_state = false;

                var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
                if (top) {
                    var search_el = top.getElement(".spt_node_search");
                    search_el.focus();
                }
            }
            else if (key == "u") {
                spt.command.undo_last();
            }
            else if (key == "r") {
                spt.command.redo_last();
            }
            else if (key == "=") {
                var scale = spt.pipeline.get_scale();
                scale = scale * 1.05;
                spt.pipeline.set_scale(scale);
            }
            else if (key == "-") {
                var scale = spt.pipeline.get_scale();
                scale = scale / 1.05;
                spt.pipeline.set_scale(scale);
            }
            else if (key == "1") {
                var scale = 0.5;
                spt.pipeline.set_scale(scale);
            }
            else if (key == "2") {
                var scale = 1.0;
                spt.pipeline.set_scale(scale);
            }
            else if (key == "3") {
                var scale = 1.5;
                spt.pipeline.set_scale(scale);
            }

            else if (key == "backspace" || key == "delete") {
                spt.pipeline.delete_selected();

            } else if (key == "t") {
                spt.process_tool.toggle_side_bar(bvr.src_el);
                var top = bvr.src_el.getParent(".spt_pipeline_tool_top");
                if (top) {
                    var search_el = top.getElement(".spt_pipeline_type_search");
                    // FIXME: focus not working when using the hot key
                    search_el.focus();
                }

            } else if (key == "h") {
                var toolTop = bvr.src_el.getParent(".spt_pipeline_tool_top");
                var left = toolTop.getElement(".spt_pipeline_tool_left");
                var right = toolTop.getElement(".spt_pipeline_tool_right");
                var show_button = toolTop.getElement(".spt_show_sidebar");
                var hide_button = toolTop.getElement(".spt_hide_sidebar");

                if (right.classList.contains("spt_left_toggle")){
                    right.removeClass("spt_left_toggle");

                    left.setStyle("margin-left", "0px");
                    left.setStyle("opacity", "1");
                    right.setStyle("margin-left", "20.3%");
                    right.setStyle("width", "79%");
                    left.gone = false;
                    setTimeout(function(){
                        left.setStyle("z-index", "");
                    }, 250);

                    hide_button.setStyle("display", "");
                    show_button.setStyle("display", "none");
                } else {
                    right.addClass("spt_left_toggle");
                    left.setStyle("margin-left", "-21%");
                    left.setStyle("opacity", "0");
                    right.setStyle("margin-left", "0px");
                    right.setStyle("width", "100%");
                    left.gone = true;
                    setTimeout(function(){
                        left.setStyle("z-index", "-1");
                    }, 250);

                    hide_button.setStyle("display", "none");
                    show_button.setStyle("display", "");
                }


            } else if (key == "q") {
                spt.process_tool.show_side_bar(bvr.src_el);

            } else if (key == "w") {
                var container = spt.pipeline.take_snapshot();
                var scale = spt.pipeline.get_scale();
                container.scale = scale;

            } else if (key == "n") {

                var canvas = spt.pipeline.get_canvas();
                var groups = canvas.getElements(".spt_pipeline_group");
                if (groups.length) {
                    var selected_index = 0;
                    for (var i = 0; i < groups.length; i++) {
                        var group = groups[i];
                        if (group.hasClass("spt_selected")) {
                            group.removeClass("spt_selected");
                            selected_index = i;
                            break;
                        }
                    }

                    selected_index += 1;
                    if (selected_index >= groups.length) {
                        selected_index = 0;
                    }

                    var group = groups[selected_index];
                    group.addClass("spt_selected");
                    spt.pipeline.group.set_top(group);
                    var nodes = spt.pipeline.group.select_nodes();
                    spt.pipeline.fit_to_node(nodes);
                }


            } else if (evt.control == true && key == "c") {
                var nodes = spt.pipeline.get_selected_nodes();
                if (nodes) {
                    spt.notify.show_message(nodes.length + " Nodes Copied");
                }

                spt.pipeline.clipboard = nodes;


                var canvas_pos = bvr.src_el.getPosition()
                var first_pos = spt.pipeline.get_position(nodes[0]);

                var new_nodes = [];
                for (var i = 0; i < nodes.length; i++ ) {
                    var node = nodes[i];

                    var node_type = spt.pipeline.get_node_type(node);
                    var node_name = spt.pipeline.get_node_name(node);

                    var pos = spt.pipeline.get_position(node);
                    var new_pos = {
                        x: pos.x - first_pos.x,
                        y: pos.y - first_pos.y
                    };

                    var new_node = {
                        node_type: node_type,
                        pos: new_pos,
                        connects: [],
                    }

                    new_nodes.push(new_node);

                }

                for (var i = 0; i < nodes.length; i++ ) {
                    var node = nodes[i];
                    var node_name = spt.pipeline.get_node_name(node);
                    var new_node = new_nodes[i];

                    var connectors = spt.pipeline.get_connectors_from_node(node_name);
                    for (var j = 0; j < connectors.length; j++ ) {
                        var connector = connectors[j];
                        var to_node = connector.get_to_node();
                        var index = 0;
                        for (var k = 0; k < nodes.length; k++ ) {
                            if (to_node == nodes[k]) {
                                index = k;
                                break;
                            }
                        }
                        new_node.connects.push(k);
                    }

                }

                spt.pipeline.clipboard = new_nodes;


            } else if (evt.control == true && key == "x") {
                var nodes = spt.pipeline.get_selected_nodes();
                if (nodes) {
                    spt.pipeline.clipboard = nodes;
                    for (var i = 0; i < nodes.length; i++ ) {
                        spt.pipeline.remove_node(nodes[i]);
                    }
                    spt.notify.show_message(nodes.length + " Nodes Cut");
                }

            } else if (evt.control == true && key == "v") {

                var selected = spt.pipeline.get_selected_nodes();

                spt.pipeline.unselect_all_nodes();
                var nodes = spt.pipeline.clipboard;
                if (nodes) {
                    var mouse_pos = {x: 0, y: 0};
                    var mouse_pos = spt.pipeline._mouse_pos;
                    var canvas_pos = bvr.src_el.getPosition()
                    mouse_pos.x = mouse_pos.x - canvas_pos.x;
                    mouse_pos.y = mouse_pos.y - canvas_pos.y;


                    var nn = spt.pipeline.clipboard;
                    var new_nodes = [];
                    for (var i = 0; i < nn.length; i++) {
                        var data = nn[i];
                        var new_node_name = null;
                        var pos = data.pos;
                        var node_type = data.node_type;
                        var new_pos = { x: pos.x+mouse_pos.x, y: pos.y+mouse_pos.y};
                        var new_node = spt.pipeline.add_node(new_node_name, new_pos.x, new_pos.y, { node_type: node_type, });
                        new_nodes.push(new_node);
                        spt.pipeline.select_node(new_node);

                        if (i == 0) {
                            for (var j = 0; j < selected.length; j++) {
                                spt.pipeline.connect_nodes(selected[j], new_node);
                            }
                        }

                    }

                    for (var i = 0; i < nn.length; i++) {
                        var data = nn[i];
                        var new_node = new_nodes[i];
                        for (var j = 0; j < data.connects.length; j++) {
                            var connect = data.connects[j];
                            spt.pipeline.connect_nodes(new_node, new_nodes[connect]);
                        }
                    }
                }
            }


            '''
        } )





        process_menu = self.get_node_context_menu()
        if process_menu:
            menus = [process_menu.get_data()]

            # Simple context menu is for renaming and
            # deleting approval, action and condition nodes..
            simple_menu = self.get_simple_node_context_menu()
            simple_menus = [simple_menu.get_data()]

            menus_in = {
                'NODE_CTX': menus,
                'SIMPLE_NODE_CTX': simple_menus
            }

            if self.is_editable == True:
                from tactic.ui.container.smart_menu_wdg import SmartMenu
                SmartMenu.attach_smart_context_menu( outer, menus_in, False )

        # inner is used to scale
        inner = DivWdg()
        outer.add(inner)

        inner.add_class("spt_pipeline_scale")
        inner.add_style("z-index: 100")
        inner.add_style("position: absolute")
        inner.add_style("top: 0px")
        inner.add_style("left: 0px")
        inner.add_style("pointer-events: none")


        # load the js
        # FIXME: there is something initialized here that if schema is loaded
        # first and the pipeline, the pipelines editor does not work
        # correctly.  Loading the other way around works fine.
        #if not Container.get_dict("JSLibraries", "spt_pipeline"):
        if True:
            script = DivWdg()
            script.add_behavior( {
            'type': 'load',
            'cbjs_action': self.get_onload_js()
            } )
            inner.add(script)

        script = DivWdg()
        script.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
            spt.pipeline.first_init(bvr);
            '''
        } )
        inner.add(script)

        node_types = self.kwargs.get("node_types")
        if node_types:
            script.add_behavior( {
                'type': 'load',
                'node_types': node_types,
                'cbjs_action': '''

                spt.pipeline.set_node_types(bvr.node_types);

                '''
            } )


        # create a size widget for the node canvas
        canvas_size_wdg = DivWdg()
        inner.add(canvas_size_wdg)
        canvas_size_wdg.add_class("spt_pipeline_canvas_size")

        #canvas_size_wdg.add_style("border: solid 1px green")
        canvas_size_wdg.add_style("pointer-events: none")




        # create a canvas where all the nodes are drawn
        canvas = DivWdg()
        inner.add(canvas)

        canvas.add_class("spt_pipeline_canvas")
        canvas.add_style("width: 600")
        canvas.add_style("height: 600")
        canvas.set_attr("spt_background_color", self.background_color)

        if self.is_editable:
            is_editable = "true"
        else:
            is_editable = 'false'

        # add custom canvas behaviors on the canvas div instead
        canvas.add_behavior( {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "is_editable": is_editable,
            "drag_el": '@',
            "cb_set_prefix": 'spt.pipeline.canvas_drag'
        } )


        canvas.add_behavior( {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "modkeys": 'CTRL',
            "drag_el": '@',
            "cb_set_prefix": 'spt.pipeline.zoom_drag'
        } )


        if self.kwargs.get("use_mouse_wheel") in [True, 'true']:
            canvas.add_behavior( {
            "type": 'wheel',
            "cbjs_action": '''
                spt.pipeline.init(bvr);
                var scale = spt.pipeline.get_scale();
                if (evt.wheel < 0) {
                    var scale = scale / 1.1;
                }
                else {
                    var scale = scale * 1.1;
                }
                spt.pipeline.set_scale( scale );

            '''
            } )

        canvas.add_behavior( {
        "type": 'drag',
        "mouse_btn": 'LMB',
        "modkeys": 'SHIFT',
        "drag_el": '@',
        "cb_set_prefix": 'spt.pipeline.select_drag'
        } )


        # create the paint where all the connectors are drawn
        paint = self.get_paint()

        # add custom canvas behaviors on the canvas div instead
        self.canvas_behaviors = self.get_canvas_behaviors()
        for canvas_behavior in self.canvas_behaviors:
            outer.add_behavior( canvas_behavior )


        #paint.add_style("border: solid 1px blue");
        #paint.add_style("z-index: 1");


        outer.add(paint)


        paint.add_behavior( {
        "type": 'drag',
        "mouse_btn": 'LMB',
        "is_editable": is_editable,
        "drag_el": '@',
        "cb_set_prefix": 'spt.pipeline.canvas_drag'
        } )


        paint.add_behavior( {
        "type": 'drag',
        "mouse_btn": 'LMB',
        "modkeys": 'CTRL',
        "drag_el": '@',
        "cb_set_prefix": 'spt.pipeline.zoom_drag'
        } )


        if self.kwargs.get("use_mouse_wheel") in [True, 'true']:
            paint.add_behavior( {
            "type": 'wheel',
            "cbjs_action": '''
                spt.pipeline.init(bvr);
                var scale = spt.pipeline.get_scale();
                if (evt.wheel < 0) {
                    spt.pipeline.set_scale( scale / 1.1 );
                }
                else {
                    spt.pipeline.set_scale( scale * 1.1 );
                }
            '''
            } )



        paint.add_behavior( {
        "type": 'drag',
        "mouse_btn": 'LMB',
        "modkeys": 'SHIFT',
        "drag_el": '@',
        "cb_set_prefix": 'spt.pipeline.select_drag'
        } )



        # add a template node
        template_div = DivWdg()
        template_div.add_style("display: none")
        template_div.add_class("spt_pipeline_template")
        inner.add(template_div)
        template_div.add_class("SPT_TEMPLATE")

        node = self.get_node("node", node_type="node")
        node.add_style("left: 0px")
        node.add_style("top: 0px")
        template_div.add(node)

        node = self.get_node("manual", node_type="manual")
        node.add_style("left: 0px")
        node.add_style("top: 0px")
        template_div.add(node)


        # add an unknown type
        node = self.get_node("unknown", node_type="unknown")
        node.add_style("left: 0px")
        node.add_style("top: 0px")
        template_div.add(node)



        # add folder group node
        folder = self.get_folder("folder")
        template_div.add(folder)

        # add approval node
        approval = self.get_approval_node("approval")
        template_div.add(approval)

        condition = self.get_condition_node("condition")
        template_div.add(condition)

        action = self.get_node("action", node_type="action")
        template_div.add(action)

        heirarchy = self.get_node("hierarchy", node_type="hierarchy")
        template_div.add(heirarchy)

        dependency = self.get_node("dependency", node_type="dependency")
        template_div.add(dependency)


        progress = self.get_node("progress", node_type="progress")
        template_div.add(progress)


        #endpoint = self.get_endpoint_node("output", node_type="output")
        #template_div.add(endpoint)

        #endpoint = self.get_endpoint_node("input", node_type="input")
        #template_div.add(endpoint)

        """
	Add template of connector panel

        Define custom connector panel and custom connector info
        per pipeline type in widget config using category "workflow_connector"
        <config>
	<my_pipeline_type>
	    <element name="panel">
	      <display class="path.to.my.ConnectorPanelWdg"/>
	    </element>
	    <element name="info">
	      <display class="path.to.my.ConnectorInfoWdg"/>
	    </element>
	</my_pipeline_type>
	</config>
	"""
        connector_panel_data = {}
        search = Search("config/widget_config")
        search.add_filter("category", "workflow_connector")
        configs = search.get_sobjects()
        for config in configs:
            pipeline_type = config.get_value("view")
            class_name = config.get_display_handler("panel")
            connector_panel = Common.create_from_class_path(class_name)
            connector_panel.add_class("spt_connector_panel_template")
            connector_panel.add_style("position", "absolute")
            template_div.add(connector_panel)
            connector_panel_data[pipeline_type] = class_name
        top.set_attr("spt_connector_panel_data", jsondumps(connector_panel_data).replace('"', "&quot;"))


        # add trigger node
        trigger = self.get_trigger_node()
        template_div.add(trigger)


        search = Search("config/widget_config")
        search.add_filter("category", "workflow")
        configs = search.get_sobjects()
        for config in configs:
            node_type = config.get_value("view")
            template = self.get_custom_node(node_type, node_type=node_type)
            template_div.add(template)


        # resize test
        show_resize = self.kwargs.get("show_resize")
        if show_resize in ['true', True]:
            resize_wdg = DivWdg()
            resize_wdg.add("Resize")
            resize_wdg.add_behavior( {
            'type': 'drag',
            "mouse_btn": 'LMB',
            "drag_el": '@',
            "cb_set_prefix": 'spt.pipeline.resize_drag'
            } )
            top.add(resize_wdg)



        pipeline_str = self.kwargs.get("pipeline")
        div = DivWdg()
        outer.add(div)

        if pipeline_str:
            pipelines = pipeline_str.split("|")
            div.add_behavior( {
            'type': 'load',
            'pipelines': pipelines,
            'cbjs_action': '''
            spt.pipeline.init(bvr);
            for (var i=0; i<bvr.pipelines.length; i++) {
                spt.pipeline.import_pipeline(bvr.pipelines[i]);
            }
            '''
            } )


        scale = self.kwargs.get("scale")
        if scale:
            scale = float(scale)
            div.add_behavior( {
            'type': 'load',
            'scale': scale,
            'cbjs_action': '''
                spt.pipeline.init(bvr);
                setTimeout( function() {
                    spt.pipeline.set_scale(bvr.scale);
                }, 0 )
            '''
            } )


        div.add_behavior( {
        'type': 'load',
        'line_mode': self.line_mode,
        'has_prefix': self.has_prefix,
        'cbjs_action': '''
            spt.pipeline.init(bvr);
            spt.pipeline.set_line_mode(bvr.line_mode);
            spt.pipeline.set_has_prefix(bvr.has_prefix);
        '''
        } )



        # add a screenspace div for items that do not move with scroll
        screen_div = DivWdg()
        outer.add(screen_div)
        screen_div.add_class("spt_screen")
        screen_div.add_style("width: 100%")
        screen_div.add_style("height: 100%")
        screen_div.add_style("overflow: hidden")
        screen_div.add_style("top: 0px")
        screen_div.add_style("left: 0px")
        screen_div.add_style("position: absolute")
        screen_div.add_style("z-index: 10")

        screen_div.add_behavior( {
        "type": 'drag',
        "is_editable": is_editable,
        "mouse_btn": 'LMB',
        "drag_el": '@',
        "cb_set_prefix": 'spt.pipeline.canvas_drag'
        } )

        self.canvas_behaviors = self.get_canvas_behaviors()
        for canvas_behavior in self.canvas_behaviors:
            behavior_type = canvas_behavior.get("type")
            behavior_action = canvas_behavior.get("cbjs_action")
            screen_div.add_behavior({
                "type": behavior_type,
                "cbjs_action": '''
                %s
                ''' % behavior_action
            })


        if self.kwargs.get("use_mouse_wheel") in [True, 'true']:
            screen_div.add_behavior( {
            "type": 'wheel',
            "cbjs_action": '''
                spt.pipeline.init(bvr);
                var scale = spt.pipeline.get_scale();
                if (evt.wheel < 0) {
                    spt.pipeline.set_scale( scale / 1.1 );
                }
                else {
                    spt.pipeline.set_scale( scale * 1.1 );
                }
            '''
            } )


        # add custom canvas behaviors on the canvas div instead
        # NOTE: at the momen the screen_div is at the top, we need to add the behaviors
        # here.
        self.canvas_behaviors = self.get_canvas_behaviors()
        for canvas_behavior in self.canvas_behaviors:
            screen_div.add_behavior( canvas_behavior )


        return top




    def get_paint(self):
        from pyasm.web import Canvas
        canvas = Canvas()
        canvas.add_class("spt_pipeline_paint")
        #canvas.add_style("position: relative")
        canvas.add_style("position: absolute")
        #canvas.add_style("border: solid 1px red")
        canvas.add_style("top: 0px")
        canvas.set_attr("width", "600")
        canvas.set_attr("height", "600")
        canvas.set_attr("spt_background_color", self.background_color)

        canvas.add_style("z-index: 1")

        canvas.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        spt.pipeline.init(bvr);
        '''
        } )


        return canvas


    def get_canvas_behaviors(self):
        return []




    def get_folder(self, group_name):

        styles = HtmlElement.style('''

            .spt_pipeline_folder {
                width: 200px;
                height: 100px;
                display: flex;
                align-items: center;
                justify-content: center;

                top: 100px;
                left: 100px;
                position: relative;
                z-index: 150;

                border-radius: 5px;
                border: 1px solid #ccc;

                cursor: hand;
            }

            .spt_pipeline_folder:hover {
                background: #eee;
            }

            .spt_pipeline_folder .spt_content {
                font-size: 14px;
                color: #666;
                padding: 10px;
                text-align: center;
            }

            ''')

        div = DivWdg()
        div.add_class("spt_pipeline_folder")
        div.add_class("spt_pipeline_folder_template")

        lip_div = DivWdg()
        div.add(lip_div)
        lip_div.add_class("spt_lip")
        lip_div.add_style("display: none")


        expand_div = DivWdg()
        div.add(expand_div)
        expand_div.add_style("display: none")


        content_div = DivWdg()
        content_div.add_class("spt_content")
        div.add(content_div)


        color_div = DivWdg()
        #content_div.add(color_div)
        color_div.add_style("margin-right: 5px")
        color_div.add_class("spt_color_swatch")
        color_div.add_style("height: 15px")
        color_div.add_style("width: 15px")
        color_div.add_style("float: left")


        group_div = DivWdg()
        content_div.add(group_div)
        group_div.add_class("spt_group")

        #group_div.add(group_name)

        #group_div.add_style("font-weight: bold")

        button = DivWdg("Click here to add your first node. Use the <i class='fa fa-wrench'></i> to add more nodes.")
        content_div.add( button )


        content_div.add_behavior( {
        'type': 'click',
        'cbjs_action': '''
        spt.pipeline.init(bvr);

        var folder = bvr.src_el.getParent(".spt_pipeline_folder");
        var group_name = folder.spt_group;
        spt.pipeline.set_current_group(group_name);

        //var parts = group_name.split("/");
        //node_name = parts[parts.length-1];

        var node = spt.pipeline.add_node();
        spt.pipeline.redraw_canvas();
        '''
        } )



        div.add_behavior( {
        "type": 'drag',
        "mouse_btn": 'LMB',
        "drag_el": '@',
        "cb_set_prefix": 'spt.pipeline.node_drag'
        } )

        div.add(styles)

        return div


    def get_node(self, name, node_type="node"):

        node = DivWdg()

        width, height = self.get_node_size()


        if node_type == "action":
            border_radius = 20
        elif node_type == "hierarchy":
            border_radius =  50
            width = width
            height = height + 40
        elif node_type == "dependency":
            border_radius = 15
            #width = width
            height = 60
            width = 100
        elif node_type == "progress":
            border_radius =  30
            #width = width
            height = 55
            width = 55
        elif node_type == "unknown":
            border_radius = 50
            width = 50
            height = 50
            border_radius =  5
            #width = width
            height = 60
            width = 80
        elif node_type == "progress":
            border_radius =  30
            #width = width
            height = 55
            width = 55
        else:
            border_radius = 3


        # add a node
        node.add_class("spt_pipeline_node")
        if node_type !="node":
            node.add_class("spt_pipeline_%s" % node_type)
        node.add_attr("spt_node_type", node_type)

        node.add_class("SPT_TEMPLATE")

        node.add_style("color", "#000")
        node.add_style("font-size", "12px")
        node.add_style("position: absolute")
        node.add_style("text-align: center")
        node.add_style("z-index: 100")

        node.add_attr("spt_element_name", name)
        node.add_attr("title", name)

        if self.is_editable == True:
            from tactic.ui.container.smart_menu_wdg import SmartMenu
            SmartMenu.assign_as_local_activator( node, 'NODE_CTX')

        offset = 0

        show_nobs = self.get_show_nobs()
        if show_nobs:
            self.add_nobs(node, width, height, offset)

        transparent = DivWdg()
        node.add(transparent)
        transparent.add_style("margin-left: -10px")
        transparent.add_style("margin-top: -10px")
        transparent.add_style("width: %spx" % (width+20))
        transparent.add_style("height: %spx" % (height+20))
        transparent.add_style("position: absolute")
        transparent.add_style("z-index", "-1")
        transparent.add_class("transparent_node_layer")
        transparent.add_behavior( {
            'type': 'hover',
            'cbjs_action_over': '''

                var el = bvr.src_el.getParent(".spt_pipeline_node");
                var nob = el.getElement(".spt_left_nob");
                spt.show(nob);
                var nob = el.getElement(".spt_right_nob");
                spt.show(nob);

            ''',
            'cbjs_action_out': '''

                var el = bvr.src_el;
                var nob = el.getElement(".spt_left_nob");
                spt.hide(nob);
                var nob = el.getElement(".spt_right_nob");
                spt.hide(nob);

            '''
            } )


        content = DivWdg()
        node.add(content)
        content.add_class("spt_content")
        content.add_style("width: %spx" % width)
        content.add_style("height: %spx" % height)
        content.add_style("border: solid 1px black")
        content.add_style("z-index: 200")
        content.add_style("overflow: 200")


        # parallelogram
        #content.add_style("-webkit-transform", "skewX(-20deg)")
        #content.add_style("transform", "skewX(-20deg)")

        if border_radius:
            content.set_round_corners(border_radius)

        extra_wdg = self.get_extra_node_content_wdg()
        if extra_wdg:
            content.add(extra_wdg)



        label = Table()
        label.add_row()
        node.add(label)
        label.add_style("position: absolute")
        label.add_color("color", "#000") # we want a dark color here

        label.add_style("width: %spx" % width)
        if node_type == "hierarchy":
            label.add_style("height: %spx" % (height*0.75))
        else:
            label.add_style("height: %spx" % height)

        label.add_style("top: 0px")
        td = label.add_cell(name)
        td.add_class("spt_label")
        td.add_style("vertical-align: middle")
        td.add_style("text-align: center")
        label.add_style("overflow: hidden")





        from tactic.ui.input import LookAheadTextInputWdg, TextInputWdg
        text = TextWdg()
        node.add(text)
        text.add_style("position: absolute")
        text.add_style("display: none")
        text.add_style("top: %spx" % (height/4) )
        text.add_style("left: %spx" % (height/4) )
        text.add_style("width: 75px")
        text.set_value(name)




        if node_type == "hierarchy":


            icon_div = DivWdg()
            node.add(icon_div)
            icon = IconButtonWdg(name="Expand", icon="FA_ARROW_DOWN")
            icon_div.add(icon)
            icon_div.add_style("margin: 0px auto")
            icon_div.add_style("top: 40px")
            icon_div.add_style("left: %spx" % (width/2-12))
            icon_div.add_style("position: absolute")
            icon_div.add_style("z-index: 300")
            icon_div.add_style("border: solid 1px transparent")
            icon_div.add_style("width: 24px")
            icon_div.add_style("text-align: center")

            icon_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var server = TacticServerStub.get();

            var node = bvr.src_el.getParent(".spt_pipeline_node");
            var node_name = spt.pipeline.get_node_name(node);
            var pipeline_code = spt.pipeline.get_current_group();

            var class_name = "tactic.ui.tools.PipelineGetInfoCmd";
            var kwargs = {
                pipeline_code: pipeline_code,
                node_name: node_name
            }
            var ret_val = server.exeucte_cmd(class_name, kwargs);
            var pipeline = ret_val.info.pipeline;
            var process = ret_val.info.process;
            alert("cow")

            /*
            var pipeline = server.eval("@SOBJECT(sthpw/pipeline['code','"+pipeline_code+"'])", {single: true});
            var search_type = pipeline.search_type;


            var expr = "@SOBJECT(config/process['pipeline_code','"+pipeline_code+"']['process','"+node_name+"'])";
            var process = server.eval(expr, {single: true});
            */

            var subpipeline = null;
            if (process) { 
                var subpipeline_code = node.properties.settings.default.subpipeline;
                if (subpipeline_code) {
                    subpipeline = server.eval("@SOBJECT(sthpw/pipeline['code','"+subpipeline_code+"'])", {single: true});
                } else {
                    var process_code = process.code;
                    subpipeline = server.eval("@SOBJECT(sthpw/pipeline['parent_process','"+process_code+"'])", {single: true});
                }
            }

            var top = spt.pipeline.top;
            var text = top.getElement(".spt_pipeline_editor_current2");

            if (text) {
                var root_html = text.innerHTML;
                bvr.breadcrumb = root_html;
            } else {
                var root_html = "";
            }


            if (!subpipeline && !process) {
                spt.alert("Save workflow before creating subpipeline.");
            } else if (!subpipeline) {
                spt.confirm( "Create new workflow?", function() {
                    // create the pipeline
                    var data = {
                        name: node_name + " Workflow",
                        search_type: search_type,
                        // This is deprecated, use subpipeline_code on process
                        //parent_process: process_code
                    }
                    subpipeline = server.insert("sthpw/pipeline", data);
                    subpipeline_code = subpipeline.code;
                    server.update(process, { subpipeline_code: subpipeline_code })

                    spt.pipeline.clear_canvas();
                    spt.pipeline.import_pipeline(subpipeline_code);

                    if (text) {
                        var html = "<span class='hand tactic_hover spt_pipeline_link' spt_pipeline_code='"+subpipeline.code+"'>"+subpipeline.name+"</span>";
                        text.innerHTML = root_html + " / " + html;
                    }

                } );
                return;
            }
            else {
                subpipeline_code = subpipeline.code;
                
                spt.pipeline.clear_canvas();
                spt.pipeline.import_pipeline(subpipeline_code);

                if (text) {
                    var html = "<span class='hand tactic_hover spt_pipeline_link' spt_pipeline_code='"+subpipeline.code+"'>"+subpipeline.name+"</span>";
                    text.innerHTML = root_html + " / " + html;
                }

            }

            evt.stopPropagation();
            '''
            } )




        # add custom node behaviors
        node_behaviors = self.get_node_behaviors()
        for node_behavior in node_behaviors:
            node.add_behavior( node_behavior )


        if (self.add_node_behaviors):
            self.add_default_node_behaviors(node, text)

        return node



    def add_nobs(self, node, width, height, offset=0):

        #mode = "vertical"
        mode = "horizontal"

        # add nobbies on the node
        left_nob = DivWdg()
        node.add(left_nob)
        left_nob.add_class("spt_left_nob")
        left_nob.set_round_corners(3, corners=['TL','BL'])
        left_nob.add_event("onmouseover", "document.id(this).setStyle('background','rgba(255,255,0,0.7')")
        left_nob.add_event("onmouseout", "document.id(this).setStyle('background','rgba(255,255,0,0.2')")
        left_nob.add_style("cursor: pointer")
        left_nob.add_style("position: absolute")
        left_nob.add_style("border: solid 1px black")
        left_nob.add_style("background: rgba(255,255,0,0.2)")
        left_nob.add_style("width: 10px")
        left_nob.add_style("height: 10px")

        if mode == "horizontal":
            left_nob.add_style("top: %spx" % (height/2-5))
            left_nob.add_style("left: %spx" % (-11-offset))
        else:
            left_nob.add_style("top: %spx" % (-offset))
            left_nob.add_style("left: %spx" % (width/2-5))

        left_nob.add_style("z-index: 100")
        left_nob.add("")


        # add nobbies on the node
        right_nob = DivWdg()
        node.add(right_nob)
        right_nob.add_class("spt_right_nob")
        right_nob.add_style("cursor: pointer")
        right_nob.add_style("position: absolute")
        right_nob.add_style("top: 0px")
        #right_nob.add_style("left: %spx" % (width+1))
        right_nob.add_style("right: %spx" % (-11-offset))
        right_nob.add_style("z-index: 100")
        right_nob.add_style("width: 12px")
        right_nob.add_style("height: 40px")

        right_nob_vis = DivWdg()
        right_nob.add(right_nob_vis)
        right_nob_vis.add("")
        right_nob_vis.set_round_corners(3, corners=['TR','BR'])
        right_nob_vis.add_style("border: solid 1px black")
        right_nob_vis.add_style("background: rgba(255,255,0,0.2)")
        right_nob_vis.add_style("width: 10px")
        right_nob_vis.add_style("height: 10px")
        right_nob_vis.add_style("margin-top: %spx" % (height/2-5))
        right_nob_vis.add_event("onmouseover", "document.id(this).setStyle('background','rgba(255,255,0,0.7')")
        right_nob_vis.add_event("onmouseout", "document.id(this).setStyle('background','rgba(255,255,0,0.2')")

        if self.nob_mode == 'dynamic':
            left_nob.add_style("display: none")
            right_nob.add_style("display: none")
            node.add_behavior( {
            'type': 'hover',
            'cbjs_action_over': '''
            var el = bvr.src_el;
            var nob = el.getElement(".spt_left_nob");
            spt.show(nob);
            var nob = el.getElement(".spt_right_nob");
            spt.show(nob);
            ''',
            'cbjs_action_out': '''
            var el = bvr.src_el;
            var nob = el.getElement(".spt_left_nob");
            spt.hide(nob);
            var nob = el.getElement(".spt_right_nob");
            spt.hide(nob);

            '''
            } )

        left_nob.add_style("display", "none")
        right_nob.add_style("display", "none")


        if self.is_editable:

            # add the behavior that will draw the connector
            left_nob.add_behavior( {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "drag_el": '@',
            "cb_set_prefix": 'spt.pipeline.drag_connector'
            } )



            right_nob.add_behavior( {
            "type": 'drag',
            "mouse_btn": 'LMB',
            "drag_el": '@',
            "cb_set_prefix": 'spt.pipeline.drag_connector'
            } )

            right_nob.add_behavior( {
            "type": 'drag',
            "modkeys": 'SHIFT',
            "mouse_btn": 'LMB',
            "drag_el": '@',
            "cb_set_prefix": 'spt.pipeline.drag_connector'
            } )




            node.add_behavior( {
            "type": 'mouseenter',
            "cbjs_action": '''
            var left_nob = bvr.src_el.getElement(".spt_left_nob");
            left_nob.setStyle("display", "");
            var right_nob = bvr.src_el.getElement(".spt_right_nob");
            right_nob.setStyle("display", "");
            '''
            } )


            node.add_behavior( {
            "type": 'mouseleave',
            "cbjs_action": '''
            var left_nob = bvr.src_el.getElement(".spt_left_nob");
            left_nob.setStyle("display", "none");
            var right_nob = bvr.src_el.getElement(".spt_right_nob");
            right_nob.setStyle("display", "none");
            '''
            } )






    def add_default_node_behaviors(self, node, text):

        if not self.is_editable:
            return


        # CTRL click will allow you to change the node name
        node.add_behavior( {
        'type': 'click_up',
        'modkeys': 'CTRL',
        'cbjs_action': '''
        var node = bvr.src_el;
        var group = spt.pipeline.get_group_by_node(node);

        var group_type = group.get_group_type();
        if (group_type=='schema') {
            var registered = node.spt_registered;
            if (registered) {
                spt.alert("Cannot rename a registered sType");
                return;
            }
        }

        spt.pipeline.set_rename_mode(node);

        '''
        } )


        text.add_behavior( {
            'type': 'keyup',
            'cbjs_action': '''
            var key = evt.key;
            if (key == "enter") {
                bvr.src_el.blur();
            }
            else if (key == "esc") {
                var node = bvr.src_el.getParent(".spt_pipeline_node");
                var old_name = node.spt_name;
                bvr.src_el.value = old_name;
                bvr.src_el.blur();
            }
            '''
        } )




        # When the text is blur, it will accept the value entered
        text.add_behavior( {
        'type': 'change',
        'filter_node_name': self.filter_node_name,
        'cbjs_action': '''
        bvr.src_el.blur();
        '''
        } )

        text.add_behavior( {
        'type': 'blur',
        'filter_node_name': self.filter_node_name,
        'cbjs_action': '''
        bvr.src_el.setStyle("display", "none");

        var node = bvr.src_el.getParent(".spt_pipeline_node");
        var value = bvr.src_el.value;

        // filter the value
        if (bvr.filter_node_name) {
            value = spt.convert_to_alpha_numeric( value );
        }

        spt.pipeline.rename_node(node, value);
        var label = node.getElement(".spt_label");
        label.setStyle("display", "");
        '''
        } )

        node.add_behavior( {
        "type": 'drag',
        "mouse_btn": 'LMB',
        "drag_el": '@',
        "cb_set_prefix": 'spt.pipeline.node_drag'
        } )


        # on normal click, select single node if not selected, otherwise
        # select the whole group
        node.add_behavior( {
        'type': 'click',
        'cbjs_action': '''
        spt.pipeline.init(bvr);
        var node = bvr.src_el;
        if (node.spt_is_selected) {
            //spt.pipeline.unselect_all_nodes();
            //spt.pipeline.select_single_node(node);
        }
        else {
            spt.pipeline.select_single_node(node);
        }
        evt.stopPropagation();
        '''
        } )


        # a double click will select the whole group
        node.add_behavior( {
        'type': 'double_click',
        'modkeys': 'ALT',
        'cbjs_action': '''
        spt.pipeline.init(bvr);

        var node = bvr.src_el;
        spt.pipeline.select_node(node);

        var select_output_nodes = function(nodes) {
            for (let i = 0; i < nodes.length; i++) {
                let cur_node = nodes[i];
                if (cur_node.spt_is_selected == true) {
                    break;
                }
                spt.pipeline.select_node(cur_node);
                let cur_output_nodes = spt.pipeline.get_output_nodes(cur_node);
                if (cur_output_nodes.length > 0) {
                    select_output_nodes(cur_output_nodes);
                }
            }
        };

        var select_input_nodes = function(nodes) {
            for (let i = 0; i < nodes.length; i++) {
                let cur_node = nodes[i];
                if (cur_node.spt_is_selected == true) {
                    break;
                }
                spt.pipeline.select_node(cur_node);
                let cur_input_nodes = spt.pipeline.get_input_nodes(cur_node);
                if (cur_input_nodes.length > 0) {
                    select_input_nodes(cur_input_nodes);
                }
            }
        };


        if (evt.alt == true) {
            var input_nodes = spt.pipeline.get_input_nodes(node);
            select_input_nodes(input_nodes);
        }
        else {
            var output_nodes = spt.pipeline.get_output_nodes(node);
            select_output_nodes(output_nodes);
        }



        '''
        } )






        node.add_behavior( {
        'type': 'click',
        'modkeys': 'SHIFT',
        'cbjs_action': '''
        spt.pipeline.init(bvr);
        var node = bvr.src_el;
        if (node.spt_is_selected) {
            spt.pipeline.select_nodes_by_group(node.spt_group);
        }
        else {
            spt.pipeline.select_node(node);
        }
        '''
        } )

        node.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.pipeline.init(bvr);
        var node = bvr.src_el;
        spt.pipeline.set_current_position(node);
        '''
        } )




    def get_node_size(self):
        width = 100
        height = 40
        return width, height

    def get_extra_node_content_wdg(self):
        return Widget()

        #icon = IconWdg("Expand", IconWdg.PIPELINE)
        #icon.add_style("position: absolute")
        #icon.add_style("top: 2px")
        #icon.add_style("left: 3px")
        #return icon


    """
    def get_endpoint_node(self, name, node_type ):

        node = DivWdg()
        node.add_class("spt_pipeline_%s" % node_type)
        node.add_class("spt_pipeline_node")
        node.add_attr("spt_node_type", node_type)


        node.add_attr("spt_element_name", name)
        node.add_attr("title", name)


        node.add_style("z-index", "200")
        node.add_style("position: absolute")

        node.add_style("width: auto")
        node.add_style("height: auto")

        width = 30
        height = 20


        self.add_nobs(node, width, height)


        content = DivWdg()
        node.add(content)


        content.add_class("spt_content")

        content.add_style("width: %spx" % width)
        content.add_style("height: %spx" % height)
        content.add_style("border: solid 1px black")

        if node_type == "input":
            content.add_style("border-radius: 0px 15px 15px 0px")
        else:
            content.add_style("border-radius: 15px 0px 0px 15px")


        label = Table()
        label.add_row()
        node.add(label)
        label.add_style("position: absolute")

        label.add_style("width: %spx" % width)
        label.add_style("height: %spx" % height)

        label.add_style("top: 0px")
        td = label.add_cell(name)
        td.add_class("spt_label")
        td.add_style("vertical-align: middle")
        td.add_style("text-align: center")
        label.add_style("overflow: hidden")

        text = TextWdg()
        node.add(text)
        text.add_style("position: absolute")
        text.add_style("display: none")
        text.add_style("top: %spx" % (height/4+5) )
        text.add_style("left: 0px")
        text.add_style("width: 65px")
        text.set_value(name)

        active = DivWdg()
        node.add(active)
        active.add_class("spt_active")

        self.add_default_node_behaviors(node, text)

        return node
    """



    def get_custom_node(self, name, node_type ):

        node = DivWdg()

        node.add_class("spt_pipeline_%s" % node_type)
        node.add_class("spt_pipeline_node")
        node.add_attr("spt_node_type", node_type)

        node.add_class("spt_custom_top")


        from pyasm.command import CustomProcessConfig
        custom_wdg = CustomProcessConfig.get_node_handler(node_type)
        node.add(custom_wdg)



        node.add_attr("spt_element_name", name)
        node.add_attr("title", name)


        if not custom_wdg.use_default_node_behavior():
            return custom_wdg



        node.add_style("z-index", "200")
        node.add_style("position: absolute")

        width = custom_wdg.get_width()
        height = custom_wdg.get_height()

        enable_context_menu = self.kwargs.get("enable_context_menu")

        if self.is_editable == True:
            from tactic.ui.container.smart_menu_wdg import SmartMenu
            SmartMenu.assign_as_local_activator( node, 'SIMPLE_NODE_CTX')


        node_behaviors = self.get_node_behaviors()
        for node_behavior in node_behaviors:
            node.add_behavior( node_behavior )




        # add custom node behaviors
        node_behaviors = custom_wdg.get_node_behaviors()
        for node_behavior in node_behaviors:
            node.add_behavior( node_behavior )


        nobs_offset = custom_wdg.get_nob_offset() or 0
        self.add_nobs(node, width, height, nobs_offset)


        transparent = DivWdg()
        node.add(transparent)
        transparent.add_style("margin-left: -10px")
        transparent.add_style("margin-top: -10px")
        transparent.add_style("width: %spx" % (width+20))
        transparent.add_style("height: %spx" % (height+20))
        transparent.add_style("position: absolute")
        transparent.add_style("top", "0")
        transparent.add_style("z-index", "-1")
        transparent.add_class("transparent_node_layer")
        transparent.add_behavior( {
            'type': 'hover',
            'cbjs_action_over': '''

                var el = bvr.src_el.getParent(".spt_pipeline_node");
                var nob = el.getElement(".spt_left_nob");
                spt.show(nob);
                var nob = el.getElement(".spt_right_nob");
                spt.show(nob);

            ''',
            'cbjs_action_out': '''

                var el = bvr.src_el;
                var nob = el.getElement(".spt_left_nob");
                spt.hide(nob);
                var nob = el.getElement(".spt_right_nob");
                spt.hide(nob);

            '''
            } )


        #content = DivWdg()
        #node.add(content)
        #content.add_class("spt_content")
        #content.add_style("overflow: hidden")
        #content.add_style("width: %spx" % width)
        #content.add_style("height: %spx" % height)
        #content.add_style("border-radius: %spx" % (width/2))
        #content.add_style("border: solid 1px black")
        #content.add( custom_node_wdg )



        label = Table()
        label.add_row()
        node.add(label)
        label.add_style("position: absolute")
        label.add_color("color", "color")

        label_width = custom_wdg.get_label_width()
        if label_width == None:
            label_width = width

        label.add_style("width: %spx" % label_width)
        label.add_style("height: %spx" % height)

        label.add_style("top: 0px")
        td = label.add_cell(name)
        td.add_class("spt_label")
        td.add_style("vertical-align: middle")
        td.add_style("text-align: center")
        label.add_style("overflow: hidden")

        custom_wdg.style_label(label)


        text = TextWdg()
        node.add(text)
        text.add_style("position: absolute")
        text.add_style("display: none")
        text.add_style("top: %spx" % (height/4+5) )
        text.add_style("left: %spx" % (height/4+5) )
        text.add_style("width: 65px")
        text.set_value(name)

        self.add_default_node_behaviors(node, text)

        if custom_wdg.show_default_name() in ['false', False]:
            label.add_style("display: none")


        active = DivWdg()
        node.add(active)
        active.add_class("spt_active")


        return node








    def get_condition_node(self, name, process=None):

        node = DivWdg()
        node.add_class("spt_pipeline_condition")
        node.add_class("spt_pipeline_node")
        node.add_attr("spt_node_type", "condition")


        node.add_attr("spt_element_name", name)
        node.add_attr("title", name)


        node.add_style("z-index", "200")

        width = 60
        height = 60


        node.add_style("position: absolute")

        node.add_style("width: auto")
        node.add_style("height: auto")

        enable_context_menu = self.kwargs.get("enable_context_menu")

        if self.is_editable == True:
            from tactic.ui.container.smart_menu_wdg import SmartMenu
            SmartMenu.assign_as_local_activator( node, 'SIMPLE_NODE_CTX')

        # add custom node behaviors
        node_behaviors = self.get_node_behaviors()
        for node_behavior in node_behaviors:
            node.add_behavior( node_behavior )


        offset = width * 0.12 # size to corner of square

        self.add_nobs(node, width, height, 5)


        content = DivWdg()
        node.add(content)
        #content.add_style("overflow: hidden")
        content.add_class("spt_content")
        content.add_style("width: %spx" % width)
        content.add_style("height: %spx" % height)
        content.add_style("border: solid 1px black")

        content.add_style("transform: rotate(-45deg)")


        label = Table()
        label.add_row()
        node.add(label)
        label.add_style("position: absolute")
        label.add_color("color", "color")

        label.add_style("width: %spx" % width)
        label.add_style("height: %spx" % height)

        label.add_style("top: 0px")
        td = label.add_cell(name)
        td.add_class("spt_label")
        td.add_style("vertical-align: middle")
        td.add_style("text-align: center")
        label.add_style("overflow: hidden")

        text = TextWdg()
        node.add(text)
        text.add_style("position: absolute")
        text.add_style("display: none")
        text.add_style("top: %spx" % (height/4+5) )
        text.add_style("left: 0px")
        text.add_style("width: 65px")
        text.set_value(name)

        active = DivWdg()
        node.add(active)
        active.add_class("spt_active")

        if (self.add_node_behaviors):
            self.add_default_node_behaviors(node, text)

        return node





    def get_approval_node(self, name, process=None):

        node = DivWdg()
        node.add_class("spt_pipeline_approval")
        node.add_class("spt_pipeline_node")
        node.add_attr("spt_node_type", "approval")


        node.add_attr("spt_element_name", name)
        node.add_attr("title", name)


        node.add_style("z-index", "200")


        width = 65
        height = 65


        node.add_style("position: absolute")

        node.add_style("width: auto")
        node.add_style("height: auto")

        if self.is_editable == True:
            from tactic.ui.container.smart_menu_wdg import SmartMenu
            SmartMenu.assign_as_local_activator( node, 'SIMPLE_NODE_CTX')

        # add custom node behaviors
        node_behaviors = self.get_node_behaviors()
        for node_behavior in node_behaviors:
            node.add_behavior( node_behavior )




        self.add_nobs(node, width, height)


        content = DivWdg()
        node.add(content)
        content.add_style("overflow: hidden")
        content.add_class("spt_content")
        content.add_style("width: %spx" % width)
        content.add_style("height: %spx" % height)
        content.add_style("border-radius: %spx" % (width/2))
        content.add_style("border: solid 1px black")




        label = Table()
        label.add_row()
        node.add(label)
        label.add_style("position: absolute")
        label.add_color("color", "color")

        label.add_style("width: %spx" % width)
        label.add_style("height: %spx" % height)

        label.add_style("top: 0px")
        td = label.add_cell(name)
        td.add_class("spt_label")
        td.add_style("vertical-align: middle")
        td.add_style("text-align: center")
        label.add_style("overflow: hidden")


        text = TextWdg()
        node.add(text)
        text.add_style("position: absolute")
        text.add_style("display: none")
        text.add_style("top: %spx" % (height/4+5) )
        text.add_style("left: %spx" % (height/4+5) )
        text.add_style("width: 65px")
        text.set_value(name)


        active = DivWdg()
        node.add(active)
        active.add_class("spt_active")


        if (self.add_node_behaviors):
            self.add_default_node_behaviors(node, text)

        return node



    def get_trigger_node(self):


        name = "trigger_template"

        node = DivWdg()
        node.add_class("spt_pipeline_trigger")
        node.add_class("spt_pipeline_node")


        node.add_attr("spt_element_name", name)
        node.add_attr("title", name)

        node.add_style("z-index", "200")


        width = 30
        height = 30


        node.add_style("position: absolute")

        node.add_style("width: auto")
        node.add_style("height: auto")


        #self.add_nobs(node, width, height)

        content = DivWdg()
        node.add(content)
        #content.add_style("overflow: hidden")
        content.add_class("spt_content")
        content.add_style("width: %spx" % width)
        content.add_style("height: %spx" % height)
        content.add_style("border-radius: %spx" % (width/2))
        content.add_style("border: solid 1px black")


        title = IconWdg(name="trigger", icon="BS_ENVELOPE")
        label = DivWdg()
        content.add(label)
        label.add(title)
        label.add_style("margin: 5px auto")
        label.add_style("text-align: center")
        label.add_style("padding-left: 2px")
        label.add_style("padding-top: 1px")
        label.add_color("color", "color")

        label = DivWdg()
        node.add(label)
        label.add_style("position: absolute")

        ##
        label.add_style("display: none")
        ##

        label.add_style("width: %spx" % width)
        label.add_style("height: %spx" % height)

        label.add_style("top: %spx" % (height/4+7) )
        label.add_class("spt_label")
        label.add(name)
        label.add_style("vertical-align: middle")
        label.add_style("overflow: hidden")
        label.add_style("text-align: center")

        text = TextWdg()
        node.add(text)
        text.add_style("position: absolute")
        text.add_style("display: none")
        text.add_style("top: %spx" % (height/4+5) )
        text.add_style("left: %spx" % (height/4+5) )
        text.add_style("width: 65px")
        text.set_value(name)


        active = DivWdg()
        node.add(active)
        active.add_class("spt_active")

        node.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''

            var node = bvr.src_el.spt_from_node;

            var process = node.getAttribute("spt_element_name");
            var pipeline_code = node.spt_group;
            var search_type = spt.pipeline.get_search_type(pipeline_code);

            var class_name = 'tactic.ui.tools.trigger_wdg.TriggerToolWdg';
            var kwargs = {
                search_type: search_type,
                pipeline_code: pipeline_code,
                process: process,
            }

            element_name = 'trigger_'+process;
            title = 'Triggers ['+process+']';
            //spt.tab.add_new(element_name, title, class_name, kwargs);
            spt.panel.load_popup(title, class_name, kwargs);

            '''
        } )


        self.add_default_node_behaviors(node, text)

        return node








    def get_connector(self, name, start, end):
        # add a connector
        connector = DivWdg()
        connector.add_style("position: relative")
        #connector.add_style("border: solid 1px blue")
        connector.add_style("z-index: 0")
        #connector.add("<img width='100%' height='100%' src='/context/line.png'/>")


        connector.add_behavior( {
        'type': 'load',
        'start': start,
        'end': end,
        'cbjs_action': '''
        spt.pipeline.init(bvr);
        var data = spt.pipeline.get_data();
        if (data.line_mode == 'curved_edge') {
            spt.pipeline.draw_curved_edge_line(from_pos, to_pos, this.color);
        } else {
            spt.pipeline.draw_connector(from_pos, to_pos, this.color);
        }
        '''
        } )


        #connector.add_behavior( {
        #'type': 'drag'
        #} )

        return connector


    def get_canvas_behavior(self):
        return []

    def get_node_behaviors(self):
        return []

    def get_node_context_menu(self):

        menu = Menu(width=180)
        menu.set_allow_icons(False)
        menu.set_setup_cbfn( 'spt.smenu_ctx.setup_cbk' )


        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        mode = "single"

        if mode == "multiple":
            menu_item = MenuItem(type='action', label='Add To Current Group')
            menu_item.add_behavior( {
                'cbjs_action': '''
                var node = spt.smenu.get_activator(bvr);
                spt.pipeline.init(node);
                var group_name = spt.pipeline.get_current_group();
                spt.pipeline.add_node_to_group(node, group_name);
                '''
            } )
            menu.add(menu_item)


        """
        menu_item = MenuItem(type='action', label='Change Color')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);
            spt.pipeline.init( { src_el: node } );
            var group = spt.pipeline.get_group_by_node(node);
            group.set_color("#CFA");
            '''
        } )
        menu.add(menu_item)
        """

        """
        menu_item = MenuItem(type='separator')
        menu.add(menu_item)
        """


        menu_item = MenuItem(type='action', label='Rename Node')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);
            spt.pipeline.set_rename_mode(node);
            '''
        } )
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Delete Node')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);
            spt.pipeline.init( { src_el: node } );
            spt.pipeline.remove_node(node);
            '''
        } )
        menu.add(menu_item)

        if mode == "multiple":
            menu_item = MenuItem(type='action', label='Delete Group')
            menu_item.add_behavior( {
                'cbjs_action': '''
                var node = spt.smenu.get_activator(bvr);
                spt.pipeline.init( { src_el: node } );
                spt.pipeline.remove_group(node.spt_group);
                '''
            } )
            menu.add(menu_item)


        return menu


    def get_simple_node_context_menu(self):

        menu = Menu(width=180)
        menu.set_allow_icons(False)
        menu.set_setup_cbfn( 'spt.smenu_ctx.setup_cbk' )


        menu_item = MenuItem(type='title', label='Actions')
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Rename Node')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);
            spt.pipeline.set_rename_mode(node);
            '''
        } )
        menu.add(menu_item)

        menu_item = MenuItem(type='action', label='Delete Node')
        menu_item.add_behavior( {
            'cbjs_action': '''
            var node = spt.smenu.get_activator(bvr);
            spt.pipeline.init( { src_el: node } );
            spt.pipeline.remove_node(node);
            '''
        } )
        menu.add(menu_item)

        return menu


    def get_onload_js(self):

        return r'''

if (!spt.pipeline) {
    spt.pipeline = {};
}

//spt.Environment.get().add_library("spt_pipeline");


spt.pipeline.top = null;

spt.pipeline.background_color = "#fff";

spt.pipeline.allow_cycle = true;

// External method to initialize callback
spt.pipeline.hide_start = function(start) {
    start.setStyle("display", "none");

    right = start.getParent(".spt_pipeline_tool_right");
    editor = right.getElement(".spt_pipeline_editor_top");
    editor.setStyle("display", "flex");

}

spt.pipeline.init_cbk = function(common_top) {
    spt.pipeline.top = common_top.getElement(".spt_pipeline_top");
    spt.pipeline._init();
}


// Internal method to find top
spt.pipeline.init = function(bvr) {
    if (typeof(bvr.src_el) == 'undefined') {
        spt.pipeline.top = bvr.getParent(".spt_pipeline_top");
    }
    else {
        spt.pipeline.top = bvr.src_el.getParent(".spt_pipeline_top");
    }
    spt.pipeline._init();
}


// Explicitly set the top
spt.pipeline.set_top = function(top) {
    spt.pipeline.top = top;
    spt.pipeline._init();
}



spt.pipeline._init = function() {
    var top = spt.pipeline.top;
    var canvas = top.getElement(".spt_pipeline_canvas");
    var canvas_size = top.getElement(".spt_pipeline_canvas_size");

    var allow_cycle = top.getAttribute("spt_allow_cycle");
    if (allow_cycle) {
        if (allow_cycle == "false") spt.pipeline.allow_cycle = false;
    }

    if (canvas) {
        spt.pipeline.background_color = canvas.getAttribute("spt_background_color");
    }

    if (typeof(canvas.connectors) == 'undefined') {
        canvas.connectors = [];
    }
    var paint = top.getElement(".spt_pipeline_paint");
    var ctx = paint.getContext('2d');
    var screen = top.getElement(".spt_screen");

    var data = top.spt_data;
    if (typeof(data) == 'undefined') {
        top.spt_data = {};
        data = top.spt_data;
        data.scale = 1.0;
        data.translate = {x: 0, y: 0};
    }
    data.canvas = canvas;
    data.canvas_size = canvas_size;
    data.paint = paint;
    data.screen = screen;
    data.screen_nodes = screen.getElements(".spt_screen_node");
    data.ctx = ctx;


    var connector_panel_data = top.getAttribute("spt_connector_panel_data");
    if (connector_panel_data) {
        connector_panel_data = JSON.decode(connector_panel_data);
    } else {
        connector_panel_data = {};
    }
    data.connector_panel_data = connector_panel_data;

}


// initialize when loading for the first time
// FIXME: this gets run twice when Project Schema and Project Workflow are both open
spt.pipeline.first_init = function(bvr) {
    var top = bvr.src_el.getParent(".spt_pipeline_top");
    // this top could be Schema Editor or Pipeline Editor
    var class_name = top.getAttribute('spt_class_name');
    var schema_editor = false;
    if (class_name.test(/schema/i))
        schema_editor = true;

    top.spt_data = {};
    var data = top.spt_data;

    data.groups = {};
    data.current_group = 'default';
    data.stype_dict = {};

    data.selected = [];

    data.scale = 1.0;
    data.translate = {x: 0, y: 0};
    data.line_mode = 'bezier';
    data.has_prefix = false;

    spt.pipeline.init(bvr);

    var server = TacticServerStub.get();
    var expr = ''
    var key = ''
    // either pipeline or stype can have color
    if (schema_editor) {
        expr = "@SOBJECT(sthpw/search_object)";
        key = 'search_type';
    }
    else {
        expr = "@SOBJECT(sthpw/pipeline)";
        key = 'code';
    }
    var sobjs = server.eval(expr);

    data.colors = {};
    data.descriptions = {};
    data.default_templates = {};
    for (var i = 0; i < sobjs.length; i++) {
        var sobj = sobjs[i];
        data.colors[sobj[key]] = sobj.color;
        data.descriptions[sobj[key]] = sobj.description;

        if (sobj.data)
            data.default_templates[sobj[key]] = sobj.data.default_template;
    }

}



spt.pipeline.get_data = function() {
    return spt.pipeline.top.spt_data;
}

spt.pipeline.set_data = function(attr, value) {
    spt.pipeline.top.spt_data[attr] = value;
}

spt.pipeline.get_canvas = function() {
    return spt.pipeline.get_data().canvas;
}


spt.pipeline.get_screen = function() {

    var top = spt.pipeline.top;
    var screen = spt.pipeline.get_data().screen;
    if (!screen) {
        screen = top.getElement(".spt_screen");
        if (screen) {
            spt.pipeline.get_data().screen = screen;
        }
    }
    return screen;
}

spt.pipeline.get_screen_nodes = function() {

    var screen_nodes = spt.pipeline.get_data().screen_nodes;
    if (!screen_nodes) {
        var screen = spt.pipeline.get_screen();
        screen_nodes = screen.getElements(".spt_screen_node");
        spt.pipeline.get_data().screen_nodes = screen_nodes;
    }
    return screen_nodes;
}


spt.pipeline.get_ctx = function() {
    return spt.pipeline.get_data().ctx;
}


spt.pipeline.get_paint = function() {
    return spt.pipeline.get_data().paint;
}







// hit test functionality
spt.pipeline.hit_test_mouse = function(mouse_411) {
    var pos = spt.pipeline.get_mouse_position(mouse_411);
    return spt.pipeline.hit_test(pos.x-2, pos.y-2, pos.x+2, pos.y+2);
}


spt.pipeline.hit_test = function(x1, y1, x2, y2) {

    var left;
    var top;
    var width;
    var height;

    if (x1 < x2) {
        left = x1;
        width = x2 -x1;
    }
    else {
        left = x2;
        width = x1 -x2;
    }

    if (y1 < y2) {
        top = y1;
        height = y2 - y1;
    }
    else {
        top = y2;
        height = y1 - y2;
    }

    if (left < 0) {
        left = 0;
    }
    if (top < 0) {
        top = 0;
    }

    if (width == 0 ) {
        width = 2;
    }
    if (height == 0) {
        height = 2;
    }



    var hit_connector = null;

    var ctx = spt.pipeline.get_ctx();
    ctx.clearRect(left,top,width,height);

    spt.pipeline.clear_selected();

    var canvas = spt.pipeline.get_canvas();
    var connectors = canvas.connectors;



    for (var i=0; i<connectors.length; i++) {
        var connector = connectors[i];
        connector.draw();

        var found = false;
        var imgd = ctx.getImageData(left, top, width, height);
        var pix = imgd.data;

        for ( var j = 0; j < pix.length; j += 4) {
            var red = pix[j];
            var green = pix[j+1];
            var blue = pix[j+2];
            if (red != 0 || blue != 0 || green != 0) {
                spt.pipeline.add_to_selected(connector);
                connector.set_color("#990");
                found = true;
                ctx.clearRect(left,top,width,height);
                hit_connector = connector;
                break;
            }
        }

        if (found == false) {
            connector.set_color("#111");
        }

    }
    spt.pipeline.redraw_canvas();

    return hit_connector;
}





spt.pipeline.clear_canvas = function() {
    var canvas = spt.pipeline.get_canvas();
    canvas.connectors = [];
    var nodes = spt.pipeline.get_all_nodes();
    for ( var i = 0; i < nodes.length; i++ ) {
        var node = nodes[i];
        spt.behavior.destroy_element(node);
    }


    // delete all the folders
    var folders = spt.pipeline.get_all_folders();
    for ( var i = 0; i < folders.length; i++ ) {
        var folder = folders[i];
        spt.behavior.destroy_element(folder);
    }



    // clear the dat
    var data = spt.pipeline.get_data();
    data.groups = {};

    // clear the current_pipeline select
    /*
    var top = spt.pipeline.top.getParent(".spt_pipeline_tool_top");
    var select = top.getElement(".spt_pipeline_editor_current");
    for (var i = select.options.length-1; i >=0; i--) {
        var select_value = select.options[i].value;
        if (select_value != 'default') {
           select.remove(i);
        }
    }
    */


    // remove connector panels
    var top = spt.pipeline.top;
    var panels = top.getElements(".spt_connector_data");
    for ( var i = 0; i < panels.length; i++ ) {
        var panel = panels[i];
        spt.behavior.destroy_element(panels);
    }

    spt.pipeline.redraw_canvas();


    // remove screen nodes
    var screen = top.getElement(".spt_screen");
    if (screen) {
        var els = screen.getElements(".spt_screen_node");
        els.forEach( function(el) {
            spt.behavior.destroy_element(el);
        } );
    }

}




// Select functionality
spt.pipeline.select_last_position = null;
spt.pipeline.select_drag_setup = function(evt, bvr, mouse_411) {
    spt.pipeline.init(bvr);
    var mouse_pos = spt.pipeline.get_mouse_position(mouse_411);
    spt.pipeline.select_last_position = mouse_pos;
}
spt.pipeline.select_drag_motion = function(evt, bvr, mouse_411) {
    spt.pipeline.redraw_canvas();
    var mouse_pos = spt.pipeline.get_mouse_position(mouse_411);
    var last_pos = spt.pipeline.select_last_position;
    var ctx = spt.pipeline.get_ctx();
    ctx.strokeRect(last_pos.x, last_pos.y, mouse_pos.x-last_pos.x, mouse_pos.y-last_pos.y);

}

spt.pipeline.select_drag_action = function(evt, bvr, mouse_411) {

    spt.pipeline.unselect_all_nodes();

    var last_pos = spt.pipeline.select_last_position;
    var mouse_pos = spt.pipeline.get_mouse_position(mouse_411);


    spt.pipeline.hit_test(last_pos.x, last_pos.y, mouse_pos.x, mouse_pos.y );
    if (last_pos.x < mouse_pos.x)
        spt.pipeline.select_nodes_by_box(last_pos, mouse_pos);
    else
        spt.pipeline.select_nodes_by_box(mouse_pos, last_pos);

    spt.pipeline.redraw_canvas();

}

// Mouse functions
spt.pipeline.get_mouse_position = function(mouse_411) {
    //var canvas = spt.pipeline.get_canvas();
    //var canvas_pos = spt.pipeline.get_el_position(canvas);

    // to get the mouse position, we need to use the unscaled position (not
    // the canvas
    var top = spt.pipeline.top;
    top_pos = top.getPosition();

    var rel_pos = {x: mouse_411.curr_x - top_pos.x, y: mouse_411.curr_y - top_pos.y}
    return rel_pos;
}



// Select methods

spt.pipeline.get_selected_nodes = function() {
    var canvas = spt.pipeline.get_canvas();
    var nodes = canvas.getElements(".spt_pipeline_node");
    var selected_nodes = [];
    for (var i=0; i<nodes.length; i++) {
        var node = nodes[i];
        if (node.spt_is_selected == true) {
            selected_nodes.push(node);
        }
    }
    return selected_nodes;
}


spt.pipeline.get_selected_node = function() {
    var nodes = spt.pipeline.get_selected_nodes();
    if (nodes.length == 0) {
        return null;
    }
    return nodes[0];
}




spt.pipeline.get_selected = function() {
    var data = spt.pipeline.get_data();
    var selected = data.selected;
    return selected;
}

// Get the first connector of the selection list
spt.pipeline.get_selected_connector = function() {
   var selected = spt.pipeline.get_selected();
   for (var k=0; k <selected.length; k++){
        if (selected[k].type =="connector")
            return selected[k];
   }
}

spt.pipeline.add_to_selected = function(item) {
    var data = spt.pipeline.get_data();
    var selected = data.selected;
    selected.push(item);
}



spt.pipeline.delete_selected = function() {
    var selected = spt.pipeline.get_selected_nodes();
    spt.pipeline.remove_nodes(selected);

    var data = spt.pipeline.get_data();
    var selected = data.selected;
    for (var i = 0; i < selected.length; i++) {
        var item = selected[i];
        if (item.type == "connector") {
            spt.pipeline.delete_connector(item);
        }
    }

    spt.pipeline.redraw_canvas();
}




spt.pipeline.clear_selected = function(item) {
    var data = spt.pipeline.get_data();
    spt.pipeline.unselect_all_nodes();
    spt.pipeline.unselect_all_connectors();
    data.selected = [];
}



spt.pipeline.select_node = function(node) {
    node.setStyle("z-index", "200");
    node.spt_is_selected = true;

    if (node.hasClass("spt_custom_top")) {
        var outer = node.getElement(".spt_custom_node");
    }
    else {
        var outer = node.getElement(".spt_content");
    }

    var box_shadow = outer.getAttribute("spt_box_shadow");
    if (box_shadow) {
        outer.setStyle("box-shadow", box_shadow);
    } else {
        outer.setStyle("box-shadow", "0px 0px 10px rgba(128,128,128,1.0)");
    }
    outer.setStyle("border", "solid 1px rgba(64,64,64,1.0)");
    outer.setStyle("opacity", "0.8");


    var group = spt.pipeline.get_group(node.spt_group);
    var group_type = group.get_group_type();
    if (group_type == 'schema') {
        var event_name = 'stype|select';
        spt.named_events.fire_event(event_name, { src_el: node } );
    }
    else if (group_type == 'pipeline') {
        var event_name = 'process|select';
        spt.named_events.fire_event(event_name, { src_el: outer } );
    }


    spt.pipeline.add_to_selected(node); 

}


spt.pipeline.unselect_node = function(node) {
    node.setStyle("z-index", "100");
    node.spt_is_selected = false;
    //var active = node.getElement(".spt_active");
    //active.setStyle("display", "none");

    if (node.hasClass("spt_custom_top")) {
        var outer = node.getElement(".spt_custom_node");
    }
    else {
        var outer = node.getElement(".spt_content");
    }
    var border_color = outer.getAttribute("spt_border_color") || "#000";
    var box_shadow = outer.getAttribute("spt_box_shadow");
    outer.setStyle("box-shadow", box_shadow);
    outer.setStyle("border", "solid 1px " + border_color);
    outer.setStyle("opacity", "1.0");


    var group = spt.pipeline.get_group(node.spt_group);
    var group_type = group.get_group_type();
    if (group_type == 'schema') {
        var event_name = 'stype|unselect';
        spt.named_events.fire_event(event_name, { src_el: node } );
    }
    else if (group_type == 'pipeline') {
        var event_name = 'process|unselect';
        spt.named_events.fire_event(event_name, { src_el: outer } );
    }

}




spt.pipeline.disable_node = function(node) {
    node.setStyle("z-index", "100");
    node.spt_is_disabled = true;
    node.setStyle("opacity", "0.4");
}


spt.pipeline.enable_node = function(node) {
    node.setStyle("z-index", "100");
    node.spt_is_disabled = false;
    node.setStyle("opacity", "1.0");
}


// For info wdg, not sure if this should be here
spt.pipeline = spt.pipeline || {};
spt.pipeline.info_node;

spt.pipeline.set_info_node = function(node) {
    spt.pipeline.top.info_node = node;
}


spt.pipeline.get_info_node = function() {
    return spt.pipeline.top.info_node;
}



// Select only this node
spt.pipeline.select_single_node = function(node) {
    var canvas = spt.pipeline.get_canvas();
    var nodes = canvas.getElements(".spt_pipeline_node");
    for (var i=0; i<nodes.length; i++) {
        var other_node = nodes[i];
        spt.pipeline.unselect_node(other_node);
    }
    spt.pipeline.select_node(node);
}


spt.pipeline.unselect_all_nodes = function() {
    var nodes = spt.pipeline.get_all_nodes();
    for (var i=0; i<nodes.length; i++) {
        var node = nodes[i];
        spt.pipeline.unselect_node(node);
    }

    var event_name = spt.pipeline.top.getAttribute("id") + "|unselect_all";
    spt.named_events.fire_event(event_name);
}


spt.pipeline.select_nodes_by_group = function(group_name) {
    spt.pipeline.unselect_all_nodes();

    var nodes = spt.pipeline.get_all_nodes();
    for (var i=0; i<nodes.length; i++) {
        var node = nodes[i];
        if (node.spt_group == group_name) {
            spt.pipeline.select_node(node);
        }
    }
}

spt.pipeline.select_nodes_by_box = function(TL, BR) {
    r1 = {
        top: TL.y,
        bottom: BR.y,
        left: TL.x,
        right: BR.x
    }


    spt.pipeline.unselect_all_nodes();

    var selected = [];

    var nodes = spt.pipeline.get_all_nodes();
    for (var i=0; i<nodes.length; i++) {
        var node = nodes[i];
        var node_name = spt.pipeline.get_node_name(node);
        var size = node.getSize();

        r2 = {
            top: node.spt_ypos,
            bottom: node.spt_ypos + size.y,
            left: node.spt_xpos,
            right: node.spt_xpos + size.x
        }

        var intersect = !(r2.left > r1.right ||
                          r2.right < r1.left ||
                          r2.top > r1.bottom ||
                          r2.bottom < r1.top);

        if (intersect) {
            spt.pipeline.select_node(node);
            selected.push(node);
        }
    }

    return selected;
}



spt.pipeline.unselect_all_connectors = function() {
    var canvas = spt.pipeline.get_canvas();
    var connectors = canvas.connectors;

    connectors.forEach( function(connector) {
        connector.unselect();
    } );
}




// Node functions

spt.pipeline.get_all_nodes = function() {
    var canvas = spt.pipeline.get_canvas();
    nodes = canvas.getElements(".spt_pipeline_node");
    return nodes;
}


spt.pipeline.get_nodes_by_type = function(node_type) {
    var canvas = spt.pipeline.get_canvas();
    nodes = canvas.getElements(".spt_pipeline_node[spt_node_type='"+ node_type +"']");
    return nodes;
}


spt.pipeline.get_node_by_name = function(name) {
    var canvas = spt.pipeline.get_canvas();
    var nodes = canvas.getElements(".spt_pipeline_node");
    for (var i = 0; i < nodes.length; i++) {
        var node_name = nodes[i].getAttribute("spt_element_name");
        if (node_name == name) {
            return nodes[i];
        }
    }
    return null;
}


spt.pipeline.set_node_name = function(node, name) {
    node.setAttribute("spt_element_name", name);
    node.spt_name = name;
    var label = node.getElement(".spt_label");
    label.innerText = name;
}


spt.pipeline.get_node_name = function(node) {
    return node.getAttribute("spt_element_name");
}


spt.pipeline.get_node_type = function(node) {
    return node.getAttribute("spt_node_type");
}


spt.pipeline.set_node_types = function(node_types) {
    spt.pipeline.top.node_types = node_types;
}


spt.pipeline.get_node_types = function() {
    return spt.pipeline.top.node_types || [];
}


spt.pipeline.get_full_node_name = function(node, group_name) {
    name = node.getAttribute("spt_element_name");
    var data = spt.pipeline.get_data();
    if (data.has_prefix && name.indexOf("/") == -1) {
        // get the prefix from the node
        var prefix = node.getAttribute("spt_prefix");
        if (!prefix) {
            prefix = group_name;
        }
        name = prefix + "/" + name;
    }
    return name;
}




spt.pipeline.get_input_nodes = function(node) {

    var group = spt.pipeline.get_group_by_node(node);
    var connectors = group.get_connectors();

    var nodes = [];
    for (var i = 0; i < connectors.length; i++) {
        var connector = connectors[i];
        var to_node = connector.get_to_node();
        var from_node = connector.get_from_node();
        if (to_node == node) {
            nodes.push(from_node);
        }
    }

    return nodes;

}



spt.pipeline.get_output_nodes = function(node) {

    var group = spt.pipeline.get_group_by_node(node);
    var connectors = group.get_connectors();

    var nodes = [];
    for (var i = 0; i < connectors.length; i++) {
        var connector = connectors[i];
        var to_node = connector.get_to_node();
        var from_node = connector.get_from_node();
        if (from_node == node) {
            nodes.push(to_node);
        }
    }

    return nodes;
}





// Group methods


spt.pipeline.get_nodes_by_group = function(group_name) {
    var group = spt.pipeline.get_group(group_name);
    if (group == null) {
        return [];
    }
    var nodes = group.get_nodes();
    return nodes;
}



spt.pipeline.add_group = function(group_name) {
    var data = spt.pipeline.get_data();
    var group = data.groups[group_name];
    if (typeof(group) == 'undefined') {
        group = new spt.pipeline.Group(group_name);
        data.groups[group_name] = group;
    }
    var color = data.colors[group_name];
    if (color) {
        group.set_color(color);
    }

    return group;
}


spt.pipeline.get_groups = function() {
    var data = spt.pipeline.get_data();
    return data.groups;
}

spt.pipeline.get_num_groups = function() {
    var data = spt.pipeline.get_data();
    var groups = data.groups;

    var element_count = 0;
    for(var e in groups)
        if(groups.hasOwnProperty(e))
            element_count++;

    return element_count;
}




spt.pipeline.get_group = function(name) {
    var data = spt.pipeline.get_data();
    var group = data.groups[name];
    if (typeof(group) == 'undefined') {
        return null;
    }
    return group;
}


spt.pipeline.get_group_by_node = function(node) {
    var group_name = node.spt_group;
    var group = spt.pipeline.get_group(group_name);
    return group;
}



// Set the current group for operation to take place
spt.pipeline.set_current_group = function(group_name) {
    var group = spt.pipeline.get_group(group_name);
    if (group == null) {
        group = spt.pipeline.add_group(group_name);
    }

    var data = spt.pipeline.get_data();
    data.current_group = group_name;
}



// Get the current group
spt.pipeline.get_current_group = function() {
    var data = spt.pipeline.get_data();
    return data.current_group;
}


spt.pipeline.set_search_type = function(pipeline_code, stype) {

    var data = spt.pipeline.get_data();

    data.stype_dict[pipeline_code] = stype;
}



// Get the current group's stype
spt.pipeline.get_search_type = function(pipeline_code) {
    if (!pipeline_code)
        pipeline_code = spt.pipeline.get_current_group();
    var data = spt.pipeline.get_data();
    return data.stype_dict[pipeline_code];
}

spt.pipeline.add_node_to_group = function(node, group_name) {

    // remove from old group
    var old_group_name = node.spt_group;
    var old_group = spt.pipeline.get_group(old_group_name);
    old_group.remove_node(node);

    var group = spt.pipeline.get_group(group_name);
    group.add_node(node);
}



// add a new node to the canvas

spt.pipeline.undo_add_nodes = []
spt.pipeline.undo_remove_nodes = []
spt.pipeline.undo_remove_connectors = []


spt.pipeline._add_node = function(name,x, y, kwargs){

    var top = spt.pipeline.top;
    var canvas = spt.pipeline.get_canvas();

    var group = null;
    var select_node = true;
    var node_type = null;
    if (typeof(kwargs) != 'undefined') {
            group = kwargs.group;
            if (kwargs.select_node != 'undefined')
                    select_node = kwargs.select_node;
            node_type = kwargs.node_type;
    }
    else {
            kwargs = {};
    }

    if (!node_type) {
            var default_node_type = top.getAttribute("spt_default_node_type");
            if (default_node_type) {
                node_type = default_node_type;
            }
            else {
                node_type = "manual";
            }
    }

    if (typeof(group) == 'undefined' || group == null) {
            group = spt.pipeline.get_current_group();

    }


    var group_info = spt.pipeline.get_group(group);
    if (group_info == null) {
            group_info = spt.pipeline.add_group(group);
    }


    var nodes = spt.pipeline.get_all_nodes();
    if (typeof(name) == 'undefined' || name == null) {
        var node_index = group_info.get_data("node_index") || 0;
        name = "node"+node_index;
        group_info.set_data("node_index", node_index+1);
    }


    if (typeof(x) == 'undefined' || x == null) {
            var size = spt.pipeline.get_canvas_size();
            var scale = spt.pipeline.get_scale();
            x = size.x/3 + nodes.length*15*scale;
            y = size.y/3 + nodes.length*10*scale;
    }

    var template_container = top.getElement(".spt_pipeline_template");

    var template_class = "spt_pipeline_" + node_type;
    var template = template_container.getElement("."+template_class);
    var is_unknown = false;
    if (!template) {
            var template_class = "spt_pipeline_unknown";
            template = template_container.getElement("."+template_class);
            is_unknown = true;
    }


    var new_node = spt.behavior.clone(template);
    if (is_unknown) {
        // change it from "unknown"
        new_node.setAttribute("spt_node_type", node_type);
    }
    new_node.spt_node_type = node_type;


    canvas.appendChild(new_node);

    // make the label the last part
    var label_parts = name.split("/");
    var label_str = label_parts[label_parts.length-1];

    var label = new_node.getElement(".spt_label");
    var input = new_node.getElement(".spt_input");
    if (label) {
        label.innerHTML = label_str;
    }
    if (input) {
        input.value = label_str;
    }
    new_node.setAttribute("spt_element_name", name);
    new_node.spt_name = name;
    new_node.setAttribute("title", name);


    // set any properties that might exist
    new_node.properties = kwargs.properties || {};

    // BACKWARDS COMPATIBILITY
    if (new_node.properties.settings && new_node.properties.settings.version == 1)
        new_node[node_type] = { description: kwargs.description || "" }


    // add to a group
    group_info.add_node(new_node);


    // switch the color
    //var color = group_info.get_color();
    var color = '';
    /*
    if (node_type == "trigger") {
            color = "#FFF";
    }
    else if (node_type == "approval") {
            color = "#FFF";
    }
    */
    if (group_info.get_node_type() == 'process')
            color = spt.pipeline.get_group_color(group);
    else // for schema
            color = spt.pipeline.get_group_color(name);

    if (is_unknown) {
            color = "#C00";
    }

    spt.pipeline.set_color(new_node, color)
    new_node.color = color;

    // position the node on the canvas
    if (x == 0 && y == 0) {
        var nodes = spt.pipeline.get_all_nodes();
        var num_nodes = nodes.length;
        x = num_nodes * 120 + 50;
        y = num_nodes * 0 + 50;
    }


    // check if there are any nodes on this exact position
    for (var i = 0; i < nodes.length; i++) {
        var pos = spt.pipeline.get_position(nodes[i]);
        if (pos.x == x && pos.y == y) {
            x += 10;
            y += 10;
        }

    }


    spt.pipeline.move_to(new_node, x, y);


    // select the node
    if (select_node)
            spt.pipeline.select_single_node(new_node);

    // fire an event
    if (kwargs.new != false) {
            var top = bvr.src_el.getParent(".spt_pipeline_top");
            var event_name = top.getAttribute("id") + "|node_create";
            spt.named_events.fire_event(event_name, { src_el: new_node } );
    }

    var editor_top = bvr.src_el.getParent(".spt_pipeline_editor_top");
    if (editor_top) {
            editor_top.addClass("spt_has_changes");
    }

    // BACKWARDS COMPATIBILITY
    if (spt.pipeline.top.getAttribute("version_2_enabled") != "false")
        spt.pipeline.set_node_kwarg(new_node, "version", 2);


    if (kwargs.is_loading) {
        new_node.has_changes = false;
    }
    else {
        new_node.has_changes = true;
    }


    spt.named_events.fire_event('pipeline|change', {});

    // if folder hide folder
    var folder = spt.pipeline.top.getElement(".spt_pipeline_folder:not(.spt_pipeline_folder_template)");
    if (folder) {
        spt.pipeline.set_current_group(group);
        spt.behavior.destroy_element(folder);
    }

    return new_node;
}

spt.pipeline.add_node = function(name, x, y, kwargs) {

    var cmd = new spt.pipeline.AddNodeCmd(name, x, y, kwargs);

    spt.command.add_to_undo(cmd);

    return cmd.execute();
}


spt.pipeline.AddNodeCmd = function(name, x, y, kwargs){

	this.execute = function() {
	    this.name = name;
        this.x = x;
        this.y = y;
        this.kwargs = kwargs;

        this.node =  spt.pipeline._add_node(this.name, this.x, this.y, this.kwargs);
        return this.node;
    };

    this.redo = function() {
    	var node = spt.pipeline.undo_add_nodes.pop();

		this.node  = spt.pipeline._add_node(node.spt_name, node.style.left.split("px")[0], node.style.top.split("px")[0], this.kwargs);

        var group = spt.pipeline.get_group_by_node(this.node)
       	var canvas = spt.pipeline.get_canvas();

       	var connectors = spt.pipeline.undo_remove_connectors.pop();


		for(var i = 0; i < connectors.length; i++){
		    var connector = spt.pipeline.reset_connector(connectors[i]);
			canvas.connectors.push(connector);
			group.add_connector(connector)
		    connector.draw()
		}

    }

    this.undo = function(){
    	this.node = spt.pipeline.reset_node(this.node)
        spt.pipeline.undo_add_nodes.push(this.node);
       	spt.pipeline._remove_nodes([this.node]);
    }


}



spt.pipeline.remove_nodes = function(nodes) {

    var cmd = new spt.pipeline.RemoveNodeCmd(nodes);

    spt.command.add_to_undo(cmd);

    cmd.execute();
}


spt.pipeline.RemoveNodeCmd = function(nodes){

	this.execute = function() {
	    this.nodes = nodes;
        spt.pipeline._remove_nodes(this.nodes);
    };

    this.redo = function() {
    	var nodes = spt.pipeline.undo_remove_nodes.pop();
    	for(var i = 0; i<nodes.length; i++){
    		nodes[i] = spt.pipeline.reset_node(nodes[i]);
    	}
    	spt.pipeline._remove_nodes(nodes);

    }

    this.undo = function(){
        spt.pipeline.undo_remove_nodes.push(this.nodes);
       	for(var i = 0; i < this.nodes.length; i++){
       		var node = nodes[i];
       		var new_node = spt.pipeline._add_node(node.spt_name, node.style.left.split("px")[0], node.style.top.split("px")[0]);

       	    var settings = node.getAttribute("spt_settings");
       	    new_node.setAttribute("spt_settings",settings);
            if(settings){
                settings_json = JSON.parse(settings);
            	new_node.update_node_settings(settings_json)
            }

       	}
       	var group = spt.pipeline.get_group_by_node(new_node)
       	var canvas = spt.pipeline.get_canvas();

       	var connectors = spt.pipeline.undo_remove_connectors.pop();


		for(var i = 0; i < connectors.length; i++){
		    var connector = spt.pipeline.reset_connector(connectors[i]);
			canvas.connectors.push(connector);
			group.add_connector(connector)
		    connector.draw()
		}

    }
}



spt.pipeline._remove_nodes = function(nodes) {
    // remove the connectors that have this node
    var canvas = spt.pipeline.get_canvas();
    var connectors = canvas.connectors;
    var to_del = [];

    // this indexes may not be needed any more.
    var indexes = {};
    for (var j = 0; j < nodes.length; j++ ) {
        var node = nodes[j];
        var name = node.getAttribute("spt_element_name");
        for (var i = 0; i < connectors.length; i++ ) {
            var connector = connectors[i];
            var to_node = connector.get_to_node();
            var from_node = connector.get_from_node();
            if (to_node == null || from_node == null
                    || to_node.getAttribute("spt_element_name") == name
                    || from_node.getAttribute("spt_element_name") == name) {
                indexes[i] = true;
                to_del.push(connector);
            }


        }
    }

    spt.pipeline.undo_remove_connectors.push(to_del);

    for (var i = 0; i < to_del.length; i++) {
        spt.pipeline.delete_connector(to_del[i]);
    }

    /*
    // get a reverse order of the indexes
    var indexes_array = [];
    for ( var i in indexes ) {
        indexes_array.push(parseInt(i));
    }
    indexes_array.sort( function(a,b) {return a-b;} );
    indexes_array.reverse();

    // remove the connectors
    for ( var i = 0; i < indexes_array.length; i++ ) {
        canvas.connectors.splice(indexes_array[i], 1);
    }
    */

    // Note: some nodes will move because of the relative position.  Need
    // to update this

    // remove the nodes
    var group;

    for (var j = nodes.length-1; j >= 0; j-- ) {
        var node = nodes[j];
        // remove the node from the group
        group = spt.pipeline.get_group_by_node(node);
        group.remove_node(node);

        spt.behavior.destroy_element(node);
    }

    // if there is only 1 node left, remove dangling connector
    if (group) {
        var final_nodes = group.get_nodes();
        if (final_nodes.length == 1) {
            spt.pipeline.delete_connector(canvas.connectors[0]);
        }
    }
    spt.pipeline.redraw_canvas();

    spt.named_events.fire_event('pipeline|change', {});
}


spt.pipeline.remove_node = function(node) {
    spt.pipeline.remove_nodes( [node] );
}


spt.pipeline.remove_group = function(group_name) {
    var nodes = spt.pipeline.get_nodes_by_group(group_name);
    spt.pipeline.remove_nodes(nodes);

    var data = spt.pipeline.get_data();
    delete data.groups[group_name];
}


spt.pipeline.set_node_property = function(node, name, value) {
    node.properties[name] = value;
    node.has_changes = true;
}

spt.pipeline.get_node_property = function(node, name) {
    return node.properties[name];
}


spt.pipeline.set_node_properties = function(node, properties) {
    node.properties = properties;
    node.has_changes = true;
}

spt.pipeline.get_node_properties = function(node) {
    return node.properties;
}

// Kwargs are ProcessInfoCmd inputs
spt.pipeline.get_node_kwargs = function(node) {
    var type = spt.pipeline.get_node_type(node);
    type = "settings";
    var property = node.properties;

    if (property) return property[type] || {};
    return {};
}

spt.pipeline.get_node_kwarg = function(node, name) {
    var kwargs = spt.pipeline.get_node_kwargs(node);
    return kwargs[name];
}

spt.pipeline.set_node_kwargs = function(node, kwargs) {
    //var type = spt.pipeline.get_node_type(node);
    var type = "settings";
    spt.pipeline.set_node_property(node, type, kwargs);
}

spt.pipeline.set_node_kwarg = function(node, name, value) {
    var kwargs = spt.pipeline.get_node_kwargs(node);
    if (!kwargs) kwargs = {};
    kwargs[name] = value;
    spt.pipeline.set_node_kwargs(node, kwargs);
}

spt.pipeline.add_node_on_save = function(node, name, value) {
    if (!node.on_saves) node.on_saves = {};
    node.on_saves[name] = value;
    node.has_changes = true;
}

// Supports both kwargs and multi kwargs
spt.pipeline.set_input_value_from_kwargs = function(node, name, input_el, properties=null) {
    var kwargs = spt.pipeline.get_node_kwargs(node);
    if (properties) kwargs = properties;
    if (kwargs) {
        var value = kwargs[name];
        if (!value && kwargs.multi) {
            value = spt.pipeline.get_node_multi_kwarg(node, name);
        }
        if (value || value === "") input_el.value = value;
    }
}

spt.pipeline.set_select_value_from_kwargs = function(node, name, input_el, properties=null) {
    var kwargs = spt.pipeline.get_node_kwargs(node);
    if (properties) kwargs = properties;
    if (kwargs) {
        var value = kwargs[name];
        if (!value && kwargs.multi) {
            value = spt.pipeline.get_node_multi_kwarg(node, name);
        }

        var options = input_el.options;
        var values = []

        for (var i=0; i<options.length; i++) {
            var option = options[i];
            values.push(option.value);
        }

        // maybe this should be done in python?
        if (values.includes(value)) input_el.value = value;
        else {
            if (kwargs.multi) spt.pipeline.set_node_multi_kwarg(node, name, options[0].value);
            else spt.pipeline.set_node_kwarg(node, name, options[0].value);
        }
    }
}

spt.pipeline.set_radio_value_from_kwargs = function(node, name, input_el, properties=null) {
    var kwargs = spt.pipeline.get_node_kwargs(node);
    if (properties) kwargs = properties;
    if (kwargs) {
        var value = kwargs[name];
        if (!value && kwargs.multi) {
            value = spt.pipeline.get_node_multi_kwarg(node, name);
        }
        if (input_el.value == value) input_el.checked = true;
    }
}

spt.pipeline.set_checkbox_value_from_kwargs = function(node, name, input_el, properties=null) {
    var kwargs = spt.pipeline.get_node_kwargs(node);
    if (properties) kwargs = properties;
    if (kwargs) {
        var value = kwargs[name];
        if (!value && kwargs.multi) {
            value = spt.pipeline.get_node_multi_kwarg(node, name);
        }
        input_el.checked = value;
    }
}

// Used for InfoWdgs with dynamic forms
spt.pipeline.get_node_multi_kwargs = function(node) {
    var multi_kwargs = spt.pipeline.get_node_kwargs(node);
    if (!multi_kwargs) return {};
    if (!multi_kwargs.multi) {
        console.log("ERROR: not multi_kwargs");
        return {};
    }
    var kwargs_name = multi_kwargs.selected;
    return multi_kwargs[kwargs_name] || {};
}

spt.pipeline.get_node_multi_kwarg = function(node, name) {
    var kwargs = spt.pipeline.get_node_multi_kwargs(node);
    return kwargs[name];
}

spt.pipeline.set_node_multi_kwarg = function(node, name, value) {
    var multi_kwargs = spt.pipeline.get_node_kwargs(node);
    if (!multi_kwargs.multi) return;
    var kwargs_name = multi_kwargs.selected;
    var kwargs = multi_kwargs[kwargs_name];
    kwargs[name] = value;
    multi_kwargs[kwargs_name] = kwargs;
    spt.pipeline.set_node_kwargs(node, multi_kwargs);
}

spt.pipeline.select_node_multi_kwargs = function(node, kwargs_name, name, value) {
    var multi_kwargs = spt.pipeline.get_node_property(node, 'settings');
    if (!multi_kwargs) multi_kwargs = {};
    multi_kwargs.multi = true;
    multi_kwargs.selected = kwargs_name;
    var kwargs = multi_kwargs[kwargs_name];
    if (!kwargs) kwargs = {};
    kwargs[name] = value;
    multi_kwargs[kwargs_name] = kwargs;
    curr_kwargs = spt.pipeline.get_node_property(node, 'settings');
    Object.assign(curr_kwargs, multi_kwargs);
    spt.pipeline.set_node_kwargs(node, curr_kwargs);
}


spt.pipeline.set_color = function(node, color) {
    if (!color) {
        return;
    }

    var content= node.getElement(".spt_content");
    var color1 = spt.css.modify_color_value(color, +10);
    var color2 = spt.css.modify_color_value(color, -5);

    if (spt.pipeline.get_node_type(node) == "condition") {
        angle = 225;
    } else {
        angle = 180;
    }

    content.setStyle("background", "linear-gradient("+angle+"deg, "+color1+", 70%, "+color2+")");

    node.spt_color = color;
}



spt.pipeline.get_color = function(node) {
    return node.spt_color;
}


spt.pipeline.get_group_color = function(group_name) {
    var data = spt.pipeline.get_data();
    var color = data.colors[group_name];
    if (typeof(color) == 'undefined') {
        color = '#BBB';
    }
    return color;
}


spt.pipeline.rename_node = function(node, value, undo_flag) {
	var cmd = new spt.pipeline.RenameNode(node, value);
    if(!undo_flag){
	    spt.command.add_to_undo(cmd);

    }
    cmd.execute();
}

spt.pipeline.RenameNode = function(node, value){

	this.execute = function() {
		this.node = node;
	   	this.old_value = node.spt_name;
	   	this.value = value;
	   	this.redo();
    };

	this.redo = function() {
		this.node = spt.pipeline.reset_node(this.node);
        spt.pipeline._rename_node(this.node, this.value);
    };

    this.undo = function() {
		this.node = spt.pipeline.reset_node(this.node);
        spt.pipeline._rename_node(this.node, this.old_value);
    };


}



spt.pipeline._rename_node = function(node, value) {
    if (!value) {
        spt.alert("Cannot not have empty name");
        return;
    }

    var input = node.getElement(".spt_input");
    var text = node.getElement(".spt_label");


    var old_name = node.spt_name;
    if (old_name != value) {
        // see if the name already exists in this group
        var group_name = spt.pipeline.get_current_group();
        var group = spt.pipeline.get_group(group_name);
        var nodes = group.get_nodes();
        for (var i = 0; i < nodes.length; i++) {
            var node_name = spt.pipeline.get_node_name(nodes[i]);
            if (value == node_name) {
                spt.alert("Name ["+value+"] already exists");
                input.value = "";
                return;
            }
        }
    }


    node.spt_name = value;
    node.setAttribute("spt_element_name", value);
    node.setAttribute("title", value);

    text.innerHTML = value;
    input.value = value;


    // fire an event
    var top = bvr.src_el.getParent(".spt_pipeline_top");
    var event_name = top.getAttribute("id") + "|node_rename";
    spt.named_events.fire_event(event_name, {
        src_el: node,
        options: {
            old_name: old_name,
            name: value,
        }
    } );

}



spt.pipeline.set_rename_mode = function(node) {
    var name = spt.pipeline.get_node_name(node);
    var args = {
        name: name,
    };

    var kwargs = {
        resize: false
    }

    var class_name = "tactic.ui.tools.NodeRenameWdg"
    var popup = spt.panel.load_popup(null, class_name, args, kwargs);
    popup.activator = node;
}



spt.pipeline.get_position = function(node) {
    // find the relative pos on the canvas
    var canvas = spt.pipeline.get_canvas();
    var canvas_pos = spt.pipeline.get_el_position(canvas);

    var node_pos = spt.pipeline.get_el_position(node);

    var rel_pos = {x: node_pos.x-(canvas_pos.x), y: node_pos.y-(canvas_pos.y)};

    return rel_pos;
}

spt.pipeline.get_el_last_position = function(el){
    var lastpos = el.getPosition();

    // Webkit position is affected by scale
    // FIXME: this still causes some drift over time ... much reduced, but
    // still there
    if ( spt.browser.is_Webkit_based() ) {
        lastpos = {x: lastpos.x, y: lastpos.y};

    }
    else {
        // TODO: this was fixed in Firefox v12: need to check for browser
        // version
        lastpos = {x: (lastpos.x), y: (lastpos.y)};

    }
    return lastpos;

}


spt.pipeline.get_el_position = function(el) {
    var pos = el.getPosition()
    var scale = spt.pipeline.get_scale();

    // Webkit position is affected by scale
    // FIXME: this still causes some drift over time ... much reduced, but
    // still there
    if ( spt.browser.is_Webkit_based() ) {
        pos = {x: pos.x/scale, y: pos.y/scale};

    }
    else {
        // TODO: this was fixed in Firefox v12: need to check for browser
        // version
        pos = {x: (pos.x/scale), y: (pos.y/scale)};

    }
    return pos
}


// folder methods

spt.pipeline.get_all_folders = function() {
    var canvas = spt.pipeline.get_canvas();
    var folders = canvas.getElements(".spt_pipeline_folder");
    return folders;
}

spt.pipeline.add_folder = function(group_name, color, title) {
    if (typeof(color) == 'undefined') {
        color = '#999';
    }

    var top = spt.pipeline.top;
    var canvas = spt.pipeline.get_canvas();

    var folders = spt.pipeline.get_all_folders();

    var template_container = top.getElement(".spt_pipeline_template");
    var template = template_container.getElement(".spt_pipeline_folder");
    var new_folder = spt.behavior.clone(template);
    new_folder.removeClass("spt_pipeline_folder_template");

    var group_label = new_folder.getElement(".spt_group");

    if (!title) {
        var parts = group_name.split("/");
        title = parts[parts.length-1];
    }

    //group_label.innerHTML = title;
    canvas.appendChild(new_folder);

    // color the folder
    spt.pipeline.set_folder_color(new_folder, color);

    new_folder.spt_group = group_name;


    var size = spt.pipeline.get_canvas_size();
    var x = size.x/3 + folders.length*15;
    var y = size.y/3 + folders.length*10;
    spt.pipeline.move_to(new_folder, x, y);
}


spt.pipeline.set_folder_color = function(folder, color) {

    return

    // only color the swatch for now
    var swatch = folder.getElement(".spt_color_swatch");
    swatch.setStyle("background", color);

    color = '#CCC'
    var color1 = spt.css.modify_color_value(color, +3);
    var color2 = spt.css.modify_color_value(color, -3);

    var content = folder.getElement(".spt_content");
    if( spt.browser.is_Firefox() ) {
        content.setStyle("background", "-moz-linear-gradient(top, "+color1+" 30%, "+color2+" 98%)");
    }
    else {
        content.setStyle("background", "-webkit-gradient(linear, 0% 0%, 0% 100%, from("+color1+"), to("+color2+"))");
    }

    var lip = folder.getElement(".spt_lip");
    lip.setStyle("background", color1);

    folder.spt_color = color;
}






spt.pipeline.get_canvas_size = function(node) {
    // find the relative pos on the canvas
    var data = spt.pipeline.get_data();
    var canvas_size = data.canvas_size;
    var size = canvas_size.getSize();
    return size;
}





spt.pipeline.get_size = function(node) {
    // find the relative pos on the canvas
    var node_size = node.getSize();
    if (node.hasClass(".spt_pipeline_condition")) {
        node_size.x = node_size.x * 1.12 // distance to corner of square
    }

    return node_size;
}




// Take the current position and set values.  This should be used if
// some other means that "move_to" was use to position the element.
spt.pipeline.set_current_position = function(node) {
    var pos = spt.pipeline.get_position(node);
    // set variables
    node.spt_xpos = pos.x;
    node.spt_ypos = pos.y;
}


spt.pipeline.move_to = function(node, x, y) {
    // move it to 0, 0
    node.setStyle("left", 0);
    node.setStyle("top", 0);

    // find the relative pos on the canvas
    var canvas = spt.pipeline.get_canvas();
    var canvas_pos = spt.pipeline.get_el_position(canvas);
    var node_pos = spt.pipeline.get_el_position(node);

    rel_pos = {x: node_pos.x-canvas_pos.x, y: node_pos.y-canvas_pos.y};

    // find out where the position is at x, y
    new_pos = {x: x-rel_pos.x, y: y-rel_pos.y};

    // move it to the location
    node.setStyle("left", new_pos.x);
    node.setStyle("top", new_pos.y);

    // set variables
    node.spt_xpos = x;
    node.spt_ypos = y;
}


spt.pipeline.move_by = function(node, rel_x, rel_y) {
    var pos = spt.pipeline.get_position(node);
    var new_pos = { x: pos.x+rel_x, y: pos.y+rel_y };
    spt.pipeline.move_to(node, new_pos.x, new_pos.y);
}




spt.pipeline.move_all_nodes = function(rel_x, rel_y) {
    var nodes = spt.pipeline.get_all_nodes();

    for (var i = 0; i < nodes.length; i++) {
        var node = nodes[i];
        var pos = spt.pipeline.get_position(node);
        var new_pos = { x: pos.x+rel_x, y: pos.y+rel_y };

        // FIXME: this is slow: need to optimize
        spt.pipeline.move_to(node, new_pos.x, new_pos.y);
    }



    spt.pipeline.redraw_canvas();

    spt.pipeline.match_snapshot();
}


spt.pipeline.move_all_folders = function(rel_x, rel_y) {
    var folders = spt.pipeline.get_all_folders();

    for (var i = 0; i < folders.length; i++) {
        var node = folders[i];
        var pos = spt.pipeline.get_position(node);
        var new_pos = { x: pos.x+rel_x, y: pos.y+rel_y };

        // FIXME: this is slow: need to optimize
        spt.pipeline.move_to(node, new_pos.x, new_pos.y);
    }

}






spt.pipeline.last_node_pos = null;
spt.pipeline.last_nodes_pos = {};
spt.pipeline.orig_node_pos = null;
spt.pipeline.changed = true;
spt.pipeline.node_drag_setup = function( evt, bvr, mouse_411) {

    spt.pipeline.init(bvr);
    spt.pipeline.last_node_pos = spt.pipeline.get_mouse_position(mouse_411);
    spt.pipeline.orig_node_pos = spt.pipeline.last_node_pos;

    var node = bvr.src_el;
    node.addClass("move");

    if (node.spt_is_selected == true) {
        // get all selected nodes and record their positions
        var nodes = spt.pipeline.get_selected_nodes();
        for (var i = 0; i < nodes.length; i++ ) {
            var name = nodes[i].spt_element_name;
            var pos = spt.pipeline.get_position(nodes[i]);
            spt.pipeline.last_node_pos[name] = pos;
        }

    }
    else {
        // This is handle on the regular click
        //spt.pipeline.select_single_node(node);
    }
    spt.pipeline.changed = false;

    spt.pipeline.draw_skip = 0;
}

spt.pipeline.node_drag_motion = function( evt, bvr, mouse_411) {


    // slow down the drawwing a bit (seems to slow down on big workflows);
    if (spt.pipeline.draw_skip != 5) {
        spt.pipeline.draw_skip += 1;
        return;
    }
    spt.pipeline.draw_skip = 0;


    var node = bvr.drag_el;
    var mouse_pos = spt.pipeline.get_mouse_position(mouse_411);
    var dx = mouse_pos.x - spt.pipeline.last_node_pos.x;
    var dy = mouse_pos.y - spt.pipeline.last_node_pos.y;
    var scale = spt.pipeline.get_scale();
    dx = dx/scale;
    dy = dy/scale;


    if (Math.abs(mouse_pos.x - spt.pipeline.orig_node_pos.x) > 5 ||
            Math.abs(mouse_pos.y - spt.pipeline.orig_node_pos.y) > 5 )
    {
        spt.pipeline.changed = true;
    }


    spt.pipeline.last_node_pos = mouse_pos;

    if (node.spt_is_selected == true) {
        // get all selected nodes and record their positions
        var nodes = spt.pipeline.get_selected_nodes();
        for (var i = 0; i < nodes.length; i++ ) {
            spt.pipeline.move_by(nodes[i], dx, dy);
            var pos = spt.pipeline.get_position(nodes[i]);
            spt.pipeline.last_node_pos[name] = pos;
        }
    }
    else {
        spt.pipeline.move_by(node, dx, dy);
    }

    spt.pipeline.redraw_canvas();

}




spt.pipeline.node_drag_action = function( evt, bvr, mouse_411) {

    var node = bvr.drag_el;
	node.removeClass("move");

	if (!spt.pipeline.changed) {
		return;
	}

	spt.named_events.fire_event('pipeline|change', {});

	var editor_top = bvr.src_el.getParent(".spt_pipeline_editor_top");
	if (editor_top) {
		editor_top.addClass("spt_has_changes");
	}

	var cmd = new spt.pipeline.NodeDragActionCmd(node, spt.pipeline.last_node_pos, spt.pipeline.orig_node_pos);

    spt.command.add_to_undo(cmd);

}


spt.pipeline.NodeDragActionCmd = function(node, last_node_pos, orig_node_pos) {

    this.redo = function() {
    	this.pos = last_node_pos;

    	this.node = node;
		this.node = spt.pipeline.reset_node(this.node)

		spt.pipeline.move_to(this.node, this.pos.x, this.pos.y);
		spt.pipeline.redraw_canvas();

    };

    this.undo = function() {
		this.pos = orig_node_pos;

		this.node = node;
		this.node = spt.pipeline.reset_node(this.node)

		spt.pipeline.move_to(this.node, this.pos.x, this.pos.y);
		spt.pipeline.redraw_canvas();
	}

}


spt.pipeline.reset_node = function(node){
	if (!document.body.contains(node)){
		var name = node.spt_name;
		var q = "[spt_element_name='" + name + "']";
		node = document.querySelectorAll(q)[0];
	}
	return node;
}

spt.pipeline.reset_connector = function(connector){
    var from_node = spt.pipeline.reset_node(connector.get_from_node())
	connector.set_from_node(from_node)
    var to_node = spt.pipeline.reset_node(connector.get_to_node())
    connector.set_to_node(to_node)

	return connector;
}



spt.pipeline.last_connector = null;
spt.pipeline.drag_connector_setup = function(evt, bvr, mouse_411) {
    spt.pipeline.init(bvr);

    // create a new connector and attach a node to it
    var from_node = bvr.src_el.getParent(".spt_pipeline_node");

    if (bvr.connector) {
        // reuse existing connector
        spt.pipeline.last_connector = bvr.connector;
        spt.pipeline.last_connector.to_node = null;
    }
    else {
        spt.pipeline.last_connector = new spt.pipeline.Connector();
    }


    spt.pipeline.last_connector.set_from_node(from_node);
    spt.named_events.fire_event('pipeline|change', {});
}



spt.pipeline.drag_connector_motion = function(evt, bvr, mouse_411) {

    var data = spt.pipeline.get_data();
    var canvas = spt.pipeline.get_canvas();

    var scale = spt.pipeline.get_scale();
    var translate = spt.pipeline.get_translate();

    var node;
    var node_pos;

    if (data.line_mode == 'bezier' || data.line_mode == 'curved_edge') {
        node = bvr.src_el.getParent(".spt_pipeline_node");

        node_pos = spt.pipeline.get_position(node);
        var size = spt.pipeline.get_size(node);
        node_pos = { x: (node_pos.x+size.x)*scale, y: (node_pos.y+size.y/2)*scale };

        var paint = spt.pipeline.get_paint();
        var offset = canvas.getPosition(paint);
        node_pos = { x: (node_pos.x+offset.x), y: (node_pos.y + offset.y)};
    }
    else {
        node = bvr.src_el.getParent(".spt_pipeline_node");
        node_pos = spt.pipeline.get_position(node);
        node_pos = { x: (node_pos.x + 50), y: (node_pos.y + 20)};

    }


    var rel_pos = spt.pipeline.get_mouse_position(mouse_411);


    // redraw canvas and add connector
    spt.pipeline.redraw_canvas();

    if (data.line_mode == 'bezier') {
        spt.pipeline.draw_connector( node_pos, rel_pos );
    } else if (data.line_mode == 'curved_edge') {
        spt.pipeline.draw_curved_edge_line( node_pos, rel_pos );
    } else {
        spt.pipeline.draw_line( node_pos, rel_pos );
    }

}

spt.pipeline.construct_graph = function(nodes, connectors) {
    var graph = {};
    for (var i = 0; i < nodes.length; i++) {
        graph[nodes[i].title] = [];
    }
    for (var i = 0; i < connectors.length; i++) {
        graph[connectors[i].from_node.title].push(connectors[i].to_node.title);
    }

    return graph;
}

spt.pipeline._detect_cycle = function(graph, node, visited, stack) {
    visited.find(x => x.node === node).bool = true;
    stack.find(x => x.node === node).bool = true;

    for (var i = 0; i < graph[node].length; i++) {
        if (!visited.find(x => x.node === graph[node][i]).bool) {
            if (spt.pipeline._detect_cycle(graph, graph[node][i], visited, stack)) {
                return true;
            }
        } else if (stack.find(x => x.node === graph[node][i]).bool) {
            return true;
        }
    }

    stack.find(x => x.node === node).bool = false;
    return false;
}

spt.pipeline.detect_cycle = function() {
    var nodes = spt.pipeline.get_all_nodes();
    var connectors = spt.pipeline.get_canvas().connectors;
    var graph = spt.pipeline.construct_graph(nodes, connectors);

    var visited = [];
    var stack = [];
    for (var i = 0; i < nodes.length; i++) {
        var object = {
            node: nodes[i].title,
            bool: false
        }

        visited.push(object);
        stack.push(object);
    }

    for (var i = 0; i < nodes.length; i++) {
        if (!visited.find(x => x.node === nodes[i].title).bool) {
            if (spt.pipeline._detect_cycle(graph, nodes[i].title, visited, stack)) {
                return true;
            }
        }
    }
    return false;
}

spt.pipeline.drag_connector_action = function(evt, bvr, mouse_411) {
    var drop_on_el = spt.get_event_target(evt);
    var to_node = drop_on_el.getParent(".spt_pipeline_node");
    var from_node = bvr.src_el.getParent(".spt_pipeline_node");
    var canvas = spt.pipeline.get_canvas();

    if (bvr.connector && to_node == null) {
        // if this is a reused connector, then delete it
        spt.pipeline.delete_connector(bvr.connector);
        spt.pipeline.redraw_canvas();
        return;
    }


    if ( to_node && from_node &&
        spt.pipeline.get_node_name(to_node) == spt.pipeline.get_node_name(from_node) )
    {
        //spt.alert("Source node and destination node are the same");
        return;
    }

    var group_name = from_node.spt_group;
    spt.pipeline.set_current_group(group_name);

    // if dropped on empty canvas, then add a node only if this is a new connector
    if (to_node == null) {

        var pos = spt.pipeline.get_mouse_position(mouse_411);

        var scale = spt.pipeline.get_scale();
        var paint = spt.pipeline.get_paint();
        var offset = canvas.getPosition(paint);
        pos = { x: (pos.x-offset.x)/scale, y: (pos.y - offset.y)/scale};

        var default_node_type = null;
        to_node = spt.pipeline.add_node(null, null, null, { node_type: null} );
        // BACKWARDS COMPATIBILITY
        if (spt.pipeline.top.getAttribute("version_2_enabled") != "false")
            spt.pipeline.set_node_kwarg(to_node, "version", 2);

        // FIXME: hard coded
        var height = 40;
        spt.pipeline.move_to(to_node, pos.x, pos.y-height/2);
    }

    if (to_node != null) {
        var to_group = to_node.spt_group;

        if (group_name != to_group) {
            spt.alert("Connections between pipelines currently not supported");
            spt.pipeline.redraw_canvas()
            return;
        }

        var connector = spt.pipeline.last_connector;

        // attach the connector to the to_node
        connector.set_to_node(to_node);

        // add it to the list of connectors
        var connectors = canvas.connectors;

        // check all of the connectors to see if is already exists
        for (var i = 0; i < connectors.length; i++) {
            if (connectors[i] == connector) continue;

            var conn_to_node = connectors[i].get_to_node();
            var conn_from_node = connectors[i].get_from_node();
            if ( (to_node == conn_to_node && conn_from_node == from_node) ||
               (to_node == conn_from_node && conn_to_node == from_node) )
            {
                spt.alert("This connection already exists");
                return;
            }

        }


        var temp = connectors.slice();
        if (!bvr.connector) {
            connectors.push(connector);
        }

        // check if cycle exists
        if (!spt.pipeline.allow_cycle) {
            if (spt.pipeline.detect_cycle()) {
                spt.alert("Cyclic connections are not allowed");
                canvas.connectors = temp;
                return;
            }
        }

        // add the connector to the source group
        if (!bvr.connector) {
            var group = spt.pipeline.add_group(group_name);
            group.add_connector(connector);
        }

        connector.select();

        // fire an event
        var top = bvr.src_el.getParent(".spt_pipeline_top");
        var event_name = top.getAttribute("id") + "|connector_create";
        spt.named_events.fire_event(event_name, { src_el: connector } );
    }

    spt.pipeline.redraw_canvas();

    var el = connector.panel;
    connector.set_attr("from_node", from_node.spt_name);
    connector.set_attr("to_node", to_node.spt_name);
    if (el) {
        if (el.update_settings) {
            el.update_settings({connector: connector});
        } else {
            var data = spt.pipeline.get_data();
            var pipeline_type = data.type;
            var connector_panel_data = data.connector_panel_data;
            if (connector_panel_data[pipeline_type]) {
                var class_name = connector_panel_data[pipeline_type];
                var kwargs = {'from_node': from_node.spt_name, 'to_node': to_node.spt_name, 'pipeline_code': group_name, 'overlap': connector.get_attr("overlap")};
                spt.panel.load(el, class_name, kwargs, {}, {show_loading: false});
            }
        }
    }

    var editor_top = canvas.getParent(".spt_pipeline_editor_top");
    if (editor_top) {
        editor_top.addClass("spt_has_changes");
    }

}


spt.pipeline.add_connector = function() {
    var canvas = spt.pipeline.get_canvas();
    var connector = new spt.pipeline.Connector();
    var connectors = canvas.connectors;
    connectors.push(connector);
    return connector;
}



spt.pipeline.connect_nodes = function(from_node, to_node) {
    var connector = spt.pipeline.add_connector();
    connector.set_from_node(from_node);
    connector.set_to_node(to_node);

    connector.draw();

    return connector;
}



spt.pipeline.delete_connector = function(connector) {
    if(!connector){
    	return;
    }
    var canvas = spt.pipeline.get_canvas();
    var connectors = canvas.connectors;
    for (var i = 0; i < connectors.length; i++) {
        if (connectors[i] == connector) {
            connectors.splice(i, 1);
            break;
        }
    }

    var groups = spt.pipeline.get_groups();
    for (var group_name in groups) {
        groups[group_name].remove_connector(connector);
    }

    // remove custom panels
    panel = connector.panel;
    if (panel) {
        spt.behavior.destroy_element(panel);
    }

    spt.pipeline.clear_selected();

    var editor_top = canvas.getParent(".spt_pipeline_editor_top");
    if (editor_top) {
        editor_top.addClass("spt_has_changes");
    }

    return connector;
}

spt.pipeline.draw_background = function() {
    var ctx = spt.pipeline.get_ctx();
    ctx.fillStyle = spt.pipeline.background_color;
    var canvas_size = spt.pipeline.get_canvas_size();
    ctx.fillRect(0, 0, canvas_size.x, canvas_size.y);
}


spt.pipeline.draw_curve = function(start, end) {

    var ctx = spt.pipeline.get_ctx();
    var width = (end.x - start.x)/2;
    ctx.bezierCurveTo(start.x+width, start.y, end.x-width, end.y, end.x, end.y);
}


spt.pipeline.draw_curve_vertical = function(start, end) {
    var ctx = spt.pipeline.get_ctx();
    //var width = (end.x - start.x)/2;
    //ctx.bezierCurveTo(start.x+width, start.y, end.x-width, end.y, end.x, end.y);
    var height = (end.y - start.y)/2;
    ctx.bezierCurveTo(start.x, start.y+height, end.x, end.y-height, end.x, end.y);
}


spt.pipeline.draw_arc = function(start, end, offset) {
    var ctx = spt.pipeline.get_ctx();
    var width = (end.x - start.x)/2;
    var cp1 = { x: start.x + offset, y: start.y };
    var cp2 = { x: end.x + offset, y: end.y };
    ctx.bezierCurveTo(cp1.x, cp1.y, cp2.x, cp2.y, end.x, end.y);
}

spt.pipeline.draw_curved_edge = function(start, end) {
    var ctx = spt.pipeline.get_ctx();
    var center_y = (start.y + end.y)/2;
    var dx = (end.x - start.x) / 2;
    var scale = spt.pipeline.get_scale();
    if (dx > 50*scale) {
        dx = 50*scale;
    }
    var center_x = start.x+dx;
    ctx.bezierCurveTo(center_x, start.y, center_x, start.y, center_x, center_y);
    ctx.bezierCurveTo(center_x, end.y, center_x, end.y, end.x, end.y);
}


spt.pipeline.set_line_mode = function(mode) {
    var data = spt.pipeline.get_data();
    data.line_mode = mode;
}

spt.pipeline.draw_connector = function(start, end, color) {
    if (typeof(color) == 'undefined') {
        color = '#111';
    }

    var back = false;
    if (start.x - 100 > end.x + 100) {
        color = "#900";
        start.x = start.x - 50;
        var back = true;
    }

    var ctx = spt.pipeline.get_ctx();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;

    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    var width = (end.x - start.x)/2;
    //var center_y = (start.y + end.y)/2;


    if (start.x > end.x) {


        var offset = {}

        var x_diff = - end.x + start.x;
        if (x_diff > 50) {
            x_diff = 50;
        }
        offset.x = x_diff/4;


        var y_diff = end.y - start.y
        if (y_diff < 0) {
            if (y_diff < -50) {
                y_diff = - 50;
            }
        }
        else {
            if (y_diff > 50) {
                y_diff = 50;
            }
        }
        offset.y = y_diff/4;



        var scale = spt.pipeline.get_scale();
        offset.x = offset.x * scale;
        offset.y = offset.y * scale;



        tmp_start = start;
        if (back) {
            tmp_end = start;
            offset.x = offset.x * 10.0;
            offset.y = offset.y * 10.0;
        }
        else {
            tmp_end = { x: start.x + offset.x, y: start.y + offset.y };
            ctx.bezierCurveTo(
                tmp_start.x + offset.x/2, tmp_start.y,
                tmp_end.x, tmp_end.y - offset.y,
                tmp_end.x, tmp_end.y
            );

        }

        tmp_start = tmp_end;
        if (back) {
            tmp_end = { x: end.x, y: end.y - offset.y};
        }
        else {
            tmp_end = { x: end.x - offset.x, y: end.y - offset.y};
        }
        if (back) {
            spt.pipeline.draw_curve(tmp_start, tmp_end);
        }
        else {
            spt.pipeline.draw_curve_vertical(tmp_start, tmp_end);
        }

        // draw the arrow
        var halfway = { x:(tmp_end.x-tmp_start.x)/2+tmp_start.x, y:(tmp_end.y-tmp_start.y)/2+tmp_start.y };

        // fudge factor to make angle of arrow look better (rather than finding the
        // the true derivative of a bezier curve (this looks good enough)
        var ff = 0.5;
        var len = Math.sqrt( (tmp_end.x-tmp_start.x)*(tmp_end.x-tmp_start.x)+(tmp_end.y-tmp_start.y)*(tmp_end.y-tmp_start.y)*ff*ff );
        var point0 = { x: (tmp_end.x-tmp_start.x)/len, y: (tmp_end.y-tmp_start.y)*ff/len };


        tmp_start = tmp_end;
        tmp_end = end;


        if (back) {
            ctx.bezierCurveTo(
                tmp_start.x - offset.x, tmp_start.y,
                tmp_end.x - offset.x, tmp_end.y,
                tmp_end.x, tmp_end.y
            );
        }
        else {
            ctx.bezierCurveTo(
                tmp_start.x, tmp_start.y + offset.y,
                tmp_end.x - offset.x/2, tmp_end.y,
                tmp_end.x, tmp_end.y
            );
        }

        spt.pipeline.draw_arrow(halfway, point0, 8);

    }
    else {
        //ctx.font = "bold 16px sans-serif";
        //ctx.fillText(">", start.x+width, center_y)
        ctx.bezierCurveTo(start.x+width, start.y, end.x-width, end.y, end.x, end.y);


        // fudge factor to make angle of arrow look better (rather than finding the
        // the true derivative of a bezier curve (this looks good enough)
        var ff = 1.5;

        var halfway = { x:(end.x-start.x)/2+start.x, y:(end.y-start.y)/2+start.y };
        var len = Math.sqrt( (end.x-start.x)*(end.x-start.x)+(end.y-start.y)*(end.y-start.y)*ff*ff );
        var point0 = { x: (end.x-start.x)/len, y: (end.y-start.y)*ff/len };

        spt.pipeline.draw_arrow(halfway, point0, 8);

    }

    ctx.stroke();
}

spt.pipeline.draw_curved_edge_line = function(start, end, color) {
    if (typeof(color) == 'undefined') {
        color = '#111';
    }

    var back = false;
    if (start.x - 100 > end.x + 100) {
        color = "#900";
        start.x = start.x - 50;
        var back = true;
    }

    var ctx = spt.pipeline.get_ctx();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;

    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    var width = (end.x - start.x)/2;
    //var center_y = (start.y + end.y)/2;

    // back
    if (start.x > end.x) {

        var offset = {}

        var x_diff = - end.x + start.x;
        if (x_diff > 50) {
            x_diff = 50;
        }
        offset.x = x_diff/4;


        var y_diff = end.y - start.y
        if (y_diff < 0) {
            if (y_diff < -50) {
                y_diff = - 50;
            }
        }
        else {
            if (y_diff > 50) {
                y_diff = 50;
            }
        }
        offset.y = y_diff/4;



        var scale = spt.pipeline.get_scale();
        offset.x = offset.x * scale;
        offset.y = offset.y * scale;



        tmp_start = start;
        if (back) {
            tmp_end = start;
            offset.x = offset.x * 10.0;
            offset.y = offset.y * 10.0;
        }
        else {
            tmp_end = { x: start.x + offset.x, y: start.y + offset.y };
            ctx.bezierCurveTo(
                tmp_start.x + offset.x/2, tmp_start.y,
                tmp_end.x, tmp_end.y - offset.y,
                tmp_end.x, tmp_end.y
            );

        }

        tmp_start = tmp_end;
        if (back) {
            tmp_end = { x: end.x, y: end.y - offset.y};
        }
        else {
            tmp_end = { x: end.x - offset.x, y: end.y - offset.y};
        }
        if (back) {
            spt.pipeline.draw_curve(tmp_start, tmp_end);
        }
        else {
            spt.pipeline.draw_curve_vertical(tmp_start, tmp_end);
        }

        tmp_start = tmp_end;
        tmp_end = end;


        if (back) {
            ctx.bezierCurveTo(
                tmp_start.x - offset.x, tmp_start.y,
                tmp_end.x - offset.x, tmp_end.y,
                tmp_end.x, tmp_end.y
            );
        }
        else {
            ctx.bezierCurveTo(
                tmp_start.x, tmp_start.y + offset.y,
                tmp_end.x - offset.x/2, tmp_end.y,
                tmp_end.x, tmp_end.y
            );
        }

    }
    // front
    else {
        spt.pipeline.draw_curved_edge(start, end);
    }
    ctx.stroke();
}

spt.pipeline.draw_text = function(text, x, y, color) {
    var ctx = spt.pipeline.get_ctx();
    if (!color) {
        //color = "#DE4A18";
        color = "#666";
    }
    ctx.fillStyle = color;
    var scale = spt.pipeline.get_scale();
    var font_size = 11*scale;
    ctx.font = 'normal '+font_size+'px sans-serif';
    ctx.fillText(text, x, y);
}

spt.pipeline.draw_line = function(start, end, color) {
    if (typeof(color) == 'undefined') {
        color = '#111';
    }
    var ctx = spt.pipeline.get_ctx();
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.lineTo(end.x, end.y);


    var halfway = { x:(end.x-start.x)/2+start.x, y:(end.y-start.y)/2+start.y };
    var len = Math.sqrt( (end.x-start.x)*(end.x-start.x)+(end.y-start.y)*(end.y-start.y) );
    var point0 = { x: (end.x-start.x)/len, y: (end.y-start.y)/len };

    spt.pipeline.draw_arrow(halfway, point0, 8);



    ctx.stroke();
}


spt.pipeline.draw_arrow = function(halfway, point0, size) {
    var ctx = spt.pipeline.get_ctx();
    ctx.moveTo(halfway.x, halfway.y);

    var angle = 3.1419 / 6;


    var point1 = {
        x: -size*(Math.cos(angle)*point0.x - Math.sin(angle)*point0.y),
        y: -size*(Math.sin(angle)*point0.x + Math.cos(angle)*point0.y)
    }
    var point2 = {
        x: -size*(Math.cos(angle)*point0.x + Math.sin(angle)*point0.y),
        y: -size*(-Math.sin(angle)*point0.x + Math.cos(angle)*point0.y)
    }

    ctx.lineTo(point1.x+halfway.x, point1.y+halfway.y);
    ctx.lineTo(halfway.x, halfway.y);
    ctx.lineTo(point2.x+halfway.x, point2.y+halfway.y);

}



spt.pipeline.draw_rect = function(pos1, pos2, color) {
    var ctx = spt.pipeline.get_ctx();
    if (color) {
        ctx.strokeStyle = color;
    }
    ctx.strokeRect(pos1.x, pos1.y, pos2.x-pos1.x, pos2.y-pos1.y);
}




// Pan functionality
spt.pipeline.orig_mouse_position = null;
spt.pipeline.last_mouse_position = null;
spt.pipeline.canvas_drag_disable = false;
spt.pipeline.canvas_drag_mode = "canvas";

spt.pipeline.canvas_drag_setup = function(evt, bvr, mouse_411) {

    var pos = spt.pipeline.get_mouse_position(mouse_411);
    spt.pipeline.last_mouse_position = pos;
    spt.pipeline.orig_mouse_position = pos;


    // do a hit test first
    var connector = spt.pipeline.hit_test(pos.x-2, pos.y-2, pos.x+2, pos.y+2);
    if (connector != null) {
        //return;
        spt.pipeline.canvas_drag_disable = true;
        spt.pipeline.canvas_drag_mode = "connector";
        spt.pipeline.canvas_drag_connector = connector;
        // This is done only after we have dragged for 5 pixels
        //spt.pipeline._existing_connector_drag_setup(evt, bvr, mouse_411);
        return;
    }


    spt.pipeline.init(bvr);

    spt.pipeline.canvas_drag_mode = "canvas";
    spt.pipeline.canvas_drag_disable = false;

    bvr.src_el.setStyle("cursor", "move");
    spt.pipeline.init(bvr);
    spt.pipeline.orig_translate = spt.pipeline.get_translate();


    var screen = spt.pipeline.get_screen();
    if (screen) {
        var screen_nodes = screen.getElements(".spt_screen_node");
        screen_nodes.forEach( function(screen_node) {
            if (screen_node.canvas_drag_motion) {
                screen_node.canvas_drag_setup();
            }
        } );
    }



    spt.body.hide_focus_elements(evt);

    spt.pipeline.draw_skip = 0;
}

spt.pipeline.canvas_drag_motion = function(evt, bvr, mouse_411) {


    var mouse_pos = spt.pipeline.get_mouse_position(mouse_411);
    var dx = mouse_pos.x - spt.pipeline.orig_mouse_position.x;
    var dy = mouse_pos.y - spt.pipeline.orig_mouse_position.y;

    var scale = spt.pipeline.get_scale();
    dx = dx/scale;
    dy = dy/scale;


    if ( spt.pipeline.canvas_drag_mode == "connector" ) {
        if (bvr.is_editable == 'false') {
            return;
        }
        if (Math.abs(dx) < 5 && Math.abs(dy) < 5) {
            return;
        }
        spt.pipeline._existing_connector_drag_motion(evt, bvr, mouse_411);
        return;
    }
    if ( spt.pipeline.canvas_drag_disable == true ) {
        return;
    }

    // slow down the drawwing a bit (seems to slow down on big workflows);
    if (spt.pipeline.draw_skip != 5) {
        spt.pipeline.draw_skip += 1;
        return;
    }


    var screen = spt.pipeline.top.getElement(".spt_screen");
    if (screen) {
        var screen_nodes = screen.getElements(".spt_screen_node");
        screen_nodes.forEach( function(screen_node) {
            if (screen_node.canvas_drag_motion) {
                screen_node.canvas_drag_motion(dx, dy);
            }
        } );
    }

    var orig_translate = spt.pipeline.orig_translate;
    spt.pipeline.set_translate(orig_translate.x+dx, orig_translate.y+dy);


    spt.pipeline.draw_skip = 0;

    spt.pipeline.match_snapshot();
}

spt.pipeline.canvas_drag_action = function(evt, bvr, mouse_411) {


    // reset the setting
    spt.pipeline.canvas_drag_disable = false;
    bvr.src_el.setStyle("cursor", "");


    var mouse_pos = spt.pipeline.get_mouse_position(mouse_411);
    var dx = mouse_pos.x - spt.pipeline.orig_mouse_position.x;
    var dy = mouse_pos.y - spt.pipeline.orig_mouse_position.y;

    var scale = spt.pipeline.get_scale();
    dx = dx/scale;
    dy = dy/scale;


    if ( spt.pipeline.canvas_drag_mode == "connector" ) {
        if (bvr.is_editable == 'false') {
            return;
        }
        spt.pipeline.canvas_drag_init = false;

        spt.pipeline.canvas_drag_mode = "canvas";

        if (Math.abs(dx) < 5 && Math.abs(dy) < 5) {
            return;
        }
        spt.pipeline._existing_connector_drag_action(evt, bvr, mouse_411);
        return;
    }



    if (Math.abs(dx) < 5 && Math.abs(dy) < 5) {
        spt.pipeline.unselect_all_nodes();
        spt.pipeline.unselect_all_connectors();
        return;
    }


    // reset the translation and move all the nodes
    spt.pipeline.set_translate(0, 0);
    spt.pipeline.move_all_nodes(dx, dy);
    spt.pipeline.move_all_folders(dx, dy);

    var nodes = spt.pipeline.get_all_nodes();
    for (var i = 0; i < nodes.length; i++) {
        spt.pipeline.set_current_position(nodes[i]);
    }
    spt.pipeline.redraw_canvas();

    spt.pipeline.match_snapshot();
}


// connector drag
spt.pipeline.canvas_drag_src_el;
spt.pipeline.canvas_drag_connector;
spt.pipeline.canvas_drag_init = false;

spt.pipeline._existing_connector_drag_setup = function(evt, bvr, mouse_411) {
    var pos = spt.pipeline.get_mouse_position(mouse_411);

    var connector = spt.pipeline.canvas_drag_connector;
    spt.pipeline.canvas_drag_src_el = connector.from_node.getElement(".spt_content");

    bvr.src_el = spt.pipeline.canvas_drag_src_el;
    bvr.connector = connector;
    spt.pipeline.drag_connector_setup(evt, bvr, mouse_411);
}

spt.pipeline._existing_connector_drag_motion = function(evt, bvr, mouse_411) {

    // only set up if the connector has moved
    if (spt.pipeline.canvas_drag_init == false) {
        spt.pipeline._existing_connector_drag_setup(evt, bvr, mouse_411);
        spt.pipeline.canvas_drag_init = true;
    }

    bvr.src_el = spt.pipeline.canvas_drag_src_el;
    bvr.connector = spt.pipeline.canvas_drag_connector;

    spt.pipeline.drag_connector_motion(evt, bvr, mouse_411);
}

spt.pipeline._existing_connector_drag_action = function(evt, bvr, mouse_411) {
    spt.pipeline.canvas_drag_init = false;

    bvr.src_el = spt.pipeline.canvas_drag_src_el;
    bvr.connector = spt.pipeline.canvas_drag_connector;
    spt.pipeline.drag_connector_action(evt, bvr, mouse_411);

    // It looks like the bvr object is actually reused by the behvior.  We set the
    // src el back to the original canvas after the drag operation
    var canvas = spt.pipeline.get_canvas();
    bvr.src_el = canvas;
}



// Zoom functionality
spt.pipeline.zoom_drag_setup = function(evt, bvr, mouse_411) {
    spt.pipeline.init(bvr);
    spt.pipeline.last_mouse_position = spt.pipeline.get_mouse_position(mouse_411);
}
spt.pipeline.zoom_drag_motion = function(evt, bvr, mouse_411) {
    var mouse_pos = spt.pipeline.get_mouse_position(mouse_411);
    var dx = mouse_pos.x - spt.pipeline.last_mouse_position.x;
    var dy = mouse_pos.y - spt.pipeline.last_mouse_position.y;

    var scale = spt.pipeline.get_scale()

    if (dx < 0) {
        scale = scale * 0.95;
    }
    else {
        scale = scale / 0.95;
    }

    spt.pipeline.set_scale( scale );


    spt.pipeline.last_mouse_position = mouse_pos;

}


spt.pipeline.zoom_drag_action = function(evt, bvr, mouse_411) {
    spt.pipeline.redraw_canvas();
}

spt.pipeline.set_scale = function(scale) {

    if (scale == 0) {
        scale = 1;
    }

    // set an arbitrary max scale so drawing optimizations don't start showing up
    if (scale > 3) return;

    var canvas = spt.pipeline.get_canvas();
    scale_el = canvas.getParent(".spt_pipeline_scale");

    var data = spt.pipeline.get_data();
    data.scale = scale;

    var translate = data.translate;
    var x = translate.x;
    var y = translate.y;


    //var transform_str = "translate("+x+"px, "+y+"px) scale("+scale+", "+scale+")";
    var transform_str = "scale("+scale+", "+scale+") translate("+x+"px, "+y+"px)";

    scale_el.setStyle("-moz-transform", transform_str)
    scale_el.setStyle("-webkit-transform", transform_str)
    scale_el.setStyle("transform", transform_str)



    var screen = spt.pipeline.get_screen();
    if (screen) {
        //screen.setStyle("transform", "scaleY("+scale+")");
        var els = spt.pipeline.get_screen_nodes();
        els.forEach( function(el) {
            el.set_scale(scale);
        } );
    }



    //TweenLite.to(scale_el, 0.2, {scale: scale});

    spt.pipeline.redraw_canvas();

    spt.pipeline.match_snapshot();

}

spt.pipeline.get_scale = function() {
    var data = spt.pipeline.get_data();
    return data.scale;
}


spt.pipeline.set_translate = function(x, y) {

    var canvas = spt.pipeline.get_canvas();
    scale_el = canvas.getParent(".spt_pipeline_scale");

    var data = spt.pipeline.get_data();
    data.translate = {x: x, y: y};

    var scale = data.scale;


    //var transform_str = "translate("+x+"px, "+y+"px) scale("+scale+", "+scale+")";
    var transform_str = "scale("+scale+", "+scale+") translate("+x+"px, "+y+"px)";


    scale_el.setStyle("-moz-transform", transform_str)
    scale_el.setStyle("-webkit-transform", transform_str)
    scale_el.setStyle("transform", transform_str)

    spt.pipeline.redraw_canvas();

}


spt.pipeline.get_translate = function() {
    var data = spt.pipeline.get_data();
    return data.translate;
}






spt.pipeline.center_node = function(node) {
    var pos = spt.pipeline.get_position(node);
    var size = spt.pipeline.get_canvas_size();

    // FIXME: hard coded
    var width = 100;
    var height = 40;

    var dd = { x: size.x/2 - pos.x - width/2, y: size.y/2 - pos.y - height/2};

    spt.pipeline.move_all_nodes( dd.x, dd.y );

}




/* Set the canvas size */
spt.pipeline.set_size = function(width, height) {
    var top = spt.pipeline.top;

    var canvas_paint = spt.pipeline.get_paint();
    var pipeline_resize = top.getElement(".spt_pipeline_resize")
    var canvas_size = pipeline_resize.getElement(".spt_pipeline_canvas_size");
    var canvas = spt.pipeline.get_canvas();
    
    if (width) {
        canvas_paint.setAttribute("width", ""+width);
        pipeline_resize.setStyle("width", ""+width);
        canvas_size.setStyle("width", ""+width);
        canvas.setStyle("width", ""+width);
    }
    if (height) {
        canvas_paint.setAttribute("height", ""+height);
        pipeline_resize.setStyle("height", ""+height);
        canvas_size.setStyle("height", ""+height);
        canvas.setStyle("height", ""+height);
    }

    spt.pipeline.redraw_canvas();

}



/* scales the view to fit the entire group */
spt.pipeline.fit_to_canvas = function(group_name) {
    var nodes = null;
    if (typeof(group_name) == 'undefined') {
        nodes = spt.pipeline.get_all_nodes();
    }
    else {
        nodes = spt.pipeline.get_nodes_by_group(group_name);
    }

    if (nodes.length == 0) {
        var nodes = spt.pipeline.get_all_folders();
    }


    // fint the to left node
    var top = null;
    var left = null;
    var bottom = null;
    var right = null;
    for (var i = 0; i < nodes.length; i++) {
        if (nodes[i].getStyle("display") == "none") {
            continue;
        }

        var pos = spt.pipeline.get_position(nodes[i]);
        if (left == null || pos.x < left) {
            left = pos.x;
        }
        if (top == null || pos.y < top) {
            top = pos.y;
        }
        if (right == null || pos.x > right) {
            right = pos.x
        }
        if (bottom == null || pos.y > bottom) {
            bottom = pos.y
        }
    }

    var size = spt.pipeline.get_canvas_size();
    var hsize = right - left + 100;
    var hscale = size.x / hsize;
    var vsize = bottom - top + 40;
    var vscale = size.y / vsize;

    if (hscale < vscale) {
        scale = hscale;
    }
    else {
        scale = vscale;
    }

    scale = scale * 0.9;
    if (scale > 1.0) {
        scale = 1.0;
    }
    spt.pipeline.set_scale(scale);

    // zero position at the specified scale
    //var zero_pos_x = 100;
    //var zero_pos_y = 100;

    var zero_pos_x = size.x/2 - hsize/2 - 100;
    var zero_pos_y = size.y/2 - vsize/2;

    var dx = - left + zero_pos_x + 100;
    var dy = - top + zero_pos_y;
    spt.pipeline.move_all_nodes(dx, dy);
    spt.pipeline.move_all_folders(dx, dy);


    // handle screen node
    var screen_nodes = spt.pipeline.get_screen_nodes();
    screen_nodes.forEach( function(screen_node) {
        if (screen_node.move_by) {
            screen_node.move_by(dx, dy);
        }
    } );



}



/* scales the view to fit the node */
spt.pipeline.fit_to_node = function(node) {
    if (!node) return;

    var nodes = null;
    if (node.length > 0) {
        nodes = node;
    }
    else {
        nodes = [node];
    }

    /*
    var top = null;
    var left = null;
    var bottom = null;
    var right = null;
    for (var i = 0; i < nodes.length; i++) {
        var pos = spt.pipeline.get_position(nodes[i]);
        if (left == null || pos.x < left) {
            left = pos.x;
        }
        if (top == null || pos.y < top) {
            top = pos.y;
        }
        if (right == null || pos.x > right) {
            right = pos.x
        }
        if (bottom == null || pos.y > bottom) {
            bottom = pos.y
        }
    }
    */

    var node = nodes[0];

    var size = spt.pipeline.get_canvas_size();
    var positions = spt.pipeline.get_position(node);

    // hard coded info width (400)
    var hcenter = (size.x-400)/2;
    var vcenter = size.y/2;

    var dx = hcenter - positions.x - 50;
    var dy = vcenter - positions.y - 20;

    spt.pipeline.move_all_nodes(dx, dy);
    spt.pipeline.move_all_folders(dx, dy);


    // handle screen node
    var screen_nodes = spt.pipeline.get_screen_nodes();
    screen_nodes.forEach( function(screen_node) {
        if (screen_node.move_by) {
            screen_node.move_by(dx, dy);
        }
    } );



}



spt.pipeline.take_snapshot = function(container) {

    var el = spt.pipeline.top;
    if (el.isLoading) return;

    el.isLoading = true;

    var c = spt.pipeline.get_canvas();
    spt.pipeline.fit_to_canvas();
    var scale = spt.pipeline.get_scale();

    if (!container) {
        var container = el.getElement(".spt_pipeline_snapshot");
    }
    container.innerHTML = "";

    var size = el.getSize();
    container.size = size;


    var nodes = spt.pipeline.get_all_nodes();
    var first_node = nodes[0]
    var first_pos = first_node.getPosition(spt.pipeline.top);
    container.pos = first_pos;


    html2canvas(el)
        .then(  canvas => {
            //document.body.appendChild(canvas);
            container.appendChild(canvas);

            var size = spt.pipeline.get_canvas_size();
            var scale = size.x / 300;
            var width = 300;
            var height = size.y / scale;
            canvas.setStyle("width", width);
            canvas.setStyle("height", height);

            spt.pipeline.match_snapshot();
            el.isLoading = false;

        });

    container.scale = spt.pipeline.get_scale();
    return container;

}


spt.pipeline.match_snapshot = function(container) {
    var top = spt.pipeline.top;

    if (!container) {
        container = top.getElement(".spt_pipeline_snapshot");
    }
    if (!container) {
        return;
    }
    var nodes = spt.pipeline.get_all_nodes();
    if (!nodes || nodes.length == 0) {
        return;
    }


    var outline = container.getParent().getElement(".spt_outline");

    var container_size = container.getSize();
    var full_scale = container.scale;
    var full_pos = container.pos;
    var full_size = container.size;

    if (!full_scale || !full_pos || !full_size) {
        return;
    }

    var cur_scale = spt.pipeline.get_scale();
    var container_width = container_size.x;
    var container_height = container_size.y;

    var ratio = full_scale / cur_scale;

    var width = container_width * ratio;
    var height = container_height * ratio;

    outline.setStyle("width", width)
    outline.setStyle("height", height)

    var center = {x: full_size.x/2, y: full_size.y/2};

    var first_node = nodes[0]
    var first_pos = first_node.getPosition(spt.pipeline.top);

    var left_pos = (full_pos.x-first_pos.x) * (container_width/full_size.x) * ratio;
    var top_pos =  (full_pos.y-first_pos.y) * (container_height/full_size.y) * ratio;

    var left_pos = center.x * (1 - ratio)
    var left_translate = (first_pos.x - (full_pos.x - center.x)/ratio - center.x)*ratio;
    left_pos -= left_translate;
    left_pos = left_pos * (container_width/full_size.x)

    var top_pos = center.y * (1 - ratio)
    var top_translate = (first_pos.y - (full_pos.y - center.y)/ratio - center.y)*ratio;
    top_pos -= top_translate;
    top_pos = top_pos * (container_height/full_size.y)

    outline.setStyle("left", left_pos);
    outline.setStyle("top", top_pos);
}


spt.pipeline.clear_snapshot = function(container) {
    var top = spt.pipeline.top;

    if (!container) {
        container = top.getElement(".spt_pipeline_snapshot");
    }

    if (!container) {
        var container = el.getElement(".spt_pipeline_snapshot");
    }
    container.innerHTML = "";

}



spt.pipeline.last_mouse_pos = null;
spt.pipeline.resize_drag_setup = function(evt, bvr, mouse_411) {
    spt.pipeline.init(bvr);

    spt.pipeline.last_mouse_pos = spt.pipeline.get_mouse_position(mouse_411);
}

spt.pipeline.resize_drag_motion = function(evt, bvr, mouse_411) {
    var top = spt.pipeline.top;

    var mouse_pos = spt.pipeline.get_mouse_position(mouse_411);
    var dx = mouse_pos.x - spt.pipeline.last_mouse_pos.x;
    var dy = mouse_pos.y - spt.pipeline.last_mouse_pos.y;

    var canvas = spt.pipeline.get_canvas();
    var width = canvas.getStyle("width");
    width = parseInt( width.replace("px", "") );
    width += dx;
    if (width < 600) {
        width = 600;
    }

    var height = canvas.getStyle("height");
    height = parseInt( height.replace("px", "") );
    height += dy;

    outer = top.getElement(".spt_pipeline_resize")
    outer.setStyle("width", ""+width);
    outer.setStyle("height", ""+height);

    var paint = spt.pipeline.get_paint();
    outer = top.getElement(".spt_pipeline_resize")
    paint.setAttribute("width", ""+width);
    paint.setAttribute("height", ""+height);
    //paint.setStyle("margin-top", "" + (-height));
    canvas.setStyle("width", ""+width);
    canvas.setStyle("height", ""+height);


    spt.pipeline.redraw_canvas();
    spt.pipeline.last_mouse_pos = mouse_pos;
}


spt.pipeline.redraw_canvas = function() {
    // clear canvas
    var canvas = spt.pipeline.get_canvas();
    var ctx = spt.pipeline.get_ctx();
    width = canvas.getStyle("width");
    width = parseInt( width.replace("px"), "" );
    height = canvas.getStyle("height");
    height = parseInt( height.replace("px"), "" );

    ctx.clearRect(0,0,width,height);

    spt.pipeline.draw_background();

    var connectors = canvas.connectors;

    for (var i=0; i<connectors.length; i++) {
        var connector = connectors[i];
        connector.draw();
    }
}


spt.pipeline.get_point_region = function(pos, rect) {

    // 3 4 5
    // 2 0 6
    // 1 8 7

    var width = rect.x;
    var height = rect.y;

    var x = pos.x;
    var y = pos.y;

    var region = null;

    if (x < 0) {
        region = 2;
        if (y < 0) {
            region = 1;
        }
        else if (y > height ) {
            region = 3;
        }

    }
    else if (x > width) {
        region = 6;
        if (y < 0) {
            region = 7;
        }
        else if (y > height ) {
            region = 5;
        }

    }
    else {
        region = 0
        if (y < 0) {
            region = 8
        }
        else if (y > height) {
            region = 4;
        }
    }

    return region;

}




// Connector class
spt.pipeline.Connector = function(from_node, to_node) {

    this.from_node = from_node;
    this.to_node = to_node;
    this.color = '#111';
    this.attrs = {};
    this.type = "connector";
    this.line_mode = null;
    this.panel;
    this.is_selected = false;

    this.draw = function() {
        if (this.from_node == null || this.to_node == null) return;

        var draw_attr = this.is_selected;

        var data = spt.pipeline.get_data();
        if (data.line_mode == 'line') {
            this.draw_line(draw_attr);
        }
        else {
            this.draw_spline(draw_attr);
        }
    }


    this.draw_spline = function(show_attr) {
        var canvas = spt.pipeline.get_canvas();
        var from_pos = spt.pipeline.get_position(this.from_node);
        var to_pos = spt.pipeline.get_position(this.to_node);

        var from_size = spt.pipeline.get_size(this.from_node);
        var to_size = spt.pipeline.get_size(this.to_node);

        var scale = spt.pipeline.get_scale();
        var translate = spt.pipeline.get_translate();

        var from_width = from_size.x;
        var from_height = from_size.y;
        var to_width = to_size.x;
        var to_height = to_size.y;

        // HACKY offset for condition nodes.  This is because rotate square does
        // not give the widget of the corners
        if (spt.pipeline.get_node_type(this.from_node) == "condition") {
            from_pos.x = from_pos.x + from_width*0.12;
        }
        if (spt.pipeline.get_node_type(this.to_node) == "condition") {
            to_pos.x = to_pos.x - to_width*0.12;
        }


        // offset by the size
        var unscaled_from_pos = {x: from_pos.x + from_width, y: from_pos.y + from_height/2 };
        var unscaled_to_pos = {x: to_pos.x, y: to_pos.y + to_height/2 };

        // offset translate
        unscaled_from_pos.x += translate.x;
        unscaled_from_pos.y += translate.y;
        unscaled_to_pos.x += translate.x
        unscaled_to_pos.y += translate.y

        // put a scale transformation on it
        // moz transform scales from the center, so have to move
        // the curves back
        var size = spt.pipeline.get_canvas_size();
        var width = size.x;
        var height = size.y;

        var from_pos = {
            x: (unscaled_from_pos.x - width/2) * scale + width/2,
            y: (unscaled_from_pos.y - height/2) * scale + height/2,
        }



        var to_pos = {
            x: (unscaled_to_pos.x - width/2) * scale + width/2,
            y: (unscaled_to_pos.y - height/2) * scale + height/2,
        }


        // don't bother drawing if it is outside the drawing site
        var from_region = spt.pipeline.get_point_region(from_pos, size);
        var to_region = spt.pipeline.get_point_region(to_pos, size);

        var draw = false;
        if (from_region == 0 || to_region == 0) {
            draw = true;
        }
        else if (from_region == 4 && to_region == 8) {
            draw = true;
        }
        else if (from_region == 8 && to_region == 4) {
            draw = true;
        }
        else if (from_region == 2 && to_region == 6) {
            draw = true;
        }
        else if (from_region == 6 && to_region == 2) {
            draw = true;
        }


        if (!draw) return;


/*
        // Use more sophisticated algorithm above
        from_pos_inside = false;
        to_pos_inside = false;
        if (from_pos.x > 0 && from_pos.y > 0 && from_pos.x < width && from_pos.y < height) {
            from_pos_inside = true;
        }
        if (to_pos.x > 0 && to_pos.y > 0 && to_pos.x < width && to_pos.y < height) {
            to_pos_inside = true;
        }

        if (! from_pos_inside &&  ! to_pos_inside) {
            return;
        }
*/


        var data = spt.pipeline.get_data();

        var line_mode = this.line_mode;
        if (!line_mode) {
            line_mode = data.line_mode;
        }


        if (line_mode == 'curved_edge') {
            spt.pipeline.draw_curved_edge_line(from_pos, to_pos, this.color);
        } else {
            spt.pipeline.draw_connector(from_pos, to_pos, this.color);
        }


        var data = spt.pipeline.get_data();
        var pipeline_type = data.type;
        var connector_panel_data = data.connector_panel_data;

        if (connector_panel_data[pipeline_type]) {
            if (!this.panel) {
                var top = spt.pipeline.top;
                var template_container = top.getElement(".spt_pipeline_template");
		var template = template_container.getElement(".spt_connector_panel_template");
                var el = spt.behavior.clone(template);
                el.removeClass("spt_connector_panel_template");
                el.addClass("spt_connector_data");

                //var from_node = this.from_node.getAttribute("spt_element_name");
                //var to_node = this.to_node.getAttribute("spt_element_name");

                var canvas = spt.pipeline.get_canvas();
                canvas.appendChild(el);

                this.panel = el;
            }
            var y = (unscaled_from_pos.y + unscaled_to_pos.y)/2;
            var dx = (unscaled_to_pos.x - unscaled_from_pos.x)/2;
            if (dx > 50) {
                dx = 50;
            }
            dx = dx - 12
            dy = -8
            spt.pipeline.move_to(this.panel, unscaled_from_pos.x+dx, y+dy);

        }

        var show_output_attr = true;

        if (show_attr) {
            var node = this.from_node;
            attrs = this.get_attrs();
            if (attrs) {
                var scale = spt.pipeline.get_scale();

                var from_attr = attrs['from_attr'] ? attrs['from_attr'] : 'output';
                var to_attr = attrs['to_attr'] ? attrs['to_attr'] : 'input';

                var from_dx =  5 * scale;
                var from_dy = -15 * scale;
                var to_dx = -30 * scale;
                var to_dy = -15 * scale;


                spt.pipeline.draw_text(from_attr, from_pos.x + from_dx, from_pos.y + from_dy);
                spt.pipeline.draw_text(to_attr, to_pos.x + to_dx, to_pos.y + to_dy);
            }
        }

        else if (show_output_attr) {
            var node = this.from_node;
            attrs = this.get_attrs();
            if (attrs) {
                var scale = spt.pipeline.get_scale();

                var from_attr = attrs['from_attr'] ? attrs['from_attr'] : 'output';
                if (from_attr != 'output') {
                    var to_attr = attrs['to_attr'] ? attrs['to_attr'] : 'input';

                    var from_dx =  (to_pos.x - from_pos.x) / 2 + 5*scale;
                    var from_dy =  (to_pos.y - from_pos.y) / 2 + 5*scale;

                    spt.pipeline.draw_text(from_attr, from_pos.x + from_dx, from_pos.y + from_dy);
                }
            }
        }





    }


    this.draw_line = function(show_column) {
        var canvas = spt.pipeline.get_canvas();
        var from_pos = spt.pipeline.get_position(this.from_node);
        var to_pos = spt.pipeline.get_position(this.to_node);

        var from_size = spt.pipeline.get_size(this.from_node);
        var to_size = spt.pipeline.get_size(this.to_node);

        var scale = spt.pipeline.get_scale();
        var translate = spt.pipeline.get_translate();
        var from_width = from_size.x;
        var from_height = from_size.y;
        var to_width = to_size.x;
        var to_height = to_size.y;

        // offset by the midpoint
        from_pos = {x: from_pos.x + from_width/2, y: from_pos.y + from_height/2 };
        to_pos = {x: to_pos.x + to_width/2, y: to_pos.y + to_height/2 };

        from_pos.x += translate.x;
        from_pos.y += translate.y;
        to_pos.x += translate.x;
        to_pos.y += translate.y;

        // put a scale transformation on it
        // moz transform scales from the center, so have to move
        // the curves back
        var size = spt.pipeline.get_canvas_size();
        width = size.x;
        height = size.y;

        from_pos = {
            x: (from_pos.x - width/2) * scale + width/2,
            y: (from_pos.y - height/2) * scale + height/2,
        }

        to_pos = {
            x: (to_pos.x - width/2) * scale + width/2,
            y: (to_pos.y - height/2) * scale + height/2,
        }

        spt.pipeline.draw_line(from_pos, to_pos, this.color);
        if (show_column) {
            var node = this.from_node;
            attrs = this.get_attrs();
            if (attrs) {
                var scale = spt.pipeline.get_scale();
                var delta_x =  (from_pos.x > to_pos.x) ? -10 : 10;
                delta_x *= scale;
                var delta_y = -35;
                delta_y *= scale;
                var from_col = attrs['from_col'] ? attrs['from_col'] : '- default -';
                var to_col = attrs['to_col'] ? attrs['to_col'] : '- default -';

                spt.pipeline.draw_text(from_col, from_pos.x + delta_x, from_pos.y + delta_y);
                spt.pipeline.draw_text(to_col, to_pos.x - delta_x, to_pos.y +delta_y);
            }
        }

    }


    this.select = function(color) {
        spt.pipeline.add_to_selected(this);
        if (!color) {
            color = "red";
        }
        this.set_color(color);
        this.is_selected = true;
    }

    this.unselect = function() {
        //spt.pipeline.add_to_selected(this);
        this.is_selected = false;
    }



    this.set_from_node = function(from_node) {
        this.from_node = from_node;
    }
    this.get_from_node = function() {
        return this.from_node;
    }
    this.set_to_node = function(to_node) {
        this.to_node = to_node;
    }
    this.get_to_node = function() {
        return this.to_node;
    }
    this.set_color = function(color) {
        this.color = color;
    }

    this.get_attr = function(name) {
        return this.attrs[name];
    }

    this.set_attr = function(name, value) {
        spt.named_events.fire_event('pipeline|connector|'+name, {
            src_el: this,
            options: {
                name: name,
                oldValue: this.attrs[name],
                value: value
            }
        });

        if (this.from_node) {
            let from_name = spt.pipeline.get_node_name(this.from_node);
            spt.named_events.fire_event('pipeline|connector|from|'+from_name+'|'+name, {
                src_el: this,
                options: {
                    name: name,
                    oldValue: this.attrs[name],
                    value: value
                }
            });
        }

        if (this.to_node) {
            let to_name = spt.pipeline.get_node_name(this.to_node);
            spt.named_events.fire_event('pipeline|connector|to|'+to_name+'|'+name, {
                src_el: this,
                options: {
                    name: name,
                    oldValue: this.attrs[name],
                    value: value
                }
            });
        }

        this.attrs[name] = value;
    }


    this.get_attrs = function() {
        return this.attrs;
    }

    /*if (!this.get_attr("overlap")) {
        this.set_attr("overlap", 100);
    }*/


}


// Group class
spt.pipeline.Group = function(name) {
    this.name = name;
    this.nodes = [];
    this.connectors = [];
    this.dangling_connectors = [];
    this.color = '#999';
    this.group_type = 'pipeline';
    this.node_type = 'process';

    this.add_node = function(node) {
        this.nodes.push(node);
        spt.pipeline.set_color(node, this.get_color());
        node.spt_group = this.name;
        node.spt_type = this.node_type;
    }

    this.remove_node = function(node) {
        node_name = node.getAttribute("spt_element_name");
        for (var i=0; i< this.nodes.length; i++) {
            if (node_name == this.nodes[i].getAttribute("spt_element_name")) {
                node.spt_group = "default"
                this.nodes.splice(i, 1);
                break;
            }
        }

        // remove any connections to this node
        var new_connectors  = [];
        for (var i = 0; i < this.connectors.length; i++) {
            var connector = this.connectors[i];
            var to_node = connector.get_to_node().spt_name;
            var from_node = connector.get_to_node().spt_name;
            if (to_node == node_name || from_node == node_name) {
                // do nothing
            }
            else {
                new_connectors.push(connector);
            }
        }
        this.connectors = new_connectors;
    }

    this.get_node = function(node_name) {
        for (var i=0; i< this.nodes.length; i++) {
            if (node_name == this.nodes[i].getAttribute("spt_element_name")) {
                return this.nodes[i];
            }
        }
    }


    this.get_name = function() {
        return this.name;
    }

    this.get_dangling_connectors = function() {
        return this.dangling_connectors;
    }
    this.add_dangling_connector = function(connector) {
        this.dangling_connectors.push(connector);
    }

    this.add_connector = function(connector) {
        this.connectors.push(connector);
    }


    this.remove_connector = function(connector) {
        for (var i = 0; i < this.connectors.length; i++) {
            if (connector == this.connectors[i]) {
                var item = this.connectors[i];
                this.connectors.splice(i, 1);
                break;
            }
        }
    }




    this.get_connectors = function() {
        return this.connectors;
    }
    this.get_nodes = function() {
        return this.nodes;
    }

    this.set_color = function(color) {
        // it is possible that color is undefined
        if (typeof(color) == 'undefined') {
            return;
        }
        this.color = color;

        var data = spt.pipeline.get_data();
        data.colors[this.get_name()] = color;


        // set all the nodes in this group to be this color
        for (var i = 0; i < this.nodes.length; i++) {
            spt.pipeline.set_color(this.nodes[i], color);
        }
    }

    this.get_color = function() {
        return this.color;
    }


    this.get_group_type = function() {
        return this.group_type;
    }
    this.set_group_type = function(group_type) {
        this.group_type = group_type;
    }

    this.get_node_type = function() {
        return this.node_type;
    }
    this.set_node_type = function(node_type) {
        this.node_type = node_type;
    }

    this.set_description = function(description) {
        this.description = description;

        var data = spt.pipeline.get_data();
        data.descriptions[this.get_name()] = description;
    }

    this.get_description = function() {
        return this.description;
    }

    this.get_data = function(name) {
        return this[name];
    }

    this.set_data = function(name, value) {
        this[name] = value;

        var data = spt.pipeline.get_data();
        if (data[name+"s"])
            data[name+"s"][this.get_name()] = value;
    }


}


// Importer
spt.pipeline.set_has_prefix = function(flag) {
    var data = spt.pipeline.get_data();
    data.has_prefix = flag;
}



spt.pipeline.import_xml = function(xml, code, color) {
    var xml_doc = spt.parse_xml(xml);

    var group = spt.pipeline.add_group(code);
    group.set_color(color);
    spt.pipeline.set_current_group(code);

    // add the nodes
    var xml_nodes = []
    process_nodes = xml_doc.getElementsByTagName("process");
    approval_nodes = xml_doc.getElementsByTagName("approval");
    for (var i = 0; i < approval_nodes.length; i++) {
        xml_nodes.push(approval_nodes[i]);
    }
    for (var i = 0; i < process_nodes.length; i++) {
        xml_nodes.push(process_nodes[i]);
    }

    spt.pipeline.import_nodes(code, xml_nodes);
    var xml_connects = xml_doc.getElementsByTagName("connect");
    spt.pipeline.load_connects(code, xml_connects);
}




spt.pipeline.import_pipeline = function(pipeline_code, color) {

    var server = TacticServerStub.get();
    results = server.eval("@SOBJECT(sthpw/pipeline['code','"+pipeline_code+"'])");
    var pipeline = results[0];
    if (!pipeline) {
        log.warning('Pipeline [' + pipeline_code + ']  does not exist');
        return;
    }

    // reset the scale
    spt.pipeline.set_scale(1);
    spt.pipeline.set_translate(0,0);


    // get all of the processes associated with this pipeline
    process_sobjs = server.eval("@SOBJECT(config/process['pipeline_code','"+pipeline_code+"'])");
    processes = {};
    for (var i = 0; i < process_sobjs.length; i++) {
        var process_sobj = process_sobjs[i];
        var name = process_sobj.process;
        var process_code = process_sobj.code;
        processes[name] = process_sobj;
    }

    // get all the triggers for the processes from the pipeline.
    var trigger_sobjs = server.eval("@SOBJECT(config/trigger['process', @GET(config/process['pipeline_code', '"+pipeline_code+"'].code)])")
    triggers = {}
    for (var i = 0; i < trigger_sobjs.length; i++) {
        var trigger_sobj = trigger_sobjs[i];
        var process_code = trigger_sobj.process;
        triggers[process_code] = trigger_sobj;
    }

    var pipeline_xml = pipeline.pipeline;
    var pipeline_stype = pipeline.search_type;
    var xml_doc = spt.parse_xml(pipeline_xml);
    var pipeline_name = pipeline.name;
    var pipeline_type = pipeline.type;
    if (typeOf(pipeline.data) == "string") {
        var pipeline_data = JSON.parse(pipeline.data) || {};
    }
    else {
        var pipeline_data = pipeline.data || {};
    }

    var node_index = pipeline_data.node_index || 0;

    // first check if the group already there
    var group = spt.pipeline.get_group(pipeline_code);
    if (group != null) {
        spt.alert("Group [" + pipeline_code + "] is already loaded." );
        return;
    }


    // add the group and set the color
    if (typeof(color) == 'undefined') {
        color = pipeline.color;
    }
    var group = spt.pipeline.add_group(pipeline_code);
    if (color == '' || color == null || typeof(color) == 'undefined') {
        color = pipeline.color;
    }
    if (color == '' || color == null || typeof(color) == 'undefined') {
        color = "#AAAAB0";
    }
    group.set_color(color);
    group.set_group_type("pipeline");
    group.set_node_type("process");
    group.set_data("node_index", node_index);

    spt.pipeline.set_current_group(pipeline_code);
    spt.pipeline.set_search_type(pipeline_code, pipeline_stype);

    var data = spt.pipeline.get_data();
    data.type = pipeline.type;
    data.project_code = pipeline.project_code;


    // add the nodes
    var xml_nodes = []
    process_nodes = xml_doc.getElementsByTagName("process");
    approval_nodes = xml_doc.getElementsByTagName("approval");
    for (var i = 0; i < approval_nodes.length; i++) {
        xml_nodes.push(approval_nodes[i]);
    }

    for (var i = 0; i < process_nodes.length; i++) {
        // add a process code
        var name = process_nodes[i].getAttribute("name");
        var process = processes[name];
        if (process) {
            process_nodes[i].setAttribute("process_code", process.code)
            var settings = process.workflow;
            if (!settings) {
                settings = {};
            } else if (typeof(settings) == "string") {
                settings = JSON.parse(settings);
            }

            // Add the triggers to settings. Note this is necessary only for version 1.
            // Version 2 will have settings.version set to 2.
            if (!settings.version) {
                var trigger = triggers[process.code];
                if (trigger != null) {
                    if (trigger.class_name) settings['command'] = { 'on_action_class' : trigger.class_name, 'execute_mode': trigger.mode, 'action':'command' }
                    if (trigger.script_path) {
                        settings['script_path_folder'] = trigger.script_path;
                        settings['script_path_title'] = process.code;
                        settings['action'] = 'script_path';

                        if (trigger.mode) settings['execute_mode'] = trigger.mode;
                    }
                }
            }


            // add the process name
            if (process.subpipeline_code) settings['subpipeline_code'] = process.subpipeline_code;
            if (process.process) settings['process'] = process.process;
            process_nodes[i].setAttribute("settings", JSON.stringify(settings));
        }

        xml_nodes.push(process_nodes[i]);

    }



    if (xml_nodes.length == 0) {
        spt.pipeline.add_folder(pipeline_code, color, pipeline_name);
    }
    else {
        spt.pipeline.import_nodes(pipeline_code, xml_nodes, 'node');
        var xml_connects = xml_doc.getElementsByTagName("connect");
        spt.pipeline.load_connects(pipeline_code, xml_connects);
    }

    container = spt.pipeline.top;
    let size = container.getSize();
    spt.pipeline.set_size(size.x, size.y);
    container.last_size = size;
    spt.pipeline.fit_to_canvas(pipeline_code);

    if (pipeline_stype == "sthpw/task") {
        spt.pipeline.set_task_color();
    }

    spt.pipeline.redraw_canvas();

    spt.pipeline.clear_snapshot();

    spt.named_events.fire_event('pipeline|save', {});
}



spt.pipeline.import_schema = function(schema_code, color) {

    var server = TacticServerStub.get();
    results = server.eval("@SOBJECT(sthpw/schema['code','"+schema_code+"'])");

    var schema_xml;
    if (results.length == 0) {
        schema_xml = "<schema/>";
    }
    else {
        var schema = results[0];
        schema_xml = schema.schema;
    }
    var xml_doc = spt.parse_xml(schema_xml);


    // first check if the group already there
    var group = spt.pipeline.get_group(schema_code);
    if (group != null) {
        spt.alert("Group [" + schema_code + "] already loaded" );
        return;
    }

    // add the group and set the color
    if (typeof(color) == 'undefined') {
        //color = schema.color;
        color = "#999";
    }
    var group = spt.pipeline.add_group(schema_code);
    if (color == '' || color == null || typeof(color) == 'undefined') {
        color = schema.color;
    }
    if (color == '' || color == null || typeof(color) == 'undefined') {
        color = "#999";
    }
    // later on , each SType node can have its own color
    group.set_color(color);
    group.set_group_type("schema");
    group.set_node_type("search_type");

    spt.pipeline.set_current_group(schema_code);

    // add the nodes
    var xml_nodes = xml_doc.getElementsByTagName("search_type");
    spt.pipeline.import_nodes(schema_code, xml_nodes);
    var xml_connects = xml_doc.getElementsByTagName("connect");
    spt.pipeline.load_connects(schema_code, xml_connects);

    spt.pipeline.redraw_canvas();

}


//if undo_flag is true, add to undo cmd
spt.pipeline.set_node_value = function(node, values, undo_flag) {

	var workflow = node.workflow;
    if (!node.workflow) {
        workflow = node.workflow = {};
    }
    orig_values = []

	for(var i = 0; i < values.length; i++){
		var name = values[i].name
		var value = values[i].value
		var kwargs = values[i].kwargs
	    var orig_value = workflow[name];
	    orig_values.push({
	    	name: name,
            value: orig_value,
            kwargs: kwargs
	    })

	}

	var cmd = new spt.pipeline.SetNodeValueCmd(node, values, orig_values);
    if(!undo_flag){
    	spt.command.add_to_undo(cmd);
    }
    return cmd.execute();
}



spt.pipeline.SetNodeValueCmd = function(node, values, orig_values) {
	this.node = node
	this.execute = function(){
		return this.redo();
	}

	this.redo = function(){
		var workflow = node.workflow;
		if (!node.workflow) {
			workflow = node.workflow = {};
		}


		for(var i = 0; i < values.length; i++){
			var name = values[i].name
			var value = values[i].value
			var kwargs = values[i].kwargs || {}
			workflow[name] = value;

			// node.properties goes into xml, code is redundant but it works for now
			spt.pipeline.set_node_property(node, "settings", workflow);

			var class_name = kwargs.class_name;
			if (class_name) {
				var update_el = node.getElement("."+class_name);
				if (update_el) {
					if (update_el.update) {
						update_el.update(value);
					}
					else {
						update_el.innerHTML = value;
					}
				}
			}

		}

		return node;

	}


	this.undo = function(){
		var workflow = node.workflow;
		if (!node.workflow) {
			workflow = node.workflow = {};
		}


		for(var i = 0; i < orig_values.length; i++){
			var name = orig_values[i].name
			var value = orig_values[i].value
			var kwargs = orig_values[i].kwargs

			workflow[name] = value;

			// node.properties goes into xml, code is redundant but it works for now
			spt.pipeline.set_node_property(node, "settings", workflow);

			var class_name = kwargs.class_name;
			if (class_name) {
				var update_el = node.getElement("."+class_name);
				if (update_el) {
					if (update_el.update) {
						update_el.update(value);
					}
					else {
						update_el.innerHTML = value;
					}
				}
			}

		}

		return node;

	}
}


spt.pipeline.get_node_value = function(node, name) {
    var workflow = node.workflow;
    if (!workflow) {
        return null;
    }

    return workflow[name];
}

spt.pipeline.get_node_values = function(node) {
    return node.workflow;
}


spt.pipeline.import_nodes = function(group, xml_nodes) {
    // find the left most and top most position
    var left = null;
    var top = null;
    for (var i=0; i<xml_nodes.length; i++) {
        var name = xml_nodes[i].getAttribute("name");
        var xpos = xml_nodes[i].getAttribute("xpos");
        var ypos = xml_nodes[i].getAttribute("ypos");
        xpos = parseInt(xpos);
        ypos = parseInt(ypos);

        if (left == null || xpos < left) {
            left = xpos;
        }
        if (top == null || ypos < top) {
            top = ypos;
        }
    }

    // randomize somewhat so that user can see that a new pipeline was loaded
    if (!top) {
        top = 90 + parseInt(Math.random()*20);
    }
    if (!left) {
        left = 90 + parseInt(Math.random()*20);
    }

    // find out how many groups there are
    var num_groups = spt.pipeline.get_num_groups();

    // put in an offset depending on the number of groups already loaded
    //var offset_top = 100 + (num_groups-1) * 50;
    var offset_top = 100;
    var offset_left = 100;


    // actually add the nodes
    for (var i=0; i<xml_nodes.length; i++) {
        var name = xml_nodes[i].getAttribute("name");
        var xpos = xml_nodes[i].getAttribute("xpos");
        var ypos = xml_nodes[i].getAttribute("ypos");
        var color = xml_nodes[i].getAttribute("color");
        if (!xpos || xpos == "0") {
            xpos = offset_left + 150*i;
        }
        if (!ypos || ypos == "0") {
            ypos = offset_top + 50*i;
        }

        xpos = parseInt(xpos) - left + offset_left;
        ypos = parseInt(ypos) - top + offset_top;


        var node_type = xml_nodes[i].getAttribute("type");
        if (node_type == "auto") {
            node_type = "action";
        }
        else if (node_type == "node") {
            node_type = "manual";
        }



        var options = {
            group: group,
            select_node: false,
            node_type: node_type,
            new: false,
            is_loading: true,
        }

        // split the name
        //var name_parts = name.split("/");
        //name = name_parts[name_parts.length-1];

        var node = spt.pipeline.add_node(name, xpos, ypos, options);

        if (color) {
            spt.pipeline.set_color(node, color);
        }


        // add the attributes
        var attributes = xml_nodes[i].attributes;
        for (var j = 0; j < attributes.length; j++) {
            var name = attributes[j].name;
            if (name == "node") continue;
            var value = attributes[j].value;
            if (name == "type" && value == "node") {
                value = "manual";
            }

            if (name == "settings" && typeOf(value) == "string") {
                value = JSON.parse(value);
            }
            node.properties[name] = value;
        }


        // remember the settings value in spt_settings in case of undo
        var settings = xml_nodes[i].getAttribute("settings");
        if (settings) {
            settings_json = JSON.parse(settings);
            if (node.update_node_settings) {
                node.update_node_settings(settings_json);
                node.setAttribute("spt_settings", settings)
            }
        }

        else {

            // hacky refressh
            var process_code = xml_nodes[i].getAttribute("process_code")
            if (process_code) {
                var el = node.getElement(".spt_panel")
                if (el) {
                    spt.panel.refresh_element(el, {process_code: process_code});
                }
            }
        }
    }
}





spt.pipeline.load_connects = function(group_name, xml_connects) {

    var group = spt.pipeline.get_group(group_name);


    // add the connectors
    for (var i=0; i<xml_connects.length; i++) {
        var to = xml_connects[i].getAttribute("to");
        var from = xml_connects[i].getAttribute("from");

        //var to_parts = to.split("/");
        //to = to_parts[to_parts.length-1];
        //var from_parts = from.split("/");
        //from = from_parts[from_parts.length-1];

        //var to_node = spt.pipeline.get_node_by_name(to);
        //var from_node = spt.pipeline.get_node_by_name(from);
        var to_node = group.get_node(to);
        var from_node = group.get_node(from);
        var is_dangling = false;


        if (!from_node || !to_node) {
            // dangling one
            var connector = new spt.pipeline.Connector();
            if (to_node)
                connector.set_to_node(to_node);
            else
                connector.set_from_node(from_node);
            is_dangling = true;
        }
        else {
            var connector = spt.pipeline.add_connector();
            connector.set_from_node(from_node);
            connector.set_to_node(to_node);

            connector.draw();

        }

        // add the attributes
        var attributes = xml_connects[i].attributes;

        for (var j = 0; j < attributes.length; j++) {
            var name = attributes[j].name;
            var value = attributes[j].value;
            connector.set_attr( name, value );
        }

        if (is_dangling)
            group.add_dangling_connector(connector);
        else
            group.add_connector(connector);

        // Load / Update connector panel
        var el = connector.panel;
        if (el) {
            if (el.update_settings) {
                el.update_settings({connector: connector});
            } else {
	        var data = spt.pipeline.get_data();
	        var pipeline_type = data.type;
	        var connector_panel_data = data.connector_panel_data;
	        if (connector_panel_data[pipeline_type]) {
                    var class_name = connector_panel_data[pipeline_type];
                    var kwargs = {
                        'from_node': from,
                        'to_node': to,
                        'pipeline_code': group_name,
                        'overlap': connector.get_attr("overlap")
                    };
                    spt.panel.load(el, class_name, kwargs, {}, {show_loading: false});
	        }
            }
        }

    }

}



spt.pipeline.load_triggers = function() {
    var group_name = spt.pipeline.get_current_group();
    var nodes = spt.pipeline.get_nodes_by_group(group_name);

    var server = TacticServerStub.get();
    var pipeline = server.eval("@SOBJECT(sthpw/pipeline['code','"+group_name+"'])", {single: true});
    if (!pipeline) {
        log.warning('Pipeline [' + pipeline_code + ']  does not exist');
        return;
    }

    var length = nodes.length;

    // get all of the triggers with this pipeline_code
    var node_names = [];
    for (var i = 0; i < length; i++) {
        var node = nodes[i];
        var node_name = node.getAttribute("spt_element_name");

        var trigger = server.eval("@SOBJECT(config/trigger['process','"+node_name+"'])", {single: true});

        if (trigger == null) {
            continue;
        }

        var size = node.getSize();
        var pos = spt.pipeline.get_position(node);
        var options = {
            'node_type': 'trigger'
        }
        var trigger = spt.pipeline.add_node(i+Math.random()*10000+"", pos.x+size.x+20, pos.y-50, options);
        var connector = spt.pipeline.add_connector();
        connector.set_color("#BBB");
        connector.set_from_node(node);
        connector.set_to_node(trigger);
        connector.draw();

        trigger.spt_connector = connector;
        trigger.spt_from_node = node;

    }

}



spt.pipeline.set_status_color = function(search_key) {

    var server = TacticServerStub.get();
    var sobject = server.get_by_search_key(search_key);

    var cmd = "tactic.ui.tools.PipelineGetStatusColorsCmd";
    var kwargs = {
        search_key: search_key
    }
    server.p_execute_cmd(cmd, kwargs)
    .then( function(ret_val) {
        var info = ret_val.info.process_colors;
        var search_keys = ret_val.info.task_search_keys;
        var group_name = spt.pipeline.get_current_group();
        var nodes = spt.pipeline.get_nodes_by_group(group_name);

        var default_color = 'rgb(128,128,128)';

        for (var i = 0; i < nodes.length; i++) {
            var node = nodes[i];
            var process = spt.pipeline.get_node_name(node);

            var color = info[process]
            if (!color) {
                color = default_color;
                node.setStyle("opacity", "0.5");
            }
            spt.pipeline.set_color(node, color);


            spt.update.add( node, {
                search_key: search_keys[process],
                return: "sobject",
                cbjs_action: `
                    var server = TacticServerStub.get();
                    var status_colors = server.get_task_status_colors().task;
                    var status = bvr.value.status;
                    var color = status_colors[status];
                    spt.pipeline.set_color(bvr.src_el, color);
                `
            } )
        }

    } );

    return;


/*
    // get all of the tass for this sobject
    var tasks = server.query("sthpw/task", {parent_key: search_key});
    var tasks_dict = {};
    for (var i = 0; i < tasks.length; i++) {
        var process = tasks[i].process;
        tasks_dict[process] = tasks[i];
    }

    var pipeline_code = sobject.pipeline_code;

    var group_name = spt.pipeline.get_current_group();
    if (group_name != pipeline_code) {
        spt.pipeline.clear_canvas();
        spt.pipeline.import_pipeline(pipeline_code);
    }

    var nodes = spt.pipeline.get_nodes_by_group(group_name);

    var colors = server.get_task_status_colors();
    var default_color = 'rgb(128,128,128)';

    var length = nodes.length;
    // get all of the triggers with this pipeline_code
    for (var i = 0; i < length; i++) {
        var node = nodes[i];
        var process = spt.pipeline.get_node_name(node);

        var task = tasks_dict[process];
        if (!task) {
            node.setStyle("opacity", "0.5");
            spt.pipeline.set_color(node, default_color);
            continue;
        }

        var status = task.status;
        var task_pipeline = task.pipeline_code;

        var color = null;
        var pipeline_colors = colors[task_pipeline];
        if (pipeline_colors) {
            color = pipeline_colors[status];
        }
        if (!color) {
            color = default_color;
        }
        spt.pipeline.set_color(node, color);
    }
*/
}



spt.pipeline.set_task_color = function(group_name) {
    if (!group_name) {
        group_name = spt.pipeline.get_current_group();
    }
    var server = TacticServerStub.get();
    var colors = server.get_task_status_colors();
    var group_colors = colors[group_name];
    if (!group_colors)
        group_colors = colors['task'];

    var nodes = spt.pipeline.get_nodes_by_group(group_name);
    for (var i = 0; i < nodes.length; i++) {
        var node = nodes[i];
        var process = spt.pipeline.get_node_name(node);

        var color = group_colors[process];
        if (color) {
            spt.pipeline.set_color(node, color);
        }
    }
}



// Export group
spt.pipeline.export_group = function(group_name) {
    var data = spt.pipeline.get_data();
    var canvas = spt.pipeline.get_canvas();

    var group = spt.pipeline.get_group(group_name);
    if (group == null) {
        var xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
        return xml;
    }

    var group_type = group.get_group_type();

    var nodes;
    var connectors;
    var dangling_connectors = [];

    if (typeof(group_name) == 'undefined') {
        nodes = spt.pipeline.get_all_nodes(group_name);
        connectors = canvas.connectors;

    }
    else {
        nodes = spt.pipeline.get_nodes_by_group(group_name);
        connectors = group.get_connectors();
        dangling_connectors = group.get_dangling_connectors();

    }

    // copy the array and sort it
    var nodes_array = []
    for (var i = 0; i < nodes.length; i++) {
        nodes_array.push(nodes[i]);
    }

    var sort_connector_func = function(a,b) {
        if (!a.get_from_node() || !b.get_from_node())
            return -1
        var a = a.get_from_node().spt_name;
        var b = b.get_from_node().spt_name;
        return a < b ? -1 : a > b ? 1 : 0;
    }
    var sortfunc = null;

    if (group_type == 'schema') {
        sortfunc = function(a,b) {
        var a = spt.pipeline.get_full_node_name(a, group_name);
        var b = spt.pipeline.get_full_node_name(b, group_name);
        return a < b ? -1 : a > b ? 1 : 0;
        }
    }
    else {
        sortfunc = function(a,b) {
        var pos_a = spt.pipeline.get_position(a);
        var pos_b = spt.pipeline.get_position(b);
        return pos_a.x - pos_b.x;
        }
    }

    dangling_connectors.sort(sort_connector_func);
    connectors.sort(sort_connector_func);
    nodes_array.sort(sortfunc);
    nodes = nodes_array;


    // first go through the nodes to find the left most and top
    var left = null;
    var top = null;
    for (var i = 0; i < nodes.length; i++) {
        var node = nodes[i];

        var pos = spt.pipeline.get_position(node);

        if (left == null || pos.x < left) {
            left = pos.x;
        }
        if (top == null || pos.y < top) {
            top = pos.y;
        }

    }

    var name_dict = {};
    var xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
    xml += '<'+group_type+'>\n';

    for (var i = 0; i < nodes.length; i++) {
        var node = nodes[i];
        var name = spt.pipeline.get_full_node_name(node, group_name);

        if (name_dict[name]) {
            throw("duplicated node name " + name + " found. Please clean up first and save again.")
            return;
        }
        else {
            name_dict[name] = true;
        }

        var tag_type = node.spt_type;
        var node_type = node.spt_node_type;

        var pos = spt.pipeline.get_position(node);
        pos = { x: pos.x-left+100, y: pos.y-top+100 };

        name = name.replace(/&/g, "&amp;amp;");

        xml += '  <'+tag_type+' name="'+name+'" type="'+node_type+'" xpos="'+Math.round(pos.x)+'" ypos="'+Math.round(pos.y)+'"';

        var properties = node.properties;
        for (var key in properties) {

            if (!properties.hasOwnProperty(key))
                continue;
            if (['name', 'xpos', 'ypos', 'type', 'names', 'namedItem', 'item', 'kwargs', 'node'].contains(key)) {
                continue;
            }

            if (spt.pipeline.get_node_types().contains(key)) {
                continue;
            }

            var value = properties[key];
            if (typeof value == "string") {
                value = value.replace(/&/g, "&amp;amp;");
                value = value.replace(/</g, "&amp;lt;");
                value = value.replace(/>/g, "&amp;gt;");
                value = value.replace(/'/g, "&amp;apos;");
            }
            if (key == "settings" && value) {

                // DEPRECATED: ignoring settings
                // Settings are now sent separately
                continue;

                settings_str = JSON.stringify(value);
                xml += " "+key+"='"+settings_str+"'";

            }
            else {
                if (value == '') {
                    continue;
                }
                xml += ' '+key+'="'+value+'"';
            }
        }
        xml += '/>\n';
    }

    // export the connectors
    for (var i = 0; i < connectors.length; i++) {
        var connector = connectors[i];

        var from_node_name = connector.get_from_node().spt_name;
        var to_node_name = connector.get_to_node().spt_name;

        if (data.has_prefix && from_node_name.indexOf("/") == -1) {
            var prefix = node.getAttribute("spt_prefix");
            if (!prefix) {
                prefix = group_name;
            }
            from_node_name = prefix + "/" + from_node_name;
        }
        if (data.has_prefix && to_node_name.indexOf("/") == -1) {
            var prefix = node.getAttribute("spt_prefix");
            if (!prefix) {
                prefix = group_name;
            }
            to_node_name = prefix + "/" + to_node_name;
        }

        xml += '  <connect from="'+from_node_name+'" to="'+to_node_name+'"';

        var attrs = connector.get_attrs();
        if (group_type == 'schema' && !('relationship' in attrs) ) {
            msg = 'Connection from [' + from_node_name + '] to [' + to_node_name + '] does not have a saved relationship. Please bring up the Connection dialog and click OK first.';
            throw(msg);
        }
        for (var key in attrs) {
            
            
            if (["from", "to", "from_node", "to_node"].indexOf(key) > -1) continue;
            
            xml += ' '+key+'="'+attrs[key]+'"';
        }


        xml += '/>\n';
    }


    for (var i = 0; i < dangling_connectors.length; i++) {
        xml += '  <connect';

        var attrs = dangling_connectors[i].get_attrs();
        for (var key in attrs) {
            xml += ' '+key+'="'+attrs[key]+'"';
        }
        xml += '/>\n';
    }

    xml += '</'+group_type+'>\n';

    return xml;

}

spt.pipeline.get_connector_by_nodes = function(from_name, to_name) {
    var pipeline_code = spt.pipeline.get_current_group();
    var group = spt.pipeline.get_group(pipeline_code);
    var connectors = group.get_connectors();

    var connector = null;

    for (var i = 0; i < connectors.length; i++) {
        from_node = connectors[i].get_from_node();
        to_node = connectors[i].get_to_node();

        if (   (from_node.spt_name == from_name) &&
               (to_node.spt_name == to_name)     ) {

            connector = connectors[i];
            break;
       }
    }

    return connector;
}


spt.pipeline.get_connectors_from_node = function(from_name) {
    var pipeline_code = spt.pipeline.get_current_group();
    var group = spt.pipeline.get_group(pipeline_code);
    var connectors = group.get_connectors();

    var result = [];

    for (var i = 0; i < connectors.length; i++) {
        from_node = connectors[i].get_from_node();

        if (from_node.spt_name == from_name) {
            result.push(connectors[i]);
       }
    }

    return result;
}

spt.pipeline.get_connectors_to_node = function(to_name) {
    var pipeline_code = spt.pipeline.get_current_group();
    var group = spt.pipeline.get_group(pipeline_code);
    var connectors = group.get_connectors();

    var result = [];

    for (var i = 0; i < connectors.length; i++) {
        to_node = connectors[i].get_to_node();

        if (to_node.spt_name == to_name) {
            result.push(connectors[i]);
       }
    }

    return result;
}

    '''


__all__.append("PipelineGetInfoCmd")
class PipelineGetInfoCmd(Command):

    def execute(self):
        pipeline_code = self.kwargs.get("pipeline_code")
        node_name = self.kwargs.get("node_name")

        pipeline = Search.eval("@SOBJECT(sthpw/pipeline['code','"+pipeline_code+"'])", {single: true});
        self.info['pipeline'] = pipeline

        expr = "@SOBJECT(config/process['pipeline_code','"+pipeline_code+"']['process','"+node_name+"'])";
        process = Search.eval(expr, {single: true});
        self.info['process'] = process




__all__.append("PipelineGetStatusColorsCmd")
class PipelineGetStatusColorsCmd(Command):

    def execute(self):

        search_key = self.kwargs.get("search_key")

        sobject = Search.get_by_search_key(search_key)

        # get all of the tass for this sobject
        tasks = Task.get_by_sobject(sobject)
        task_search_keys = {}

        tasks_dict = {}
        for task in tasks:
            process = task.get_value("process")
            tasks_dict[process] = task
            task_search_key = task.get_search_key()
            task_search_keys[process] = (task_search_key)

        pipeline_code = sobject.get("pipeline_code")
        pipeline = Pipeline.get_by_sobject(sobject)
        process_names = pipeline.get_process_names()

        colors =  Task.get_status_colors()
        colors = colors.get("task")

        default_color = 'rgb(128,128,128)'
        default_color = ""

        process_colors = {}

        for process in process_names:
            task = tasks_dict.get(process)

            if not task:

                # check the message status
                key = "%s|%s|status" % (search_key, process)
                message = Search.get_by_code("sthpw/message", key)
                if not message:
                    color = default_color
                else:
                    status = message.get("message")
                    if status:
                        status = status.replace("_", " ")
                        status = status.title()
                    color = colors.get(status)
                    if not color:
                        color = default_color


            else:
                status = task.get("status")
                color = colors.get(status)
                if not color:
                    color = default_color

            process_colors[process] = color

        self.info['process_colors'] = process_colors
        self.info['task_search_keys'] = task_search_keys






class NodeRenameWdg(BaseRefreshWdg):


    def get_styles(self):

        styles = HtmlElement.style('''

            .spt_rename_node {
                display: flex;
                height: 40px;
            }

            .spt_node_name_input {
                padding: 10px;
            }

            .spt_node_name_submit {
                background: #ccc;
                cursor: hand;
                display: flex;
                align-items: center;
                padding: 10px;
                text-transform: uppercase;
                color: white;
            }

            .spt_node_name_submit:hover {
                background: #999;
            }

            ''')

        return styles


    def get_display(self):

        top = DivWdg()
        top.add_class("spt_rename_node")

        name = self.kwargs.get("name") or ""

        name_input = HtmlElement.text()
        top.add(name_input)
        name_input.add_class("spt_node_name_input")
        name_input.add_attr("value", name)
        name_input.add_behavior({
            'type': 'load',
            'cbjs_action': '''

            bvr.src_el.select();

            var popup = bvr.src_el.getParent(".spt_popup");
            var title = popup.getElement(".spt_popup_title");
            title.setStyle("display", "none");

            var input_top = bvr.src_el.getParent(".spt_rename_node");
            input_top.rename = function () {
                var inp = this.getElement(".spt_node_name_input");
                var name = inp.value;

                var node = popup.activator;
                spt.pipeline.set_node_name(node, name);

                spt.popup.close(popup);

                var pipeline_top = node.getParent(".spt_pipeline_top");
                pipeline_top.hot_key_state = true;
            }


            '''
            })

        name_input.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''

            var popup = bvr.src_el.getParent(".spt_popup");
            var node = popup.activator;

            var top = node.getParent(".spt_pipeline_top");

            if (!top.hot_key_state) return;

            top.hot_key_state = false;
            document.activeElement.blur();
            bvr.src_el.focus();

            '''
            })

        name_input.add_behavior({
            'type': 'keyup',
            'cbjs_action': '''

            var key = evt.key;
            if (key == 'enter') {
                var top = bvr.src_el.getParent(".spt_rename_node");
                top.rename();
                spt.named_events.fire_event('pipeline|change', {});
            }

            '''
            })

        btn = DivWdg("Rename")
        top.add(btn)
        btn.add_class("spt_node_name_submit")
        btn.add_behavior({
            'type': 'click_up',
            'cbjs_action': '''

            var top = bvr.src_el.getParent(".spt_rename_node");
            top.rename();
            spt.named_events.fire_event('pipeline|change', {});

            '''
            })

        top.add(self.get_styles())

        return top








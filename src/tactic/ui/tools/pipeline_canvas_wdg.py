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

__all__ = ['BaseNodeWdg', 'PipelineCanvasWdg']

from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Container, Common, jsondumps
from pyasm.web import DivWdg, WebContainer, Table, Widget
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

    def get_title_background(self):
        return "rgba(0,0,0,0.5)"


    def show_default_name(self):
        return True

    def get_width(self):
        return 120

    def get_height(self):
        return 40

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
        top.add_style("height", height)
        top.add_style("box-sizing", "border-box")

        top.add_attr("spt_border_color", border_color)
        top.add_attr("spt_box_shadow", box_shadow)

        shape = self.get_shape()
        if shape == "star":
            self.set_star_shape()

        elif shape == "parallelogram":
            self.set_parallelogram_shape()

        elif shape == "circle":
            top.add_style("border-radius: %spx" % (height/2))

        elif shape == "elipse":
            top.add_style("width", height)
            top.add_style("border-radius: %spx" % border_radius)

        elif shape == "diamond":
            top.add_style("transform: rotate(-45deg)")
            top.add_style("width", height)

        else:
            top.add_style("border-radius: %spx" % border_radius)

        top.add_style("border: solid %spx %s" % (border_width, border_color))
        top.add_style("box-shadow: %s" % box_shadow)


        content_div = DivWdg()
        content_div.add_style("overflow: hidden")
        top.add(content_div)

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
            width: 0;
            height: 0;
            border-left: 50px solid transparent;
            border-right: 50px solid transparent;
            border-bottom: 100px solid red;
            position: relative;
        }
        .star-six:after {
            width: 0;
            height: 0;
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
        self.unique_id = self.top.set_unique_id();

        self.is_editable = self.kwargs.get("is_editable")
        if self.is_editable in ['false', False]:
            self.is_editable = False
        else:
            self.is_editable = True
        #self.is_editable = False


        default_node_type = self.kwargs.get("default_node_type") or ""
        self.top.add_attr("spt_default_node_type", default_node_type)


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
        canvas_title.add_style("padding: 3px")
        canvas_title.add_style("position: absolute")
        canvas_title.add_style("font-weight: bold")
        canvas_title.add_style("top: 0px")
        canvas_title.add_style("left: 0px")
        canvas_title.add_style("z-index: 150")

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


    def get_display(self):

        top = self.top

        self.width = self.kwargs.get("width")
        if not self.width:
            self.width = "auto"
        self.height = self.kwargs.get("height")
        if not self.height:
            self.height = 600
        self.background_color = self.kwargs.get("background_color")
        if not self.background_color:
            self.background_color = "white"


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
            

        top.add_style("position: relative")

        show_title = self.kwargs.get("show_title")
        if show_title not in ['false', False]:
            top.add(self.get_canvas_title())


        # outer is used to resize canvas
        outer = DivWdg()

        top.add(outer);
        outer.add_class("spt_pipeline_resize")
        outer.add_class("spt_resizable")
       

        outer.add_style("overflow: hidden")

        if self.kwargs.get("show_border") not in [False, 'false']:
            outer.add_border()

        # set the size limit
        outer.add_style("width: %s" % self.width)
        outer.add_style("height: %s" % self.height)

        process_menu = self.get_node_context_menu()
        menus = [process_menu.get_data()]

        # Simple context menu is for renaming and 
        # deleting approval, action and condition nodes..        
        simple_menu = self.get_simple_node_context_menu()
        simple_menus = [simple_menu.get_data()]   
    
        menus_in = {
            'NODE_CTX': menus,
            'SIMPLE_NODE_CTX': simple_menus 
        }

        from tactic.ui.container.smart_menu_wdg import SmartMenu
        SmartMenu.attach_smart_context_menu( outer, menus_in, False )

        # inner is used to scale
        inner = DivWdg()
        outer.add(inner)
        #outer.add_color("background", "background", -2)
        inner.add_class("spt_pipeline_scale")
        inner.add_style("z-index: 100")
        inner.add_style("position: relative")


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

        # create a canvas where all the nodes are drawn
        canvas = DivWdg()
        inner.add(canvas)
        
        canvas.add_class("spt_pipeline_canvas")
        canvas.add_style("width: %s" % self.width)
        canvas.add_style("height: %s" % self.height)
        canvas.add_style("z-index: 200")
        canvas.set_attr("spt_background_color", self.background_color)

        #canvas.add_class("spt_window_resize")
        #canvas.add_attr("spt_window_resize_xoffset", 500)
        #canvas.add_attr("spt_window_resize_offset", 200)


        canvas.add_behavior( {
        "type": 'drag',
        "mouse_btn": 'LMB',
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
                    spt.pipeline.set_scale( scale / 1.1 );
                }
                else {
                    spt.pipeline.set_scale( scale * 1.1 );
                }
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
            canvas.add_behavior( canvas_behavior )


        #paint.add_style("border: solid 1px blue");
        #paint.add_style("z-index: 1");
                
        
        outer.add(paint)
        
                
        paint.add_behavior( {
        "type": 'drag',
        "mouse_btn": 'LMB',
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

        heirarchy = self.get_node("heirarcy", node_type="hierarchy")
        template_div.add(heirarchy)

        dependency = self.get_node("dependency", node_type="dependency")
        template_div.add(dependency)


        progress = self.get_node("progress", node_type="progress")
        template_div.add(progress)


        endpoint = self.get_endpoint_node("output", node_type="output")
        template_div.add(endpoint)

        endpoint = self.get_endpoint_node("input", node_type="input")
        template_div.add(endpoint)
	
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

       
        return top




    def get_paint(self):
        from pyasm.web import Canvas
        canvas = Canvas()
        canvas.add_class("spt_pipeline_paint")
        #canvas.add_style("float: left")
        canvas.add_style("position: relative")

        canvas.add_style("margin-top: -%s" % self.height)
        canvas.set_attr("width", self.width)
        canvas.set_attr("height", self.height)
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
        div = DivWdg()
        div.add_class("spt_pipeline_folder")
        div.add_border()
        div.add_style("border-style: dashed")
        div.add_style("width: 140px")
        div.add_style("height: 80px")
        div.add_style("top: 100px")
        div.add_style("left: 100px")
        div.add_style("position: relative")
        div.add_style("z-index: 150")
        div.set_round_corners(size=5, corners=['TR','BR','BL', 'TL'])
        div.add_gradient("background", "background")

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
        content_div.add_style("padding: 10px")
        content_div.add_style("height: 60px")
        content_div.add_style("text-align: center")


        color_div = DivWdg()
        content_div.add(color_div)
        color_div.add_style("margin-right: 5px")
        color_div.add_class("spt_color_swatch")
        color_div.add_style("height: 15px")
        color_div.add_style("width: 15px")
        color_div.add_style("float: left")


        group_div = DivWdg()
        content_div.add(group_div)
        group_div.add_class("spt_group")

        group_div.add(group_name)

        group_div.add_style("font-weight: bold")


        content_div.add("<br/>")
        content_div.add("<br/>")

        button = DivWdg("Click to Start")
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

        node_name = "node0";
        spt.pipeline.add_node(node_name);


        var top = bvr.src_el.getParent(".spt_pipeline_folder")
        spt.behavior.destroy_element(top);
        spt.pipeline.redraw_canvas();
        '''
        } )



        div.add_behavior( {
        "type": 'drag',
        "mouse_btn": 'LMB',
        "drag_el": '@',
        "cb_set_prefix": 'spt.pipeline.node_drag'
        } )

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
            border_radius =  5
            #width = width
            height = 60
            width = 80
        elif node_type == "progress":
            border_radius =  30
            #width = width
            height = 55
            width = 55
        elif node_type == "unknown":
            border_radius = 50;
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

        node.add_style("color", "#000")
        node.add_style("font-size", "12px")
        node.add_style("position: absolute")
        node.add_style("text-align: center")
        node.add_style("z-index: 100")

        node.add_attr("spt_element_name", name)
        node.add_attr("title", name)

        from tactic.ui.container.smart_menu_wdg import SmartMenu
        SmartMenu.assign_as_local_activator( node, 'NODE_CTX' )


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
            icon = IconButtonWdg(name="Expand", icon="BS_ARROW_DOWN")
            icon_div.add(icon)
            icon_div.add_style("margin: 0px auto")
            icon_div.add_style("top: 40px")
            icon_div.add_style("left: %spx" % (width/2-12))
            icon_div.add_style("position: absolute")
            icon_div.add_style("z-index: 300")
            icon_div.add_style("border: solid 1px transparent")
            icon_div.add_style("width: 24px");
            icon_div.add_style("text-align: center");

            icon_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            var server = TacticServerStub.get();

            var node = bvr.src_el.getParent(".spt_pipeline_node");
            var node_name = spt.pipeline.get_node_name(node);
            var pipeline_code = spt.pipeline.get_current_group();
            var pipeline = server.eval("@SOBJECT(sthpw/pipeline['code','"+pipeline_code+"'])", {single: true});
            var search_type = pipeline.search_type;


            var expr = "@SOBJECT(config/process['pipeline_code','"+pipeline_code+"']['process','"+node_name+"'])";
            var process = server.eval(expr, {single: true});

            var subpipeline_code = process.subpipeline_code;
            if (subpipeline_code) {
                var subpipeline = server.eval("@SOBJECT(sthpw/pipeline['code','"+subpipeline_code+"'])", {single: true});
            }
            else {
                var process_code = process.code;

                var subpipeline = server.eval("@SOBJECT(sthpw/pipeline['parent_process','"+process_code+"'])", {single: true});
            }

            var top = spt.pipeline.top;
            var text = top.getElement(".spt_pipeline_editor_current2");

            if (text) {
                var root_html = text.innerHTML; 
                bvr.breadcrumb = root_html;
            }
            else {
                var root_html = "";
            }


            if (!subpipeline) {
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
            spt.pipeline.unselect_all_nodes();
            spt.pipeline.select_single_node(node);
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
        'cbjs_action': '''
        spt.pipeline.init(bvr);
        var node = bvr.src_el;
        spt.pipeline.select_nodes_by_group(node.spt_group);
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


    def get_endpoint_node(self, name, node_type ):

        node = DivWdg()
        node.add_class("spt_pipeline_%s" % node_type)
        node.add_class("spt_pipeline_node")
        node.add_attr("spt_node_type", node_type)


        node.add_attr("spt_element_name", name)
        node.add_attr("title", name)


        node.add_style("z-index", "200");
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

        node.add_style("z-index", "200");
        node.add_style("position: absolute")

        width = custom_wdg.get_width()
        height = custom_wdg.get_height()

        enable_context_menu = self.kwargs.get("enable_context_menu")

        if enable_context_menu not in ['false', False]:
            from tactic.ui.container.smart_menu_wdg import SmartMenu
            SmartMenu.assign_as_local_activator( node, 'SIMPLE_NODE_CTX')

 
        node_behaviors = self.get_node_behaviors()
        for node_behavior in node_behaviors:
            node.add_behavior( node_behavior )



 
        # add custom node behaviors
        node_behaviors = custom_wdg.get_node_behaviors()
        for node_behavior in node_behaviors:
            node.add_behavior( node_behavior )


        nobs_offset = 0
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


        node.add_style("z-index", "200");

        width = 60
        height = 60


        node.add_style("position: absolute")

        node.add_style("width: auto")
        node.add_style("height: auto")


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





    def get_approval_node(self, name, process=None):

        node = DivWdg()
        node.add_class("spt_pipeline_approval")
        node.add_class("spt_pipeline_node")
        node.add_attr("spt_node_type", "approval")


        node.add_attr("spt_element_name", name)
        node.add_attr("title", name)


        node.add_style("z-index", "200");


        width = 65
        height = 65


        node.add_style("position: absolute")

        node.add_style("width: auto")
        node.add_style("height: auto")


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

        self.add_default_node_behaviors(node, text)

        return node



    def get_trigger_node(self):


        name = "trigger_template"

        node = DivWdg()
        node.add_class("spt_pipeline_trigger")
        node.add_class("spt_pipeline_node")


        node.add_attr("spt_element_name", name)
        node.add_attr("title", name)

        node.add_style("z-index", "200");


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

        label = DivWdg()
        node.add(label)
        label.add_style("position: absolute")

        ##
        label.add_style("display: none")
        ##

        label.add_style("width: %spx" % width)
        label.add_style("height: %spx" % height)

        label.add_style("top: %spx" % (height/4+7) )
        label.add_class("spt_label");
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


//spt.Environment.get().add_library("spt_pipeline");

spt.pipeline = {};

spt.pipeline.top = null;

spt.pipeline.background_color = "#fff";

spt.pipeline.allow_cycle = true;

// External method to initialize callback
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

    var data = top.spt_data;
    if (typeof(data) == 'undefined') {
        top.spt_data = {};
        data = top.spt_data;
        data.scale = 1.0;
    }
    data.canvas = canvas;
    data.paint = paint;
    data.ctx = ctx;

    var connector_panel_data = top.getAttribute("spt_connector_panel_data");
    if (connector_panel_data) {
        connector_panel_data = JSON.decode(connector_panel_data);
    } else {
        connector_panel_data = {};
    }
    data.connector_panel_data = connector_panel_data;

    // FIXME: need this delay because the table seems to resize itself somewhere
    setTimeout( function() {
        var size = canvas.getSize();
        if (size.x == 0 || size.y == 0) {
            return;
        }
        spt.pipeline.set_size(size.x, size.y);
    }, 500);
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
    for (var i = 0; i < sobjs.length; i++) {
        var sobj = sobjs[i];
        data.colors[sobj[key]] = sobj.color;
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
    //var nodes = spt.pipeline.get_selected_nodes();
    //return nodes;
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
        outer.setStyle("box-shadow", "0px 0px 15px rgba(128,128,128,1.0)");
    }
    outer.setStyle("border", "solid 1px rgba(128,128,0,1.0)");
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
    var border_color = outer.getAttribute("spt_border_color");
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

    var top = bvr.src_el.getParent(".spt_pipeline_top");
    var event_name = top.getAttribute("id") + "|unselect_all";
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
    spt.pipeline.unselect_all_nodes();

    var nodes = spt.pipeline.get_all_nodes();
   
    for (var i=0; i<nodes.length; i++) {
        var node = nodes[i];
        
        if ((TL.x <node.spt_xpos && node.spt_xpos < BR.x ) && (TL.y < node.spt_ypos && node.spt_ypos < BR.y)) {
            spt.pipeline.select_node(node);
        }
    }
}



// Node functions

spt.pipeline.get_all_nodes = function() {
    var canvas = spt.pipeline.get_canvas();
    nodes = canvas.getElements(".spt_pipeline_node");
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



spt.pipeline.get_node_name = function(node) {
    return node.getAttribute("spt_element_name");
}


spt.pipeline.get_node_type = function(node) {
    return node.getAttribute("spt_node_type");
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
            nodes.push(from_node);
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
			node_type = "node";
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
		name = "node"+nodes.length;
	}

	if (typeof(x) == 'undefined' || x == null) {
		var size = canvas.getSize();
		x = size.x/3 + nodes.length*15;
		y = size.y/3 + nodes.length*10;
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
	new_node.properties = {};


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
}

spt.pipeline.get_node_property = function(node, name) {
    return node.properties[name];
}


spt.pipeline.set_node_properties = function(node, properties) {
    node.properties = properties;
}

spt.pipeline.get_node_properties = function(node) {
    return node.properties;
}




spt.pipeline.set_color = function(node, color) {
    if (!color) {
        return;
    }

    var content= node.getElement(".spt_content");
    var color1 = spt.css.modify_color_value(color, +10);
    var color2 = spt.css.modify_color_value(color, -10);

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
        color = '#999';
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
    var input = node.getElement(".spt_input");
    var label = node.getElement(".spt_label");
    label.setStyle("display", "none");
    input.setStyle("display", "");
    input.focus();
    input.select();
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

    var group_label = new_folder.getElement(".spt_group");

    if (!title) {
        var parts = group_name.split("/");
        title = parts[parts.length-1];
    }

    group_label.innerHTML = title;
    canvas.appendChild(new_folder);

    // color the folder
    spt.pipeline.set_folder_color(new_folder, color);

    new_folder.spt_group = group_name;


    var size = canvas.getSize();
    var x = size.x/3 + folders.length*15;
    var y = size.y/3 + folders.length*10;
    spt.pipeline.move_to(new_folder, x, y);
}


spt.pipeline.set_folder_color = function(folder, color) {

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
    var canvas = spt.pipeline.get_canvas();
    var canvas_size = canvas.getSize();
    return canvas_size;
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
}

spt.pipeline.node_drag_motion = function( evt, bvr, mouse_411) {

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
    spt.pipeline.last_connector = new spt.pipeline.Connector();
    spt.pipeline.last_connector.set_from_node(from_node);
}



spt.pipeline.drag_connector_motion = function(evt, bvr, mouse_411) {

    var data = spt.pipeline.get_data();
    var canvas = spt.pipeline.get_canvas();
    var canvas_pos = spt.pipeline.get_el_position(canvas);
  
    var scale = spt.pipeline.get_scale();
    var node;
    var node_pos;
    var node_lastpos;
    
    if (data.line_mode == 'bezier' || data.line_mode == 'curved_edge') {
        node = bvr.src_el.getParent(".spt_pipeline_node");
        node_pos = spt.pipeline.get_position(node);
        node_lastpos = spt.pipeline.get_el_last_position(node);

        var size = spt.pipeline.get_size(node);
        
        node_pos = { x: (node_pos.x + size.x), y: (node_pos.y + size.y/2)};
        
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

    if ( to_node && from_node &&
        spt.pipeline.get_node_name(to_node) == spt.pipeline.get_node_name(from_node) )
    {
        //spt.alert("Source node and destination node are the same");
        return;
    }

    var group_name = from_node.spt_group;
    spt.pipeline.set_current_group(group_name);

    if (to_node == null) {
        var pos = spt.pipeline.get_mouse_position(mouse_411);
        var default_node_type = null;
        to_node = spt.pipeline.add_node(null, null, null, { node_type: null} );
        // FIXME: hard coded

        var height = 40;
        spt.pipeline.move_to(to_node, pos.x-height/2, pos.y);
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
        connectors.push(connector);

        // check if cycle exists
        if (!spt.pipeline.allow_cycle) {
            if (spt.pipeline.detect_cycle()) {
                spt.alert("Cyclic connections are not allowed");
                canvas.connectors = temp;
                return;
            }
        }

        // add the connector to the source group
        var group = spt.pipeline.add_group(group_name);
        group.add_connector(connector);

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

spt.pipeline.draw_text = function(text, x, y) {
    var ctx = spt.pipeline.get_ctx();
    ctx.fillStyle = '#DE4A18';
    ctx.font = 'normal 11px sans-serif';
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


// Pan functionality
spt.pipeline.orig_mouse_position = null;
spt.pipeline.last_mouse_position = null;
spt.pipeline.canvas_drag_disable = false;

spt.pipeline.canvas_drag_setup = function(evt, bvr, mouse_411) {

    spt.pipeline.init(bvr);

    var pos = spt.pipeline.get_mouse_position(mouse_411);

    // do a hit test first
    var connector = spt.pipeline.hit_test(pos.x-2, pos.y-2, pos.x+2, pos.y+2);
    if (connector != null) {
        spt.pipeline.canvas_drag_disable = true;
        return;
    }

    bvr.src_el.setStyle("cursor", "move");
    spt.pipeline.init(bvr);
    spt.pipeline.last_mouse_position = pos;
    spt.pipeline.orig_mouse_position = pos;

    spt.body.hide_focus_elements(evt);
}

spt.pipeline.canvas_drag_motion = function(evt, bvr, mouse_411) {

    if ( spt.pipeline.canvas_drag_disable == true ) {
        return;
    }

    var mouse_pos = spt.pipeline.get_mouse_position(mouse_411);
    var dx = mouse_pos.x - spt.pipeline.last_mouse_position.x;
    var dy = mouse_pos.y - spt.pipeline.last_mouse_position.y;
    var scale = spt.pipeline.get_scale();
    dx = dx/scale;
    dy = dy/scale;


    spt.pipeline.move_all_nodes(dx, dy);
    spt.pipeline.move_all_folders(dx, dy);

    spt.pipeline.last_mouse_position = mouse_pos;
    spt.pipeline.redraw_canvas();


}

spt.pipeline.canvas_drag_action = function(evt, bvr, mouse_411) {

    spt.pipeline.canvas_drag_disable = false;


    var mouse_pos = spt.pipeline.get_mouse_position(mouse_411);
    var dx = mouse_pos.x - spt.pipeline.orig_mouse_position.x;
    var dy = mouse_pos.y - spt.pipeline.orig_mouse_position.y;
    if (Math.abs(dx) < 5 && Math.abs(dy) < 5) {
        spt.pipeline.unselect_all_nodes();
    }



    bvr.src_el.setStyle("cursor", "");
    var nodes = spt.pipeline.get_all_nodes();
    for (var i = 0; i < nodes.length; i++) {
        spt.pipeline.set_current_position(nodes[i]);
    }
    spt.pipeline.redraw_canvas();

    // reset the setting
    spt.pipeline.last_mouse_position = null;
    spt.pipeline.canvas_drag_disable = false;

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
    spt.pipeline.redraw_canvas();
}


spt.pipeline.zoom_drag_action = function(evt, bvr, mouse_411) {
    spt.pipeline.redraw_canvas();
}

spt.pipeline.set_scale = function(scale) {

    var data = spt.pipeline.get_data();
    data.scale = scale;

    var canvas = spt.pipeline.get_canvas();
    //canvas.setStyle("border", "solid 1px blue");
    
    var scale_str = "scale("+scale+", "+scale+")"
 
    scale_el = canvas.getParent(".spt_pipeline_scale");
    //canvas.setStyle("border", "solid 1px blue");

    scale_el.setStyle("-moz-transform", scale_str)
    scale_el.setStyle("-webkit-transform", scale_str)  
    scale_el.setStyle("transform", scale_str)

    //TweenLite.to(scale_el, 0.2, {scale: scale});
    
    spt.pipeline.redraw_canvas();
    
}

spt.pipeline.get_scale = function() {
    var data = spt.pipeline.get_data();
    return data.scale;
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
    var canvas = spt.pipeline.get_canvas();
    var paint = spt.pipeline.get_paint();
    outer = top.getElement(".spt_pipeline_resize")
    outer.setStyle("width", ""+width);
    if (height) {
        outer.setStyle("height", ""+height);
    }

    paint.setAttribute("width", ""+width);
    if (height) {
        paint.setAttribute("height", ""+height);
        paint.setStyle("margin-top", "" + (-height));
    }
    canvas.setStyle("width", ""+width);
    if (height) {
        canvas.setStyle("height", ""+height);
    }
    spt.pipeline.redraw_canvas();

/*
    var cookie = new Cookie('pipeline_canvas');
    var state = JSON.parse( cookie.read() );
    if (state == null) {
        state = {};
    }
    state.height = height;
    state.width = width;
    cookie.write(JSON.stringify(state))
*/
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

    var canvas = spt.pipeline.get_canvas();
    var size = canvas.getSize();
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

    scale = scale * 0.85;
    //scale = 1.0
    if (scale > 1.0) {
        scale = 1.0;
    }
    spt.pipeline.set_scale(scale);

    // zero position at the specified scale
    //var zero_pos_x = size.x/2 - size.x/2 * scale;
    //var zero_pos_y = size.y/2 - size.y/2 * scale;


    var zero_pos_x = 100;
    var zero_pos_y = 100;

    var zero_pos_x = size.x/2 - hsize/2 - 100;
    var zero_pos_y = size.y/2 - vsize/2;

    var dx = - left + zero_pos_x + 100;
    var dy = - top + zero_pos_y;
    spt.pipeline.move_all_nodes(dx, dy);
    spt.pipeline.move_all_folders(dx, dy);


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
    paint.setStyle("margin-top", "" + (-height));
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




// Connector class
spt.pipeline.Connector = function(from_node, to_node) {

    this.from_node = from_node;
    this.to_node = to_node;
    this.color = '#111';
    this.attrs = {};
    this.type = "connector";
    this.panel;

    this.draw = function() {
        var data = spt.pipeline.get_data();
        if (data.line_mode == 'line') {
            this.draw_line();
        }
        else {
            this.draw_spline();
        }
    }


    this.draw_spline = function(show_attr) {
        var canvas = spt.pipeline.get_canvas();
        var from_pos = spt.pipeline.get_position(this.from_node);
        var to_pos = spt.pipeline.get_position(this.to_node);

        var from_size = spt.pipeline.get_size(this.from_node);
        var to_size = spt.pipeline.get_size(this.to_node);

        var scale = spt.pipeline.get_scale();
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
        unscaled_from_pos = {x: from_pos.x + from_width, y: from_pos.y + from_height/2 };
        unscaled_to_pos = {x: to_pos.x, y: to_pos.y + to_height/2 };

        // put a scale transformation on it
        // moz transform scales from the center, so have to move
        // the curves back
        var size = canvas.getSize();
        width = size.x;
        height = size.y;

        from_pos = {
            x: (unscaled_from_pos.x - width/2) * scale + width/2,
            y: (unscaled_from_pos.y - height/2) * scale + height/2,
        }



        to_pos = {
            x: (unscaled_to_pos.x - width/2) * scale + width/2,
            y: (unscaled_to_pos.y - height/2) * scale + height/2,
        }

        var data = spt.pipeline.get_data();
        if (data.line_mode == 'curved_edge') {
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


    }


    this.draw_line = function(show_column) {
        var canvas = spt.pipeline.get_canvas();
        var from_pos = spt.pipeline.get_position(this.from_node);
        var to_pos = spt.pipeline.get_position(this.to_node);

        var from_size = spt.pipeline.get_size(this.from_node);
        var to_size = spt.pipeline.get_size(this.to_node);

        var scale = spt.pipeline.get_scale();
        //var scale = 1;
        var from_width = from_size.x;
        var from_height = from_size.y;
        var to_width = to_size.x;
        var to_height = to_size.y;

        // offset by the midpoint
        from_pos = {x: from_pos.x + from_width/2, y: from_pos.y + from_height/2 };
        to_pos = {x: to_pos.x + to_width/2, y: to_pos.y + to_height/2 };

        // put a scale transformation on it
        // moz transform scales from the center, so have to move
        // the curves back
        var size = canvas.getSize();
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


    // get all of the processes associated with this pipeline
    process_sobjs = server.eval("@SOBJECT(config/process['pipeline_code','"+pipeline_code+"'])");
    processes = {};
    for (var i = 0; i < process_sobjs.length; i++) {
        var process_sobj = process_sobjs[i];
        var name = process_sobj.process;
        var process_code = process_sobj.code;
        processes[name] = process_sobj;
    }

    
    var pipeline_xml = pipeline.pipeline;
    var pipeline_stype = pipeline.search_type;
    var xml_doc = spt.parse_xml(pipeline_xml);
    var pipeline_name = pipeline.name;
    var pipeline_type = pipeline.type;

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
        color = "#999";
    }
    group.set_color(color);
    group.set_group_type("pipeline");
    group.set_node_type("process");

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
            } else {
                settings = JSON.parse(settings);
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

    //spt.pipeline.fit_to_canvas(pipeline_code);

    if (pipeline_stype == "sthpw/task") {
        spt.pipeline.set_task_color();
    }

    spt.pipeline.redraw_canvas();

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

        var options = {
            group: group,
            select_node: false,
            node_type: node_type,
            new: false,
        }

        // split the name
        //var name_parts = name.split("/");
        //name = name_parts[name_parts.length-1];

        var node = spt.pipeline.add_node(name, xpos, ypos, options);

        // add the attributes
        var attributes = xml_nodes[i].attributes;
        for (var j = 0; j < attributes.length; j++) {
            var name = attributes[j].name;
            var value = attributes[j].value;
            node.properties[name] = value;
        }



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

    /*
    //var colors = server.get_task_status_colors();
    var colors = {
        'In Progress': 'rgb(0,0,255)',
        Pending: 'rgb(255,255,0)',
        Complete: 'rgb(0,255,0)',
    }
    */

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
            throw("duplicated node name ' + name + ' found. Please clean up first and save again.")
            return;
        }
        else {
            name_dict[name] = true;
        }

        var tag_type = node.spt_type;
        var node_type = node.spt_node_type;

        var pos = spt.pipeline.get_position(node);
        pos = { x: pos.x-left+100, y: pos.y-top+100 };

        if (node_type != "node") {
            xml += '  <'+tag_type+' name="'+name+'" type="'+node_type+'" xpos="'+pos.x+'" ypos="'+pos.y+'"';
        }
        else {
            xml += '  <'+tag_type+' name="'+name+'" xpos="'+pos.x+'" ypos="'+pos.y+'"';
        }

        var properties = node.properties;
        for (var key in properties) {
           
            if (!properties.hasOwnProperty(key))
                continue;
            if (['name','xpos','ypos','type','names','namedItem','item'].contains(key)) {
                continue;
            }

            var value = properties[key];
            if (key == "settings" && value) {
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
            if (['from','to'].contains(key)) 
                continue;
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

    '''





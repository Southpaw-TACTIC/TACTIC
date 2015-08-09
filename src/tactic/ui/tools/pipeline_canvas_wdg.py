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

__all__ = ['PipelineCanvasWdg']

from tactic.ui.common import BaseRefreshWdg

from pyasm.common import Container
from pyasm.web import DivWdg, WebContainer, Table, Widget
from pyasm.search import Search, SearchType

from pyasm.widget import ProdIconButtonWdg, IconWdg, TextWdg
from tactic.ui.container import GearMenuWdg, Menu, MenuItem

from tactic.ui.widget import ActionButtonWdg, IconButtonWdg


class PipelineCanvasWdg(BaseRefreshWdg):
    '''Pipeline Widget'''

    def init(my):
        my.top = DivWdg()
        my.set_as_panel(my.top)
        my.top.add_class("spt_pipeline_top")
        my.unique_id = my.top.set_unique_id();

        my.is_editable = my.kwargs.get("is_editable")
        if my.is_editable in ['false', False]:
            my.is_editable = False
        else:
            my.is_editable = True
        #my.is_editable = False

    def get_unique_id(my):
        return my.unique_id


    def get_canvas_title(my):

        canvas_title = DivWdg()
        canvas_title.add_border()
        canvas_title.add_style("padding: 3px")
        canvas_title.add_style("position: absolute")
        canvas_title.add_style("font-weight: bold")
        canvas_title.add_style("top: 0px")
        canvas_title.add_style("left: 0px")
        canvas_title.add_style("z-index: 200")

        canvas_title.add_class("spt_pipeline_editor_current2")
        canvas_title.add_relay_behavior( {
            'type': 'mouseup',
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


    def get_display(my):

        top = my.top

        my.width = my.kwargs.get("width")
        if not my.width:
            my.width = "auto"
        my.height = my.kwargs.get("height")
        if not my.height:
            my.height = 600


        # create an inner and outer divs
        my.nob_mode = my.kwargs.get('nob_mode')
        if not my.nob_mode:
            my.nob_mode = "visible"

        my.line_mode = my.kwargs.get('line_mode')
        if not my.line_mode:
            my.line_mode = "bezier"


        my.has_prefix = my.kwargs.get('has_prefix')
        if my.has_prefix in [True, 'true']:
            my.has_prefix = True
        else:
            my.has_prefix = False

        my.filter_node_name = my.kwargs.get('filter_node_name')
        if my.filter_node_name in [True, 'true']:
            my.filter_node_name = True
        else:
            my.filter_node_name = False
            

        top.add_style("position: relative")
        top.add(my.get_canvas_title())


        # outer is used to resize canvas
        outer = DivWdg()

        top.add(outer);
        outer.add_class("spt_pipeline_resize")
        outer.add_class("spt_resizable")
       

        outer.add_style("overflow: hidden")
        outer.add_border()

        # set the size limit
        outer.add_style("width: %s" % my.width)
        outer.add_style("height: %s" % my.height)

        menu = my.get_node_context_menu()
        menus = [menu.get_data()]
        menus_in = {
            'NODE_CTX': menus,
        }
        from tactic.ui.container.smart_menu_wdg import SmartMenu
        SmartMenu.attach_smart_context_menu( outer, menus_in, False )



        # inner is used to scale
        inner = DivWdg()
        outer.add(inner)
        outer.add_color("background", "background", -10)
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
            'cbjs_action': my.get_onload_js()
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
        canvas.add_style("width: %s" % my.width)
        canvas.add_style("height: %s" % my.height)
        canvas.add_style("z-index: 200")
        
 
      
        #canvas.add_style("width: 100%")
        #canvas.add_style("height: 100%")


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


        """
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
        """


 
        canvas.add_behavior( {
        "type": 'drag',
        "mouse_btn": 'LMB',
        "modkeys": 'SHIFT',
        "drag_el": '@',
        "cb_set_prefix": 'spt.pipeline.select_drag'
        } )


        canvas.add_behavior( {
        "type": 'click_up',
        "cbjs_action": '''
        spt.pipeline.init(bvr);
        spt.pipeline.unselect_all_nodes();
        spt.pipeline.hit_test_mouse(mouse_411);
        '''
        } )

        canvas.add_behavior( {
        "type": 'click_up',
        "cbjs_action": '''
        // Add edited flag
        var editor_top = bvr.src_el.getParent(".spt_pipeline_editor_top");
        editor_top.addClass("spt_has_changes");
        '''
        }) 



        # create the paint where all the connectors are drawn
        paint = my.get_paint()

        # add custom canvas behaviors on the canvas div instead
        my.canvas_behaviors = my.get_canvas_behaviors()
        for canvas_behavior in my.canvas_behaviors:
            canvas.add_behavior( canvas_behavior )


        #paint.add_style("border: solid 1px blue");
        paint.add_style("z-index: 1");
        
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


        paint.add_behavior( {
        "type": 'click_up',
        "cbjs_action": '''
        spt.pipeline.init(bvr);
        spt.pipeline.unselect_all_nodes();
        spt.pipeline.hit_test_mouse(mouse_411);
        '''
        } )






        # add a template node
        template_div = DivWdg()
        template_div.add_style("display: none")
        template_div.add_class("spt_pipeline_template")
        inner.add(template_div)

        node = my.get_node("XXXXX")
        node.add_style("left: 0px")
        node.add_style("top: 0px")
        template_div.add(node)

        node = my.get_node("XXXXX", node_type="manual")
        node.add_style("left: 0px")
        node.add_style("top: 0px")
        template_div.add(node)



        # add folder group node
        folder = my.get_folder("XXXXX")
        template_div.add(folder)

        # add approval node
        approval = my.get_approval_node("XXXXX")
        template_div.add(approval)

        approval = my.get_condition_node("XXXXX")
        template_div.add(approval)

        action = my.get_node("XXXXX", node_type="action")
        template_div.add(action)

        heirarchy = my.get_node("XXXXX", node_type="hierarchy")
        template_div.add(heirarchy)

        dependency = my.get_node("XXXXX", node_type="dependency")
        template_div.add(dependency)


        endpoint = my.get_endpoint_node("XXXXX", node_type="output")
        template_div.add(endpoint)

        endpoint = my.get_endpoint_node("XXXXX", node_type="input")
        template_div.add(endpoint)



        # add custom node
        custom = my.get_custom_node("custom", "email")
        template_div.add(custom)


        # add trigger node
        trigger = my.get_trigger_node()
        template_div.add(trigger)



        # resize test
        show_resize = my.kwargs.get("show_resize")
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



        pipeline_str = my.kwargs.get("pipeline")
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


        scale = my.kwargs.get("scale")
        if scale:
            scale = float(scale)
            div.add_behavior( {
            'type': 'load',
            'scale': scale,
            'cbjs_action': '''
                spt.pipeline.init(bvr);
                spt.pipeline.set_scale(bvr.scale);
            '''
            } )


        div.add_behavior( {
        'type': 'load',
        'line_mode': my.line_mode,
        'has_prefix': my.has_prefix,
        'cbjs_action': '''
            spt.pipeline.init(bvr);
            spt.pipeline.set_line_mode(bvr.line_mode);
            spt.pipeline.set_has_prefix(bvr.has_prefix);
        '''
        } )

        return top




    def get_paint(my):
        from pyasm.web import Canvas
        canvas = Canvas()
        canvas.add_class("spt_pipeline_paint")
        #canvas.add_style("float: left")
        canvas.add_style("position: relative")

        canvas.add_style("margin-top: -%s" % my.height)
        canvas.set_attr("width", my.width)
        canvas.set_attr("height", my.height)

        canvas.add_style("z-index: 50")

        canvas.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        spt.pipeline.init(bvr);
        '''
        } )

	


     
        return canvas




    def get_canvas_behaviors(my):
        return []


    def get_folder(my, group_name):
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
        #div.set_round_corners(corners=['TR','BR','BL'])
        div.set_round_corners(size=5, corners=['TR','BR','BL', 'TL'])
        div.add_gradient("background", "background", -10)

        lip_div = DivWdg()
        div.add(lip_div)
        lip_div.add_class("spt_lip")
        lip_div.add_style("display: none")
        # disable for now
        """
        lip_div.add_color("background", "background", -10)
        lip_div.add_style("margin-left: -1px")
        lip_div.add_style("margin-top: -12px")
        lip_div.add_style("width: 30px")
        lip_div.add_style("height: 10px")
        lip_div.add_style("position: absolute")
        lip_div.add_border()
        lip_div.set_round_corners(corners=['TR','TL'])
        """


        expand_div = DivWdg()
        div.add(expand_div)
        expand_div.add_style("display: none")
        # disable for now
        """
        expand_div.add_style("position: absolute")
        expand_div.add_style("width: 10px")
        expand_div.add_style("height: 80px")
        expand_div.add_style("top: -1px")
        expand_div.add_style("left: 129px")
        expand_div.add_border()
        expand_div.add("<br/>"*2)
        expand_div.set_round_corners(corners=['TR','BR'])
        expand_div.add_style("vertical-align: middle")
        icon = IconWdg("Expand", IconWdg.ARROWHEAD_DARK_RIGHT)
        expand_div.add(icon)
        icon.add_style("margin-left: -3")
        expand_div.add_attr("title", "Click to expand group")

        expand_div.add_behavior( {
        'type': 'hover',
        'cbjs_action_over': '''
        bvr.src_el.setStyle("background", "#F00");
        ''',
        'cbjs_action_out': '''
        bvr.src_el.setStyle("background", "");
        '''
        } )
        """
        

        content_div = DivWdg()
        content_div.add_class("spt_content")
        div.add(content_div)
        content_div.add_style("padding: 10px")
        content_div.add_style("height: 60px")


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

        button = IconButtonWdg(title="Create First Node", icon=IconWdg.ADD)
        content_div.add( button )

        button.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.pipeline.init(bvr);

        var folder = bvr.src_el.getParent(".spt_pipeline_folder");
        var group_name = folder.spt_group;
        spt.pipeline.set_current_group(group_name);

        var parts = group_name.split("/");
        node_name = parts[parts.length-1];
        spt.pipeline.add_node(node_name);


        var top = bvr.src_el.getParent(".spt_pipeline_folder")
        spt.behavior.destroy_element(top);
        spt.pipeline.redraw_canvas();
        '''
        } )
        button.add_style("float: right")


        content_div.add("<br/>")
        #div.add("There are no nodes in this pipeline")
        #div.add("<br/><br/>")



        #content_div.add("0 nodes")
        content_div.add("(no processes)")

        div.add_behavior( {
        "type": 'drag',
        "mouse_btn": 'LMB',
        "drag_el": '@',
        "cb_set_prefix": 'spt.pipeline.node_drag'
        } )

        return div


    def get_node(my, name, node_type="node"):

        node = DivWdg()

        width, height = my.get_node_size()

        if node_type == "action":
            border_radius = 20 
        elif node_type == "hierarchy":
            border_radius =  50 
            width = width
            height = height + 50
        elif node_type == "dependency":
            border_radius =  5
            #width = width
            width = 60
            height = width
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


        # add nobbies on the node
        left_nob = DivWdg()
        left_nob.add_class("spt_left_nob")
        left_nob.set_round_corners(3, corners=['TL','BL'])
        left_nob.add_event("onmouseover", "$(this).setStyle('background','rgba(255,255,0,0.7')")
        left_nob.add_event("onmouseout", "$(this).setStyle('background','rgba(255,255,0,0.2')")
        left_nob.add_style("cursor: pointer")
        left_nob.add_style("position: absolute")
        left_nob.add_style("border: solid 1px black")
        left_nob.add_style("background: rgba(255,255,0,0.2)")
        left_nob.add_style("width: 10px")
        left_nob.add_style("height: 10px")
        left_nob.add_style("top: %spx" % (height/2-5))
        left_nob.add_style("left: -11px")
        left_nob.add_style("z-index: 100")
        left_nob.add("")
        node.add(left_nob)
        
            

        # add nobbies on the node
        right_nob = DivWdg()
        node.add(right_nob)
        right_nob.add_class("spt_right_nob")
        right_nob.add_style("cursor: pointer")
        right_nob.add_style("position: absolute")
        right_nob.add_style("top: 0px")
        right_nob.add_style("left: %spx" % (width+1))
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
        right_nob_vis.add_event("onmouseover", "$(this).setStyle('background','rgba(255,255,0,0.7')")
        right_nob_vis.add_event("onmouseout", "$(this).setStyle('background','rgba(255,255,0,0.2')")

        if my.nob_mode == 'dynamic':
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

        
        if my.is_editable:

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




        # active glow
        """
        BASE = "/context/themes2/default/pipeline"
        active = DivWdg()
        node.add(active)
        active.add_class("spt_active");
        active.add("<img src='%s/node_glow.png' height='%s' width='125'/>" % (BASE, (height+20)))
        active.add_style("position: absolute")
        active.add_style("top: -9px")
        active.add_style("left: -11px")
        active.add_style("z-index: -200")
        active.add_style("display: none")

        active.add_style("box-shadow: 0px 0px 10px rgba(0,0,0,0.5)")
        """



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

        extra_wdg = my.get_extra_node_content_wdg()
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
            icon_div.add_style("top: 50px")
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

            if (!subpipeline) {
                // create the pipeline
                var data = {
                    name: node_name + "_pipeline",
                    parent_process: process_code
                }
                subpipeline = server.insert("sthpw/pipeline", data);
            }

            var subpipeline_code = subpipeline.code;

            spt.pipeline.clear_canvas();
            spt.pipeline.import_pipeline(subpipeline_code);

            var top = spt.pipeline.top;
            var text = top.getElement(".spt_pipeline_editor_current2");

            var html = "<span class='hand spt_pipeline_link' spt_pipeline_code='"+subpipeline.code+"'>"+subpipeline.name+"</span>";
            text.innerHTML = text.innerHTML + " / " + html;

            evt.stopPropagation();
            '''
            } )




        # add custom node behaviors
        node_behaviors = my.get_node_behaviors()
        for node_behavior in node_behaviors:
            node.add_behavior( node_behavior )



        my.add_default_node_behaviors(node, text)

        return node



    def add_nobs(my, node, height, offset=0):

        # add nobbies on the node
        left_nob = DivWdg()
        node.add(left_nob)
        left_nob.add_class("spt_left_nob")
        left_nob.set_round_corners(3, corners=['TL','BL'])
        left_nob.add_event("onmouseover", "$(this).setStyle('background','rgba(255,255,0,0.7')")
        left_nob.add_event("onmouseout", "$(this).setStyle('background','rgba(255,255,0,0.2')")
        left_nob.add_style("cursor: pointer")
        left_nob.add_style("position: absolute")
        left_nob.add_style("border: solid 1px black")
        left_nob.add_style("background: rgba(255,255,0,0.2)")
        left_nob.add_style("width: 10px")
        left_nob.add_style("height: 10px")
        left_nob.add_style("top: %spx" % (height/2-5))
        left_nob.add_style("left: %spx" % (-11-offset))
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
        right_nob_vis.add_event("onmouseover", "$(this).setStyle('background','rgba(255,255,0,0.7')")
        right_nob_vis.add_event("onmouseout", "$(this).setStyle('background','rgba(255,255,0,0.2')")

        if my.nob_mode == 'dynamic':
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
       

        if my.is_editable:

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






    def add_default_node_behaviors(my, node, text):

        if not my.is_editable:
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
        'filter_node_name': my.filter_node_name,
        'cbjs_action': '''
        bvr.src_el.blur();
        '''
        } )

        text.add_behavior( {
        'type': 'blur',
        'filter_node_name': my.filter_node_name,
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
        'type': 'click_up',
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



    def get_node_size(my):
        width = 100
        height = 40 
        return width, height

    def get_extra_node_content_wdg(my):
        return Widget()

        #icon = IconWdg("Expand", IconWdg.PIPELINE)
        #icon.add_style("position: absolute")
        #icon.add_style("top: 2px")
        #icon.add_style("left: 3px")
        #return icon


    def get_endpoint_node(my, name, node_type ):

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


        my.add_nobs(node, height)


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

        my.add_default_node_behaviors(node, text)

        return node






    def get_custom_node(my, name, node_type ):

        node = DivWdg()
        node.add_class("spt_pipeline_custom")
        node.add_class("spt_pipeline_node")
        node.add_attr("spt_node_type", "custom")


        node.add_attr("spt_element_name", name)
        node.add_attr("title", name)


        node.add_style("z-index", "200");
        node.add_style("position: absolute")

        node.add_style("width: auto")
        node.add_style("height: auto")


        class NotificationNodeWdg(BaseRefreshWdg):
            def get_width(my):
                return 50 
            def get_height(my):
                return 50 

            def get_node_behaviors(my):
                return []

            def get_node_type(my):
                return "email"

            def get_handler_class(my):
                return CustomWorkflowHandler

            def get_display(my):
                top = my.top
                #top.add_style("width: %s" % my.get_width())
                #top.add_style("height: %s" % my.get_height())
                top.add_style("border-radius: 50px")
                top.add_style("text-align: center")

                icon_div = DivWdg()
                top.add(icon_div)
                icon = IconWdg(name="notification", icon="BS_ENVELOPE")
                icon_div.add(icon)
                icon_div.add_style("margin: -20px auto 0px auto")
                return top

        from pyasm.command import BaseProcessTrigger
        class NotificationNodeHandler(BaseProcessTrigger):
            def execute(my):
                pipeline = my.input.get("pipeline")
                process = my.input.get("process")
                sobject = my.input.get("sobject")

                # send email
                print "sending email!!!!!"
                print "sending email!!!!!"
                print "sending email!!!!!"
                print "sending email!!!!!"
                print "sending email!!!!!"
                print "sending email!!!!!"
                print "sending email!!!!!"



        custom_node_wdg = NotificationNodeWdg()

        width = custom_node_wdg.get_width()
        height = custom_node_wdg.get_height()



        # add custom node behaviors
        node_behaviors = custom_node_wdg.get_node_behaviors()
        for node_behavior in node_behaviors:
            node.add_behavior( node_behavior )


        my.add_nobs(node, height, 5)


        node.add(custom_node_wdg)
        custom_node_wdg.add_class("spt_content")

        custom_node_wdg.add_style("width: %spx" % width)
        custom_node_wdg.add_style("height: %spx" % height)
        custom_node_wdg.add_style("border: solid 1px black")


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

        my.add_default_node_behaviors(node, text)

        return node







    def get_condition_node(my, name, process=None):

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



        # add custom node behaviors
        node_behaviors = my.get_node_behaviors()
        for node_behavior in node_behaviors:
            node.add_behavior( node_behavior )


        offset = width * 0.12 # size to corner of square

        my.add_nobs(node, height, 5)


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

        my.add_default_node_behaviors(node, text)

        return node





    def get_approval_node(my, name, process=None):

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



        # add custom node behaviors
        node_behaviors = my.get_node_behaviors()
        for node_behavior in node_behaviors:
            node.add_behavior( node_behavior )




        my.add_nobs(node, height)


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

        my.add_default_node_behaviors(node, text)

        return node



    def get_trigger_node(my):


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


        #my.add_nobs(node, height)

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


        my.add_default_node_behaviors(node, text)

        return node








    def get_connector(my, name, start, end):
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
        spt.pipeline.draw_connector(bvr.start, bvr.end);
        '''
        } )


        #connector.add_behavior( {
        #'type': 'drag'
        #} )

        return connector


    def get_canvas_behavior(my):
        return []

    def get_node_behaviors(my):
        return []

    def get_node_context_menu(my):

        menu = Menu(width=180)
        menu.set_allow_icons(False)
        menu.set_setup_cbfn( 'spt.dg_table.smenu_ctx.setup_cbk' )


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



    def get_onload_js(my):

        return r'''


spt.Environment.get().add_library("spt_pipeline");

spt.pipeline = {};


spt.pipeline.top = null;

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

    // FIXME: need this delay because the table seems to resize itself somewhere
    setTimeout( function() {
        var size = canvas.getSize()
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
    //var active = node.getElement(".spt_active");
    //active.setStyle("display", "");
    var content = node.getElement(".spt_content");
    content.setStyle("box-shadow", "0px 0px 15px rgba(128,128,128,1.0)");
    content.setStyle("border", "solid 1px rgba(128,128,0,1.0)");
    content.setStyle("opacity", "0.8");

    
    var group = spt.pipeline.get_group(node.spt_group);
    var group_type = group.get_group_type();
    if (group_type=='schema') {
        var event_name = 'stype|select';
        spt.named_events.fire_event(event_name, { src_el: node } );
    }
}


spt.pipeline.unselect_node = function(node) {
    node.setStyle("z-index", "100");
    node.spt_is_selected = false;
    //var active = node.getElement(".spt_active");
    //active.setStyle("display", "none");
    var content = node.getElement(".spt_content");
    content.setStyle("box-shadow", "");
    content.setStyle("border", "solid 1px black");
    content.setStyle("opacity", "1.0");
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
spt.pipeline.add_node = function(name, x, y, kwargs) {

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
        node_type = "node";
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
    if (!template) {
        alert("Can't find template for ["+template_class+"]");
        return;
    }


    var new_node = spt.behavior.clone(template);
    new_node.spt_node_type = node_type;


    canvas.appendChild(new_node);

    // make the label the last part
    var label_parts = name.split("/");
    var label_str = label_parts[label_parts.length-1];

    var label = new_node.getElement(".spt_label");
    var input = new_node.getElement(".spt_input");
    label.innerHTML = label_str;
    input.value = label_str;
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
    else // for schema {
        color = spt.pipeline.get_group_color(name);

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

    return new_node;
}



spt.pipeline.remove_nodes = function(nodes) {

    // remove the connectors that have this node
    var canvas = spt.pipeline.get_canvas();
    var connectors = canvas.connectors;

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
                spt.pipeline.delete_connector(connector);
            }
        }
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
    for (var j = nodes.length-1; j >= 0; j-- ) {
        var node = nodes[j];

        // remove the node from the group
        var group = spt.pipeline.get_group_by_node(node);
        group.remove_node(node);

        spt.behavior.destroy_element(node);
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
    var content= node.getElement(".spt_content");
    var color1 = spt.css.modify_color_value(color, +10);
    var color2 = spt.css.modify_color_value(color, -10);
    /*
    if( spt.browser.is_Firefox() ) {
        content.setStyle("background", "-moz-linear-gradient(top, "+color1+" 30%, "+color2+" 95%)");
    } 
    else {
        content.setStyle("background", "-webkit-gradient(linear, 0% 0%, 0% 100%, from("+color1+"), to("+color2+"))");
    }
    */

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



spt.pipeline.rename_node = function(node, value) {

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

spt.pipeline.add_folder = function(group_name, color) {

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

    var parts = group_name.split("/");
    var title = parts[parts.length-1];

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

    color = '#999'
    var color1 = spt.css.modify_color_value(color, +5);
    var color2 = spt.css.modify_color_value(color, -5);

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
spt.pipeline.node_drag_setup = function( evt, bvr, mouse_411) {
    spt.pipeline.init(bvr);
    spt.pipeline.last_node_pos = spt.pipeline.get_mouse_position(mouse_411);

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
}

spt.pipeline.node_drag_motion = function( evt, bvr, mouse_411) {
    var node = bvr.drag_el;
    var mouse_pos = spt.pipeline.get_mouse_position(mouse_411);
    var dx = mouse_pos.x - spt.pipeline.last_node_pos.x;
    var dy = mouse_pos.y - spt.pipeline.last_node_pos.y;
    var scale = spt.pipeline.get_scale();
    dx = dx/scale;
    dy = dy/scale;
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
    spt.named_events.fire_event('pipeline|change', {});
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
    
    if (data.line_mode == 'bezier') {
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
    }
    else {
        spt.pipeline.draw_line( node_pos, rel_pos );
    }

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
        to_node = spt.pipeline.add_node();
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

        connectors.push(connector);

        // add the connector to the source group
        var group = spt.pipeline.add_group(group_name);
        group.add_connector(connector);

        connector.select();

        // fire an event
        var top = bvr.src_el.getParent(".spt_pipeline_top");
        var event_name = top.getAttribute("id") + "|connector_create";
        spt.named_events.fire_event(event_name, { src_el: connector } );

    }

    spt.pipeline.redraw_canvas()
}


spt.pipeline.add_connector = function() {
    var canvas = spt.pipeline.get_canvas();
    var connector = new spt.pipeline.Connector();
    var connectors = canvas.connectors;
    connectors.push(connector);
    return connector;
}


spt.pipeline.delete_connector = function(connector) {
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

    spt.pipeline.clear_selected(); 
    return connector;
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
    outer.setStyle("height", ""+height);

    paint.setAttribute("width", ""+width);
    paint.setAttribute("height", ""+height);
    paint.setStyle("margin-top", "" + (-height));
    canvas.setStyle("width", ""+width);
    canvas.setStyle("height", ""+height);
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

    //scale = scale * 0.85;
    scale = 1.0

    // zero position at the specified scale
    //var zero_pos_x = size.x/2 - size.x/2 * scale;
    //var zero_pos_y = size.y/2 - size.y/2 * scale;


    var zero_pos_x = 100;
    var zero_pos_y = 100;

    var zero_pos_x = size.x/2 - hsize/2 - 100;
    var zero_pos_y = size.y/2 - vsize/2;

    var dx = - left + zero_pos_x; 
    var dy = - top + zero_pos_y;
    spt.pipeline.move_all_nodes(dx, dy);
    spt.pipeline.move_all_folders(dx, dy);

    spt.pipeline.set_scale(scale);

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
        from_pos = {x: from_pos.x + from_width, y: from_pos.y + from_height/2 };
        to_pos = {x: to_pos.x, y: to_pos.y + to_height/2 };

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

        spt.pipeline.draw_connector(from_pos, to_pos, this.color);

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


    this.select = function() {
        spt.pipeline.add_to_selected(this);
        this.set_color("red");
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
    
    var pipeline_xml = pipeline.pipeline;
    var pipeline_stype = pipeline.search_type;
    var xml_doc = spt.parse_xml(pipeline_xml);

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

    if (xml_nodes.length == 0) {
        spt.pipeline.add_folder(pipeline_code, color);
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

        console.log(name + ": " + node_type);
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
            if (value == '') {
                continue;
            }
            xml += ' '+key+'="'+value+'"';
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

    '''





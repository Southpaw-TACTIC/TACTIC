###########################################################
#
# Copyright (c) 2009, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#
__all__ = ["TileLayoutWdg"]

from pyasm.common import Common
from pyasm.search import Search, SearchKey
from pyasm.web import DivWdg, Table
from pyasm.widget import ThumbWdg, IconWdg, TextWdg, HiddenWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.container import SmartMenu

from table_layout_wdg import FastTableLayoutWdg
from tactic.ui.widget import IconButtonWdg, SingleButtonWdg



from tool_layout_wdg import ToolLayoutWdg
class TileLayoutWdg(ToolLayoutWdg):

    def get_content_wdg(my):
        div = DivWdg()
        div.add_class("spt_tile_layout_top")
        inner = DivWdg()
        div.add(inner)

        # set up the context menus
        menus_in = {
            'DG_HEADER_CTX': [ my.get_smart_header_context_menu_data() ],
            'DG_DROW_SMENU_CTX': [ my.get_data_row_smart_context_menu_details() ]
        }
        SmartMenu.attach_smart_context_menu( inner, menus_in, False )


        from tactic.ui.filter import FilterData
        filter_data = FilterData.get()
        data_list = filter_data.get_values_by_prefix("tile_layout")
        if data_list:
            data = data_list[0]
        else:
            data = {}
        my.scale = data.get("scale")

        
        inner.add_style("margin-left: 20px")

        if my.sobjects:
            inner.add( my.get_scale_wdg() )

            for sobject in my.sobjects:
                kwargs = my.kwargs.copy()
                tile = my.get_tile_wdg(sobject)
                inner.add(tile)
        else:
            table = Table()
            inner.add(table)
            my.handle_no_results(table)

        my.add_layout_behaviors(inner)


        inner.add("<br clear='all'/>")
        return div


    def add_layout_behaviors(my, layout_wdg):

        layout_wdg.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_tile_content',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var top = bvr.src_el.getParent(".spt_tile_top");
            var search_key = top.getAttribute("spt_search_key");
            var name = top.getAttribute("spt_name");
            var search_code = top.getAttribute("spt_search_code");
            var class_name = 'tactic.ui.tools.SObjectDetailWdg'
            var kwargs = {
                search_key: search_key
            }
            spt.tab.add_new(search_code, name, class_name, kwargs);
            '''
        } )

        bg1 = layout_wdg.get_color("background3")
        bg2 = layout_wdg.get_color("background3", 5)
        layout_wdg.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_tile_top',
            'cbjs_action': '''
            bvr.src_el.setStyle("opacity", "0.8");
            var el = bvr.src_el.getElement(".spt_tile_title");
            el.setStyle("background", "%s");
            ''' % bg2
        } )

        layout_wdg.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_tile_top',
            'cbjs_action': '''
            bvr.src_el.setStyle("opacity", "1.0");
            var el = bvr.src_el.getElement(".spt_tile_title");
            el.setStyle("background", "%s");
            ''' % bg1
        } )




    def get_tile_wdg(my, sobject):

        div = DivWdg()
        div.add_class("spt_tile_top")


        top_view = my.kwargs.get("top_view")
        if top_view:
            title_wdg = my.get_view_wdg(sobject, top_view)
        else:
            title_wdg = my.get_title(sobject)
        div.add( title_wdg )


        div.add_attr("spt_search_key", sobject.get_search_key())
        div.add_attr("spt_name", sobject.get_name())
        div.add_attr("spt_search_code", sobject.get_code())

        SmartMenu.assign_as_local_activator( div, 'DG_DROW_SMENU_CTX' )

        div.add_border()
        div.set_box_shadow()
        div.add_color("background", "background", -3)
        div.add_style("margin: 10px")
        div.add_style("overflow: hidden")

        div.add_style("float: left")

        thumb_div = DivWdg()
        thumb_div.add_class("spt_tile_content")
        div.add(thumb_div)

        width =  240
        height = 160

        thumb_div.add_style("width: %s" % width)
        thumb_div.add_style("height: %s" % height)
        thumb_div.add_style("overflow: hidden")

        thumb = ThumbWdg2()
        thumb.set_sobject(sobject)
        thumb_div.add(thumb)


        bottom_view = my.kwargs.get("bottom_view")
        if bottom_view:
            div.add( my.get_view_wdg(sobject, bottom_view) )


        return div


    def get_view_wdg(my, sobject, view):
        div = DivWdg()
        div.add_style("overflow: hidden")

        kwargs = {
            'search_key': sobject.get_search_key(),
            'sobject': sobject,
            'view': view,
        }
        from tactic.ui.panel import CustomLayoutWdg
        layout = CustomLayoutWdg(**kwargs)
        div.add(layout.get_buffer_display())
        return div




    def get_scale_wdg(my):


        div = DivWdg()
        div.add_style("padding: 5px")
        div.add_class("spt_table_search")
        hidden = HiddenWdg("prefix", "tile_layout")
        div.add(hidden)

        div.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
spt.tile_layout = {}
spt.tile_layout.layout = null;

spt.tile_layout.set_layout = function(layout) {
    if (!layout.hasClass("spt_layout")) {
        layout = layout.getParent(".spt_layout");
    }
    spt.tile_layout.layout = layout;
}

spt.tile_layout.get_scale = function() {
    var scale_value = spt.tile_layout.layout.getElement(".spt_scale_value");
    var value = scale_value.value;
    value = parseInt(value);
    return value;
}


spt.tile_layout.set_scale = function(scale) {

    var scale_value = spt.tile_layout.layout.getElement(".spt_scale_value");
    scale_value.value = scale;

    var size_x = 240*scale/100;
    var size_y = 160*scale/100;

    //var top = bvr.src_el.getParent(".spt_tile_layout_top");
    var top = spt.tile_layout.layout;
    var els = top.getElements(".spt_tile_content");
    for (var i = 0; i < els.length; i++) {
        var el = els[i];
        el.setStyle( "width",  size_x);
        el.setStyle( "height", size_y);
    }

}


spt.tile_layout.drag_start_x = null;
spt.tile_layout.drag_start_value = null;

spt.tile_layout.drag_setup = function(evt, bvr, mouse_411) {
    spt.tile_layout.set_layout(bvr.src_el);
    spt.tile_layout.drag_start_x = mouse_411.curr_x;
    var src_el = spt.behavior.get_bvr_src( bvr );
    if (!src_el.value) {
        src_el.value = 0;
    }
    spt.tile_layout.drag_start_value = src_el.value;
    src_el.focus();
    src_el.select();
}
spt.tile_layout.drag_motion = function(evt, bvr, mouse_411) {
    var start_value = spt.tile_layout.drag_start_value; 
    if (isNaN(parseInt(start_value))) {
        return;
    }
    var dx = mouse_411.curr_x - spt.tile_layout.drag_start_x;
    var increment = parseInt(dx / 5);
    var multiplier;
    if (increment < 0)
        multiplier = 0.975;
    else
        multiplier = 1 / 0.975;
    increment = Math.abs(increment);
    var scale = spt.tile_layout.drag_start_value;
    for (var i = 0; i < increment; i++) {
        scale = scale * multiplier;
    }
    scale = parseInt(scale);
    spt.tile_layout.set_scale(scale);

}


        ''' } )





        table = Table()
        div.add(table)
        table.add_row()

        less_div = DivWdg()
        less_div.add("<input type='button' value='&lt;&lt;'/>")
        table.add_cell(less_div)

        less_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tile_layout.set_layout(bvr.src_el);
            var scale = spt.tile_layout.get_scale();
            scale = scale * 0.95;
            scale = parseInt(scale);
            spt.tile_layout.set_scale(scale);
            '''
        } )


 
        value_wdg = TextWdg("scale")
        value_wdg.add_class("spt_scale_value")
        td = table.add_cell(value_wdg)
        td.add("&nbsp;%")
        td.add_style("padding: 3px 8px")
        if my.scale:
            value_wdg.set_value(my.scale)
        value_wdg.add_style("width: 24px")
        value_wdg.add_style("text-align: center")
        value_wdg.add_behavior( {
        'type': 'change',
        'cbjs_action': '''
        var value = bvr.src_el.value;
        var scale = parseInt(value);
        spt.tile_layout.set_layout(bvr.src_el);
        spt.tile_layout.set_scale(scale);
        '''
        } )
        value_wdg.add_behavior( {
        'type': 'load',
        'cbjs_action': '''
        var value = bvr.src_el.value;
        if (!value) {
            value = 100;
        }
        var scale = parseInt(value);
        spt.tile_layout.set_layout(bvr.src_el);
        spt.tile_layout.set_scale(scale);
        '''
        } )



 
        value_wdg.add_behavior( {
            'type': 'smart_drag',
            'bvr_match_class': 'spt_scale_value',
            'ignore_default_motion' : True,
            "cbjs_setup": 'spt.tile_layout.drag_setup( evt, bvr, mouse_411 );',
            "cbjs_motion": 'spt.tile_layout.drag_motion( evt, bvr, mouse_411 );'
        } )



        more_div = DivWdg()
        more_div.add("<input type='button' value='&gt;&gt;'/>")
        table.add_cell(more_div)

        more_div.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            spt.tile_layout.set_layout(bvr.src_el);
            var scale = spt.tile_layout.get_scale();
            scale = scale / 0.95;
            scale = parseInt(scale);
            spt.tile_layout.set_scale(scale);
            '''
        } )



        return div


    def get_title(my, sobject):
        div = DivWdg()

        div.add_class("spt_tile_title")

        div.add_color("background", "background3")
        div.add_style("padding: 5px")
        div.add_style("height: 15px")

        title = sobject.get_name()
        if not title:
            title = sobject.get_code()

        description = sobject.get_value("description")
        if description:
            div.add_attr("title", sobject.get_code())

        div.add(title)


        return div


from pyasm.biz import Snapshot
from pyasm.web import HtmlElement
__all__.append("ThumbWdg2")
class ThumbWdg2(BaseRefreshWdg):
    def get_display(my):

        width = "100%"


        div = DivWdg()

        path = my.get_path()
        if path:
            img = HtmlElement.img(src=path)
        else:
            img = DivWdg()
        img.add_class("spt_image")
        div.add(img)
        img.add_style("width: %s" % width)

        return div


    def get_path(my):
        icon_path = None
        path = None
        sobject = my.get_current_sobject()

        search_type = sobject.get_search_type()
        search_code = sobject.get_value("code", no_exception=True)
        if not search_code:
            search_code = sobject.get_id()
        snapshot = Snapshot.get_snapshot(search_type, search_code, context='icon')
        if not snapshot:
            snapshot = Snapshot.get_snapshot(search_type, search_code, context='publish')
        if snapshot:
            file_type = "web"
            icon_path = snapshot.get_web_path_by_type(file_type)

            file_type = "main"
            path = snapshot.get_web_path_by_type(file_type)

        if not icon_path and path:
            path = my.find_icon_link(path)
 
        return path


    def find_icon_link(my, file_path, repo_path=None):
        base = "/context/icons/mime-types"
        icon = None
        if not file_path:
            return ""
            #return ThumbWdg.get_no_image()
        #ext = File.get_extension(file_path)
        import os
        root, ext = os.path.splitext(file_path)
        ext = ext[1:]

        if ext == "xls":
            icon = "gnome-application-vnd.ms-excel.png"
        elif ext == "mp3" or ext == "wav":
            icon = "mp3_and_wav.jpg"
        elif ext == "aif" or ext == 'aiff':
            icon = "gnome-audio-x-aiff.png"
        elif ext == "mpg":
            icon = "gnome-video-mpeg.png"
        elif ext in ["mov", "MOV"] or ext == "mp4":
            icon = "quicktime-logo.png"    
        elif ext == "ma" or ext == "mb" or ext == "anim":
            icon = "maya.png"
        elif ext == "lwo":
            icon = "lwo.jpg"
        elif ext == "max":
            icon = "max.jpg"
        elif ext == "fbx":
            icon = "fbx.jpg"
        elif ext == "hip" or ext == "otl":
            icon = "houdini.png"
        elif ext in ["scn", "scntoc", "xsi"]:
            icon = "xsi_scn.jpg"
        elif ext == "emdl":
            icon = "xsi_emdl.png"
        elif ext == "fla":
            icon = "flash.png"
        elif ext == "dae":
            icon = "collada.png"
        elif ext == "pdf":
            icon = "pdficon_large.gif"
        elif ext == "shk":
            icon = "icon_shake_white.gif"
        elif ext == "comp":
            icon = "fusion.png"
        elif ext == "txt":
            icon = "gnome-textfile.png"
        elif ext == "obj":
            icon = "3d_obj.png"
        elif ext in ["rdc", "RDC"]:
            icon = "red_camera.png"
        elif ext == 'ps':
            icon = "ps_icon.jpg"
        elif ext == 'psd':
            icon = "ps_icon.jpg"
        elif ext == 'ai':
            icon = "icon_illustrator_lg.png"
        elif ext == 'unity3d':
            icon = "unity_icon.jpg"
        elif repo_path and os.path.isdir(repo_path):
            icon = "folder.png"
        else:
            icon = "default_doc.png"
        return "%s/%s" % ( base,icon)





class TileLayoutWdgOld(FastTableLayoutWdg):

    ARGS_KEYS = {

        "search_type": {
            'description': "search type that this panels works with",
            'type': 'TextWdg',
            'order': 0,
            'category': 'Required'
        },
        "view": {
            'description': "view to be displayed",
            'type': 'TextWdg',
            'order': 1,
            'category': 'Required'
        },
        "element_names": {
            'description': "Comma delimited list of elemnent to view",
            'type': 'TextWdg',
            'order': 1,
            'category': 'Optional'
        },


    } 


    def get_display(my):

        my.view_editable = True

        if my.kwargs.get("do_search") != "false":
            my.handle_search()

        my.kwargs['show_gear'] = 'false'


        # set the sobjects to all the widgets then preprocess
        for widget in my.widgets:
            widget.set_sobjects(my.sobjects)
            widget.set_parent_wdg(my)
            # preprocess the elements
            widget.preprocess()



        # extraneous variables inherited from TableLayoutWdg
        my.edit_permission = False

        top = DivWdg()
        my.set_as_panel(top)
        top.add_class("spt_sobject_top")

        inner = DivWdg()
        top.add(inner)

        inner.add_color("background", "background")
        inner.add_color("color", "color")
        #inner.add_style("background", "transparent")
        #inner.add_style("color", "FFF")
        #inner.add_style("opactiy: 0.8")


        inner.add_class("spt_table")
        inner.add_class("spt_layout")
        inner.add_attr("spt_version", "2")



        # add an upload_wdg
        from tactic.ui.input import Html5UploadWdg
        upload_wdg = Html5UploadWdg()
        inner.add(upload_wdg)
        my.upload_id = upload_wdg.get_upload_id()

        # set up the context menus
        menus_in = {
            'DG_HEADER_CTX': [ my.get_smart_header_context_menu_data() ],
            'DG_DROW_SMENU_CTX': [ my.get_data_row_smart_context_menu_details() ]
        }
        SmartMenu.attach_smart_context_menu( inner, menus_in, False )




        thumb = ThumbWdg()
        thumb.handle_layout_behaviors(inner)

        is_refresh = my.kwargs.get("is_refresh")
        if my.kwargs.get("show_shelf") not in ['false', False]:
            action = my.get_action_wdg()
            inner.add(action)

        scale_wdg = my.get_scale_wdg()
        inner.add(scale_wdg)

        content = DivWdg()
        inner.add(content)

        index = 0

        for sobject in my.sobjects:
            sobject_div = DivWdg()
            content.add(sobject_div)
            sobject_div.add_class("spt_sobject_tile")

            SmartMenu.assign_as_local_activator( sobject_div, 'DG_DROW_SMENU_CTX' )

            # FIXME: this should likely be more generic
            sobject_div.add_class("spt_table_row")
            sobject_div.add_attr("spt_search_key", sobject.get_search_key(use_id=True))



            #sobject_div.add_border()
            sobject_div.add_style('margin-top: 5')
            #sobject_div.add_style('margin-left: -1')
            sobject_div.add_style('padding-left: 5px')
            sobject_div.add_style('padding-right: 5px')

            sobject_div.add_style('float: left')
            sobject_div.add_style("vertical-align: top")

            my.scale = 0.5
            width = 250*my.scale
            height = 220*my.scale

            sobject_div.add_style("width: %spx" % width)
            sobject_div.add_style("height: %spx" % height)


            sobject_div.add_gradient("background", "background", 0, -5)
            sobject_div.add_style("overflow: hidden")

            """
            detail_button = SingleButtonWdg(title='Show Detail', icon=IconWdg.ZOOM)
            code = sobject.get_code()
            search_key = SearchKey.get_by_sobject(sobject)

            sobject_div.add(detail_button)
            detail_button.add_style("float: right")
            detail_button.add_behavior( {
            'type': 'click_up',
            'code': code,
            'search_key': search_key,
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var element_name = "detail_" + bvr.code;
            var title = "Detail ["+bvr.code+"]";
            var class_name = 'tactic.ui.tools.SObjectDetailWdg';
            var kwargs = {
                search_key: bvr.search_key
            };
            spt.tab.add_new(element_name, title, class_name, kwargs);
            '''
            } )
            """

            sobject_div.add( my.get_default_card_wdg(sobject) )


        top.add_class("spt_table_top");
        class_name = Common.get_full_class_name(my)
        top.add_attr("spt_class_name", class_name)


        # NOTE: adding a fake header to conform to a table layout.  Not
        # sure if this is the correct interface for this
        header_row_div = DivWdg()
        header_row_div.add_class("spt_table_header_row")
        content.add(header_row_div)
        content.add_class("spt_table_table");

        my.handle_load_behaviors(content)

        inner.add_class("spt_table_content");
        inner.add_attr("spt_search_type", my.kwargs.get('search_type'))
        inner.add_attr("spt_view", my.kwargs.get('view'))

        inner.add("<br clear='all'/>")
        inner.add("<br clear='all'/>")



        limit_span = DivWdg()
        inner.add(limit_span)
        limit_span.add_style("margin-top: 4px")
        limit_span.add_class("spt_table_search")
        limit_span.add_style("width: 250px")
        limit_span.add_style("margin: 5 auto")
        
        info = my.search_limit.get_info()
        if info.get("count") == None:
            info["count"] = len(my.sobjects)

        from tactic.ui.app import SearchLimitSimpleWdg
        limit_wdg = SearchLimitSimpleWdg(
            count=info.get("count"),
            search_limit=info.get("search_limit"),
            current_offset=info.get("current_offset"),
        )
        inner.add(limit_wdg)




        if my.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top


    def get_scale_wdg(my):
        scale_wdg = DivWdg()
        scale_wdg.add_class("spt_scale_top")
        scale_wdg.add_color("background", "background", -10)
        scale_wdg.add_style("padding: 5px")


        scale_wdg.add_behavior( {
            'type': 'load',
            'cbjs_action': '''
spt.tile_layout = {};
spt.tile_layout.layout = null;

spt.tile_layout.set_layout = function(layout) {
    if (!layout.hasClass("spt_layout")) {
        layout = layout.getParent(".spt_layout");
    }
    spt.tile_layout.layout = layout;
}

spt.tile_layout.get_scale = function() {
    var scale_value = spt.tile_layout.layout.getElement(".spt_scale_value");
    var value = scale_value.value;
    value = parseInt(value);
    return value;
}


spt.tile_layout.set_scale = function(scale) {

    var scale_value = spt.tile_layout.layout.getElement(".spt_scale_value");
    scale_value.value = scale;

    var size_x = 120*scale/100;
    var size_y = 80*scale/100;

    var top = spt.tile_layout.layout;
    var tiles = top.getElements(".spt_sobject_tile");
    var divs = top.getElements(".spt_thumb_div");
    var images = top.getElements(".spt_image");
    for ( var i = 0; i < tiles.length; i++) {

        tiles[i].setStyle("width", size_x);
        tiles[i].setStyle("height", size_y+20);

        divs[i].setStyle("width", size_x);
        divs[i].setStyle("height", size_y);

        images[i].setStyle("width", size_x);
        images[i].setStyle("height", size_y);
    }
}
        ''' } )



        from pyasm.web import Table
        from pyasm.widget import TextWdg, IconWdg
        from tactic.ui.widget import IconButtonWdg

        table = Table()
        scale_wdg.add(table)
        table.add_row()

        table.add_cell("<b>Scale: </b>")


        icon = IconButtonWdg(tip="Smaller", icon=IconWdg.LEFT)
        td = table.add_cell(icon)
        icon.add_style("float: left")
        icon.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tile_layout.set_layout(bvr.src_el);
        var scale = spt.tile_layout.get_scale();
        scale = scale * 0.9;
        scale = parseInt(scale);
        spt.tile_layout.set_scale(scale);
        '''
        } )


        value_wdg = TextWdg()
        value_wdg.add_class("spt_scale_value")
        td = table.add_cell(value_wdg)
        td.add("%")
        value_wdg.set_value("100")
        value_wdg.add_style("width: 24px")
        value_wdg.add_style("text-align: center")
        #value_wdg.add_style("float: left")
        value_wdg.add_behavior( {
        'type': 'change',
        'cbjs_action': '''

        var value = bvr.src_el.value;
        value = parseInt(value);

        var size_x = 120*value/100;
        var size_y = 80*value/100;

        var top = bvr.src_el.getParent(".spt_layout");
        var tiles = top.getElements(".spt_sobject_tile");
        var divs = top.getElements(".spt_thumb_div");
        var images = top.getElements(".spt_image");
        for ( var i = 0; i < tiles.length; i++) {

            tiles[i].setStyle("width", size_x);
            tiles[i].setStyle("height", size_y+20);

            divs[i].setStyle("width", size_x);
            divs[i].setStyle("height", size_y);

            images[i].setStyle("width", size_x);
            images[i].setStyle("height", size_y);
        }
        '''
        } )


        icon = IconButtonWdg(tip="Larger", icon=IconWdg.RIGHT)
        table.add_cell(icon)
        icon.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
        spt.tile_layout.set_layout(bvr.src_el);
        var scale = spt.tile_layout.get_scale();
        scale = scale * 1.1;
        scale = parseInt(scale);
        spt.tile_layout.set_scale(scale);
        '''
        } )



        return scale_wdg

    def get_default_card_wdg(my, sobject):

        div = DivWdg()
        div.add_style("overflow", "hidden")
        div.add_border()

        title_div = DivWdg()
        div.add(title_div)

        title_div.add_style("height: 15px")
        title_div.add_gradient("background", "background", -10)
        title_div.add_style("vertical-align: middle")
        title_div.add_style("padding: 3px 0 0 5px")
        title_div.add_style("font-weight: bold")


        title_div.add(sobject.get_name() )
        #if sobject.has_value("name"):
        #    title_div.add( sobject.get_value("name") )


        edit_div = DivWdg()
        title_div.add(edit_div)
        edit_div.add_style("float: right")
        edit_div.add_style("margin-top: -5px")

        edit_button = IconButtonWdg(title='Edit', icon=IconWdg.EDIT)
        edit_button.add_style("display: none")
        edit_div.add(edit_button)

        search_type = sobject.get_search_type()
        search_id = sobject.get_id()
        edit_button.add_behavior( {
        'type': 'click_up',
        'search_type': search_type,
        'search_id': search_id,
        'cbjs_action': '''
        var class_name = 'tactic.ui.panel.EditWdg';
        var kwargs = {
            search_type: bvr.search_type,
            search_id: bvr.search_id
        };
        spt.panel.load_popup("Edit", class_name, kwargs);
        '''
        } )


        thumb_div = DivWdg()
        div.add( thumb_div )
        thumb_div.add_class("spt_thumb_div")
        thumb_div.add_style("height: 180px")
        thumb_div.add_color("background", "background3")
        thumb_div.add_style("overflow", "hidden")

        thumb = ThumbWdg()
        thumb_div.add(thumb)
        thumb.set_sobject(sobject)
        thumb.set_option("aspect", "height")
        thumb.set_icon_size("%s" % int(180*my.scale))

        #padding_left = 35*(my.scale)
        #thumb_div.add_style("padding-left: %spx" % padding_left)


        detail_div = DivWdg()
        div.add(detail_div)
        detail_div.add_style("height: 50px")
        detail_div.add_style("overflow-y: auto")
        detail_div.add_color("background", "background")
        detail_div.add_style("opacity: 0.85")

        table = Table()
        detail_div.add(table)

        table.add_color("color", "color")
        table.add_style("margin-top: 10px")

        if sobject.has_value("title"):
            table.add_row()
            td = table.add_cell("Title: ")
            td.add_style("vertical-align: top")
            td.add_style("width: 50%")
            title = sobject.get_value("title")
            td = table.add_cell()
            if not title:
                title = "<i>-- None --</i>"
                td.add_style("opacity: 0.5")
            td.add(title)



        if sobject.has_value("description"):
            table.add_row()
            td = table.add_cell("Description: ")
            td.add_style("vertical-align: top")
            td.add_style("width: 50%")
            description = sobject.get_value("description")
            td = table.add_cell()
            if not description:
                description = "<i>-- None --</i>"
                td.add_style("opacity: 0.5")
            td.add(description)


        if sobject.has_value("keywords"):
            table.add_row()
            td = table.add_cell("Keywords: ")
            td.add_style("vertical-align: top")
            td.add_style("width: 50%")
            keywords = sobject.get_value("keywords")
            keywords = keywords.split(" ")

            td = table.add_cell()
            td.add_color("color", "color3")
            for keyword in keywords:
                keyword_div = DivWdg()
                td.add(keyword_div)
                keyword_div.add_style("float: left")
                keyword_div.add_style("padding: 1 3 1 3")
                keyword_div.add_style("margin: 2 3 2 3")
                keyword_div.add(keyword)
                keyword_div.add_color("background", "background3")
                keyword_div.set_round_corners()


        return div




    def get_card_wdg(my, sobject):

        show_title = my.kwargs.get("show_title")
        show_title = True
        if show_title in ['true', True]:
            show_title = True
        else:
            show_title = False


        sobject_div = DivWdg()

        for widget in my.widgets:

            # Not sure why this doesn't work on a reused widget
            if isinstance(widget, ThumbWdg):
                widget = ThumbWdg()

            widget.set_sobject(sobject)

            if show_title:
                sobject_div.add( widget.get_title() )
                sobject_div.add( ": " )

            sobject_div.add( widget.get_buffer_display() )
            sobject_div.add('<br/>')

        return sobject_div



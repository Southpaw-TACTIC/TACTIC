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
from pyasm.widget import ThumbWdg, IconWdg
from tactic.ui.container import SmartMenu

from table_layout_wdg import FastTableLayoutWdg
from tactic.ui.widget import IconButtonWdg, SingleButtonWdg

class TileLayoutWdg(FastTableLayoutWdg):

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
        value_wdg.add_style("text-align: right")
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


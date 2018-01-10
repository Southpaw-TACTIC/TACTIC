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
__all__ = ["ToolLayoutWdg","CustomLayoutWithSearchWdg", "CustomAggregateWdg", "CustomItemLayoutWithSearchWdg","RepoBrowserLayoutWdg","CardLayoutWdg"]

from pyasm.common import Common, Container
from pyasm.search import Search, SearchKey
from pyasm.web import DivWdg, Table
from pyasm.widget import ThumbWdg, IconWdg
from tactic.ui.container import SmartMenu

from table_layout_wdg import FastTableLayoutWdg
from tactic.ui.widget import IconButtonWdg, SingleButtonWdg

class ToolLayoutWdg(FastTableLayoutWdg):

    ARGS_KEYS = {
        "search_type": {
            'description': "Search type that this panels works with",
            'type': 'TextWdg',
            'order': 0,
            'category': 'Required'
        },
         "search_limit_mode": {
            'description': "Determine whether to show the simple search limit at just top, bottom, or both'",
            'type': 'TextWdg',
            'order': 1,
            'category': 'Display'
        },
        "expand_mode" : {
            'description': 'Support Tile Layout gallery, single_gallery, plain, detail, and custom mode',
            'type': 'SelectWdg',
            'values': 'gallery|single_gallery|plain|detail|custom',
            'order' : '2',
            'category': 'Display'

        },
        "tool_icon" : {
            'description': 'Add icons to the no-content pane which indicates tools to modify settings. Also takes a | seperated list of icon keys.',
            'type': 'IconSelectWdg',
            'order' : '3',
            'category': 'Display'
        },
        "tool_msg" : {
            'description': 'Add a message to the no-content pane which indicates how users can modify settings.',
            'type': 'TextWdg',
            'order' : '4',
            'category': 'Display'
        },
        "show_border": {
            'description': "determines whether or not to show borders on the table",
            'type': 'SelectWdg',
            'values': 'true|false',
            "order": '5',
            'category': 'Display'
        },
        "show_collection_tool": {
            'description': "determines whether to show the collection button or not",
            'type': 'SelectWdg',
            'values': 'true|false',
            "order": '6',
            'category': 'Display'
        }
    } 

    def can_inline_insert(my):
        return False

    def can_save(my):
        return False

    def can_expand(my):
        return False

    def can_add_columns(my):
        return False

    def can_select(my):
        return False

    def can_use_gear(my):
        return True

    def can_use_search(my):
        return True


    def init(my):
        # set up the context menus
        my.show_context_menu = my.kwargs.get("show_context_menu")
        if my.show_context_menu in ['false', False]:
            my.show_context_menu = False
        elif my.show_context_menu == 'none':
            pass
        else:
            my.show_context_menu = True

        my.expand_mode = my.kwargs.get("expand_mode")
        my.process = my.kwargs.get("process")
       


    def handle_no_results(my, table):
        super(ToolLayoutWdg, my).handle_no_results(table)
        table.add_style("width: 100%")
        return

        
    def get_display(my):

        my.view_editable = True



        #if my.kwargs.get("do_search") != "false":
        #    my.handle_search()
        my._process_search_args()


        #my.kwargs['show_gear'] = 'false'

        from tile_layout_wdg import TileLayoutWdg
        my.tile_layout = TileLayoutWdg(search_type=my.search_type, expand_mode=my.expand_mode, process=my.process)


        # set the sobjects to all the widgets then preprocess
        for widget in my.widgets:
            widget.set_sobjects(my.sobjects)
            widget.set_parent_wdg(my)
            # preprocess the elements
            widget.preprocess()


        """
        # TEST code to return only the content
        temp = my.kwargs.get("temp")
        if temp:
            content = DivWdg()
            content.add( my.get_content_wdg() )
            return content
        """





        # extraneous variables inherited from TableLayoutWdg
        my.edit_permission = True

        top = my.top
        my.set_as_panel(top)
        top.add_class("spt_sobject_top")
        top.add_class("spt_layout_top")

        inner = DivWdg()
        top.add(inner)
        # This is handled elsewhere
        #inner.add_color("background", "background")
        inner.add_color("color", "color")
        inner.add_attr("spt_version", "2")
        inner.add_class("spt_table")
        inner.add_class("spt_layout")
        my.layout_wdg = inner

        class_name = Common.get_full_class_name(my)
        inner.add_attr("spt_class_name", class_name)


        if not Container.get_dict("JSLibraries", "spt_html5upload"):
            from tactic.ui.input import Html5UploadWdg
            upload_wdg = Html5UploadWdg()
            inner.add(upload_wdg)
            my.upload_id = upload_wdg.get_upload_id()

            inner.add_attr('upload_id',my.upload_id)
        
        
        
        # this interferes with Html5Upload function on first load, commenting it out
        #thumb = ThumbWdg()
        #thumb.handle_layout_behaviors(inner)

        is_refresh = my.kwargs.get("is_refresh")
        if my.kwargs.get("show_shelf") not in ['false', False]:
            action = my.get_action_wdg()
            inner.add(action)
        
        info = my.search_limit.get_info()
        if info.get("count") == None:
            info["count"] = len(my.sobjects)

        show_search_limit = my.kwargs.get("show_search_limit")
        if show_search_limit in ['false', False]:
            search_limit_mode = None
        else:
            search_limit_mode = my.kwargs.get('search_limit_mode') 
            if not search_limit_mode:
                search_limit_mode = 'bottom'



        if search_limit_mode in ['top','both']:
            from tactic.ui.app import SearchLimitSimpleWdg
            limit_wdg = SearchLimitSimpleWdg(
                count=info.get("count"),
                search_limit=info.get("search_limit"),
                current_offset=info.get("current_offset")
            )
            inner.add(limit_wdg)

        content = DivWdg()
        inner.add( content )
        content.add( my.get_content_wdg() )


        # NOTE: a lot of scaffolding to convince that search_cbk that this
        # is a proper layout
        top.add_class("spt_table_top");
        class_name = Common.get_full_class_name(my)
        top.add_attr("spt_class_name", class_name)


        # NOTE: adding a fake header to conform to a table layout.  Not
        # sure if this is the correct interface for this
        header_row_div = DivWdg()
        header_row_div.add_class("spt_table_header_row")
        content.add(header_row_div)
        content.add_class("spt_table_table")
        content.set_id(my.table_id)

        my.handle_load_behaviors(content)


        inner.add_class("spt_table_content");
        inner.add_attr("spt_search_type", my.kwargs.get('search_type'))
        inner.add_attr("spt_view", my.kwargs.get('view'))


        limit_span = DivWdg()
        inner.add(limit_span)
        limit_span.add_style("margin-top: 4px")
        limit_span.add_class("spt_table_search")
        limit_span.add_style("width: 250px")
        limit_span.add_style("margin: 5 auto")

      
        inner.add_attr("total_count", info.get("count"))

               
        if search_limit_mode in ['bottom','both']:
            from tactic.ui.app import SearchLimitSimpleWdg
            limit_wdg = SearchLimitSimpleWdg(
                count=info.get("count"),
                search_limit=info.get("search_limit"),
                current_offset=info.get("current_offset"),
            )
            inner.add(limit_wdg)



        my.add_layout_behaviors(inner)

        if my.kwargs.get("is_refresh") == 'true':
            return inner
        else:
            return top


    def add_layout_behaviors(my, layout_wdg):


        #my.tile_layout.add_layout_behaviors(layout_wdg)

        """
        layout_wdg.add_relay_behavior( {
            'type': 'click',
            'bvr_match_class': 'spt_item_content',
            'cbjs_action': '''
            spt.tab.set_main_body_tab();
            var top = bvr.src_el.getParent(".spt_item_top");
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
        

        main_bg1 = layout_wdg.get_color("background")
        main_bg2 = layout_wdg.get_color("background", 5)

        bg1 = layout_wdg.get_color("background3")
        bg2 = layout_wdg.get_color("background3", 5)
        layout_wdg.add_relay_behavior( {
            'type': 'mouseover',
            'bvr_match_class': 'spt_item_top',
            'cbjs_action': '''
            bvr.src_el.setStyle('background', '%s');
            var el = bvr.src_el.getElement(".spt_tile_title");
            if (el) {
                el.setStyle("background", "%s");
            }
            ''' % (main_bg2, bg2)
        } )

        layout_wdg.add_relay_behavior( {
            'type': 'mouseout',
            'bvr_match_class': 'spt_item_top',
            'cbjs_action': '''
            bvr.src_el.setStyle('background', '%s');
            var el = bvr.src_el.getElement(".spt_tile_title");
            if (el) {
                el.setStyle("background", "%s");
            }
            ''' %(main_bg1, bg1)
        } )
        """





    def get_content_wdg(my):

        div = DivWdg()
        div.add_class("spt_tool_top")

        #table = Table()
        from tactic.ui.container import ResizableTableWdg
        from table_layout_wdg import FastTableLayoutWdg

        #table = ResizableTableWdg()
        table = Table()
        table.add_style("table-layout", "fixed")
        table.add_style("width: 100%")
        div.add(table)
        table.add_row()

        td = table.add_cell()
        #td.add_style("width: 30%")


        kwargs = my.kwargs.copy()


        td.add_style("vertical-align: top")
        layout_div = DivWdg()
        layout_div.add_style("min-height: 500px")
        layout_div.add_style("height: auto")
        td.add(layout_div)
        #td.add_style("overflow: hidden")
        kwargs['height'] = 500

        kwargs['show_shelf'] = False
        kwargs['show_search_limit'] = False
        kwargs['expand_on_load'] = True

        layout = FastTableLayoutWdg(**kwargs)
        layout_div.add(layout)
        layout.set_sobjects(my.sobjects)
        #from tactic.ui.panel import TileLayoutWdg
        #layout = TileLayoutWdg(**my.kwargs)
        #layout_div.add(layout)


        td = table.add_cell()
        td.add_border(color="#EEE")
        td.add_style("vertical-align: top")

        content = DivWdg()
        td.add(content)
        content.add_class("spt_tool_content")
        content.add_border(color="#EEE")
        content.add_style("margin: -1px")
        content.add_style("height: auto")
        #content.add_style("padding: 0px 20px")



        no_content_wdg = DivWdg()
        content.add(no_content_wdg)
        no_content_wdg.add("<br/>"*3)

        '''
        The no content message displays tool icons
        and a message in format:
                         <tools>
                          <msg>
        '''
        tool_icons = my.kwargs.get('tool_icon')
        if isinstance(tool_icons, basestring):
            tool_icon_lst = tool_icons.split("|")
        else:
            tool_icon_lst = None

        if tool_icon_lst:
            for icon in tool_icon_lst:
                icon = IconWdg(icon=icon) 
                icon.add_style("padding", "5px")
                no_content_wdg.add(icon)
            no_content_wdg.add("</br></br>")
       
        tool_msg = my.kwargs.get('tool_msg')
        if tool_msg:
            no_content_wdg.add("<p>%s<p>" % tool_msg)
        else:
            no_content_wdg.add("Click the tool(s) to modify settings.") 
       
        #no_content_wdg.add_style("opacity: 0.5")
        no_content_wdg.add_style("margin: 30px auto")
        no_content_wdg.add_color("color", "color3")
        no_content_wdg.add_color("background", "background3")
        no_content_wdg.add_style("text-align", "center")
        no_content_wdg.add_style("padding-top: 20px")
        no_content_wdg.add_style("padding-bottom: 20px")
        no_content_wdg.add_style("width: 350px")
        no_content_wdg.add_style("height: 110px")
        no_content_wdg.add_style("margin: 30px auto")
        no_content_wdg.add_border()


        return div







from custom_layout_wdg import CustomLayoutWdg
class CustomLayoutWithSearchWdg(ToolLayoutWdg):

    ARGS_KEYS = CustomLayoutWdg.ARGS_KEYS.copy()
    ARGS_KEYS['search_type'] = 'search type of the sobject to be displayed'

    def init(my):
        my.do_search = False
        super(CustomLayoutWithSearchWdg, my).init()

    def get_content_wdg(my):
        kwargs = my.kwargs.copy()
        kwargs["search"] = my.search
        layout = CustomLayoutWdg(**kwargs)
        layout.set_sobjects(my.sobjects)
        return layout


class CustomAggregateWdg(CustomLayoutWithSearchWdg):

    def init(my):
        my.do_search = False
        super(CustomLayoutWithSearchWdg, my).init()





class CustomItemLayoutWithSearchWdg(ToolLayoutWdg):

    ARGS_KEYS = CustomLayoutWdg.ARGS_KEYS.copy()
    ARGS_KEYS['search_type'] = 'search type of the sobject to be displayed'

    def get_content_wdg(my):
        div = DivWdg()
        for sobject in my.sobjects:
            kwargs = my.kwargs.copy()
            layout = CustomLayoutWdg(**kwargs)
            layout.set_sobjects(my.sobjects)
            layout.set_sobject(sobject)
            div.add(layout)
        div.add("<br clear='all'/>")
        return div





class RepoBrowserLayoutWdg(ToolLayoutWdg):

    ARGS_KEYS = CustomLayoutWdg.ARGS_KEYS.copy()
    ARGS_KEYS['search_type'] = 'search type of the sobject to be displayed'

    def can_use_gear(my):
        return False

    def get_content_wdg(my):

        sobjects = my.sobjects

        from tactic.ui.tools import RepoBrowserWdg
        kwargs = my.kwargs.copy()

        kwargs['search'] = my.search

        kwargs['open_depth'] = 1
        layout = RepoBrowserWdg(**kwargs)
        #layout.set_sobjects(my.sobjects)
        return layout




class CardLayoutWdg(ToolLayoutWdg):

    ARGS_KEYS = CustomLayoutWdg.ARGS_KEYS.copy()
    ARGS_KEYS['search_type'] = 'search type of the sobject to be displayed'


    def add_layout_behaviors(my, layout_wdg):
        my.tile_layout.add_layout_behaviors(layout_wdg)




    def get_content_wdg(my):
        div = DivWdg()

        inner = DivWdg()
        div.add(inner)

        # set up the context menus
        menus_in = {
            #'DG_HEADER_CTX': [ my.get_smart_header_context_menu_data() ],
            'DG_DROW_SMENU_CTX': [ my.get_data_row_smart_context_menu_details() ]
        }
        SmartMenu.attach_smart_context_menu( inner, menus_in, False )

        if my.sobjects:
            for i, sobject in enumerate(my.sobjects):
                if i == 0:
                    my.first = True
                else:
                    my.first = False
                
                inner.add(my.get_item_wdg(sobject))
                inner.add("<hr/>")
        else:
            table = Table()
            inner.add(table)
            my.handle_no_results(table);

        return div



    def get_shelf_wdg(my):
        return my.tile_layout.get_scale_wdg()



    def get_item_wdg(my, sobject):

        my.element_names = my.kwargs.get("element_names")
        if not my.element_names:
            my.element_names = ["preview","code","name","description",]
        else:
            my.element_names = my.element_names.split(",")

        if my.element_names[0] == "preview":
            has_preview = True
            my.element_names = my.element_names[1:]
        else:
            has_preview = False

        view = my.kwargs.get("view")
        if not view:
            view = "table"
        from pyasm.widget import WidgetConfigView
        search_type = sobject.get_search_type()
        my.config = WidgetConfigView.get_by_search_type(search_type, view)



        div = DivWdg()
        div.add_class("spt_item_top")
        div.add_style("padding: 10px")
        SmartMenu.assign_as_local_activator( div, 'DG_DROW_SMENU_CTX' )
        #div.add_class("spt_table_row")
        #div.add_class("spt_table_row_%s" % my.table_id)
        div.add_attr("spt_search_key", sobject.get_search_key(use_id=True))
        div.add_attr("spt_search_code", sobject.get_code())
        name = sobject.get_value("name", no_exception=True)
        if not name:
            name = sobject.get_code()
        div.add_attr("spt_name", name)

        table = Table()

        div.add(table)
        table.set_max_width()
        tr = table.add_row()

        width = my.kwargs.get("preview_width")
        if not width:
            width = "240px"

        if has_preview:
            td = table.add_cell()
            td.add_style("width: %s" % width);
            td.add_style("vertical-align: top")

            options = my.config.get_display_options("preview")
            redirect_expr = options.get("redirect_expr")
            if redirect_expr:
                parent = Search.eval(redirect_expr, sobject, single=True)
                #parent = sobject.get_parent()
                tile_wdg = my.tile_layout.get_tile_wdg(parent)
            else:
                tile_wdg = my.tile_layout.get_tile_wdg(sobject)

            td.add(tile_wdg)

        info_div = my.get_info_wdg(sobject)
        td = table.add_cell(info_div)
        td.add_style("vertical-align: top")


        return div


    def get_info_wdg(my, sobject):

        div = DivWdg()
        div.add_style("margin: 10px 20px 20px 20px")
        div.add_style("padding: 0px 20px")
        #div.add_color("background", "background", -3)
        #div.add_border()
        #div.add_color("color", "color3")
        #div.set_round_corners(5)

        div.add_style("height", "100%")
        div.add_style("position: relative")

        element_names = my.element_names
        config = my.config


        table = Table()
        table.add_style("height", "100%")
        div.add(table)
        for element_name in element_names:
            table.add_row()
            title = Common.get_display_title(element_name)
            td = table.add_cell("%s: " % title)
            td.add_style("width: 200px")
            td.add_style("padding: 5px")


            element = config.get_display_widget(element_name)

            if my.first:
                try:
                    element.handle_layout_behaviors(my.layout_wdg)
                except Exception as e:
                    print "e :", e
                    pass


            element.set_sobject(sobject)
            element.preprocess()
            td = table.add_cell(element)
            td.add_style("padding: 5px")
            #value = sobject.get_value(element_name, no_exception=True) or "N/A"
            #table.add_cell(value)


        show_notes = my.kwargs.get("show_notes")
       
        if show_notes in [True, 'true']:
            div.add("<br/>")
            from tactic.ui.widget import DiscussionWdg
            search_key = sobject.get_search_key()
            notes_wdg = DiscussionWdg(search_key=search_key)
            notes_wdg.set_sobject(sobject)
            div.add(notes_wdg)

        return div




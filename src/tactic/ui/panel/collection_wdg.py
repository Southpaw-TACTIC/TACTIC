###########################################################
#
# Copyright (c) 2005, Southpaw Technology
#                     All Rights Reserved
#
# PROPRIETARY INFORMATION.  This software is proprietary to
# Southpaw Technology, and is not to be reproduced, transmitted,
# or disclosed in any way without written permission.
#
#
#


__all__ = ["CollectionAddWdg", "CollectionAddCmd", "CollectionListWdg", "CollectionItemWdg", "CollectionLayoutWdg", "CollectionContentWdg", "CollectionRemoveCmd", "CollectionDeleteCmd"]



from pyasm.common import Common, Environment, Container, TacticException
from pyasm.search import SearchType, Search
from pyasm.web import DivWdg, Table, SpanWdg
from pyasm.command import Command
from pyasm.widget import CheckboxWdg, IconWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ButtonNewWdg, IconButtonWdg, ActionButtonWdg
from tactic.ui.container import DialogWdg
from tactic.ui.input import LookAheadTextInputWdg

from tool_layout_wdg import ToolLayoutWdg

import re


class CollectionAddWdg(BaseRefreshWdg):

    def get_display(my):
        search_type = my.kwargs.get("search_type")

        search = Search(search_type)
        if not search.column_exists("_is_collection"):
            return my.top

        search.add_filter("_is_collection", True)
        collections = search.get_sobjects()

        top = my.top
        top.add_class("spt_dialog")
        button = IconButtonWdg(title='Add to Collection', icon="BS_TH_LARGE", show_arrow=True)
        top.add(button)

        detail_wdg = DivWdg()
        top.add(detail_wdg)

        dialog = DialogWdg()
        top.add(dialog)
        
        dialog.set_as_activator(button, offset={'x':-25,'y': 0})
        dialog.add_title("Collections")

        dialog.add("<div style='margin: 10px'><b>Add selected items to a collection</b></div>")

        add_div = DivWdg()
        dialog.add(add_div)
        icon = IconWdg(name="Add new collection", icon="BS_PLUS")
        icon.add_style("opacity: 0.6")
        icon.add_style("padding-right: 3px")
        add_div.add(icon)
        add_div.add("Create new Collection")
        add_div.add_style("text-align: center")
        add_div.add_style("background-color: #EEEEEE")
        add_div.add_style("padding: 5px")
        add_div.add_style("height: 20px")
        add_div.add_class("hand")


        insert_view = "edit_collection"

        add_div.add_behavior( {
            'type': 'click_up',
            'insert_view': insert_view,
            'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_table_top");
                var table = top.getElement(".spt_table");
                var search_type = top.getAttribute("spt_search_type");
                
                // Hide the dialog when popup loads.
                var dialog_top = bvr.src_el.getParent(".spt_dialog_top");
                dialog_top.style.visibility = "hidden";

                kwargs = {
                  search_type: search_type,
                  mode: "insert",
                  view: bvr.insert_view,
                  save_event: bvr.event_name,
                  show_header: false,
                  'num_columns': 2,
                  default: {
                    _is_collection: true
                  }
                };
                spt.panel.load_popup("Add New Collection", "tactic.ui.panel.EditWdg", kwargs);
            '''
        } )

        content_div = DivWdg()
        dialog.add(content_div)
        content_div.add_style("width: 270px")
        content_div.add_style("padding: 5px")
        content_div.add_style("padding-bottom: 0px")

        custom_cbk = {}
        custom_cbk['enter'] = '''

            var top = bvr.src_el.getParent(".spt_dialog");
            var input = top.getElement(".spt_main_search");
            var search_value = input.value.toLowerCase();
            var collections = top.getElements(".spt_collection_div");
            var num_result = 0;
            for (i = 0; i < collections.length; i++) {
                // Access the Collection title (without number count) 
                var collection_title = collections[i].attributes[0].value.toLowerCase();

                if (collection_title.indexOf(search_value) != '-1') {
                    collections[i].style.display = "block";
                    num_result += 1;
                }
                else {
                    collections[i].style.display = "none";
                }
            }
            // if no search results, display all
            if (num_result == 0) {
                for (i = 0; i < collections.length; i++) {
                    collections[i].style.display = "block";
                }
            }

        '''
        filters = []
        filters.append(("_is_collection",True))
        filters.append(("status","Verified"))
        text = LookAheadTextInputWdg(
            search_type = "workflow/asset",
            column="name",
            icon="BS_SEARCH",
            icon_pos="right",
            width="100%",
            hint_text="'Enter' to search for Colllection...",
            value_column="name",
            filters=filters,
            custom_cbk=custom_cbk,
            is_collection=True
        )
        text.add_class("spt_main_search")

        content_div.add(text)
        # set minimum if there is at least one collection
        if len(collections) > 0:
            content_div.add_style("min-height: 300")
        content_div.add_style("max-height: 300")
        content_div.add_style("overflow-y: auto")

        content_div.add("<br clear='all'/>")

        for collection in collections:

            search_type = collection.get_base_search_type()
            parts = search_type.split("/")
            collection_type = "%s/%s_in_%s" % (parts[0], parts[1], parts[1])
            search = Search(collection_type)
            search.add_filter("parent_code", collection.get_code())
            num_items = search.get_count()


            collection_div = DivWdg()
            collection_div.add_class("spt_collection_div")
            content_div.add(collection_div)
            collection_div.add_style("margin: 3px 5px 0px 5px")

            go_wdg = DivWdg()
            collection_div.add(go_wdg)
            go_wdg.add_style("float: right")

            icon = IconWdg(name="View Collection", icon="BS_CHEVRON_RIGHT")
            go_wdg.add(icon)
            #go_wdg.add_behavior( {
            #    'type': 'click_upX',
            #    'cbjs_action': '''
            #    alert("Not Implemented");
            #    '''
            #} )


            name = collection.get_value("name")
            # Adding Collection title (without the number count) as an attribute
            collection_div.set_attr("collection_name", name)

            if not name:
                name = collection.get_value("code")

            check_div = DivWdg()
            collection_div.add(check_div)

            check = CheckboxWdg("collection_key")
            check.add_class("spt_collection_checkbox")
            check_div.add(check)
            check_div.add_style("float: left")
            check_div.add_style("margin-right: 5px")
            check_div.add_style("margin-top: -3px")

            check.add_attr("collection_key", collection.get_search_key() )

            info_div = DivWdg()
            collection_div.add(info_div)
            info_div.add(name)

            if num_items:
                info_div.add(" (%s)" % num_items)

            collection_div.add("<hr/>")


        add_button = DivWdg()
        add_button.add("Add")
        add_button.add_style("margin: 0px 10px 10px 10px")
        add_button.add_style("width: 50px")
        add_button.add_class("btn btn-primary")
        dialog.add(add_button)

        add_button.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var search_keys = spt.table.get_selected_search_keys(false);

            if (search_keys.length == 0) {
                spt.notify.show_message("No assets selected.");
                return;
            }

            var top = bvr.src_el.getParent(".spt_dialog");
            var checkboxes = top.getElements(".spt_collection_checkbox");
            var cmd = "tactic.ui.panel.CollectionAddCmd";
            var server = TacticServerStub.get();
            var is_checked = false;

            var dialog_top = bvr.src_el.getParent(".spt_dialog_top");

            for (i = 0; i < checkboxes.length; i++) {
                var checked_collection_attr = checkboxes[i].attributes;
                var collection_key = checked_collection_attr[3].value;
                // Preventing a collection being added to itself, check if search_keys contain collection_key.
                if (search_keys.indexOf(collection_key) != -1) {
                    spt.notify.show_message("Collection cannot be added to itself.");
                    return;
                }

                if (checkboxes[i].checked == true) {
                    // if there is at least one checkbox selected, set is_checked to 'true'
                    is_checked = true;

                    var search_keys = spt.table.get_selected_search_keys(false);
                    var kwargs = {
                        collection_key: collection_key,
                        search_keys: search_keys
                    }
                    server.execute_cmd(cmd, kwargs);
                }
            }

            if (is_checked == false) {
                spt.notify.show_message("No collection selected.");
                return;
            }
            else {
                spt.notify.show_message("Assets added to Collection.");
                // refresh dialog_top, so users can see the number change in Collections
                spt.panel.refresh(dialog_top);
            }
            
            '''
        } )
        

        return top




class CollectionAddCmd(Command):

    def execute(my):

        collection_key = my.kwargs.get("collection_key")
        search_keys = my.kwargs.get("search_keys")

        collection = Search.get_by_search_key(collection_key)
        if not collection:
            raise Exception("Collection does not exist")


        search_type = collection.get_base_search_type()
        parts = search_type.split("/")
        collection_type = "%s/%s_in_%s" % (parts[0], parts[1], parts[1])
        search = Search(collection_type)
        search.add_filter("parent_code", collection.get_code())
        items = search.get_sobjects()


        search_codes = [x.get_value("search_code") for x in items]
        search_codes = set(search_codes)



        has_keywords = SearchType.column_exists(search_type, "keywords")

        if has_keywords:
            collection_keywords = collection.get_value("keywords", no_exception=True)
            collection_keywords = collection_keywords.split(" ")
            collection_keywords = set(collection_keywords)



        # create new items

        sobjects = Search.get_by_search_keys(search_keys)
        for sobject in sobjects:
            if sobject.get_code() in search_codes:
                continue

            new_item = SearchType.create(collection_type)
            new_item.set_value("parent_code", collection.get_code())
            new_item.set_value("search_code", sobject.get_code())
            new_item.commit()


            # copy the metadata of the collection
            if has_keywords:
                keywords = sobject.get_value("keywords")

                keywords = keywords.split(" ")
                keywords = set(keywords)

                keywords = keywords.union(collection_keywords)
                keywords = " ".join(keywords)

                sobject.set_value("keywords", keywords)
                sobject.commit()





class CollectionLayoutWdg(ToolLayoutWdg):

    def get_content_wdg(my):

        my.search_type = my.kwargs.get("search_type")
        my.collection_key = my.kwargs.get("collection_key")

        top = DivWdg()
        top.add_class("spt_collection_top")

        if not SearchType.column_exists(my.search_type, "_is_collection"):
            msg_div = DivWdg()
            top.add(msg_div)
            msg_div.add("Search Type [%s] does not support collections" % my.search_type)
            msg_div.add_style("padding: 40px")
            msg_div.add_style("width: 300px")
            msg_div.add_style("margin: 100px auto")
            msg_div.add_border()

            return top


        top.add_style("margin: 5px 20px")


        table = Table()
        top.add(table)
        table.add_row()
        table.add_style("width: 100%")

        #tr, header = table.add_row_cell()
        #header.add_style("height: 40px")

        table.add_row()
        left = table.add_cell()
        left.add_style("vertical-align: top")
        left.add_style("width: 300px")
        left.add_style("max-width: 300px")
        left.add_style("height: auto")

        right = table.add_cell()
        right.add_style("vertical-align: top")
        right.add_style("width: auto")
        right.add_style("height: auto")

        left.add(my.get_collection_wdg())
        right.add(my.get_right_content_wdg())

        return top




    def get_collection_wdg(my):

        div = DivWdg()
        div.add_style("margin: 15px 0px")

        title_div = DivWdg("Collection Manager") 
        div.add(title_div)
        div.add_class("spt_collection_left")
        title_div.add_style("font-size: 1.2em")
        title_div.add_style("font-weight: bold")

        div.add("<hr/>")

        # Shelf
        shelf_div = DivWdg()
        div.add(shelf_div)
        shelf_div.add_style("float: right")
        shelf_div.add_style("margin-bottom: 15px")


        #button = IconButtonWdg(title='Delete Selected Collection', icon="BS_TRASH")
        #shelf_div.add(button)
        #button.add_style("display: inline-block")
        #button.add_style("width: auto")

        button = IconButtonWdg(title='Add New Collection', icon="BS_PLUS")
        shelf_div.add(button)
        button.add_style("display: inline-block")
        button.add_style("vertical-align: top")

        insert_view = "edit_collection"

        button.add_behavior( {
            'type': 'click_up',
            'insert_view': insert_view,
            'search_type': my.search_type,
            'cbjs_action': '''
                kwargs = {
                  search_type: bvr.search_type,
                  mode: 'insert',
                  view: bvr.insert_view,
                  save_event: bvr.event_name,
                  show_header: false,
                  num_columns: 2,
                  default: {
                    _is_collection: true
                  }
                };
                var popup = spt.panel.load_popup('Add New Collection', 'tactic.ui.panel.EditWdg', kwargs);
            '''
        } )
        text_div = DivWdg()
        shelf_div.add(text_div)

        custom_cbk = {}
        custom_cbk['enter'] = '''

            var top = bvr.src_el.getParent(".spt_collection_left");
            var input = top.getElement(".spt_main_search");
            var search_value = input.value.toLowerCase();
            var collections = top.getElements(".spt_collection_div");

            var num_result = 0;
            for (i = 0; i < collections.length; i++) {
                // Access the Collection title (without number count) 
                var collection_title = collections[i].attributes[4].nodeValue.toLowerCase();

                if (collection_title.indexOf(search_value) != '-1') {
                    collections[i].style.display = "block";
                    num_result += 1;
                }
                else {
                    collections[i].style.display = "none";
                }
            }
            // if no search results, display all
            if (num_result == 0) {
                for (i = 0; i < collections.length; i++) {
                    collections[i].style.display = "block";
                }
            }

        '''

        filters = []
        filters.append(("_is_collection",True))
        filters.append(("status","Verified"))
        text = LookAheadTextInputWdg(
            search_type = "workflow/asset",
            column="name",
            icon="BS_SEARCH",
            icon_pos="right",
            width="100%",
            hint_text="'Enter' to search for Colllection...",
            value_column="name",
            filters=filters,
            custom_cbk=custom_cbk,
            is_collection=True
        )
        text.add_class("spt_main_search")

        text_div.add(text)
        text_div.add_style("width: 270px")
        text_div.add_style("display: inline-block")

        # Asset Library folder access
        div.add("<br clear='all'/>")
        asset_lib_div = DivWdg()
        div.add(asset_lib_div)
        folder_icon = IconWdg(icon="FOLDER_2", width='30px')

        asset_lib_div.add(folder_icon)
        asset_lib_div.add_style("margin: 5px 0px 5px -5px")
        asset_lib_div.add_style("height: 20px")
        asset_lib_div.add_style("padding-top: 5px")
        asset_lib_div.add_style("padding-bottom: 5px")
        asset_lib_div.add_style("font-weight: bold")

        asset_lib_div.add("Asset Library")
        asset_lib_div.add_class("tactic_hover")
        asset_lib_div.add_class("hand")
        asset_lib_div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_collection_top");
                var content = top.getElements(".spt_collection_content");

                spt.panel.refresh(top);
                '''
            } )


        # collection
        search = Search(my.search_type)
        search.add_filter("_is_collection", True)
        collections = search.get_sobjects()

        collections_div = DivWdg()
        collections_div.add_class("spt_collection_list")
        div.add(collections_div)
        collections_div.add_style("margin: 5px 0px 5px -5px")

        from tactic.ui.panel import ThumbWdg2


        parts = my.search_type.split("/")
        collection_type = "%s/%s_in_%s" % (parts[0], parts[1], parts[1])


        collections_div.add_relay_behavior( {
            'type': 'mouseup',
            'search_type': my.search_type,
            'collection_type': collection_type,
            'bvr_match_class': 'spt_collection_item',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_collection_top");
            var content = top.getElement(".spt_collection_content");

            bvr.src_el.setStyle("border", "solid 3x blue");
            var list = bvr.src_el.getParent(".spt_collection_list");
            var items = list.getElements(".spt_collection_item");
            for (var i = 0; i < items.length; i++) {
                items[i].setStyle("box-shadow", "");
            }



            var collection_key = bvr.src_el.getAttribute("spt_collection_key");
            var collection_code = bvr.src_el.getAttribute("spt_collection_code");
            var collection_path = bvr.src_el.getAttribute("spt_collection_path");

            var expr = "@SEARCH("+bvr.collection_type+"['parent_code','"+collection_code+"']."+bvr.search_type+")";


            var cls = "tactic.ui.panel.CollectionContentWdg";
            var kwargs = {
                collection_key: collection_key,
                path: collection_path,
                search_type: bvr.search_type,
                show_shelf: false,
                show_search_limit: false,
                expression: expr,
            }
            spt.panel.load(content, cls, kwargs);

            bvr.src_el.setStyle("box-shadow", "0px 0px 3px rgba(0,0,0,0.5)");



            '''
        } )


        collections_div.add_relay_behavior( {
            'type': 'mouseup',
            'search_type': my.search_type,
            'bvr_match_class': 'spt_collection_open',
            'cbjs_action': '''
            var item = bvr.src_el.getParent(".spt_collection_item");
            var next = item.getNext();

            if (bvr.src_el.hasClass("spt_open")) {
                next.innerHTML = "";
                bvr.src_el.setStyle("opacity", 1.0);
                bvr.src_el.removeClass("spt_open");
            }
            else {
                var collection_key = bvr.src_el.getAttribute("spt_collection_key");
                var collection_path = bvr.src_el.getAttribute("spt_collection_path");

                var cls = "tactic.ui.panel.CollectionListWdg";
                var kwargs = {
                    parent_key: collection_key,
                    path: collection_path,
                }
                spt.panel.load(next, cls, kwargs, null, {show_loading: false});

                bvr.src_el.setStyle("opacity", 0.3);
                bvr.src_el.addClass("spt_open");

                evt.stopPropagation();
            }



            '''
        } )



        for collection in collections:

            collection_wdg = CollectionItemWdg(collection=collection, path=collection.get_value("name"))
            collections_div.add(collection_wdg)
            collection_wdg.add_class("spt_collection_div")

            subcollection_wdg = DivWdg()
            collections_div.add(subcollection_wdg)
            subcollection_wdg.add_class("spt_subcollection_wdg")
            subcollection_wdg.add_style("padding-left: 15px")


        return div




    def get_right_content_wdg(my):

        div = DivWdg()
        div.add_style("width: 100%")
        div.add_class("spt_collection_content")

        #shelf_wdg = my.get_header_wdg()
        #shelf_wdg.add_style("float: right")
        #div.add(shelf_wdg)

        tile = CollectionContentWdg(
                search_type=my.search_type,
                show_shelf=False,
                show_search_limit=False,
                sobjects=my.sobjects
        )
        div.add(tile)

        return div


class CollectionContentWdg(BaseRefreshWdg):

    def get_display(my):

        my.collection_key = my.kwargs.get("collection_key")

        collection = Search.get_by_search_key(my.collection_key)
        print collection

        top = my.top

        my.kwargs["scale"] = 75;
        my.kwargs["show_scale"] = False;

        from tile_layout_wdg import TileLayoutWdg
        tile = TileLayoutWdg(
            **my.kwargs
        )

        path = my.kwargs.get("path")
        if collection and path:
            title_div = DivWdg()
            top.add(title_div)
            title_div.add_style("float: left")
            title_div.add_style("margin: 15px 0px 15px 30px")

            asset_lib_span_div = SpanWdg()
            title_div.add(asset_lib_span_div)

            icon = IconWdg(name="Asset Library", icon="BS_FOLDER_OPEN")
            icon.add_behavior( {
                'type': 'mouseover',
                'cbjs_action': '''
                bvr.src_el.setStyle('opacity', 1.0);
                '''
            } )
            icon.add_behavior( {
                'type': 'mouseout',
                'cbjs_action': '''
                bvr.src_el.setStyle('opacity', 0.6);
                '''
            } )
            asset_lib_span_div.add(icon)

            asset_lib_span_div.add(" <a class='spt_collection_link'><b>Asset Library</b></a> ")

            # make icon and All Assets title clickable to return to view all assets
            asset_lib_span_div.add_behavior( {
                'type': 'click_up',
                'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_collection_top");
                var content = top.getElements(".spt_collection_content");

                spt.panel.refresh(top);
                '''
            } )

            path = path.strip("/")
            parts = path.split("/")

            for part in parts:
                title_div.add(" / ")
                title_div.add(" <a class='spt_collection_link'><b>%s</b></a> " % part)
                title_div.add_style("margin-top: 10px")
            #title_div.add("/ %s" % collection.get_value("name") )

        #scale_wdg = tile.get_scale_wdg()
        #top.add(scale_wdg)
        #scale_wdg.add_style("float: right")

        top.add(my.get_header_wdg())

        top.add(tile)

        return top

 

    def get_header_wdg(my):

        div = DivWdg()

        if my.collection_key:

            button = IconButtonWdg(title='Remove Selected Items from Collection', icon="BS_MINUS")
            div.add(button)
            button.add_style("display: inline-block")
            button.add_style("vertical-align: top")

            button.add_behavior( {
                'type': 'click_up',
                'collection_key': my.collection_key,
                'cbjs_action': '''
                var search_keys = spt.table.get_selected_search_keys(false);

                if (search_keys.length == 0) {
                    spt.notify.show_message("Nothing selected to remove");
                    return;
                }
                var ok = null;
                var cancel = function() { return };
                var msg = "Are you sure you wish to remove the selected Assets from the Collection?";

                var ok = function() {
                    var cls = 'tactic.ui.panel.CollectionRemoveCmd';
                    var kwargs = {
                        collection_key: bvr.collection_key,
                        search_keys: search_keys,
                    }
                    var server = TacticServerStub.get();
                    try {
                        server.execute_cmd(cls, kwargs);
                        spt.table.remove_selected();
                    } catch(e) {
                        spt.alert(spt.exception.handler(e));
                    }
                }
                
                spt.confirm(msg, ok, cancel);

                '''
            } )



            button = IconButtonWdg(title='Delete Collection', icon="BS_TRASH")
            #button = ActionButtonWdg(title='Delete Collection', icon="BS_TRASH")
            div.add(button)
            button.add_style("display: inline-block")
            button.add_style("vertical-align: top")

            button.add_behavior( {
                'type': 'click_up',
                'collection_key': my.collection_key,
                'cbjs_action': '''
                var ok = null;
                var cancel = function() { return };
                var msg = "Are you sure you wish to delete the Collection?";

                var ok = function() {
                    var cls = 'tactic.ui.panel.CollectionDeleteCmd';
                    var kwargs = {
                        collection_key: bvr.collection_key,
                    }
                    var server = TacticServerStub.get();
                    try {
                        server.execute_cmd(cls, kwargs);
                    } catch(e) {
                        spt.alert(e);
                        return;
                    }

                    var top = bvr.src_el.getParent(".spt_collection_top");
                    if (top) {
                        var layout = top.getParent(".spt_layout");
                        spt.table.set_layout(layout);
                    }

                    spt.table.run_search();
                }

                spt.confirm(msg, ok, cancel);
                '''
            } )



        """
        button = IconButtonWdg(title='Download Selected Items', icon="BS_DOWNLOAD")
        div.add(button)
        button.add_style("display: inline-block")
        button.add_style("vertical-align: top")

        text_div = DivWdg()
        div.add(text_div)
        text_div.add_style("width: 200px")
        text = LookAheadTextInputWdg(
            name="name",
            icon="BS_SEARCH",
            icon_pos="right",
            width="100%"
        ) 
        text_div.add(text)
        text_div.add_style("display: inline-block")
        """

        div.add_style("width: auto")
        div.add_style("float: right")

        div.add("<br clear='all'/>")


        return div



class CollectionRemoveCmd(Command):

    def execute(my):

        my.collection_key = my.kwargs.get("collection_key")
        my.search_keys = my.kwargs.get("search_keys")

        collection = Search.get_by_search_key(my.collection_key)
        sobjects = Search.get_by_search_keys(my.search_keys)
        search_codes = [x.get_code() for x in sobjects]


        search_type = collection.get_base_search_type()
        parts = search_type.split("/")
        collection_type = "%s/%s_in_%s" % (parts[0], parts[1], parts[1])

        search = Search(collection_type)
        search.add_filter("parent_code", collection.get_code())
        search.add_filters("search_code", search_codes)

        items = search.get_sobjects()

        for item in items:
            item.delete()


class CollectionDeleteCmd(Command):

    def execute(my):

        my.collection_key = my.kwargs.get("collection_key")

        collection = Search.get_by_search_key(my.collection_key)

        search_type = collection.get_base_search_type()
        parts = search_type.split("/")
        collection_type = "%s/%s_in_%s" % (parts[0], parts[1], parts[1])

        search = Search(collection_type)
        search.add_filter("parent_code", collection.get_code())
        items = search.get_sobjects()

        for item in items:
            item.delete()

        collection.delete()





class CollectionListWdg(BaseRefreshWdg):

    def get_display(my):

        parent_key = my.kwargs.get("parent_key")
        collection = Search.get_by_search_key(parent_key)

        collection_path = my.kwargs.get("path")

        search_type = collection.get_base_search_type()
        parts = search_type.split("/")
        collection_type = "%s/%s_in_%s" % (parts[0], parts[1], parts[1])

        search = Search(collection_type)
        search.add_filter("parent_code", collection.get_value("code"))
        collections = search.get_sobjects()
        collection_codes = [x.get_value("search_code") for x in collections]

        search = Search(search_type)
        search.add_filter("_is_collection", True)
        search.add_filters("code", collection_codes)
        collections = search.get_sobjects()

        top = my.top
        top.add_class("spt_collection_list")

        for item in collections:

            path = "%s/%s" % (collection_path, item.get_value("name") )
            collection_wdg = CollectionItemWdg(collection=item, path=path)
            top.add(collection_wdg)

            subcollection_wdg = DivWdg()
            top.add(subcollection_wdg)
            subcollection_wdg.add_class("spt_subcollection_wdg")
            subcollection_wdg.add_style("padding-left: 15px")

        return top


class CollectionItemWdg(BaseRefreshWdg):

    def get_display(my):

        collection = my.kwargs.get("collection")
        path = my.kwargs.get("path")

        search_type = collection.get_base_search_type()
        parts = search_type.split("/")
        collection_type = "%s/%s_in_%s" % (parts[0], parts[1], parts[1])

        search = Search(collection_type)
        search.add_filter("parent_code", collection.get_value("code"))
        search.add_column("search_code")
        items = search.get_sobjects()
        codes = [x.get_value("search_code") for x in items]

        count = search.get_count()


        # find the children that are actually collections
        search = Search(search_type)
        search.add_filter("_is_collection", True)
        search.add_filters("code", codes)
        has_child_collections = search.get_count() > 0


        top = my.top

        collection_div = top
        collection_div.add_class("tactic_hover")
        collection_div.add_class("hand")
        collection_div.add_class("spt_collection_item")
        collection_div.add_attr("spt_collection_key", collection.get_search_key())
        collection_div.add_attr("spt_collection_code", collection.get_code())
        collection_div.add_attr("spt_collection_path", path)

        # This is for Drag and Drop from a tile widget
        collection_div.add_class("spt_tile_top")
        collection_div.add_attr("spt_search_key", collection.get_search_key())
        collection_div.add_attr("spt_search_code", collection.get_code())

        collection_div.add_style("height: 20px")
        collection_div.add_style("padding-top: 10px")

        if has_child_collections:
            icon = IconWdg(name="View Collection", icon="BS_CHEVRON_DOWN")
            icon.add_style("float: right")
            collection_div.add(icon)
            icon.add_class("spt_collection_open")
            icon.add_attr("spt_collection_key", collection.get_search_key())
            icon.add_attr("spt_collection_path", path)


        from tactic.ui.panel import ThumbWdg2
        thumb_wdg = ThumbWdg2()
        thumb_wdg.set_sobject(collection)
        collection_div.add(thumb_wdg)
        thumb_wdg.add_style("width: 45px")
        thumb_wdg.add_style("float: left")
        thumb_wdg.add_style("margin-top: -10px")

        if count:
            count_div = DivWdg()
            collection_div.add(count_div)
            #count_div.add_style("margin-top: -10px")
            #count_div.add_style("margin-left: -10px")

            count_div.add_style("width: 15px")
            count_div.add_style("height: 15px")
            count_div.add_style("font-size: 0.8em")
            count_div.add_style("border-radius: 10px")
            count_div.add_style("background: #DDD")
            count_div.add_style("position: absolute")
            count_div.add_style("text-align: center")
            count_div.add_style("margin-left: 23px")
            count_div.add_style("margin-top: -8px")
            count_div.add_style("box-shadow: 0px 0px 3px rgba(0,0,0,0.5)")

            count_div.add(count)
            #count_div.add_update( {
            #    'parent_key': collection.get_search_key(),
            #    'expression': "@COUNT(%s)" % collection_type,
            #} )


        name = collection.get_value("name")
        collection_div.add(name)



        return top







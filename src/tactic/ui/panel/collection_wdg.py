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

import tacticenv

__all__ = ["CollectionAddWdg", "CollectionAddCmd", "CollectionListWdg", "CollectionItemWdg", "CollectionLayoutWdg"]



from pyasm.common import Common, Environment, Container, TacticException
from pyasm.search import SearchType, Search
from pyasm.web import DivWdg, Table
from pyasm.command import Command
from pyasm.widget import CheckboxWdg, IconWdg
from tactic.ui.common import BaseRefreshWdg
from tactic.ui.widget import ButtonNewWdg
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

        button = ButtonNewWdg(title='Add to Collection', icon="BS_TH_LARGE", show_arrow=True)
        top.add(button)

        detail_wdg = DivWdg()
        top.add(detail_wdg)

        dialog = DialogWdg()
        top.add(dialog)
        dialog.set_as_activator(button, offset={'x':-25,'y': 0})
        dialog.add_title("Collections")

        dialog.add("<div style='margin: 10px'><b>Add selected items to a collection</b></div>")

        content_div = DivWdg()
        dialog.add(content_div)
        content_div.add_style("width: 300px")
        content_div.add_style("padding: 10px")


        text = LookAheadTextInputWdg(
            name="name",
            icon="BS_SEARCH",
            icon_pos="right",
        ) 

        content_div.add(text)
        text.add_style("width: 100%")


        content_div.add_style("max-height: 300px")
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
            content_div.add(collection_div)
            collection_div.add_style("margin: 3px 5px 0px 5px")

            go_wdg = DivWdg()
            collection_div.add(go_wdg)
            go_wdg.add_style("float: right")

            icon = IconWdg(name="View Collection", icon="BS_CHEVRON_RIGHT")
            go_wdg.add(icon)
            go_wdg.add_behavior( {
                'type': 'click_upX',
                'cbjs_action': '''
                alert("go to !!!");
                '''
            } )


            name = collection.get_value("name")
            if not name:
                name = collection.get_value("code")

            check_div = DivWdg()
            collection_div.add(check_div)

            check = CheckboxWdg("collection_key")
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


            check.add_behavior( {
                'type': 'click',
                'cbjs_action': '''
                var search_keys = spt.table.get_selected_search_keys(false);
                if (search_keys.length == 0) {
                    spt.notify.show_message("Nothig selected");
                    return;
                }
                var collection_key = bvr.src_el.getAttribute("collection_key");

                var cmd = "tactic.ui.panel.base_table_layout_wdg.CollectionAddCmd";
                var kwargs = {
                    collection_key: collection_key,
                    search_keys: search_keys
                }
                var server = TacticServerStub.get();
                server.execute_cmd(cmd, kwargs);
                '''
            } )


        add_div = DivWdg()
        dialog.add(add_div)
        icon = IconWdg(name="Add new collection", icon="BS_PLUS")
        add_div.add(icon)
        add_div.add("Create new Collection")
        add_div.add_style("margin: 10px")
        add_div.add_class("hand")


        insert_view = "insert"

        add_div.add_behavior( {
            'type': 'click_up',
            'insert_view': insert_view,
            'cbjs_action': '''
                var top = bvr.src_el.getParent(".spt_table_top");
                var table = top.getElement(".spt_table");
                var search_type = top.getAttribute("spt_search_type")
                kwargs = {
                  search_type: search_type,
                  mode: 'insert',
                  view: bvr.insert_view,
                  save_event: bvr.event_name,
                  show_header: false,
                  default: {
                    _is_collection: true,
                  }
                };
                spt.panel.load_popup('Add New Collection', 'tactic.ui.panel.EditWdg', kwargs);
            '''
        } )

 

        """
        button = ActionButtonWdg(title="Add")
        button.add_style("margin: 10px")
        dialog.add(button)


        button.add_behavior( {
            'type': 'click',
            'cbjs_action': '''
            var search_keys = spt.table.get_selected_search_keys(false);

            var top = bvr.src_el.getParent(".spt_content_top");
            var values = spt.api.get_input_values(top);
            console.log(values);

            '''
        } )
        """

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

        top = DivWdg()
        top.add_class("spt_collection_top")
        top.add_style("margin: 5px 20px")

        table = Table()
        top.add(table)
        table.add_row()
        table.add_style("width: 100%")

        tr, header = table.add_row_cell()
        header.add_style("height: 40px")

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

        shelf_wdg = my.get_header_wdg()
        #shelf_wdg.add_style("float: right")
        header.add(shelf_wdg)

        left.add(my.get_collection_wdg())
        right.add(my.get_right_content_wdg())

        return top



    def get_header_wdg(my):

        div = DivWdg()

        button = ButtonNewWdg(title='Remove Selected Items', icon="BS_TRASH")
        div.add(button)

        button = ButtonNewWdg(title='Download Selected Items', icon="BS_DOWNLOAD")
        div.add(button)

        text = LookAheadTextInputWdg(
            name="name",
            icon="BS_SEARCH",
            icon_pos="right",
        ) 
        div.add(text)


        return div



    def get_collection_wdg(my):

        div = DivWdg()
        div.add_style("margin: 15px 0px")

        title_div = DivWdg("Collection Manager") 
        div.add(title_div)
        title_div.add_style("font-size: 1.2em")
        title_div.add_style("font-weight: bold")

        div.add("<hr/>")

        # Shelf
        shelf_div = DivWdg()
        div.add(shelf_div)

        button = ButtonNewWdg(title='Delete Selected Collection', icon="BS_TRASH")
        shelf_div.add(button)
        button.add_style("float: right")
        button = ButtonNewWdg(title='Add New Collection', icon="BS_PLUS")
        shelf_div.add(button)
        button.add_style("float: right")

        text = LookAheadTextInputWdg(
            name="name",
            icon="BS_SEARCH",
            icon_pos="right",
        ) 
        shelf_div.add(text)

        div.add("<br/>")

        # collection
        search = Search(my.search_type)
        search.add_filter("_is_collection", True)
        collections = search.get_sobjects()

        collections_div = DivWdg()
        div.add(collections_div)
        collections_div.add_style("margin: 5px 10px")

        from tactic.ui.panel import ThumbWdg2


        collections_div.add_relay_behavior( {
            'type': 'mouseup',
            'search_type': my.search_type,
            'collection_type': collection_type,
            'bvr_match_class': 'spt_collection_item',
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_collection_top");
            var content = top.getElement(".spt_collection_content");

            var collection_key = bvr.src_el.getAttribute("spt_collection_key");

            var cls = "tactic.ui.panel.TileLayoutWdg";
            var kwargs = {
                search_type: bvr.search_type,
                show_shelf: false,
                show_search_limit: false,
            }
            spt.panel.load(content, cls, kwargs);

            '''
        } )


        collections_div.add_relay_behavior( {
            'type': 'mouseup',
            'search_type': my.search_type,
            'bvr_match_class': 'spt_collection_open',
            'cbjs_action': '''
            var item = bvr.src_el.getParent(".spt_collection_item");
            var next = item.getNext();

            var collection_key = bvr.src_el.getAttribute("spt_collection_key");

            var cls = "tactic.ui.panel.CollectionListWdg";
            var kwargs = {
                parent_key: collection_key,
            }
            spt.panel.load(next, cls, kwargs);

            '''
        } )



        for collection in collections:

            collection_wdg = CollectionItemWdg(collection=collection)
            collections_div.add(collection_wdg)

            subcollection_wdg = DivWdg()
            collections_div.add(subcollection_wdg)
            subcollection_wdg.add_class("spt_subcollection_wdg")
            subcollection_wdg.add_style("padding-left: 15px")


        return div




    def get_right_content_wdg(my):

        div = DivWdg()
        div.add_style("width: 100%")
        div.add_class("spt_collection_content")

        from tile_layout_wdg import TileLayoutWdg
        tile = TileLayoutWdg(
                search_type=my.search_type,
                show_shelf=False,
                show_search_limit=False,
                sobjects=my.sobjects
        )
        div.add(tile)

        return div




class CollectionListWdg(BaseRefreshWdg):

    def get_display(my):

        parent_key = my.kwargs.get("parent_key")
        collection = Search.get_by_search_key(parent_key)

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

        for item in collections:

            collection_wdg = CollectionItemWdg(collection=item)
            top.add(collection_wdg)

            subcollection_wdg = DivWdg()
            top.add(subcollection_wdg)
            subcollection_wdg.add_class("spt_subcollection_wdg")
            subcollection_wdg.add_style("padding-left: 15px")

        return top


class CollectionItemWdg(BaseRefreshWdg):

    def get_display(my):

        collection = my.kwargs.get("collection")

        search_type = collection.get_base_search_type()
        parts = search_type.split("/")
        collection_type = "%s/%s_in_%s" % (parts[0], parts[1], parts[1])

        search = Search(collection_type)
        search.add_filter("parent_code", collection.get_value("code"))
        count = search.get_count()


        top = my.top

        collection_div = top
        collection_div.add_class("tactic_hover")
        collection_div.add_class("hand")
        collection_div.add_class("spt_collection_item")
        collection_div.add_attr("spt_collection_key", collection.get_search_key())

        collection_div.add_style("height: 20px")
        collection_div.add_style("padding-top: 10px")

        if count:
            icon = IconWdg(name="View Collection", icon="BS_CHEVRON_DOWN")
            icon.add_style("float: right")
            collection_div.add(icon)
            icon.add_class("spt_collection_open")
            icon.add_attr("spt_collection_key", collection.get_search_key())


        from tactic.ui.panel import ThumbWdg2
        thumb_wdg = ThumbWdg2()
        thumb_wdg.set_sobject(collection)
        collection_div.add(thumb_wdg)
        thumb_wdg.add_style("width: 45px")
        thumb_wdg.add_style("float: left")
        thumb_wdg.add_style("margin-top: -15px")

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

            count_div.add(count)


        name = collection.get_value("name")
        collection_div.add(name)



        return top







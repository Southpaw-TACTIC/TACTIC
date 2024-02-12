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


__all__ = ['Document', 'DocumentWdg', 'DocumentItemWdg', 'DocumentSaveCmd']


from pyasm.common import Common, jsonloads, jsondumps
from pyasm.biz import Project
from pyasm.command import Command
from pyasm.search import Search, SearchType, SObject

from pyasm.web import DivWdg, HtmlElement

from tactic.ui.common import BaseRefreshWdg, BaseTableElementWdg, SimpleTableElementWdg
from tactic.ui.panel import ViewPanelWdg



class Document(object):

    def set_document(self, document):
        self.document = document


    def __init__(self, **kwargs):

        self.kwargs = kwargs

        self.document = {}
        self.document['content'] = []

        if self.kwargs.get("type"):
            self.document["type"] = self.kwargs.get("type")

        if self.kwargs.get("document"):
            self.document = jsonloads(self.kwargs.get("document") )

        # store for fast look up
        self.sobjects = self.kwargs.get("sobjects")
        self.sobjects_dict = {}
        for sobject in self.sobjects:
            code = sobject.get_code()
            self.sobjects_dict[code] = sobject



    def get_document(self):
        return self.document


    def get_sobjects_from_document(self, document):

        content = document.get("content") or []

        sobjects = []

        for item in content:
            self._get_sobjects_from_item(item, sobjects)

        # we have a list of sobjects
        gstack = []
        for sobject in sobjects:

            if sobject.get("is_group"):
                group_level = sobject.get("group_level") or 0

                # keep track of the group stack
                if group_level < len(gstack):
                    if group_level == 0:
                        gstack = []
                    else:
                        gstack = gstack[:group_level]

                gstack.append(sobject)

                continue

            else:
                for item in gstack:
                    item.sobjects.append(sobject)

        return sobjects



    def _get_sobjects_from_item(self, item, sobjects):
        item_type = item.get("type")

        title = item.get("title")

        group_level = item.get("group_level") or 0
        search_key = item.get("search_key")
        expression = item.get("expression")

        if item_type == "title":
            sobject = item
            sobjects.append(sobject)

        elif item_type == "sobject":
            code = item.get("code")
            if code:
                sobject = self.sobjects_dict.get(code)
                if sobject:
                    sobject = sobject.get_sobject_dict(mode="fast")
                else:
                    return
            else:
                sobject = item.get("sobject")

            if sobject and sobject.get("__search_key__"):
                search_key = sobject.get("__search_key__")
                if not search_key:
                    search_key = "sthpw/virtual?id=%s" % sobject.get("id")

            if sobject or search_key:

                if search_key and search_key.startswith("sthpw/virtual"):
                    pass
                elif not sobject and search_key:
                    sobject = Search.get_by_search_key(search_key)

                if not sobject:
                    return


                if isinstance(sobject, dict):

                    search_type = self.kwargs.get("search_type")
                    if not search_type:
                        search_type = "sthpw/virtual"

                    s = SearchType.create(search_type)
                    for n, v in sobject.items():
                        if v is None:
                            continue
                        s.set_value(n,v)
                    sobject = s
                    SObject.cache_sobject(sobject.get_search_key(), s, search_type=search_type)

                name = sobject.get_value("name", no_exception=True)
                if not name:
                    name = sobject.get_value("code", no_exception=True)
                if not name:
                    name = sobject.get_value("id")

                title = name
                sobject.set_value("title", title)

                sobject.set_value("is_group", False)
                sobject.set_value("group_level", group_level)

                sobjects.append(sobject)



            elif expression:
                new_sobjects = Search.eval(expression)
                if not isinstance(new_sobjects, list):
                    new_sobjects = new_sobjects.get_sobjects()

                for sobject in new_sobjects:

                    name = sobject.get_value("name", no_exception=True)
                    if not name:
                        name = sobject.get("code")


                    title = name
                    sobject.set_value("title", title)

                    sobject.set_value("is_group", False)
                    sobject.set_value("group_level", group_level)


                    sobjects.append(sobject)
            else:

                return

        else:
            children = item.get("children")

            if expression:
                search = Search.eval(expression)
                new_sobjects = search.get_sobjects()
            elif search_key:
                new_sobject = Search.get_by_search_key(search_key)
                new_sobjects = [new_sobject]
            else:

                #sobject = SearchType.create(self.search_type)
                sobject = SearchType.create("sthpw/virtual")
                sobject.set_id(1)
                sobject.set_value("id", 1)
                name = item.get("title")
                if not title:
                    return
                sobject.set_value("code", name)
                sobject.set_value("name", name)

                new_sobjects = [sobject]


            for sobject in new_sobjects:
                sobject.set_value("is_group", True)
                sobject.set_value("group_level", group_level)
                if children:
                    sobject.set_value("children", children)


                # need to put this in here because groups in TableLayoutWdg depends on it
                sobject.sobjects = []

                # some dummy dates
                sobject.set_value("bid_start_date", "2018-03-15")
                sobject.set_value("bid_end_date", "2018-03-15")

                name = sobject.get_value("name")
                title = name

                sobject.set_value("title", title)

                sobjects.append(sobject)


            if children:
                search = Search.eval(children)
                child_sobjects = search.get_sobjects()

                for child_sobject in child_sobjects:
                    item = {
                        "type":"sobject",
                        "group_level": group_level + 1,
                        #"search_key": child_sobject.get_search_key(),
                        "sobject": child_sobject,
                    }

                    self._get_sobjects_from_item(item, sobjects)



    def generate_document(self, sobjects, element_names=[]):

        content = self.document.get("content")

        for sobject in sobjects:

            item = {}
            content.append(item)
            item['type'] = "sobject"

            sobject_dict = sobject.get_sobject_dict()

            item['sobject'] = sobject_dict


        return self.document



class DocumentWdg(BaseRefreshWdg):

    def set_document(self, document):
        if isinstance(document, Document):
            document = document.get_document()

        self.document = document


    def init(self):

        self.document = None

        if self.kwargs.get("document"):
            self.document = jsonloads(self.kwargs.get("document") )




    def get_sobjects_from_document(self, document):

        content = document.get("content") or []

        sobjects = []

        for item in content:
            self._get_sobjects_from_item(item, sobjects)

        # we have a list of sobjects
        gstack = []
        for sobject in sobjects:

            if sobject.get_value("is_group"):
                group_level = sobject.get_value("group_level") or 0

                # keep track of the group stack
                if group_level < len(gstack):
                    if group_level == 0:
                        gstack = []
                    else:
                        gstack = gstack[:group_level]

                gstack.append(sobject)

                continue

            else:
                for item in gstack:
                    item.sobjects.append(sobject)


        return sobjects





    def _get_sobjects_from_item(self, item, sobjects):
        item_type = item.get("type")

        title = item.get("title")

        group_level = item.get("group_level") or 0
        search_key = item.get("search_key")
        expression = item.get("expression")


        if item_type == "sobject":
            sobject = item.get("sobject")

            if sobject or search_key:

                if not sobject:
                    sobject = Search.get_by_search_key(search_key)

                if not sobject:
                    return


                if isinstance(sobject, dict):

                    search_type = self.kwargs.get("search_type")
                    if not search_type:
                        search_type = "sthpw/task"

                    s = SearchType.create(search_type)
                    for n, v in sobject.items():
                        s.set_value(n,v)
                    sobject = s
                    SObject.cache_sobject(sobject.get_search_key(), s, search_type=search_type)

                name = sobject.get_value("name", no_exception=True)
                if not name:
                    name = sobject.get_value("code", no_exception=True)
                if not name:
                    name = sobject.get_value("id")

                title = name
                sobject.set_value("title", title)

                sobject.set_value("is_group", False)
                sobject.set_value("group_level", group_level)

                sobjects.append(sobject)



            elif expression:
                new_sobjects = Search.eval(expression)
                if not isinstance(new_sobjects, list):
                    new_sobjects = new_sobjects.get_sobjects()

                for sobject in new_sobjects:

                    name = sobject.get_value("name", no_exception=True)
                    if not name:
                        name = sobject.get("code")


                    title = name
                    sobject.set_value("title", title)

                    sobject.set_value("is_group", False)
                    sobject.set_value("group_level", group_level)


                    sobjects.append(sobject)
            else:

                return

        else:
            children = item.get("children")

            if expression:
                search = Search.eval(expression)
                new_sobjects = search.get_sobjects()
            elif search_key:
                new_sobject = Search.get_by_search_key(search_key)
                new_sobjects = [new_sobject]
            else:

                #sobject = SearchType.create(self.search_type)
                sobject = SearchType.create("sthpw/virtual")
                sobject.set_id(1)
                sobject.set_value("id", 1)
                name = item.get("title")
                if not title:
                    return
                sobject.set_value("code", name)
                sobject.set_value("name", name)

                new_sobjects = [sobject]


            for sobject in new_sobjects:
                sobject.set_value("is_group", True)
                sobject.set_value("group_level", group_level)
                if children:
                    sobject.set_value("children", children)


                # need to put this in here because groups in TableLayoutWdg depends on it
                sobject.sobjects = []

                # some dummy dates
                sobject.set_value("bid_start_date", "2018-03-15")
                sobject.set_value("bid_end_date", "2018-03-15")

                name = sobject.get_value("name")
                title = name

                sobject.set_value("title", title)

                sobjects.append(sobject)


            if children:
                search = Search.eval(children)
                child_sobjects = search.get_sobjects()

                for child_sobject in child_sobjects:
                    item = {
                        "type":"sobject",
                        "group_level": group_level + 1,
                        #"search_key": child_sobject.get_search_key(),
                        "sobject": child_sobject,
                    }

                    self._get_sobjects_from_item(item, sobjects)
          

    def get_display(self):

        top = self.top
        top.add_class("spt_document_top")

        from pyasm.biz import CustomScript

        # drag script setup
        drag_action_script = self.kwargs.get("drag_action_script") or ""
        custom_script_sobject = CustomScript.get_by_path(drag_action_script)
        script = ""
        if custom_script_sobject:
            script = custom_script_sobject.get_value("script") or ""


        # document/table setup
        kwargs = self.kwargs
        document = self.document

        # on load behaviors setup
        new_group_count = document.get("new_group_count") or 0

        api_div = DivWdg()
        top.add(api_div)
        api_div.add_behavior( {
            'type': 'load',
            'new_group_count': new_group_count,
            'drag_action': script,
            'cbjs_action': self.get_onload_js()
        } )

        # sobjects setup
        search_type = kwargs.get("search_type")
        top.add_attr("spt_search_type",search_type)


        if document is not None and document != {}:
            sobjects = self.get_sobjects_from_document(document)
            document_mode = True
            init_load_num = -1
            search_limit = None

            # enforce some needed kwargs to make a document work
            kwargs['document_mode'] = document_mode
            kwargs['search_limit'] = search_limit
            kwargs['init_load_num'] = init_load_num
            kwargs['auto_grouping'] = False
            kwargs['group_elements'] = None

        elif kwargs.get("sobjects"):

            sobjects = kwargs.get("sobjects")

            document_mode = True
            init_load_num = -1
            search_limit = None

            # enforce some needed kwargs to make a document work
            kwargs['document_mode'] = document_mode
            kwargs['search_limit'] = search_limit
            kwargs['init_load_num'] = init_load_num
            kwargs['auto_grouping'] = False
            kwargs['group_elements'] = None

        else:
            sobjects = []


        view = document.get("view")
        if view:
            kwargs['view'] = view


        layout_wdg = ViewPanelWdg(
            **kwargs
        )

        top.add(layout_wdg)

        if sobjects:
            layout_wdg.set_sobjects(sobjects)

        return top


    def get_onload_js(self):

        return r'''

spt.document = {};

// action types: ADD, DELETE, RENAME, MOVE
spt.document.actions = spt.document.actions || {};


// document item api
spt.document.item = spt.document.item || {};
spt.document.item.new_group_count = bvr.new_group_count || 0;

spt.document.item.toggle_edit = function(top) {
    var label = top.getElement(".spt_document_label");
    var input = top.getElement(".spt_document_input");

    if (top.toggled) {
        spt.document.item.close_edit(top);
        input.blur();
    } else {
        spt.document.item.open_edit(top);
        input.focus();
    }
}

spt.document.item.open_edit = function(top) {
    console.log("opening...");
    var label = top.getElement(".spt_document_label");
    var input = top.getElement(".spt_document_input");

    label.setStyle("display", "none");
    input.setStyle("display", "");
    top.toggled = true;
    input.value = label.getElement(".spt_group_label").innerText;
    input.setSelectionRange(0, input.value.length);
}

spt.document.item.close_edit = function(top) {
    console.log("closing...");
    var label = top.getElement(".spt_document_label");
    var input = top.getElement(".spt_document_input");

    label.setStyle("display", "");
    input.setStyle("display", "none");
    top.toggled = false;

    if (input.value != "" && input.value != label.innerText) {
        label.getElement(".spt_group_label").innerText = input.value;
        return true;
    }
    else return false;
}


spt.document.item.keyup_behavior = function(top, key) {
    var input = top.getElement(".spt_document_input");

    if (key == "enter") {
        input.blur();
    } else if (key == "esc") {
        input.value = "";
        input.blur();
    }
}

spt.document.item.generate_name = function() {
    var group_name = "New Group";
    var count = spt.document.item.new_group_count;
    if (count != 0) group_name += count;

    console.log(group_name, count);

    return group_name;
}



spt.document.export = function(kwargs) {

    if (!kwargs) {
        kwargs = {};
    }

    max_group_level = kwargs.max_group_level;
    if (typeof(max_group_level) == 'undefined') {
        max_group_level = -1;
    }


    var min_group_level = kwargs.min_group_level;
    if (typeof(min_group_level) == 'undefined') {
        min_group_level = 0;
    }


    var table = spt.table.get_table()
    var rows = table.getElements(".spt_table_row_item");

    var document = {};
    document['type'] = 'table';
    document['new_group_count'] = spt.document.item.new_group_count;

    var content = [];
    document['content'] = content;

    for (var i = 0; i < rows.length; i++) {

        var row = rows[i];
        
        // Check for clone row
        if (row.hasClass("spt_clone")) {
            break;
        }

        // Check for dynamic row
        if (row.getAttribute("spt_dynamic") == "true") continue;
        if (row.getAttribute("spt_deleted") == "true") continue;

        var group_level = row.getAttribute("spt_group_level");
        if (max_group_level != -1 && group_level > max_group_level) {
            continue;
        }
        if (group_level < min_group_level) {
            continue;
        }





        var item = {};

        if (row.hasClass("spt_table_group_row")) {
            var row_type = "group";
        }
        else if (row.hasClass("spt_table_row")) {
            var row_type = "item";
        }
        else if (row.hasClass("spt_table_insert_row")) {
            var row_type = "item";
            item["new"] = true;
        }
        else if (row.hasClass("spt_table_group_insert_row")) {
            var row_type = "group";
            item["new"] = true;
        }


        var children = row.getAttribute("spt_children");
        if (children) {
            item["children"] = children;
        }


        if (!group_level) {
            group_level = 0;
        }
        item["group_level"] = parseInt(group_level);

        if (row_type == "group") {
            if (row.getAttribute("spt_deleted") == "true") {
                break;
            }

            item["type"] = "group";

            var swap_top = row.getElement(".spt_swap_top");
            var state = swap_top.getAttribute("spt_state");
            item["state"] = state;

            var title_wdg = row.getElement(".spt_table_group_title");
            if (title_wdg) {
                var label_wdg = title_wdg.getElement(".spt_group_label");
                if (label_wdg) {
                    item["title"] = label_wdg.innerHTML;
                }
                else {
                    item["title"] = title_wdg.innerHTML;
                }
            }
        } else {

            if (kwargs.mode == "report") {
                var element_names = spt.table.get_element_names();
                var cells = row.getElements(".spt_cell_edit");
                var index = 0;
                var data = {};
                data["id"] = i;
                cells.forEach( function(cell) {
                    var element_name = element_names[index];
                    var value = cell.getAttribute("spt_report_value");
                    if (value == null) {
                        value = cell.getAttribute("spt_input_value");
                    }
                    data[element_name] = value;
                    index += 1;
                } );
                item["type"] = "sobject";
                item["sobject"] = data;
            }
            else {
                var search_key = row.getAttribute("spt_search_key_v2");
                item["type"] = "sobject";
                item["search_key"] = search_key;
            }


        }

        content.push(item);
        
    }


    // export state

    var layout = spt.table.get_layout();
    var els = layout.getElements(".spt_state_save");

    if (els.length != 0) {
        document.state = {};
    }

    for (var i = 0; i < els.length; i++) {
        var el = els[i];
        var state_name = el.getAttribute("spt_state_name");
        var state_data = el.getAttribute("spt_state_data");
        if (state_data != null) {
            state_data = JSON.parse(state_data);
        }
        else {
            state_data = {};
        }

        document.state[state_name] = state_data;
    }
    return document
}


spt.document.extract_content = function(name) {
    var document = spt.document.export();
    var content = document.content;
    var start_row = -1;
    var end_row = content.length;

    for (var i=0; i<content.length; i++) {
        if (content[i].group_level == 1 && start_row > -1) {
            end_row = i;
            break;
        }
        if (content[i].title == name) {
            start_row = i;
        }
    }
    return content.slice(start_row, end_row);
}


spt.document.drag_row_setup = function(evt, bvr, mouse_411) {

    spt.document.top = bvr.src_el.getParent(".spt_layout");

    spt.document.first_mouse_pos = { x: mouse_411.curr_x,  y: mouse_411.curr_y };
    spt.document.first_pos = bvr.src_el.getPosition(spt.document.top);
}


spt.document.drag_row_motion = function(evt, bvr, mouse_411) {

    var dx = mouse_411.curr_x - spt.document.first_mouse_pos.x;
    var dy = mouse_411.curr_y - spt.document.first_mouse_pos.y;

    if (Math.abs(dy) < 3) {
        return;
    }


    if (!spt.document.clone) {
        spt.document.clone = spt.behavior.clone(bvr.src_el);
        spt.document.clone.inject(bvr.src_el, "after");

        bvr.src_el.setStyle("opacity", "0.3");


        var clone = spt.document.clone;
        clone.getElement("td").setStyle("diplay", "inline-block");
        group_level = clone.getAttribute("spt_group_level");
        if (group_level != 2){
            clone.getElement("td").setStyle("width", "230px");
        }

        clone.setStyle("position", "absolute");
        clone.setStyle("left", "15px");
        clone.setStyle("width", "300px");
        clone.setStyle("background", "var(--spt_palette_background)");
        clone.setStyle("box-shadow", "0px 0px 15px rgba(0,0,0,0.5)");
        clone.setStyle("z-index", "200");
        clone.setStyle("cursor", "pointer");
        clone.setStyle("pointer-events", "none");


        var tds = clone.getElements("td")
        if (tds[0].hasClass("spt_table_select")) {
            spt.behavior.destroy_element(tds[0]);
        }
        else {
            tds[0].setStyle("max-width", "");
            tds[0].setStyle("width", "100%");
        }



        clone.setStyle("width", "calc(100% - 5px)");
        clone.setStyle("height", "fit-content");

        document.id(document.body).setStyle("cursor", "ns-resize");
        bvr.src_el.setStyle("cursor", "ns-resize");

        document.activeElement.blur();


    }



    var pos = {
        x: spt.document.first_pos.x + dx,
        y: spt.document.first_pos.y + dy
    }

    spt.document.clone.setStyle("top", pos.y);
    //spt.document.clone.setStyle("left", pos.x);


    // indicate where the item will be dropped
    var drop_on_el = spt.get_event_target(evt);

    if (spt.document.last_drop_on_el) {
        spt.document.last_drop_on_el.setStyle("border-bottom", "");
    }
    
    if (!drop_on_el.hasClass("spt_table_row_item")) {
        drop_on_el = drop_on_el.getParent(".spt_table_row_item");
    }
    if (drop_on_el) {
        drop_on_el.setStyle("border-bottom", "solid 3px #F5A623");

    }
    spt.document.last_drop_on_el = drop_on_el;


}

spt.document.last_drop_on_el = null;


spt.document.drag_row_action = function(evt, drag_bvr, mouse_411) {

    if (spt.document.clone) {
        spt.behavior.destroy_element(spt.document.clone);
        spt.document.clone = null;
    }

    if (spt.document.last_drop_on_el) {
        spt.document.last_drop_on_el.setStyle("border-bottom", "");
        spt.document.last_drop_on_el = null;
    }

    drag_bvr.src_el.setStyle("opacity", "1.0");

    var dx = mouse_411.curr_x - spt.document.first_mouse_pos.x;
    var dy = mouse_411.curr_y - spt.document.first_mouse_pos.y;

    if (Math.abs(dy) < 3) {
        var el = drag_bvr.src_el.getElement(".spt_cell_edit");
        if (el) {
            el.click();
        }
        return;
    }

    if (bvr.drag_action && bvr.drag_action != "") {
        drag_bvr.script = bvr.drag_action;
        var success = spt.CustomProject.exec_custom_script(evt, drag_bvr);
        return;
    }

    var drop_on_el = spt.get_event_target(evt);
    var prev_index = drag_bvr.src_el.rowIndex;
    
    if (!drop_on_el.hasClass("spt_table_row_item")) {
        drop_on_el = drop_on_el.getParent(".spt_table_row_item");
    }
    if (drop_on_el) {

        var src_group_level = String.toInt(drag_bvr.src_el.getAttribute("spt_group_level"));
        var dest_group_level = String.toInt(drop_on_el.getAttribute("spt_group_level"));
        if (isNaN(src_group_level) || isNaN(dest_group_level)) {
            return;
        }
        
        
        // Get all child groups and entries
        var rows_to_move = [];
        rows_to_move.push(drag_bvr.src_el);

        if (src_group_level < dest_group_level) {
            spt.alert("Cannot drop item on a lower level");
            return;
        } else if (src_group_level == dest_group_level+2) {
            spt.alert("Cannot drop");
            return;
        } else if (src_group_level == dest_group_level || src_group_level == dest_group_level+1) {

            // bring along all group_levels higher than this one
            var group_level = drag_bvr.src_el.getAttribute("spt_group_level");
            var sibling = drag_bvr.src_el.getNext();
            while (sibling != null) {
                var sibling_group_level = sibling.getAttribute("spt_group_level");

                if (sibling_group_level > group_level) {
                    rows_to_move.push(sibling);
                }
                else {
                    break;
                }

                sibling = sibling.getNext();
            }
            rows_to_move.reverse();
        }

        // Determine where to inject
        var inject_el = drop_on_el;
        if (src_group_level == dest_group_level) {
            
            var sibling = drop_on_el;
            var next_sibling = drop_on_el.getNext();

            while (sibling != null) {
                var sibling_group_level = next_sibling.getAttribute("spt_group_level");
 
                if (sibling_group_level <= src_group_level) {
                    inject_el = sibling;
                    break;
                } 
                sibling = next_sibling;
                next_sibling = sibling.getNext();
            }
        }
        
        var inject_el_index = inject_el.rowIndex;

        // Move rows 
        for (var i = 0; i < rows_to_move.length; i++) {
            rows_to_move[i].inject(inject_el, "after");
        }

        // change spt_dynamic based on parent group
        if (!drag_bvr.src_el.hasClass("spt_table_group_row")) {
            var drop_on_group = drop_on_el.hasClass("spt_table_group_row") 
                ? drop_on_el 
                : spt.table.get_parent_groups(drop_on_el, dest_group_level-1);
            
            var spt_dynamic = drop_on_group.getAttribute("spt_dynamic");
            drag_bvr.src_el.setAttribute("spt_dynamic", spt_dynamic);
        }
            
        var index = drag_bvr.src_el.rowIndex;

        var top = drag_bvr.src_el.getParent(".spt_document_top");
        var search_type = top.getAttribute("spt_search_type");

        // fire a client event
        var event = "reorderX|"+search_type;
        spt.named_events.fire_event(event, {
            src_el: drag_bvr.src_el,
            options: {
                prev_index: prev_index,
                index: index,
                inject_el_index: inject_el_index,
            },

        });


        document.id(document.body).setStyle("cursor", 'default');
        drag_bvr.src_el.setStyle("cursor", "default");
        

    }
}


spt.document.delete = function(src_el) {

    var parent_row = src_el.getParent("tr");
    if (parent_row.hasClass("spt_group_row")) {
    var delete_group_cmd = spt.document.delete_group(src_el);
    Command.execute_cmd(delete_group_cmd);
    Command.add_to_undo(delete_group_cmd);
    }
    else if (parent_row.hasClass("spt_table_row_item")) {
    var delete_row_cmd = spt.document.delete_row(src_el);
    Command.execute_cmd(delete_row_cmd);
    Command.add_to_undo(delete_row_cmd);
    }


}


spt.document.delete_group = function(src_el) {

    parent_row = src_el.getParent("tr");
    
    // delete all group_levels higher than this one
    var rows_to_delete = [];
    rows_to_delete.push(parent_row);
    var group_level = parent_row.getAttribute("spt_group_level");
    var sibling = parent_row.getNext();
    while (sibling != null) {
    var sibling_group_level = sibling.getAttribute("spt_group_level");

    if (sibling_group_level > group_level) {
        rows_to_delete.push(sibling);
    } else {
        break;
    }

    sibling = sibling.getNext();
    }

    var layout = src_el.getParent(".spt_layout");
    var gantt_top = layout.getElement(".spt_gantt_top");
    spt.gantt.set_top( gantt_top );
    var gantt_rows = gantt_top.getElements(".spt_gantt_row_item");

    var delete_group = new Command();
    delete_group.rows_to_delete = rows_to_delete;
    
    delete_group.undo = function() {
    for (var i = 0; i < this.rows_to_delete.length; i++) {
            var row = this.rows_to_delete[i];
            if (row.hasClass("spt_group_row")) {
                row.setAttribute("spt_deleted", false);
                var index = row.rowIndex;
                var gantt_row = gantt_rows[index];
                //gantt_row.setStyle("background-color", "");
                gantt_row.setStyle("opacity", 1);
            } else {
                cmd = row.cmd;
                cmd.undo()
            }
        } 

    }

    delete_group.redo = function() {
        for (var i = 0; i < this.rows_to_delete.length; i++) {
            var row = this.rows_to_delete[i];
            if (row.hasClass("spt_group_row")) {
                row.setAttribute("spt_deleted", true);
                var index = row.rowIndex;
                var gantt_row = gantt_rows[index];
                //gantt_row.setStyle("background-color", "rgb(220, 93, 93)");
                gantt_row.setStyle("opacity", ".5");
            } else {
                cmd = spt.document.delete_row(row);
                row.cmd = cmd;
                Command.execute_cmd(cmd);
            }
        }
    }
    
    delete_group.execute = function() {
        this.redo();
    }

    return delete_group;

}

spt.document.delete_row = function(src_el) {
    
    var delete_row = new Command();
  
    if (src_el.hasClass("spt_table_row")) { 
        delete_row.parent = src_el;
        var child_row = src_el.getElement(".spt_menu_item");
        delete_row.element = child_row;
    } else {
    delete_row.element = src_el;
    var parent_row = src_el.getParent("tr");
    delete_row.parent = parent_row;
    }

    var search_key = delete_row.parent.get("spt_search_key_v2");
    var document_top = src_el.getParent(".spt_document_top");
    var gantt_items_top = document_top.getElement(".spt_gantt_items_top");
    var spt_gantt_rows = gantt_items_top.getElements(".spt_gantt_row_item");
    for (var i = 0; i < spt_gantt_rows.length; i++) {
        var gantt_row = spt_gantt_rows[i];
        if (gantt_row.getAttribute("spt_search_key") == search_key) {
            sister_gantt_row = gantt_row;
            break;
        }
    }
    if (!sister_gantt_row) {
        console.log("Could not find the sister gantt row.");
        return;
    }
    delete_row.sister_gantt_row = sister_gantt_row;

    // What if previousSibling changes?
    delete_row.sibling = delete_row.parent.previousSibling;
    
    var add_to_extra_data = function(el, name, value) {
        var extra_data = el.extra_data;
        if (!extra_data) {
            extra_data = {}
        }
        extra_data[name] = value
        el.extra_data = extra_data;
    }

    delete_row.undo = function() {
        this.parent.setStyle("background-color", "");
        this.parent.setAttribute("spt_background", "");
        this.parent.setStyle("opacity", 1);
        
        var child = this.sister_gantt_row.getElement("div");
        //child.setStyle("background-color", "");
        this.sister_gantt_row.setStyle("opacity", 1);
        
        this.parent.setAttribute("spt_deleted", false);
        add_to_extra_data(this.parent, 's_status', '');
        
        this.parent.addClass("spt_row_changed");
    }

    delete_row.redo = function() {
        this.parent.setStyle("background-color", "rgb(220, 93, 93)");
        this.parent.setAttribute("spt_background", "rgb(220, 93, 93)");
        
        this.parent.setStyle("opacity", .5);
        
        var child = this.sister_gantt_row.getElement("div");
        //child.setStyle("background-color", "rgb(220, 93, 93)");
        this.sister_gantt_row.setStyle("opacity", .5);
        
        this.parent.setAttribute("spt_deleted", true);
        add_to_extra_data(this.parent, 's_status', 'deleted');
    
        // If a new row is added, then deleted, we don't want
        // spt.table.has_changes() to see deleted row.
        if (this.parent.hasClass("spt_table_insert_row")) {
            this.parent.removeClass("spt_row_changed");
        } else {
            this.parent.addClass("spt_row_changed");
        }
    
    }
    
    delete_row.execute = function() {
        this.redo();
    }

    return delete_row;
} 




spt.document.add_rows = function( row, search_type, group_level) {
    spt.table.add_rows(row, "sthpw/task", group_level);
}


// document undo/redo functionality


spt.document.add_action = function() {

    var undo_el = spt.document.get_undo_el();
    var commands = undo_el.commands;

    var action = function() {
        

    }

}




spt.document.undo = function() {

}

spt.document.redo = function() {

}



        '''



class DocumentItemWdg(SimpleTableElementWdg):

    ARGS_KEYS = {
        "view": {
            'description': "Custom view to display",
            'type': 'TextWdg',
            'order': 0,
            'category': 'Required'
        },
    }
 

    def handle_tr(self, tr):

        sobject = self.get_current_sobject()
        group_level = sobject.get_value("group_level", no_exception=True)

        tr.add_attr("spt_group_level", group_level)

        children = sobject.get_value("children", no_exception=True)
        if children:
            tr.add_attr("spt_children", children)


    def handle_td(self, td):
        sobject = self.get_current_sobject()
        
        name = sobject.get_value("name", no_exception=True) or "N/A"

        td.add_style("overflow: hidden")
        td.add_style("text-overflow: ellipsis")
        td.add_style("padding: 0")
        td.add_attr("data-toggle", "tooltip")
        td.add_attr("title", name)


    def get_display(self):

        view = self.kwargs.get("view")
        if not view:
            return super(DocumentItemWdg, self).get_display()

        sobject = self.get_current_sobject()
        search_key = sobject.get_search_key()

        from tactic.ui.panel import CustomLayoutWdg
        layout = CustomLayoutWdg(view=view, sobject=sobject, search_key=search_key)

        return layout



class DocumentSaveCmd(Command):

    def execute(self):
        view = self.kwargs.get("view") or "document"
        document = self.kwargs.get("document")
        search_type = self.kwargs.get("search_type")
        project_code = self.kwargs.get("project_code") or Project.get_project_code()

        # content = document.get("content")

        # group_titles = [item.get("title") for item in content if item.get("group_level") == 1]

        # if "discipline" in view:
        #     group_titles = [item.get("title").strip().lower() for item in content if item.get("group_level") == 1]
        # else:
        #     group_titles = [item.get("title").strip().lower() for item in content if item.get("group_level") == 2]

        # if len(group_titles) != len(set(group_titles)):
        #     raise ValueError('Group names are not unique')

        search = Search("config/widget_config")
        search.add_filter("view", view)
        search.add_filter("search_type", search_type)
        search.add_filter("category", "%s library" % project_code)
        config = search.get_sobject()

        if config:
            config.set_json_value("config", document)
        else: 
            config = SearchType.create("config/widget_config")
            config.set_value("view", view)
            config.set_value("search_type", search_type)
            config.set_value("category", "%s library" % project_code)
            config.set_json_value("config", document)

        config.commit()








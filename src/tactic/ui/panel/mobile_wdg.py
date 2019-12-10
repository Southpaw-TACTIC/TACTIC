

from tactic.ui.common import BaseRefreshWdg
from pyasm.web import DivWdg, HtmlElement

class MobileTableWdg(BaseRefreshWdg):


    def get_display(self):

        top = self.top

        top.add_class("spt_mobile_table d-block d-sm-none row")

        div = DivWdg()
        top.add(div)

       
        top.add_behavior({
            'type': 'load',
            'cbjs_action': self.get_onload_js()
        })

        top.add(self.get_styles())

        
        table_id = self.kwargs.get("table_id")
        top.add_behavior({
            'type': 'listen',
            'event_name': 'loading_pending|%s' % table_id,
            'cbjs_action': '''
                var layout = bvr.src_el.getParent(".spt_layout");
                spt.table.set_layout(layout);
                
                if (spt.mobile_table) spt.mobile_table.load();
            '''
        })

        top.add_behavior({
            'type': 'listen',
            'event_name': 'window_resize',
            'cbjs_action': '''
                var layout = bvr.src_el.getParent(".spt_layout");
                spt.table.set_layout(layout);
                
                if (spt.mobile_table) spt.mobile_table.load();
            '''
        })

        return top


    def get_styles(self):
        style = HtmlElement.style("""
.spt_mobile_table {
    flex-direction: column;
    overflow-y: auto;
    overflow-x: hidden;
    height: calc(100% - 80px);
    width: 100%;
}

.spt_mobile_table .spt_resize_handle {
    display: none;
}

.spt_mobile_table .spt_table_row {
    height: unset !important;
    min-height: unset !important;
}

.spt_mobile_table .spt_table_row .spt_filter_button {
    display: none;
}
        """)

        return style


    def get_onload_js(self):
        return '''

if (spt.mobile_table) {
    spt.mobile_table.load();
    return;
}

spt.Environment.get().add_library("spt_mobile_table");
spt.mobile_table = {}

spt.mobile_table.top;
spt.mobile_table.set_top = function() {
    spt.mobile_table.top = spt.table.get_layout().getElement(".spt_mobile_table");
}

spt.mobile_table.get_top = function() {
    spt.mobile_table.top = spt.table.get_layout().getElement(".spt_mobile_table");
    return spt.mobile_table.top;
}


spt.mobile_table._convert_el_to_div = function(el) {

    let new_el = new Element("div");
    let attrs = el.getAttributeNames()
    attrs.forEach(function(attr) {
        new_el.setAttribute(attr, el.getAttribute(attr));
    });

    return new_el;

}

spt.mobile_table._handle_row = function(row) {
    let new_row = spt.mobile_table._convert_el_to_div(row);

    spt.mobile_table._remove_desktop_styles(row);
    
    new_row.addClass("row");

    return new_row;
}

spt.mobile_table._handle_cell = function(cell) {
        
    let new_cell = spt.mobile_table._convert_el_to_div(cell);
    new_cell.innerHTML = cell.innerHTML;
    
    spt.mobile_table._remove_desktop_styles(cell);

    return new_cell;
}

spt.mobile_table._handle_header = function(header) {
    let new_header = spt.mobile_table._convert_el_to_div(header)
    new_header.innerHTML = header.innerHTML;

    spt.mobile_table._remove_desktop_styles(new_header);

    return new_header;
}

spt.mobile_table._remove_desktop_styles = function(el) {
    el.setAttribute("table_style", el.getAttribute("style"));
    el.removeAttribute("style");
    
    let children = el.getChildren();
    if (children.length > 0) {
        el.innerHTML = "";
        children.forEach(function(child) {
            let new_child = spt.mobile_table._remove_desktop_styles(child);
            new_child.inject(el);
        });
    }
    return el;
}

spt.mobile_table._reapply_desktop_styles = function(el) {

}



spt.mobile_table.headers = [];

spt.mobile_table.create_card = function(row) {

    let new_row = spt.mobile_table._handle_row(row);
    let children = row.getChildren();
    
    for (var i=0; i<children.length; i++) {
        let child = children[i];
        if (child.hasClass("spt_table_select")) continue;
       
        let header = spt.mobile_table.headers[i-1];
        if (header) {
            var label = header.clone();
        } else {
            var label = new Element("div");
            label.innerHTML = "HEADER";
        }
        label.addClass("col-6");
        label.inject(new_row);

        let new_child = spt.mobile_table._handle_cell(child)
        new_child.addClass("col-6");
        new_child.inject(new_row);
    }

    let card = new Element("div");
    new_row.inject(card);

    let col = new Element("div");
    col.addClass("col-md-4 card box-shadow m-2");
    card.inject(col);
    return col;
}

spt.mobile_table.get_mobile_cards = function() {
    mobile_table = spt.mobile_table.get_top();
    let rows = mobile_table.getElements(".spt_table_row");
    return rows;
}


spt.mobile_table.load = function() {
    mobile_table = spt.mobile_table.get_top();
    if (!spt.is_shown(mobile_table)) return;

    
    let headers = spt.table.get_headers()
    let new_headers = [];
    headers.forEach(function(header) {
        let new_header = spt.mobile_table._handle_header(header);
        new_headers.push(new_header);
    });
    spt.mobile_table.headers = new_headers;

    let mobile_rows = spt.mobile_table.get_mobile_cards();
    let rows = spt.table.get_all_rows();
    let new_rows = rows.slice(mobile_rows.length);
    if (!new_rows || new_rows.length == 0) return;
    new_rows.forEach(function(row){
        let card = spt.mobile_table.create_card(row);
        card.inject(mobile_table);
    });

}

spt.mobile_table.load();

        '''



from tactic.ui.common import BaseRefreshWdg
from pyasm.web import DivWdg

class MobileTableWdg(BaseRefreshWdg):


    def get_display(self):

        top = self.top

        top.add_class("spt_mobile_table")

        div = DivWdg()
        top.add(div)

       
        top.add_behavior({
            'type': 'load',
            'cbjs_action': self.get_onload_js()
        })

        return top


    def get_onload_js(self):

        return '''

spt.table.mobile_table = {}


convert_el_to_div = function(el) {

    var new_el = new Element("div");
    var attrs = el.getAttributeNames()
    attrs.forEach(function(attr) {
        if (attr == "class") {
            new_el.setAttribute("table_class", el.getAttribute(attr));
        } else if (attr == "style") {
            new_el.setAttribute("table_style", el.getAttribute(attr));
        } else {
            new_el.setAttribute(attr, el.getAttribute(attr));
        }
    });

    return new_el;

}

handle_row = function(row) {
    var new_row = convert_el_to_div(row);
    new_row.addClass("row");
    return new_row;
}

handle_cell = function(cell) {
        
    var new_cell = convert_el_to_div(cell);
    new_cell.innerHTML = cell.innerHTML;
    return new_cell;
}


spt.table.mobile_table.create_card = function(row) {

    new_row = handle_row(row);
    var children = row.getChildren();
    children.forEach(function(child) {
        label = new Element("div")
        label.innerHTML = "ATTRIBUTE";
        label.addClass("col-6")
        label.inject(new_row)
        
        new_child = handle_cell(child)
        new_child.addClass("col-6")
        new_child.inject(new_row);
    });

    var card = new Element("div");
    new_row.inject(card);

    var col = new Element("div");
    col.addClass("col-md-4 card box-shadow m-2");
    card.inject(col);
    return col;
}

spt.table.mobile_table.load = function() {

    var layout = bvr.src_el.getParent(".spt_layout");
    spt.table.set_layout(layout);

    var rows = spt.table.get_all_rows();
    rows.forEach(function(row){
        var card = spt.table.mobile_table.create_card(row);
        card.inject(bvr.src_el);
    });

    bvr.src_el.addClass("row");
}


spt.table.mobile_table.load()
        '''

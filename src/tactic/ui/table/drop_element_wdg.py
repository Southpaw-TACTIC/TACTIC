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


__all__ = ['DropElementWdg', 'DropElementAction', 'RelatedElementAction']

import re

from pyasm.common import Common, jsonloads, jsondumps
from pyasm.command import Command, DatabaseAction
from pyasm.search import Search, SearchKey, SearchType
from pyasm.web import DivWdg, WebContainer, SpanWdg, Widget
from pyasm.biz import Schema, Project
from pyasm.prod.biz import ShotInstance
from pyasm.widget import HiddenWdg, IconWdg
from pyasm.biz import ExpressionParser

from tactic.ui.common import SimpleTableElementWdg



class DropElementWdg(SimpleTableElementWdg):

    ARGS_KEYS = {
    'accepted_drop_type': {
        'description': 'This will enforce the SType that can be accepted on this drop',
        'category': 'Options',
        'order': 1
    
    },
    'cbjs_drop_action': {
        'description': 'Custom javascript callback to call when a drop has occured.  This is optional',
        'type': 'TextAreaWdg',
        'category': 'Options',
        'order': 3
    },
      'instance_type': {
        'description': 'The SType name for the table that carries out the association',
        'category': 'Options',
        'order': 2
    },
        'display_expr': {
        'description': 'Display Expression for the dropped item. e.g. @GET(.code)',
        'category': 'Options',
        'order': 4
    }
    #'cbpy_drop_action': 'Custom python callback when save is done'
    }
    """
    def get_args_keys(cls):
        return cls.ARGS_KEYS
    get_args_keys = classmethod(get_args_keys)
    """


    def get_width(my):
        return 150

    
    def _get_sorted_instances(my):
        sobject = my.get_current_sobject()

        instance_type = my.get_option("instance_type")
        instances = sobject.get_related_sobjects(instance_type)
        # sorting now
        name_dict ={}
        for inst in instances:
            name_dict[inst] = inst.get_display_value()

        return sorted(instances, key=name_dict.__getitem__)

    def is_editable(cls):
        return False
    is_editable = classmethod(is_editable)



    def handle_layout_behaviors(my, layout):
        #my.menu.set_activator_over(layout, "spt_drop_item")
        #my.menu.set_activator_out(layout, "spt_drop_item")
        layout.add_behavior( {
            'type': 'load',
            'cbjs_action': get_onload_js()
        } )



    def handle_td(my, td):
        # FIXME: this is some hackery borrowed from the work to make gantt widget not commit on change
        # ... need to clean this up at some point!
        version = my.parent_wdg.get_layout_version()
        if version != "2":
            td.add_attr('spt_input_type', 'gantt')
            td.add_class("spt_input_inline")
        super(DropElementWdg, my).handle_td(td)

    def get_value_wdg(my):
        return my.value_wdg


    def handle_tr(my, tr):
        # define the drop zone
        version = my.parent_wdg.get_layout_version()
        





    def handle_th(my, th, wdg_idx=None):
        th.add_attr('spt_input_type', 'inline')

        """
        # handle finger menu
        my.top_class = "spt_drop_element_menu"
        from tactic.ui.container import MenuWdg, MenuItem
        my.menu = MenuWdg(mode='horizontal', width = 25, height=20, top_class=my.top_class)


        menu_item = MenuItem('action', label=IconWdg("Add User", IconWdg.ADD))
        my.menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''
            '''
        } )


        widget = DivWdg()
        widget.add_class(my.top_class)
        widget.add_styles('position: absolute; display: none; z-index: 1000')
        widget.add(my.menu)
        th.add(widget)
        """


 

    """ FIXME: Waiting until this is implemented
    def handle_th(my, th, wdg_idx=None):

        from tactic.ui.container import MenuWdg, MenuItem
        my.menu = MenuWdg(mode='horizontal', width = 40)
        th.add(my.menu)

        menu_item = MenuItem('action', label='delete')
        my.menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''alert('cow');'''
        } )


        menu_item = MenuItem('action', label='kill')
        my.menu.add(menu_item)
        menu_item.add_behavior( {
            'type': 'click_up',
            'cbjs_action': '''alert('cow');'''
        } )
    """


    def add_drop_behavior(my, widget, accepted_search_type=''):

        js_callback = my.get_option("cbjs_drop_action")
        if not js_callback:
            js_callback = 'spt.drop.sobject_drop_action(evt,bvr)'

        py_callback = my.get_option("cbpy_drop_action")
        #assert(py_callback)

        # define the drop zone
        widget.set_attr('SPT_ACCEPT_DROP', 'DROP_ROW')
        widget.add_behavior( {
            'type': 'accept_drop',
            'drop_code': 'DROP_ROW',
            'accepted_search_type': accepted_search_type,
            'cbjs_action': js_callback,
            'cbpy_action': py_callback,
        } )

        widget.add_behavior( {
            'type': 'mouseleave',
            'cbjs_action': '''
            var orig_border_color = bvr.src_el.getAttribute('orig_border_color');
            var orig_border_style = bvr.src_el.getAttribute('orig_border_style');
                bvr.src_el.setStyle('border-color', orig_border_color)
                bvr.src_el.setStyle('border-style', orig_border_style)
                '''
            })


    def get_text_value(my): 
        sorted_instances = my._get_sorted_instances()
        names = ''
        for inst in sorted_instances:
            names += '%s ' % inst.get_display_value()
        return names 

    def get_display(my):
        my.display_expr = my.kwargs.get('display_expr')
        my.values = []

        instance_type = my.get_option("instance_type")
        accepted_type = my.get_option("accepted_drop_type")

        div = DivWdg()
        div.add_class("spt_drop_element_top")
        div.add_style("width: 100%")
        div.add_style("height: 100%")
        div.add_style("min-width: 100px")
        div.add_style("max-height: 300px")
        div.add_style("overflow-y: auto")

        my.value_wdg = HiddenWdg(my.get_name())
        my.value_wdg.add_class("spt_drop_element_value")
        div.add( my.value_wdg )



        version = my.parent_wdg.get_layout_version()
        #if version != "2":
        my.add_drop_behavior(div, accepted_type)



        # add the hidden div which holds containers info for the sobject
        template_div = DivWdg()
        template_div.add_style("display: none")
        template_item = my.get_item_div(None)

        # float left for the new icon beside it
        item_div = template_item.get_widget('item_div')
        item_div.add_style('float: left')

        template_item.add_class("spt_drop_template")
        #template_item.add_style('float: left')
        new_icon = IconWdg("New", IconWdg.NEW)
        new_icon.add_style('padding-left','3px')
        #TODO: insert the new_icon at add(new_icon, index=0) and make sure
        # the js-side sobject_drop_action cloning align the template div properly
        #template_item.add(" - ")
        template_item.add(new_icon)
        template_div.add(template_item)
        div.add(template_div)


        # list out the relationships
        #sobject = my.get_current_sobject()
        #search_type = sobject.get_base_search_type()

 
        content_div = DivWdg()
        div.add(content_div)
        # shrink wrapping for FF
        content_div.add_style('float: left')
        content_div.add_class("spt_drop_content")

        if instance_type:
            instance_wdg = my.get_instance_wdg(instance_type)
            content_div.add(instance_wdg)
            
        return div





    def get_instance_wdg(my, instance_type):
        sorted_instances = my._get_sorted_instances()
        content_div = Widget()

        for instance in sorted_instances:
            item_div = my.get_item_div(instance)
            item_div.add_attr( "spt_search_key", SearchKey.get_by_sobject(instance) )
            item_div.add_class("spt_drop_item")

            # no need for that
            #item_div.add('&nbsp;')
            content_div.add(item_div)
        value_wdg = my.get_value_wdg()
        json = jsondumps(my.values)
        json = json.replace('"', '&quot;')
        value_wdg.set_value(json)

        return content_div




    def get_item_div(my, sobject):
        ''' get the item div the sobject'''
        top = DivWdg()
        top.add_style("padding: 3px 2px")
        top.add_attr('title','Click to remove')
        # FIXME: put this here for now
        top.add_behavior( {
            'type': 'click_up',
            #'cbjs_action': '''spt.dg_table_action.sobject_drop_remove(evt,bvr)'''
            'cbjs_action': '''spt.drop.sobject_drop_remove(evt,bvr)'''
        } )

        top.add_class("spt_drop_item")
        top.add_class("SPT_DROP_ITEM")

        item_div = DivWdg()
        item_div.add_class("hand")
        item_div.add_style("float: clear")
        top.add(item_div, "item_div")


        #my.menu.set_over(item_div, event="mousein")
        #my.menu.set_out(top, event="mouseleave")


        # set this as the place for the display value to go
        item_div.add_class("spt_drop_display_value")

        add_icon = True
        ExpressionParser.clear_cache()
        if sobject:
            if add_icon:
                my._add_icon(sobject, item_div)

            if my.display_expr:
                display_value = Search.eval(my.display_expr, sobjects = sobject, single=True)
            else:
                display_value = sobject.get_display_value()
            if isinstance(display_value, list):
                display_value = display_value[0]
            item_div.add( display_value )
            my.values.append( SearchKey.get_by_sobject(sobject) )
        return top

    def _add_icon(my, sobject, item_div):
        '''add icon to the item_div'''
        if sobject.get_base_search_type() == 'sthpw/login_in_group':
            icon = IconWdg(icon=IconWdg.USER)
            item_div.add(icon)


class DropElementAction(DatabaseAction):

    # Specific server side call-back to handle dragging a user on a group
    #
    def execute(my):
        web = WebContainer.get_web()
        value = web.get_form_value( my.get_input_name() )
        if not value:
            value = my.get_data()

        if not value:
            return


        src_search_keys = jsonloads(value)
        #print "xxx: ", type(src_search_keys), src_search_keys

        # get all fo the sobjects from the search keys
        #src_sobjects = SearchKey.get_by_search_keys(src_search_keys)
        instance_type = my.get_option("instance_type")
        # path is used for self-relating in an instance table
        src_path = my.get_option("path")

        src_sobjects = []
        src_instances = []
        for src_search_key in src_search_keys:
            src_sobject = SearchKey.get_by_search_key(src_search_key)

            if src_sobject.get_base_search_type() == instance_type:
                src_instances.append(src_sobject)
            else:
                src_sobjects.append(src_sobject)


        dst_sobject = my.sobject

        
        # get all of the current instances and see if any were removed
        instances = dst_sobject.get_related_sobjects(instance_type)
        for instance in instances:
            exists = False
            for src_instance in src_instances:
                if src_instance.get_search_key() == instance.get_search_key():
                    exists = True

            if not exists:
                instance.delete()


        # add all the new sobjects
        for src_sobject in src_sobjects:

            instance = SearchType.create(instance_type)
            instance.add_related_connection(src_sobject, dst_sobject, src_path=src_path)

            instance.commit()




def get_onload_js():

    return '''

spt.drop = {};

spt.drop.src_el = null;

// Drop functionality
spt.drop.sobject_drop_setup = function( evt, bvr )
{
    var ghost_el = $("drag_ghost_copy");
    if (!ghost_el) {
        ghost_el =  new Element('div', {
			styles: {
				background: '#393950',
                                color: '#c2c2c2',
                                border: 'solid 1px black',
                                textAlign: 'left',
                                padding: '10px',
                                filter: 'alpha(opacity=60)',
                                opacity: '0.6',
                                position: 'absolute', 
                                display: 'none', 
                                left: '0px', top: '0px',
                                zIndex: '400'
                                    
			},
            element_copied: '_NONE_',
			id: 'drag_ghost_copy',
            class: 'SPT_PUW'
		});
            ghost_el.inject(document.body);
            bvr.drag_el = ghost_el
    }

    ghost_el.setStyle("width","auto");
    ghost_el.setStyle("height","auto");
    ghost_el.setStyle("text-align","left");
    
    // Assumes that source items being dragged are from a DG table ...
    //var src_el = bvr.src_el; 
    var src_el = spt.behavior.get_bvr_src( bvr );
    spt.drop.src_el = src_el;

    var src_table_top = src_el.getParent(".spt_table_top");
    var src_layout = src_table_top.getElement(".spt_layout");
   
    spt.table.set_layout(src_layout);
    
    var src_search_keys = spt.table.get_selected_codes();
  

    if (src_search_keys.length == 0) {
        // if items aren't selected in the table then just get the specific row that was dragged ...
        var server = TacticServerStub.get();
        var row = src_el.getParent(".spt_table_row");
        var src_search_key = row.getAttribute("spt_search_key_v2");
        var tmps = server.split_search_key(src_search_key)
        if (tmps && tmps[1] != null) {
            src_search_keys = [tmps[1]];
        }
    }

    var inner_html = [ "<i><b>--- Drop Contents ---</b></i><br/><pre>" ];
    for( var c=0; c < src_search_keys.length; c++ ) {
        var search_key = src_search_keys[c];
        if (!search_key) continue;

        if( search_key.indexOf("-1") != -1 ) {
            continue;
        }
        inner_html.push( "  " + search_key.strip() );
        if( c + 1 < src_search_keys.length ) {
            inner_html.push( "<br>" );
        }
    }
    inner_html.push("</pre>");

    if (ghost_el) {
        ghost_el.innerHTML = inner_html.join("");
    }
    
}


// Called when selected search_types are dropped onto a drop zone
//
spt.drop.sobject_drop_action = function( evt, bvr )
{
    //var src_el = bvr._drop_source_bvr.src_el; 
    var src_el = spt.drop.src_el;
  
    if( bvr._drag_copy_el ) {
   
        spt.mouse._delete_drag_copy( bvr._drag_copy_el );
        delete bvr._drag_copy_el;
    }
    //var dst_el = bvr.src_el;
    var dst_el = spt.get_event_target(evt);
  
    // sometimes, spt.drop.src_el is cleared during motion for unknown reasons.
    if (!src_el)
        src_el = spt.behavior.get_bvr_src( bvr );

    if (!src_el)
        return;
    
    
    spt.drop.src_el = null;
    var dst_layout = dst_el.getParent(".spt_layout");
    var src_layout = src_el.getParent(".spt_layout");

    // backwards compatibiity to old table
    var dst_version = dst_layout? dst_layout.getAttribute("spt_version") : '2';
    if (dst_version != "2") {
        return spt.dg_table_action.sobject_drop_action(evt, bvr);
    }

    // get the source serach_type
    var search_type = src_layout.getAttribute("spt_search_type");

    var accepted_search_type = bvr.accepted_search_type;
    if (typeof(accepted_search_type) != 'undefined' && accepted_search_type != '' && accepted_search_type != search_type) {
        spt.alert('Only search types ['+accepted_search_type+'] are accepted');
        return;
    }

    
    spt.drop.add_src_to_dst(src_el, dst_el);
}
 

spt.drop.add_src_to_dst = function( src_el, dst_el )
{
    // get all the source items
    var src_layout = src_el.getParent(".spt_layout");
    if (!src_layout) {
        log.warning("The source table is not the matching fast table layout.");
        return;
    }
    spt.table.set_layout(src_layout);
    var src_rows = spt.table.get_selected_rows();
    if (src_rows.length == 0) {
        if (src_el.hasClass("spt_table_row")) {
            src_rows = [src_el];
        }
        else {
            src_rows = [src_el.getParent(".spt_table_row")];
        }
    }
    var src_search_keys = [];
    var src_display_values = [];
    for (var i = 0; i < src_rows.length; i++) {
        var row = src_rows[i];

        var search_key = row.getAttribute("spt_search_key_v2");
        src_search_keys.push(search_key);

        var display_value = row.getAttribute("spt_display_value");
        if (display_value == null) {
            display_value = search_key;
        }
        src_display_values.push( display_value );
    }



    // get all the dst items
    var dst_layout = dst_el.getParent(".spt_layout");
    spt.table.set_layout(dst_layout);
    var dst_rows = spt.table.get_selected_rows();
    if (dst_rows.length == 0) {
        if (dst_el.hasClass("spt_table_row")) {
            dst_rows = [dst_el];
        }
        else {
            dst_rows = [dst_el.getParent(".spt_table_row")];
        }
    }


    for (var i=0; i < dst_rows.length; i++){
        var top_el = dst_rows[i].getElement(".spt_drop_element_top");
        if (top_el)
            spt.drop.clone_src_to_droppable(top_el, src_search_keys, src_display_values);
    }

}


// function to clone src contents to a droppable td
spt.drop.clone_src_to_droppable = function(top_el, src_search_keys, src_display_values)
{
    var template = top_el.getElement(".spt_drop_template");
    var content = top_el.getElement(".spt_drop_content");

    // get the values
    var items = content.getElements(".spt_drop_item");
    var value = [];
    for (var i=0; i<items.length; i++) {
        var search_key = items[i].getAttribute("spt_search_key");
        value.push(search_key);
    }


    for (var i=0; i<src_search_keys.length; i++) {
        var src_search_key = src_search_keys[i];
        var src_display_value = src_display_values[i];

        if (value.indexOf(src_search_key) != -1) {
            alert("Item ["+src_display_value+"] already present");
            continue;
        }



        var clone = spt.behavior.clone(template);
        var item = clone.getElement(".spt_drop_display_value");
        item.innerHTML = src_display_value;
        clone.setAttribute("spt_search_key", src_search_key);

        content.appendChild(clone);

        value.push(src_search_key);
    }

    //var value_wdg = top_el.getElement(".spt_drop_element_value");
    //value_wdg.value = value;

    var value = JSON.stringify(value);

    // get the value
    var cell = top_el.getParent(".spt_cell_edit");
    spt.table.accept_edit(cell, value, false);
}


spt.drop.sobject_drop_remove = function( evt, bvr ) {
    var src_el = bvr.src_el;

    src_el.setStyle("border", "solid 1px red");

    var top_el = src_el.getParent(".spt_drop_element_top");
    var content = top_el.getElement(".spt_drop_content");

    src_el.destroy();

    // get the values
    var items = content.getElements(".spt_drop_item");
    var value = [];
    for (var i=0; i<items.length; i++) {
        var search_key = items[i].getAttribute("spt_search_key");
        value.push(search_key);
    }
    value = JSON.stringify(value);


    //var value_wdg = top_el.getElement(".spt_drop_element_value");
    //value_wdg.value = value;


    // set the row as being edited
    /*
    spt.dg_table.edit.widget = top_el;
    var key_code = spt.kbd.special_keys_map.ENTER;
    spt.dg_table.edit_cell_cbk( value_wdg, key_code );
    */

    var cell = top_el.getParent(".spt_cell_edit");
    spt.table.accept_edit(cell, value, false);
 
}
    '''






class RelatedElementAction(DatabaseAction):
    '''On inserting an sObject, add the relationship in a diff sType for many-to-many relationship
       this is most useful to put in the name or code column's Edit Mode
    
      <action class="tactic.ui.table.RelatedElementAction">
        <instance_type>prod/asset_in_asset</instance_type>
        <path>sub</path>
      </action>
    '''
    def execute(my):
        my.is_insert = False
        # this can only be determined in the execute method
        if my.sobject.is_insert() == True:
            my.is_insert = True
        super(RelatedElementAction, my).execute()


    def postprocess(my):
        web = WebContainer.get_web()
        value = web.get_form_value( my.get_input_name() )
        if not value:
            return
        
        # get all fo the sobjects from the search keys
        instance_type = my.get_option("instance_type")
        
        # path is used for self-relating in an instance table
        src_path = my.get_option("path")

    
        #src_sobject = my.sobject

        search = Search(my.sobject.get_search_type())
        search.add_id_filter(my.sobject.get_id())
        src_sobject = search.get_sobject()

        # this is passed in from EditCmd in insert mode
        parent_key = my.get_option('parent_key')
        # in some rare cases we have project as the parent_key
        if parent_key and my.is_insert and 'sthpw/project' not in parent_key:
            # this is the parent
            dst_sobject = SearchKey.get_by_search_key(parent_key)

            # add all the new sobjects
            #instances = dst_sobject.get_related_sobject(instance_type)
            instance = SearchType.create(instance_type)
            instance.add_related_connection(src_sobject, dst_sobject, src_path=src_path)

            instance.commit()





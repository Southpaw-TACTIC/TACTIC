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

__all__ = ['CreateSelectWdg', 'CreateSelectAction']

from pyasm.common import UserException
from pyasm.web import *
from pyasm.search import Search
from pyasm.command import DatabaseAction
from input_wdg import *
from icon_wdg import IconWdg
from web_wdg import HintWdg


class CreateSelectWdg(AjaxWdg, BaseInputWdg):

    ID = "CreateSelectWdg"
    SELECT_NAME = "creator_select"
    SELECT_ITEMS = 'select_items'
    DELETE_MODE = "delete_mode"
    NEW_ITEM = 'new_item'
    NEW_ITEM_LABEL = 'new_item_label'
    EMPTY = "EMPTY"
    TYPE = "TYPE"

    def __init__(self,name=None, value=None ):
        self.items = []
        self.new_item = ''
        self.search_key = ''
        self.col_name = ''
        self.type_select_val = ''
        super(CreateSelectWdg, self).__init__()

    
    def init_cgi(self):
    
        self.search_key = self.get_search_key()

        col_name = self.web.get_form_value('col_name')
        items = self.web.get_form_value('%s|%s' %(col_name, self.SELECT_ITEMS))
        delimiter = self.get_delimiter()
        if items:
            self.items = items.split(delimiter)
        self.new_item = self.web.get_form_value(self.NEW_ITEM)

        self.type_select_val = self.web.get_form_value(self.TYPE)
        
    def init_setup(self):
       
        hidden = HiddenWdg(self.DELETE_MODE)
        self.add_ajax_input(hidden)
        hidden = HiddenWdg(self.NEW_ITEM)
        self.add_ajax_input(hidden)
        hidden = HiddenWdg(self.NEW_ITEM_LABEL)
        self.add_ajax_input(hidden)
        hidden = HiddenWdg('search_type')
        self.add_ajax_input(hidden)
        hidden = HiddenWdg('search_id')
        self.add_ajax_input(hidden)
       
        if self.is_from_ajax():
            col_name = self.web.get_form_value('col_name')
        else:
            col_name = self.get_name()
        self.col_name = HiddenWdg('col_name', col_name)
        self.add_ajax_input(self.col_name)
        
        self.select_items = HiddenWdg('%s|%s' %(col_name, self.SELECT_ITEMS))
        self.add_ajax_input(self.select_items)

    def get_search_key(self):
        search_key = '%s|%s' % (self.web.get_form_value('search_type'), \
            self.web.get_form_value('search_id'))
        return search_key

    def get_my_sobject(self):
        sobject = self.get_current_sobject()
        if not self.search_key:
            search_id = self.web.get_form_value('search_id')
            if search_id != '-1':
                self.search_key = self.get_search_key()
                sobject = Search.get_by_search_key(self.search_key)
        return sobject
        

    def get_delimiter(self):
        return '|'

    def get_display(self):
        delimiter = self.get_delimiter()

        self.init_setup()
        sobject = self.get_my_sobject()

        select_items_name = '%s|%s' %(self.col_name.get_value(), self.SELECT_ITEMS)
        self.set_ajax_top_id(self.ID)
        widget = DivWdg(id=self.ID)
        # mode select
        mode_cb = FilterCheckboxWdg('display_mode', label='simple view', css='small')
        
        

        # return simple widget if selected
        if mode_cb.is_checked(False):
            mode_cb.set_checked()

            type_select = SelectWdg(self.TYPE, label='Type: ')
            type_select.set_option('values','sequence|map|string')
            type = self.get_my_sobject().get_value('type')
            if type:
                type_select.set_value(type)
            widget.add(type_select)
            widget.add(HtmlElement.br(2))
            text = TextWdg(select_items_name)
            text.set_value(self.get_value())
            text.set_attr('size', '70')
            widget.add(text)
            widget.add(HtmlElement.br(2))
            widget.add(mode_cb)
            return widget

        if self.is_from_ajax():
            widget = Widget()
        else:
            widget.add_style('display', 'block')
        widget.add(self.col_name)
        widget.add(self.select_items) 

        items = []
        sobj_items= []
        prod_setting_type = 'sequence'

        if sobject:
            sobj_value = sobject.get_value(self.col_name.get_value())
            sobj_items = sobj_value.split(delimiter)
            prod_setting_type = sobject.get_value('type') 
       
        delete_widget = Widget()
        delete_mode = HiddenWdg('delete_mode')
        delete_mode.set_persist_on_submit()

        # only needs it for the first time
        # NOTE: this essentially prevents a sequence from having no value at all
        if not self.items and not delete_mode.get_value()=='true':
            items.extend(sobj_items)
        items.extend(self.items)
      
        self.type_select = self.get_type_select(prod_setting_type)
       
        self.select_items.set_value(delimiter.join(items)) 
       
        self.select = self.get_item_list(items)
        item_span = ''
        if self.type_select_val == 'map':
            item_span = self.get_map_wdg()
            self.select.add_empty_option( '-- Map items --', self.EMPTY)
        else:
            item_span = self.get_sequence_wdg()
            self.select.add_empty_option( '-- Sequence items --', self.EMPTY)


        # delete item button
        icon = IconWdg('Select an item to remove', icon=IconWdg.DELETE)
        icon.add_class('hand')
        drop_script = ["drop_item('%s')" %self.SELECT_NAME]
        drop_script.append(self.get_refresh_script())
        icon.add_event('onclick', ';'.join(drop_script) )
        delete_widget.add(delete_mode)
        delete_widget.add(icon)
       
        function_script = '''function append_item(select_name, new_item, new_item_extra)
            {
                var new_item_val = get_elements(new_item).get_value()
                if (new_item_extra != null)
                    new_item_val = new_item_val + ':' + get_elements(new_item_extra).get_value()
                
                var items = get_elements('%s')
                var items_arr = new Array()
                var delimiter = '%s'
                if (items.get_value())
                    items_arr = items.get_value().split(delimiter)
                for (var i=0; i < items_arr.length; i++)
                {
                    if (new_item_val == items_arr[i])
                        return
                }

                var idx = document.form.elements[select_name].selectedIndex
                // skip the title item
                if (idx < 0)
                    idx = 0
                if (idx == 0)
                    idx = items_arr.length
                else
                    idx = idx - 1
                
                items_arr.splice(idx, 0, new_item_val)
                items.set_value(items_arr.join(delimiter))
            }
                '''% (select_items_name, delimiter)
        widget.add(HtmlElement.script(function_script))

        function_script = '''function drop_item(select_name)
            {
               
                var items = get_elements('%s')
                var items_arr = new Array()
                var delimiter = '%s'
                if (items.get_value())
                    items_arr = items.get_value().split(delimiter)

                var idx = document.form.elements[select_name].selectedIndex
                if (idx == 0 || idx == -1)
                {
                    alert('You need to pick an item to remove')
                    return
                }
                alert("'"+ items_arr[idx-1] + "' removed.")
                items_arr.splice(idx-1, 1)
                items.set_value(items_arr.join(delimiter))

                var delete_mode = get_elements('delete_mode')
                delete_mode.set_value('true')
            }
                '''% (select_items_name, delimiter)
        widget.add(HtmlElement.script(function_script))

        self.draw_widgets(widget, delete_widget, item_span)
        
        widget.add(HtmlElement.br(2))
        widget.add(mode_cb)
        self.add(widget)
        return super(CreateSelectWdg, self).get_display()

    def draw_widgets(self, widget, delete_widget, item_span):
        '''actually drawing the widgets'''
        widget.add(self.type_select)
        widget.add(SpanWdg(self.select, css='med'))
        widget.add(delete_widget)
        widget.add(HtmlElement.br(2))
        widget.add(item_span)

    def get_item_list(self, items):
        self.select = SelectWdg(self.SELECT_NAME)
        self.select.set_attr("size", '%s' %(len(items)+1))
        self.select.set_option('values', items)
        return self.select
        
    def get_type_select(self, item_type):
        type_select = SelectWdg(self.TYPE, label='Type: ')
        type_select.set_option('values','sequence|map|string')
        
        self.add_ajax_input(type_select)

        if self.type_select_val:
            type_select.set_value(self.type_select_val)
        else:
            type_select.set_value(item_type)
            self.type_select_val = item_type

        type_select.add_event('onchange', self.get_refresh_script(show_progress=False))
        return type_select

    def get_sequence_wdg(self):
        text_span = SpanWdg('New item ')
        text_span.add(HtmlElement.br())
        text = TextWdg(self.NEW_ITEM)
        text_span.add(text)

        button = self.get_sequence_button()
        text_span.add(button)
        return text_span

    def get_sequence_button(self):
        # add button
        widget = Widget()
        from pyasm.prod.web import ProdIconButtonWdg
        add = ProdIconButtonWdg('Add')
        script = ["append_item('%s','%s')" % (self.SELECT_NAME, self.NEW_ITEM )]
        script.append( self.get_refresh_script() )
        add.add_event('onclick', ';'.join(script))
        widget.add(add)

        hint = HintWdg('New item will be inserted before the currently selected item. '\
                'Click on [Edit/Close] to confirm the final change.', title='Tip') 
        widget.add(hint)
        return widget

    def get_map_wdg(self):
        text_span = SpanWdg('New [value] : [label] pair ')
        text_span.add(HtmlElement.br())
        text = TextWdg(self.NEW_ITEM)
        text_span.add(text)
        text_span.add(SpanWdg(':', css='small'))
        text = TextWdg(self.NEW_ITEM_LABEL)
        text_span.add(text)
        
        text_span.add(self.get_map_button())
        return text_span

    def get_map_button(self):
        widget = Widget()
        # add button
        from pyasm.prod.web import ProdIconButtonWdg
        add = ProdIconButtonWdg('Add')
        script = ["append_item('%s','%s','%s')" \
            % (self.SELECT_NAME, self.NEW_ITEM, self.NEW_ITEM_LABEL)]
        script.append( self.get_refresh_script() )
        add.add_event('onclick', ';'.join(script))
        widget.add(add)

        hint = HintWdg('New value:label pair will be inserted after the currently selected item.\
                Click on [Edit/Close] to confirm the final change.') 
        widget.add(hint)
        return widget

class CreateSelectAction(DatabaseAction):

    def check(self):
        self.web = WebContainer.get_web()
        self.items = self.web.get_form_value('%s|%s' %(self.name, CreateSelectWdg.SELECT_ITEMS))
        self.type = self.web.get_form_value(CreateSelectWdg.TYPE)

        
        if self.type == 'map' and ':' not in self.items:
            raise UserException('The values in the drop-down does not appear to be a map.\
                    Please choose "sequence" for Type and retry.') 
        return True

    def execute(self):
        
        self.sobject.set_value(self.name, self.items)
        self.sobject.set_value('type', self.type)
        self.sobject.commit()

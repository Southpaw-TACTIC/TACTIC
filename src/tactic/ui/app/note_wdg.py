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

__all__ = ['NoteSheetWdg','NoteTableElementWdg','NoteViewerWdg', 'SingleNoteViewerWdg']

from pyasm.web import WebContainer, Widget, HtmlElement, DivWdg, SpanWdg, FloatDivWdg, Table
from pyasm.widget import HiddenWdg, SubmitWdg, SelectWdg, TextWdg, IconButtonWdg, IconSubmitWdg, IconWdg, SwapDisplayWdg, TextAreaWdg, WidgetConfig, WidgetConfigView, CheckboxWdg
from pyasm.search import Search, SearchType, SearchKey
from pyasm.biz import Project, Pipeline
from pyasm.common import Container, Xml, Common, TacticException
from tactic.ui.filter import FilterData
from tactic.ui.common import BaseRefreshWdg, BaseTableElementWdg
from tactic.ui.panel import TableLayoutWdg
from tactic.ui.widget import TextBtnWdg, ActionButtonWdg

from dateutil import parser
       
class NoteSheetWdg(BaseRefreshWdg):

    ARGS_KEYS = {
    
     'use_parent': {
        'description': "whether to enter note for this sobject's parent",
        'type': 'SelectWdg',
        'values': 'true|false',
        'category':  'Display'

    },

    'append_context': {
        'description': "append one or more contexts. e.g. main|director",
        'type': 'TextWdg',
        'category': 'Display'
    }
    }

        
    def init(self):
        # for snapshot and task
        self.child_mode = self.kwargs.get('child_mode') == 'true'
        self.search_key = self.kwargs.get('search_key')
        self.element_class = self.kwargs.get('element_class')
        self.use_parent = self.kwargs.get('use_parent') == 'true'
        self.append_context = self.kwargs.get('append_context')
        
        self.orig_parent = None
         
        incoming_process = False
      
        if self.search_key:
            # coming in as search_key but it's actually the note's parent
            self.parent = Search.get_by_search_key(self.search_key)
            self.orig_parent = self.parent
            self.orig_parent_search_type = self.parent.get_search_type()

            if self.use_parent:
                self.parent = self.parent.get_parent()
                if not self.parent:
                    raise TacticException('Try not to set the display option [use_parent] to true since the parent cannot be found.')
                self.search_key = SearchKey.get_by_sobject(self.parent)
                # swap the kwargs key
                self.kwargs['search_key'] = self.search_key
                self.kwargs['use_parent'] = 'false'

            self.parent_search_type = self.parent.get_search_type()
            self.parent_search_id = self.parent.get_id()
        else:
            self.parent_search_type = self.kwargs.get('search_type')
            self.orig_parent_search_type = self.parent_search_type

            self.parent_search_id = self.kwargs.get('search_id')
            self.parent = Search.get_by_id(self.parent_search_type, self.parent_search_id)
            self.orig_parent = self.parent
            if self.use_parent:
                self.parent = self.parent.get_parent()
                if not self.parent:
                    raise TacticException('Try not to use the display option [use_parent] since the parent cannot be found.')
            if self.parent:
                self.search_key = SearchKey.get_by_sobject(self.parent)   
            if self.use_parent:
                self.kwargs['search_key'] =self.search_key
                self.kwargs['use_parent'] = 'false'

        self.process_names = []
        # get the process names
        process_names = self.kwargs.get('process_names')
        if not process_names:
            if self.orig_parent_search_type in ['sthpw/task','sthpw/snapshot']:
                #self.parent = self.parent.get_parent()
                # most tasks don't have context by default
                if self.orig_parent_search_type == 'sthpw/task':
                    context = self.orig_parent.get_value('context')
                    if not context:
                        context = self.orig_parent.get_value('process')
                else:
                    context = self.orig_parent.get_value('context')
                self.process_names = [context]
                self.child_mode = True
                self.kwargs['child_mode'] = 'true'

            else:
                self.pipeline_code = self.kwargs.get('pipeline_code')
                if not self.pipeline_code and self.parent.has_value('pipeline_code'):
                    self.pipeline_code = self.parent.get_value('pipeline_code')
                pipeline = Pipeline.get_by_code(self.pipeline_code)
                if pipeline:
                    self.process_names = pipeline.get_process_names()
        else:
            self.process_names = process_names.split("|")
            incoming_process = True


        self.is_refresh = self.kwargs.get('is_refresh')

        # if nothing is derived from pipeline, use defualts
        if not self.process_names: 
            self.process_names = ['default']
        if self.append_context and not incoming_process:
            contexts = self.append_context.split('|')
            self.process_names.extend(contexts)
           
        # for proper refresh
        self.kwargs['process_names'] = '|'.join(self.process_names)

    def _get_main_config(self, view, process_names):
        '''get the main config for this table layout'''
        xml = Xml()
        xml.create_doc("config")
        root = xml.get_root_node()
        view_node = xml.create_element(view)
        #root.appendChild(view_node)
        xml.append_child(root, view_node)
        
        for idx, process_name in enumerate(process_names):
            element  = xml.create_element('element')
            Xml.set_attribute(element, 'name', process_name)
            #view_node.appendChild(element)
            xml.append_child(view_node, element)
            display =   xml.create_element('display')
            if self.element_class:
                Xml.set_attribute(display, 'class',self.element_class)
            else:
                Xml.set_attribute(display, 'class', "tactic.ui.app.NoteTableElementWdg")
            #element.appendChild(display)
            xml.append_child(element, display)

            op_element = xml.create_data_element('parent_key', self.search_key)
            xml.append_child(display, op_element)
            

        config_xml = xml.to_string()
        widget_config = WidgetConfig.get(view=view, xml = config_xml)
        widget_config_view = WidgetConfigView('sthpw/note', view, [widget_config])

        return widget_config_view

    def _get_edit_config(self, view, process_names):
        xml = Xml()
        xml.create_doc("config")
        root = xml.get_root_node()
        view_node = xml.create_element(view)
        #root.appendChild(view_node)
        xml.append_child(root, view_node)
        for idx, process_name in enumerate(process_names):
            element  = xml.create_element('element')
            Xml.set_attribute(element, 'name', process_name)
            #view_node.appendChild(element)
            xml.append_child(view_node, element)
            display =   xml.create_element('display')
            Xml.set_attribute(display, 'class', "pyasm.widget.TextAreaWdg")
            #element.appendChild(display)
            xml.append_child(element, display)
        
        config_xml = xml.to_string()
        widget_config = WidgetConfig.get(view=view, xml = config_xml)
        widget_config_view = WidgetConfigView('sthpw/note', view, [widget_config])
        return widget_config_view

    def _get_inner_div(self):
        '''get the inner div for the process dialog'''
        inner_div = FloatDivWdg()
        inner_div.add_style("padding: 5px")
        inner_div.add_style('height: 260px')
        inner_div.add_color("background", "background")
        inner_div.add_color("color", "color")
        return inner_div

    def get_display(self):
        if self.is_refresh:
            top = Widget()
            self.add(top)
        else:
            container = DivWdg()
            self.add(container)
            #parent = SearchKey.get_by_search_key(self.search_key)
            top = DivWdg()
            container.add(top)
            self.set_as_panel(top)
            top.add_style("margin-top: -2px")
            
            top.add_class("spt_uber_notes_top")


        from tactic.ui.app import HelpButtonWdg
        help_button = HelpButtonWdg(alias="note-sheet-widget")
        top.add(help_button)
        help_button.add_style("float: right")

        table_id = 'sub_table'
        view = 'table'
        span = DivWdg(css='spt_input_group')
        top.add(span)

        span.add_border()
        span.add_style("height: 27px")
        span.add_style("padding: 5px")

        button_div = DivWdg()
        span.add(button_div)
        button_div.add_style("float: left")
        button_div.add_style("margin-right: 10px")


        table = Table()
        button_div.add(table)
        table.add_row()

        from tactic.ui.widget import SingleButtonWdg
        refresh = SingleButtonWdg(title="Refresh", icon=IconWdg.REFRESH)
        table.add_cell(refresh)
        refresh.add_style("float: left")
        refresh.add_behavior({
        'type': 'click_up',
        'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_uber_notes_top");
            var tbody = top.getElements('.spt_table_tbody')[2];
            var values = spt.api.Utility.get_input_values(tbody);
            spt.panel.refresh(top, values, false);
        '''
        }) 


        save = SingleButtonWdg(title="Save", icon=IconWdg.SAVE)
        table.add_cell(save)
        save.add_style("float: left")
        save.add_behavior( {
            'type': 'click_up',
            'update_current_only': True,
            'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_uber_notes_top");
            var table = top.getElement(".spt_table");
            bvr.src_el = table;
            spt.dg_table.update_row(evt, bvr)
            '''
        })


        process = SingleButtonWdg(title="Show Processes", icon=IconWdg.PROCESS, show_arrow=True)
        table.add_cell(process)

        from tactic.ui.container import DialogWdg
        process_dialog = DialogWdg(display=False)
        span.add(process_dialog)
        process_dialog.set_as_activator(process)
        process_dialog.add_title("Processes")

        process_div = DivWdg()
        process_dialog.add(process_div)
        #process_div.add_style("padding: 5px")
        process_div.add_color("background", "background")
        process_div.add_color("color", "color")
        process_div.add_border()

        refresh = ActionButtonWdg(title="Refresh")
        refresh.add_style('margin: 0 auto 10px auto')
        process_div.add(refresh)
        refresh.add_behavior( {
        'type': 'click_up',
        'cbjs_action': '''
            var top = bvr.src_el.getParent(".spt_uber_notes_top");
            var tbody = top.getElements('.spt_table_tbody')[2];
            var values = spt.api.Utility.get_input_values(tbody);
            spt.panel.refresh(top, values, false);
        '''
        } )
        process_div.add("<hr/>")


        selected_process_names = []
        step = 0
        
        for idx, value in enumerate(self.process_names):
            checkbox_name = 'note_process_cb'
            if self.child_mode:
                selected_process_names.append(value)
                #break
            cb = CheckboxWdg(checkbox_name, label=value)

           
            cb.persistence = True
            cb.persistence_obj = cb
            key = cb.get_key()
            cb.set_option('value', value)
            #cb.set_persistence()

            cb.add_behavior({
                'type': 'click_up',
                'cbjs_action': '''
                    spt.input.save_selected(bvr, '%s','%s');
                ''' % (checkbox_name, key)
            }) 

            # only 1 is selected in child_mode
            if cb.is_checked():
                selected_process_names.append(value)


            if idx == 0 or idx == 10 * step:
                # add a new inner div
                inner_div = self._get_inner_div()
                process_div.add(inner_div, 'inner%s'%step)
                step += 1
                
            inner_div.add(cb)

            inner_div.add("<br/>")
            

        # if less than 10, make it wider
        if len(self.process_names) < 10:
            inner_div.add_style('width: 100px')

        # add a master private checkbox
        if not self.child_mode:
            checkbox_name = 'note_master_private_cb'
            cb = CheckboxWdg(checkbox_name, label='make notes private')
            cb.persistence = True
            cb.persistence_obj = cb
            key = cb.get_key()
            cb.add_behavior({ 
                'type': 'click_up',
                'propagate_evt': True,
                'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_uber_notes_top");
                    var tbody = top.getElements('.spt_table_tbody')[2];
                    var inputs = spt.api.Utility.get_inputs(tbody,'is_private');
                    for (var i = 0; i < inputs.length; i++)
                        inputs[i].checked = bvr.src_el.checked;
                    spt.input.save_selected(bvr, '%s','%s');
                    '''%(checkbox_name, key)
                    })

            cb_span = DivWdg(cb, css='small')
            cb_span.add_styles('border-left: 1px dotted #bbb; margin-left: 10px')
            span.add(cb_span)

        main_config_view = self._get_main_config(view, selected_process_names)
        
        sobject_dict = {}

        # TODO: do a union all search or by order number = 1
        for value in selected_process_names:
            search = Search('sthpw/note')
            search.add_filter('project_code', Project.get_project_code())
            search.add_filter('context', value)
            search.add_filter('search_type',self.parent_search_type)
            search.add_filter('search_id',self.parent_search_id)
            search.add_order_by('timestamp desc')
            search.add_limit(1)
            sobject = search.get_sobject()
            if sobject:
                sobject_dict[value] = sobject
        #sobjects = search.get_sobjects()
        # virtual sobject for placeholder, we can put more than 1 maybe?
        sobject = SearchType.create('sthpw/note')

        edit_config = self._get_edit_config('edit', selected_process_names)
        edit_configs = {'sthpw/note': edit_config}
        Container.put("CellEditWdg:configs", edit_configs)

        table = TableLayoutWdg(table_id=table_id, search_type='sthpw/note', view='table',
            config=main_config_view, aux_info={'sobjects': sobject_dict, 'parent': self.parent}, mode="simple", show_row_select=False, show_insert=False, show_commit_all=True, show_refresh='false', state={'parent_key': self.search_key} )
        table.set_sobject(sobject)

        top.add(table)


        return super(NoteSheetWdg, self).get_display()



class NoteTableElementWdg(BaseTableElementWdg):

    def get_args_keys(self):
        return {
        'parent_key': 'parent sobject for the notes',
        'name': 'context of the note',
        'is_refresh': 'if it is a refresh',
        'state': 'state for this widget on first draw' 
        }

    def run_init(self):
        self.is_refresh = self.kwargs.get('is_refresh')
        self.parent_key = self.kwargs.get('parent_key')
        if not self.parent_key:
            self.parent_key  = self.state.get('parent_key')
    
    def handle_td(self, td):
        td.add_class("spt_uber_notes")

    def handle_th(self, th, xx):
        th.add_gradient("background", "background", -5, -5)

    def get_display(self):
        self.run_init()

        name = self.get_name()
        if not name:
            name = self.kwargs.get("name")
        if self.is_refresh:
            widget = Widget()
        else:   
            widget = DivWdg()
            self.set_as_panel(widget) 

            widget.add_class("spt_note_top")

            widget.set_attr("spt_name", name)
            widget.set_attr("spt_parent_key", self.parent_key)
            
        web = WebContainer.get_web()
        value = web.get_form_value(name)

        text = TextAreaWdg(name)
        widget.add(text)
        if value:
            text.set_value(value)
        text.add_style("width: 100%")
        text.add_style("min-width: 200")
        text.add_attr("rows", "5")
        text.add_class('spt_note_text')

        color = text.get_color("background", -10);

        text.add_behavior( {
        'type': 'blur',
        'cbjs_action': '''
        var el = bvr.src_el;
        var td = el.getParent(".spt_table_td");
        var tbody = el.getParent(".spt_table_tbody");
        td.setStyle('background-color','#909977');
        td.addClass('spt_value_changed');
        tbody.addClass('spt_value_changed');
        td.setAttribute('spt_input_value', el.value);
        '''
        } )

        action_wdg = self.get_action_wdg(name)
        widget.add(action_wdg)
        return widget

    def get_action_wdg(self, name):
        '''get the action widget for ui option of note entry'''

        note_wdg = DivWdg()
        note_wdg.add_style("padding-top: 3px")

        # note options
        
        option = DivWdg(css='spt_uber_note_option')
        cb = CheckboxWdg('is_private')
        #cb.set_default_checked()

        checkbox_name = 'note_master_private_cb'
        master_cb = CheckboxWdg(checkbox_name)
        if master_cb.is_checked():
            cb.set_default_checked()

        option.add_style('margin-right','5px') 
        option.add_style('float','right') 
       
        option.add(cb)
        option.add('private')
        

        #commit = TextBtnWdg(label='save', size='small')
        commit = ActionButtonWdg(title='save', tip="Save Changes")
        commit.add_style('margin-top: -5px')
        commit.add_style('margin-bottom: 5px')
        commit.add_style('float: right')
        commit.add_behavior({
        'type': 'click_up', 
        'cbjs_action': '''
            var td = bvr.src_el.getParent(".spt_table_td");
            var text = td.getElement(".spt_note_text");
            text.blur();
            spt.dg_table.update_row(evt, bvr);
            td.setStyle('background-color','');
            ''',
        'cell_only': True
        }) 
        #commit.set_scale("0.75")
        
        
        

        # do some gynastics to handle a refresh.
        if self.parent_wdg:
            info = self.parent_wdg.get_aux_info()
            sobject_dict = info.get('sobjects')
            sobject = sobject_dict.get(self.get_name())
            parent = info.get('parent')
        else:
            sobject = None
            parent = None

        if not sobject:
            
            if self.parent_key:
                parent = SearchKey.get_by_search_key(self.parent_key)
            # get the latest note
            #search_key = self.kwargs.get("search_key")
            #if search_key:
            #    sobject = SearchKey.get_by_search_key(search_key)

            search = Search('sthpw/note')
            search.add_parent_filter(parent)
            search.add_filter('context', name)
            # Make the assumption that the last one entered is by timestamp
            search.add_order_by('timestamp desc')
            sobject = search.get_sobject()


        # Show a history of notes
        if sobject:
            history = ActionButtonWdg(title='history', tip="Show note history")
            #history = TextBtnWdg(label='history', size='small')
            #history.get_top_el().add_style("margin-left: 4px")
            #history.get_top_el().add_style('float: left')
            history.add_style("float: left")
            history.add_style("margin-top: -5px")
            history.add_style("margin-bottom: 5px")
            note_wdg.add(history)

            self.parent_key = SearchKey.get_by_sobject(parent)
            
            context = name
            filter = '[{"prefix":"main_body","main_body_enabled":"on","main_body_column":"context","main_body_relation":"is","main_body_value":"%s"}]' % context
            history.add_behavior( {
                'type': 'click_up',
                'cbjs_action': "spt.popup.get_widget(evt, bvr)",
                'options': {
                    'class_name': 'tactic.ui.panel.ViewPanelWdg',
                    'title': 'Notes History',
                    'popup_id': 'Notes_History_%s'%context 
                },
                'args': {
                    'search_type': 'sthpw/note',
                    'view': 'summary',
                    'parent_key': self.parent_key,
                    'filter': filter,

                }
            } )

        
        note_wdg.add(commit)
        note_wdg.add(option)
   
        note_wdg.add("<br clear='all'/>")
        
        from pyasm.biz import PrefSetting
        quick_text = PrefSetting.get_value_by_key('quick_text')
        if quick_text: 
            quick_sel = SelectWdg('quick_text', label='quick: ')  
            quick_sel.set_option('values',quick_text)
            quick_sel.add_empty_option('-- text --', '')
            quick_sel.add_behavior({'type': 'change', 
            'cbjs_action': '''var val = bvr.src_el.value; 
            var text=bvr.src_el.getParent('.spt_note_top').getElement('.spt_note_text')
            text.value = text.value + val;
            '''})

        
            note_wdg.add(SpanWdg(quick_sel, css='small'))
            note_wdg.add(HtmlElement.br(2))
        # Show the last note
        note_wdg.add("<i>Last note</i> ")

        if sobject:
            timestamp = sobject.get_value("timestamp")
            timestamp = parser.parse(timestamp)
            timestamp = timestamp.strftime("%m/%d %H:%M")
            timestamp_div = SpanWdg()
            timestamp_div.add( "(%s)" % timestamp)
            note_wdg.add( timestamp_div)
            timestamp_div.add_style("font-size: 11px")
            timestamp_div.add_style("font-style: italic")

            # add a private tag
            access = sobject.get_value("access")
            if access == 'private':
                private = SpanWdg()
                #private.add_style('float: right')
                private.add(" &nbsp; <i>-- private --</i>")
                note_wdg.add(private)


        hr = DivWdg("<hr/>")
        hr.add_style("height: 1px")
        hr.add_style("margin-top: -5px")
        note_wdg.add(hr)

        div = DivWdg()
        note_wdg.add(div)
        div.add_style("max-height", "50px")
        div.add_style("overflow", "auto")
        div.add_style("padding: 3px")
        if sobject:
            value = sobject.get_value('note')
            from pyasm.web import WikiUtil
            value = WikiUtil().convert(value)
            div.add(value)

        else:
            no_notes = DivWdg()
            div.add(no_notes)
            no_notes.add('<i> -- No Notes --</i>')
            no_notes.add_style("font-size: 11px")
            no_notes.add_style("opacity: 0.7")


        return note_wdg
       
    def is_editable(cls):
        '''Determines whether this element is editable'''
        return False
    is_editable = classmethod(is_editable)

class NoteViewerWdg(BaseRefreshWdg):

    ARGS_KEYS = {
        'view': {
            'order': '1',
            'type': 'TextWdg',
            'description': "view for the note table"
        },
        'append_context': {
            'order': '2',
            'type': 'TextWdg',
            'description': "append contexts separated by |"
        }

    }

    def init(self):
        # for snapshot and task
        #      self.child_mode = self.kwargs.get('child_mode') == 'true'
        self.parent_key = self.kwargs.get('parent_key')
        self.append_context = self.kwargs.get('append_context')
        self.is_refresh = self.kwargs.get('is_refresh') == 'true'
        self.view = self.kwargs.get('view')
        if not self.view:
            self.view = 'table'

        self.orig_parent = None
        self.use_parent = False 
        incoming_process = False
      
        if self.parent_key:
         
            self.parent = Search.get_by_search_key(self.parent_key)
            self.orig_parent = self.parent
            self.orig_parent_search_type = self.parent.get_search_type()


            self.parent_search_type = self.parent.get_search_type()
            self.parent_search_id = self.parent.get_id()
        else:
            self.parent_search_type = self.kwargs.get('search_type')
            self.orig_parent_search_type = self.parent_search_type

            self.parent_search_id = self.kwargs.get('search_id')
            self.parent = Search.get_by_id(self.parent_search_type, self.parent_search_id)
            self.orig_parent = self.parent
            if self.use_parent:
                self.parent = self.parent.get_parent()
                if not self.parent:
                    raise TacticException('Try not to use the display option [use_parent] since the parent cannot be found.')
            if self.parent:
                self.parent_key = SearchKey.get_by_sobject(self.parent)   
            if self.use_parent:
                self.kwargs['parent_key'] = self.parent_key
                self.kwargs['use_parent'] = 'false'

        self.process_names = []
        self.checked_processes = []
        # get the process names
        web = WebContainer.get_web()
        process_names = web.get_form_values('process_names')
        #process_names = self.kwargs.get('process_names')
        if not process_names:
            if self.orig_parent_search_type in ['sthpw/task','sthpw/snapshot']:
                #self.parent = self.parent.get_parent()
                # most tasks don't have context by default
                if self.orig_parent_search_type == 'sthpw/task':
                    context = self.orig_parent.get_value('context')
                    if not context:
                        context = self.orig_parent.get_value('process')
                else:
                    context = self.orig_parent.get_value('context')
                self.process_names = [context]
                self.child_mode = True
                self.kwargs['child_mode'] = 'true'

            else:
                self.pipeline_code = self.kwargs.get('pipeline_code')
                if not self.pipeline_code and self.parent.has_value('pipeline_code'):
                    self.pipeline_code = self.parent.get_value('pipeline_code')
                pipeline = Pipeline.get_by_code(self.pipeline_code)
                if pipeline:
                    self.process_names = pipeline.get_process_names()
        else:
            self.process_names = process_names
            incoming_process = True



        # if nothing is derived from pipeline, use defualts
        if not self.process_names: 
            self.process_names = ['default']
        if self.append_context and not incoming_process:
            contexts = self.append_context.split('|')
            self.process_names.extend(contexts)
           
        # for proper refresh
        #self.kwargs['process_names'] = '|'.join(self.process_names)

    def get_viewer(self):
        top = DivWdg(css='spt_note_viewer_top')
            
        # draw checkbox options
        swap = SwapDisplayWdg()
        title = SpanWdg('main context')

        split_div = FloatDivWdg(css='spt_split_cb')
        div = DivWdg(css='spt_main_context_cb')
        content_div = DivWdg()
        content_div.add_color('color','color')
        content_div.add_style('padding: 10px') 
        SwapDisplayWdg.create_swap_title(title, swap, content_div, is_open=False)
        div.add(swap)

        div.add(title)

        checkbox_name = 'split_screen'
        split_cb = CheckboxWdg(checkbox_name, label='Split View')
        split_cb.persistence = True
        split_cb.persistence_obj = split_cb
        key = split_cb.get_key()
      
        #cb.add_style('float: left') 
        split_cb.add_behavior({'type': 'click_up',
        
                'propagate_evt': True,
                'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_note_viewer_top");
                    var table_top = top.getElement(".spt_note_viewer_table");

                    var cbs = top.getElement('.spt_main_context_cb');
                    var values = spt.api.Utility.get_input_values(cbs);

                    var processes = values.note_context_cb;
                    var kwargs = { process_names: processes};
                    if (bvr.src_el.checked) {
		        kwargs.split_view = 'true';
			kwargs.show_context = 'true';
                        kwargs.left_process_names = processes;
                        kwargs.right_process_names = processes;
                   
                    }

                    spt.input.save_selected(bvr, '%s','%s');
                    spt.app_busy.show("Note Viewer", 'Loading') ;
                    setTimeout(function(){
                        spt.panel.refresh(table_top, kwargs, false);
                        if (bvr.src_el.checked) 
                            spt.hide(cbs);
                        else 
                            spt.show(cbs);
                        spt.app_busy.hide();
                        }, 50 );
                    
                ''' % ( checkbox_name, key)
                })
       	split_div.add(split_cb)
        
        top.add(split_div)
        top.add(div)
        div.add(content_div)
        top.add(HtmlElement.br())
        
        
        checkbox_name = 'note_main_context_cb'
        cb = CheckboxWdg(checkbox_name)
        cb.persistence = True
        cb.persistence_obj = cb

        self.checked_process_names = cb.get_values()
        
        for value in self.process_names:
            #self.checked_process_names = web.get_form_values('process_names')
            cb = CheckboxWdg(checkbox_name, label=value)
            
            if value in self.checked_process_names:
                self.checked_processes.append(value)
            # FIXME: this is very tenous.  Accessing private members to
            # override behavior
            
            cb.persistence = True
            cb.persistence_obj = cb
            key = cb.get_key()
            cb.set_option('value', value)

            cb.add_behavior({
                'type': 'click_up',
                'propagate_evt': True,
                'cbjs_action': '''
                    var top = bvr.src_el.getParent(".spt_note_viewer_top")
                    var table_top = top.getElement('.spt_note_viewer_table');
                    var cbs = top.getElement('.spt_main_context_cb');
                    var values = spt.api.Utility.get_input_values(cbs);
                   
                    var processes = values.note_main_context_cb;
                    var kwargs = { process_names: processes};
                    spt.input.save_selected(bvr, '%s','%s');
                    spt.panel.refresh(table_top, kwargs, false);
                ''' % (checkbox_name, key)
            }) 
            content_div.add(cb)

        table_top = DivWdg(css='spt_note_viewer_table')
        expression = "@SOBJECT(sthpw/note['context','in','%s'])" %'|'.join(self.checked_processes)

        if split_cb.is_checked():
            table = self.get_split_viewer()
        else:
            table_id = 'main_table1'
        
            table = TableLayoutWdg(table_id=table_id, search_type='sthpw/note', view=self.view,\
                 show_row_select=True, show_insert=False, state={'parent_key': self.parent_key}, inline_search=False, show_refresh=True, expression=expression )
        
        self.set_as_panel(table_top)
        table_top.add_style('float: left')
    
        top.add(table_top)
        table_top.add(table)

        return top

    def get_split_viewer(self):
        table = Table()
        table.add_row()
        td = table.add_cell()
        inner_wdg = SingleNoteViewerWdg(processes_names=self.process_names, parent_key=self.kwargs.get('parent_key'), resize='true', checkbox_name = 'left_context_cb', show_context='true', append_context=self.append_context, view=self.view)
        td.add(inner_wdg)

        td = table.add_cell()
        inner_wdg = SingleNoteViewerWdg(processes_names=self.process_names, parent_key=self.kwargs.get('parent_key'), resize='true', checkbox_name = 'right_context_cb', show_context='true', append_context=self.append_context, view=self.view)
        td.add(inner_wdg)
        return table
      
    
    def get_display(self):
        if self.is_refresh:
            top = Widget()
            self.add(top)
            web = WebContainer.get_web()
            self.checked_processes = web.get_form_values('process_names')
            left_checked_processes = web.get_form_values('left_process_names')
            right_checked_processes = web.get_form_values('right_process_names')
            is_split_view = web.get_form_value('split_view') == 'true'
        else:
            top = self.get_viewer()
            
            
            

       

        if self.is_refresh:
            if is_split_view:
               viewer = self.get_split_viewer()
               top.add(viewer)
            else:
               inner_wdg = SingleNoteViewerWdg(processes_names=self.process_names, parent_key=self.kwargs.get('parent_key'), resize='false', append_context=self.append_context, view=self.view)
               top.add(inner_wdg)
                
        return top


class SingleNoteViewerWdg(BaseRefreshWdg):

    def init(self):
        web = WebContainer.get_web()
        self.parent_key = self.kwargs.get('parent_key')
        self.append_context = self.kwargs.get('append_context')
        self.is_refresh = self.kwargs.get('is_refresh') == 'true'
        self.resize = self.kwargs.get('resize') =='true'
        self.checkbox_name = self.kwargs.get('checkbox_name')
        self.orig_parent = None
        self.show_context = self.kwargs.get('show_context') 
        if not self.show_context:
            self.show_context = web.get_form_value('show_context')
  
        self.show_context = self.show_context =='true'
        self.view = self.kwargs.get('view')


        incoming_process = False
      
        if self.parent_key:
            self.parent = Search.get_by_search_key(self.parent_key)
            self.orig_parent = self.parent
            self.orig_parent_search_type = self.parent.get_search_type()

            self.parent_search_type = self.parent.get_search_type()
            self.parent_search_id = self.parent.get_id()
        else:
            self.parent_search_type = self.kwargs.get('search_type')
            self.orig_parent_search_type = self.parent_search_type

            self.parent_search_id = self.kwargs.get('search_id')
            self.parent = Search.get_by_id(self.parent_search_type, self.parent_search_id)
            self.orig_parent = self.parent
            if self.use_parent:
                self.parent = self.parent.get_parent()
                if not self.parent:
                    raise TacticException('Try not to use the display option [use_parent] since the parent cannot be found.')
            if self.parent:
                self.parent_key = SearchKey.get_by_sobject(self.parent)   
            if self.use_parent:
                self.kwargs['parent_key'] = self.parent_key
                self.kwargs['use_parent'] = 'false'

        self.process_names = []
        self.checked_processes = []
        # get the process names
        process_names = web.get_form_values('process_names')
        #process_names = self.kwargs.get('process_names')
        
        if not process_names:
            if self.orig_parent_search_type in ['sthpw/task','sthpw/snapshot']:
                #self.parent = self.parent.get_parent()
                # most tasks don't have context by default
                if self.orig_parent_search_type == 'sthpw/task':
                    context = self.orig_parent.get_value('context')
                    if not context:
                        context = self.orig_parent.get_value('process')
                else:
                    context = self.orig_parent.get_value('context')
                self.process_names = [context]
                self.child_mode = True
                self.kwargs['child_mode'] = 'true'

            else:
                self.pipeline_code = self.kwargs.get('pipeline_code')
                if not self.pipeline_code and self.parent.has_value('pipeline_code'):
                    self.pipeline_code = self.parent.get_value('pipeline_code')
                pipeline = Pipeline.get_by_code(self.pipeline_code)
                if pipeline:
                    self.process_names = pipeline.get_process_names()
        else:
            self.process_names = process_names
            incoming_process = True


        # if nothing is derived from pipeline, use defualts
        if not self.process_names: 
            self.process_names = ['default']
        if self.append_context and not incoming_process:
            contexts = self.append_context.split('|')
            self.process_names.extend(contexts)
           
        # for proper refresh
        #self.kwargs['process_names'] = '|'.join(self.process_names)


    def get_viewer(self):
        top = DivWdg(css='spt_single_note_viewer_top')
            
        # draw checkbox options
        swap = SwapDisplayWdg()
        title = SpanWdg('context')
        title.add_color('color','color')
        div = DivWdg(css='spt_context_cb')
        div.add_color('color','color')
        SwapDisplayWdg.create_swap_title(title, swap, div, is_open=False)
        
        checkbox_name = 'split_screen'
        checked_process_names = []
        if self.show_context:
            top.add(swap)
            top.add(title)
            top.add(div)
            
            #checkbox_name = 'note_context_cb'
            checkbox_name = self.checkbox_name
            cb = CheckboxWdg(checkbox_name)
            cb.persistence = True
            cb.persistence_obj = cb

            checked_process_names = cb.get_values()
            for value in self.process_names:
                #self.checked_process_names = web.get_form_values('process_names')
                cb = CheckboxWdg(checkbox_name, label=value)
                
                if value in checked_process_names:
                    self.checked_processes.append(value)
                # FIXME: this is very tenous.  Accessing private members to
                # override behavior
                
                cb.persistence = True
                cb.persistence_obj = cb
                key = cb.get_key()
                cb.set_option('value', value)

                cb.add_behavior({
                    'type': 'click_up',
                    'propagate_evt': True,
                    'cbjs_action': '''
                        var top = bvr.src_el.getParent(".spt_single_note_viewer_top")
                        var table_top = top.getElement('.spt_note_viewer_table');
                        var cbs = top.getElement('.spt_context_cb');
                        var values = spt.api.Utility.get_input_values(cbs);
                        var processes = values.%s;
                        var kwargs = { process_names: processes};
                        spt.input.save_selected(bvr, '%s','%s');
                        spt.panel.refresh(table_top, kwargs, false);
                    ''' % (checkbox_name, checkbox_name, key)
                }) 
                div.add(cb)
        else:
            web = WebContainer.get_web()
            checked_process_names = web.get_form_values('process_names')
        table_top = DivWdg(css='spt_note_viewer_table')
        expression = "@SOBJECT(sthpw/note['context','in','%s'])" %'|'.join(checked_process_names)
        table_id = 'main_table1'
    
        table = TableLayoutWdg(table_id=table_id, search_type='sthpw/note', view=self.view,\
             show_row_select=True, show_insert=False, state={'parent_key': self.parent_key}, inline_search=False, show_refresh=True, expression=expression )
        if self.resize:
            from tactic.ui.container import ResizeScrollWdg
            inner_wdg = ResizeScrollWdg( width='500px', height='500px', scroll_bar_size_str='thick', scroll_expansion='inside' )
            inner_wdg.add(table)
            table_top.add(inner_wdg)
        else:
            table_top.add(table)

        self.set_as_panel(table_top)
        top.add(table_top)

        return top


    def get_display(self):
        if self.is_refresh:
            top = Widget()
            self.add(top)
            web = WebContainer.get_web()
            self.checked_processes = web.get_form_values('process_names')
            left_checked_processes = web.get_form_values('left_process_names')
            right_checked_processes = web.get_form_values('right_process_names')
            is_split_view = web.get_form_values('split_view') == 'true'
        else:
            top = self.get_viewer()
            
       
        self.process_names = [x  for x in self.process_names if x ]
        if self.is_refresh:
            if self.process_names:
                table = Table()
                table.add_row()
                td = table.add_cell()
                expression = "@SOBJECT(sthpw/note['context','in','%s'])" %'|'.join(self.process_names)
                table_id = 'main_table_left'
        
                left_table = TableLayoutWdg(table_id=table_id, search_type='sthpw/note', view=self.view,\
                    show_row_select=True, show_insert=False, state={'parent_key': self.parent_key}, inline_search=False, show_refresh=True, expression=expression )
                if self.resize:
                    from tactic.ui.container import ResizeScrollWdg
                    inner_wdg = ResizeScrollWdg( width='500px', height='500px', scroll_bar_size_str='thick', scroll_expansion='inside' )
                    inner_wdg.add(left_table)
                    td.add(inner_wdg)
                else:
                    td.add(left_table)
                top.add(table)
		
        return top
